import contextlib
import inspect
import logging
import time
from typing import Any, Callable, TypeVar, cast

import pydantic

from . import errors, metrics, utils
from .models import Request, Response
from .queue_client import QueueClient

logger = logging.getLogger(__name__)


TException = TypeVar("TException", bound=Exception)
ExceptionPredicate = Callable[[TException], bool]

IsinstanceType = type[Exception] | tuple[type[Exception]]


class RpcServer:
    def __init__(self, queue_client: QueueClient, service_name: str = "") -> None:
        self._queue_client = queue_client

        if service_name:
            self.service_name = self._queue_client.clean_service_name(service_name)
        else:
            self.service_name = self._queue_client.service_name

        self._prefetch_count = 1
        self._started = False

        self._handlers: dict[str, Callable] = {}
        self._retryable_errors_predicates: list[ExceptionPredicate] = []
        self._retryable_errors_configured = False

        self.bind(self._ping)
        self.bind(self._help)

    def bind(
        self,
        handler: Callable | None = None,
        *,
        name: str | None = None,
    ) -> Callable:
        """
        Binds to be exposed handlers (functions) to RPC server instance:

        @server.bind
        def add(*, a: float, b: float) -> float:
            ...

        # or

        def sub(*, a: float, b: float) -> float:
            ...

        server.bind(sub)

        # or

        @server.bind(name="mul")
        def multiply(*, a: float, b: float) -> float:
            ...

        """

        def decorator(handler: Callable) -> Callable:
            self._bind_handler(handler=handler, name=name)
            return handler

        if handler:
            return decorator(handler)

        return decorator

    def _bind_handler(self, *, handler: Callable, name: str | None = None) -> None:
        handler_name = name or handler.__name__
        if handler_name in self._handlers:
            raise KeyError(f"Handler {handler_name} already defined")

        if hasattr(handler, "raw_function"):
            # Unwrap `pydantic.validate_call` decorator
            handler = handler.raw_function

        utils.assert_handler_is_coroutine(handler)
        utils.assert_handler_kwargs_only(handler)

        self._handlers[handler_name] = pydantic.validate_call(validate_return=True)(
            handler
        )

    @pydantic.validate_call
    def retryable_if(
        self,
        error_types: IsinstanceType | ExceptionPredicate | None = None,
        predicate: ExceptionPredicate | None = None,
    ) -> None:
        """
        Configure which exceptions to mark as retryable.
        `error_types` could be an Exception type, a tuple of of Exception types or a Predicate.
        Predicate could be a callable callable that returns boolean

        The error must match *any* `error_types` *and* predicate same time.

        Examples:

        rpc_server.retryable_if(ConnectionError)

        rpc_server.retryable_if( (ConnectionRefusedError, ConnectionResetError) )

        rpc_server.retryable_if(
            httpx.HTTPStatusError,
            lambda error: 500 <= error.response.status_code < 600
        )

        rpc_server.retryable_if(lambda error: "retry" in str(error))
        """
        if not (error_types or predicate):
            return

        if (
            predicate
            and isinstance(predicate, type)
            and issubclass(predicate, Exception)
        ):
            raise TypeError("`predicate` must be function")

        if not isinstance(error_types, (type, tuple)):
            if predicate:
                raise TypeError("Only one predicate is allowed")

            predicate = error_types
            error_types = None

        is_retryable: ExceptionPredicate

        if error_types and predicate:

            def is_retryable(error: Exception) -> bool:
                assert predicate
                return isinstance(error, error_types) and predicate(error)

        elif error_types:

            def is_retryable(error: Exception) -> bool:
                return isinstance(error, error_types)

        else:
            assert predicate

            predicate = cast(ExceptionPredicate, predicate)
            is_retryable = predicate

        self._retryable_errors_predicates.append(is_retryable)

    def _configure_default_retryable_errors(self) -> None:
        if self._retryable_errors_configured:
            return
        self._retryable_errors_configured = True

        with contextlib.suppress(ImportError):
            import httpx

            self.retryable_if(
                httpx.HTTPStatusError,
                lambda error: error.response.is_server_error,
            )

        with contextlib.suppress(ImportError):
            import requests

            self.retryable_if(
                requests.HTTPError,
                lambda error: 500 <= error.response.status_code < 600,
            )

        with contextlib.suppress(ImportError):
            from torch.cuda import OutOfMemoryError  # type: ignore[import-not-found]

            self.retryable_if(OutOfMemoryError)

        # https://grpc.github.io/grpc/core/md_doc_statuscodes.html
        GRPC_RETRYABLE_CODES = {
            "UNKNOWN",
            "DEADLINE_EXCEEDED",
            "RESOURCE_EXHAUSTED",
            "INTERNAL",
            "UNAVAILABLE",
        }

        with contextlib.suppress(ImportError):
            import grpc

            def if_retryable_grpc(error: Exception) -> bool:
                if not hasattr(error, "code"):
                    return False

                status_code = error.code()

                return status_code.name in GRPC_RETRYABLE_CODES

            self.retryable_if(grpc.RpcError, if_retryable_grpc)

        with contextlib.suppress(ImportError):
            import grpclib

            self.retryable_if(
                grpclib.GRPCError,
                lambda error: error.status.name in GRPC_RETRYABLE_CODES,
            )

    def set_prefetch_count(self, prefetch_count: int) -> None:
        if self._started:
            raise RuntimeError("Prefetch count must be configured before server start")

        self._prefetch_count = prefetch_count

    async def start(self) -> None:
        if self._started:
            raise RuntimeError("Server has been already started")

        self._configure_default_retryable_errors()

        queue_name = f"service.{self.service_name}"

        await self._queue_client.declare_consume_named_queue(
            queue_name=queue_name,
            handler=self._on_message,
            prefetch_count=self._prefetch_count,
        )

        logger.info("RPC server is consuming messages from `%s`", queue_name)
        self._started = True

    async def _on_message(
        self,
        body: bytes,
        content_type: str,
        message_id: str,
        message_type: str,
        app_id: str,
        priority: int,
        published_timestamp: float | None = None,
        reply_callback: Callable | None = None,
    ) -> None:
        consumed_timestamp = time.time()

        try:
            request = Request.model_validate_message(
                body=body,
                content_type=content_type,
                message_type=message_type,
            )
        except Exception as error:
            if reply_callback:
                response = Response.build_from_error(error)
                await reply_callback(**response.model_dump_message())
            raise

        timings = request.timings
        queued_for = None
        if published_timestamp is not None:
            timings.append(("queue.published", published_timestamp))
            queued_for = consumed_timestamp - published_timestamp

        timings.append(
            (
                f"queue.consumed by {self._queue_client.app_id}",
                consumed_timestamp,
            )
        )

        with metrics.server_requests_in_progress.labels(
            method=request.method_name
        ).track_inprogress():
            elapsed = -time.perf_counter()

            try:
                async with utils.max_timeout() as max_timeout:
                    response = await self._process_request(request)
            except TimeoutError:
                if not max_timeout.expired():
                    raise

                response = Response.build_from_error(
                    errors.ExecutionTimeoutLimitError(
                        "The execution timeout limit has been exceeded"
                    )
                )
            except Exception as error:
                response = Response.build_from_error(error)

            elapsed += time.perf_counter()
        timings.append(("execution.completed", consumed_timestamp + elapsed))

        response.context = request.context
        response.timings = timings

        metrics.server_request_processed(
            priority=priority or 0,
            method=request.method_name,
            error=response.error,
            queued_for=queued_for or 0,
            elapsed=elapsed,
        )

        if reply_callback:
            await reply_callback(**response.model_dump_message())

        logger.info(
            "[MID:%s] Processed `%s` from `%s` service to method `%s`. In queue: %ims, execution: %ims, success: %s%s",
            message_id,
            message_type,
            app_id or "unknown",
            request.method_name,
            (None if queued_for is None else max(queued_for * 1000, 0)),
            elapsed * 1000,
            response.error is None,
            (f", error: {response.error.message}" if response.error else ""),
        )

    async def _process_request(self, request: Request) -> Response:
        handler = self._handlers.get(request.method_name)
        if handler is None:
            raise errors.UnknownMethodError(request.method_name)

        try:
            result = await handler(**request.arguments)
        except Exception as error:
            logger.debug(
                "Exception while processing '%s'", request.method_name, exc_info=True
            )
            error_type: type[errors.RpcError] = errors.ExecutionError
            if any(predicate(error) for predicate in self._retryable_errors_predicates):
                error_type = errors.RetryableExecutionError

            raise error_type(repr(error))

        if isinstance(result, pydantic.BaseModel):
            result = result.model_dump()

        return Response(result=result)

    async def _ping(self) -> None:
        return None

    async def _help(self) -> dict[str, Any]:
        """
        Returns methods list
        """
        return {
            "methods": [
                {
                    "method_name": method_name,
                    "signature": f"{method_name}{inspect.signature(handler)}",
                    "description": handler.__doc__,
                }
                for method_name, handler in self._handlers.items()
            ],
        }
