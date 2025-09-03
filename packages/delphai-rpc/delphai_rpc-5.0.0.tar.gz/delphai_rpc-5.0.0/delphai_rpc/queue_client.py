import asyncio
import contextvars
import functools
import importlib.metadata
import inspect
import logging
import re
import socket
import time
import uuid
import zlib
from typing import Any, Callable, cast

import aio_pika
import aio_pika.exceptions
import zstandard
from aio_pika import IncomingMessage, Message
from aio_pika.abc import (
    AbstractConnection,
    AbstractIncomingMessage,
    AbstractRobustChannel,
    AbstractRobustConnection,
    AbstractRobustExchange,
    AbstractRobustQueue,
    ConsumerTag,
)
from aio_pika.connection import URL

from . import errors, metrics, types, utils

logger = logging.getLogger(__name__)


HOST_NAME = socket.gethostname()
PACKAGE_NAME = __package__.split(".")[0]
PACKAGE_VERSION = importlib.metadata.version(PACKAGE_NAME)

COMPRESS_MIN_SIZE = 1024 * 10
COMPRESS_MIN_RATE = 0.7

CONTENT_DECODERS: dict[str, Callable[[bytes], bytes]] = {
    "deflate": zlib.decompress,
    "zstd": zstandard.decompress,
}

SERVICE_NAME_RE = re.compile(r"[^a-z0-9-]+")


priority_contextvar: contextvars.ContextVar[int | None] = contextvars.ContextVar(
    "priority_contextvar", default=types.Priority.DEFAULT.value
)


class QueueClient:
    def __init__(self, service_name: str, connection_string: str | URL) -> None:
        self.service_name = self.clean_service_name(service_name)
        self.app_id = f"{self.service_name}@{HOST_NAME}"

        connection_url = aio_pika.connection.make_url(connection_string)
        if not connection_url.query.get("name"):
            connection_url %= {
                "name": f"{self.service_name} ({PACKAGE_NAME} v{PACKAGE_VERSION})"
            }
        self._connection_url = connection_url

        self._lock = asyncio.Lock()

        self._reset()

    @staticmethod
    def clean_service_name(service_name: str) -> str:
        return SERVICE_NAME_RE.sub("-", service_name.strip().lower())

    def _reset(self) -> None:
        self._connection: AbstractRobustConnection | None = None

        self._channels: dict[str, AbstractRobustChannel] = {}
        self._exchanges: dict[str, AbstractRobustExchange] = {}
        self._queues: dict[str, tuple[AbstractRobustQueue, ConsumerTag]] = {}
        self._instance_queue: tuple[AbstractRobustQueue, ConsumerTag] | None = None
        self._instance_channel: AbstractRobustChannel | None = None
        self._tasks: set[asyncio.Task] = set()
        self._reply_futures: dict[str, asyncio.Future] = {}

    def _track_current_task(self) -> None:
        current_task = asyncio.current_task()
        assert current_task

        self._tasks.add(current_task)
        current_task.add_done_callback(self._tasks.discard)

    async def _ensure_connection(self) -> None:
        async with self._lock:
            if self._connection:
                return

            self._connection = await aio_pika.connect_robust(self._connection_url)
            self._connection.close_callbacks.add(self._on_connection_close)

    async def _create_channel(self) -> AbstractRobustChannel:
        assert self._connection

        return cast(
            AbstractRobustChannel,
            await self._connection.channel(
                # raise an DeliveryError when mandatory message will be returned
                on_return_raises=True,
            ),
        )

    async def _ensure_channel(self, name: str = "") -> AbstractRobustChannel:
        await self._ensure_connection()

        async with self._lock:
            if not name:
                if not self._instance_channel:
                    self._instance_channel = await self._create_channel()

                return self._instance_channel

            else:
                if name not in self._channels:
                    self._channels[name] = await self._create_channel()

                return self._channels[name]

    async def _on_connection_close(
        self,
        connection: AbstractConnection | None = None,
        exc: BaseException | None = None,
    ) -> None:
        if self._tasks:
            for task in self._tasks:
                task.cancel()
            await asyncio.gather(*self._tasks, return_exceptions=True)

    async def stop(self) -> None:
        try:
            queues = tuple(self._queues.items())
            for queue_name, (queue, consumer_tag) in queues:
                await queue.cancel(consumer_tag=consumer_tag)
                del self._queues[queue_name]
        except aio_pika.exceptions.ChannelInvalidStateError:
            for task in self._tasks:
                task.cancel()

        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)

        connection = self._connection
        if connection:
            self._reset()
            await connection.close()

    async def send(
        self,
        *,
        body: bytes,
        content_type: str | None = None,
        exchange_name: str = "",
        routing_key: str = "",
        priority: int | None = None,
        timeout: float | None = None,
        type: str | None = None,
        reply_to: str | None = None,
        _correlation_id: str | None = None,
    ) -> None:
        async with utils.timeout(timeout):
            if utils.get_current_timeout() == 0:
                return

            if reply_to == "":
                reply_to = await self._declare_consume_instance_queue()

            content_encoding = None
            if len(body) > COMPRESS_MIN_SIZE:
                loop = asyncio.get_running_loop()
                compressed = await loop.run_in_executor(None, zlib.compress, body)
                if len(compressed) < len(body) * COMPRESS_MIN_RATE:
                    body = compressed
                    content_encoding = "deflate"
                del compressed

            if priority is None:
                priority = priority_contextvar.get()
            assert priority is not None

            message = Message(
                body=body,
                content_type=content_type,
                content_encoding=content_encoding,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                priority=int(priority),
                expiration=utils.get_current_timeout(),
                message_id=str(uuid.uuid1()),
                timestamp=time.time(),
                type=type,
                app_id=self.app_id,
                correlation_id=_correlation_id,
                reply_to=reply_to,
            )
            if message.expiration == 0:
                return

            exchange = await self._get_exchange(exchange_name)

            try:
                await exchange.publish(
                    message=message,
                    routing_key=routing_key,
                )
            except aio_pika.exceptions.PublishError:
                raise errors.UnknownServiceError("Message was not delivered to a queue")

            metrics.message_published(
                message, exchange=exchange_name, routing_key=routing_key
            )

    async def send_and_receive(
        self,
        *,
        body: bytes,
        content_type: str | None = None,
        exchange_name: str = "",
        routing_key: str = "",
        priority: int | None = None,
        timeout: float | None = None,
        type: str | None = None,
        handler: Callable = dict,
    ) -> Any:
        correlation_id = str(uuid.uuid1())
        future = asyncio.get_running_loop().create_future()
        self._reply_futures[correlation_id] = future
        try:
            async with utils.timeout(timeout):
                await self.send(
                    body=body,
                    content_type=content_type,
                    exchange_name=exchange_name,
                    routing_key=routing_key,
                    priority=priority,
                    timeout=timeout,
                    type=type,
                    reply_to="",
                    _correlation_id=correlation_id,
                )

                message = await future
                return await self._call_handler(message, handler)
        finally:
            self._reply_futures.pop(correlation_id, None)

    async def _get_exchange(self, exchange_name: str) -> AbstractRobustExchange:
        channel = await self._ensure_channel()

        async with self._lock:
            if not exchange_name:
                return cast(AbstractRobustExchange, channel.default_exchange)

            if exchange_name not in self._exchanges:
                try:
                    self._exchanges[exchange_name] = cast(
                        AbstractRobustExchange,
                        await channel.get_exchange(exchange_name),
                    )
                except aio_pika.exceptions.ChannelNotFoundEntity:
                    raise errors.UnknownServiceError(
                        f"Exchange `{exchange_name}` was not found"
                    )
            return self._exchanges[exchange_name]

    async def _declare_consume_instance_queue(self) -> str:
        channel = await self._ensure_channel()

        async with self._lock:
            if self._instance_queue is not None:
                queue, _ = self._instance_queue
                return queue.name

            queue = await channel.declare_queue(
                name=f"instance.{self.service_name}.{uuid.uuid4().hex}",
                exclusive=True,
                auto_delete=True,
            )
            consumer_tag = await queue.consume(callback=self._on_message_instance_queue)
            self._instance_queue = (queue, consumer_tag)

            return queue.name

    async def _on_message_instance_queue(
        self,
        message: AbstractIncomingMessage,
    ) -> None:
        assert isinstance(message, IncomingMessage)
        self._track_current_task()

        future = self._reply_futures.pop(message.correlation_id or "", None)
        if not future or future.done():
            logger.warning(
                "[MID:%s] [CID:%s] Missing, unknown or delayed correlation_id",
                message.message_id,
                message.correlation_id,
            )
            await message.reject()
            metrics.message_consumed(message, error="UNKNOWN_CORRELATION_ID")
            return

        future.set_result(message)

    async def declare_consume_named_queue(
        self,
        queue_name: str,
        handler: Callable,
        prefetch_count: int = 1,
    ) -> None:
        channel = await self._ensure_channel(name=queue_name)

        async with self._lock:
            if queue_name in self._queues:
                raise ValueError(f"Queue `{queue_name}` is already declared")

            await channel.set_qos(prefetch_count=prefetch_count)

            exchange = await channel.declare_exchange(
                name=queue_name,
                type=aio_pika.ExchangeType.TOPIC,
                durable=True,
            )
            self._exchanges[exchange.name] = exchange

            queue = await channel.declare_queue(
                name=queue_name,
                durable=True,
                arguments={
                    "x-max-priority": max(types.Priority),
                    "x-dead-letter-exchange": f"{queue_name}.dlx",
                },
            )

            await queue.bind(exchange, "#")
            callback = functools.partial(self._on_message_named_queue, handler=handler)
            consumer_tag = await queue.consume(callback=callback)
            self._queues[queue_name] = (queue, consumer_tag)

    async def _on_message_named_queue(
        self,
        message: AbstractIncomingMessage,
        handler: Callable,
    ) -> None:
        assert isinstance(message, IncomingMessage)

        self._track_current_task()

        if message.priority:
            priority_contextvar.set(message.priority)

        timeout = None
        if message.timestamp and message.expiration:
            timeout = cast(float, message.expiration) - (
                time.time() - message.timestamp.timestamp()
            )

        try:
            async with utils.timeout(timeout):
                return await self._call_handler(message=message, handler=handler)
        except (asyncio.TimeoutError, asyncio.CancelledError) as exc:
            logger.info(
                "[MID:%s] [CID:%s] Execution of `%s` from `%s` - %s",
                message.message_id,
                message.correlation_id,
                message.type,
                message.app_id or "unknown",
                exc,
            )
        except Exception:
            logger.exception("Error in handler")

    async def _call_handler(
        self,
        message: AbstractIncomingMessage,
        handler: Callable,
    ) -> Any:
        assert isinstance(message, IncomingMessage)

        logger.debug(
            "[MID:%s]%s Got `%s` from `%s` app",
            message.message_id,
            f" [CID:{message.correlation_id}]" if message.correlation_id else "",
            message.type,
            message.app_id or "unknown",
        )

        try:
            body = message.body
            content_encoding = message.content_encoding
            if content_encoding:
                try:
                    decoder = CONTENT_DECODERS[content_encoding]
                except KeyError:
                    raise errors.BadMessageError(
                        f"Unknown content_encoding: `{content_encoding}`"
                    )
                else:
                    loop = asyncio.get_running_loop()
                    try:
                        body = await loop.run_in_executor(None, decoder, body)
                    except Exception as error:
                        raise errors.BadMessageError(
                            f"Message decompression failed: `{error!r}`"
                        )

            reply_callback = None
            if message.reply_to:
                reply_callback = functools.partial(
                    self.send,
                    routing_key=message.reply_to,
                    _correlation_id=message.correlation_id,
                )

            result = handler(
                body=body,
                content_type=message.content_type,
                reply_callback=reply_callback,
                message_id=message.message_id,
                message_type=message.type,
                app_id=message.app_id,
                priority=message.priority,
                published_timestamp=(
                    message.timestamp.timestamp() if message.timestamp else None
                ),
            )

            if inspect.isawaitable(result):
                result = await result

        except (Exception, asyncio.CancelledError) as error:
            await message.reject()

            if not isinstance(
                error,
                (
                    asyncio.TimeoutError,
                    asyncio.CancelledError,
                    errors.BadMessageError,
                    errors.RpcError,
                ),
            ):
                error = Exception()

            metrics.message_consumed(message, error=error)
            raise
        else:
            await message.ack()
            metrics.message_consumed(message)

            return result
