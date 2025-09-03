import asyncio
import logging
import time
from typing import Any

import tenacity

from . import errors, metrics, utils
from .models import Request, Response
from .queue_client import QueueClient
from .types import AbstractOptions, Priority

logger = logging.getLogger(__name__)


class Options(AbstractOptions):
    timeout: float | None = 60
    priority: Priority | None = None
    no_wait: bool = False
    retry: bool | dict = False


DEFAULT_RETRY_OPTIONS: dict[str, Any] = {
    "wait": tenacity.wait_fixed(1) + tenacity.wait_random_exponential(max=60),
    "retry": tenacity.retry_if_exception_type(errors.RetryableError),
    "reraise": True,
}


class RpcClient:
    def __init__(
        self,
        queue_client: QueueClient,
        *args: Options,
        **kwargs: Any,
    ) -> None:
        self._queue_client = queue_client
        self._options = Options(*args, **kwargs)

    def get_service(
        self,
        service_name: str,
        *args: Options,
        **kwargs: dict[str, Any],
    ) -> "RpcService":
        options = self._options.update(*args, **kwargs)
        return RpcService(self, service_name, options)

    async def call(
        self,
        *,
        service_name: str,
        method_name: str,
        arguments: dict[str, Any] | None = None,
        options: Options | dict | None = None,
    ) -> Any:
        if not options:
            options = self._options

        elif isinstance(options, Options):
            options = self._options.update(options)

        else:
            options = self._options.update(**options)

        if options.retry or isinstance(options.retry, dict):
            retry_options = DEFAULT_RETRY_OPTIONS
            if isinstance(options.retry, dict):
                retry_options = dict(retry_options, **options.retry)

            retrying = tenacity.AsyncRetrying(**retry_options)
            do_call = retrying.wraps(self._call)
        else:
            do_call = self._call

        async with utils.timeout(options.timeout):
            return await do_call(
                service_name=self._queue_client.clean_service_name(service_name),
                method_name=method_name,
                arguments=arguments or {},
                options=options,
            )

    async def _call(
        self,
        *,
        service_name: str,
        method_name: str,
        arguments: dict[str, Any],
        options: Options,
    ) -> Any:
        request = Request(method_name=method_name, arguments=arguments)

        with metrics.client_requests_in_progress.labels(
            service=service_name,
            method=method_name,
        ).track_inprogress():
            elapsed = -time.perf_counter()

            try:
                if options.no_wait:
                    # To be removed soon:
                    await self._queue_client.send(
                        **request.model_dump_message(),
                        exchange_name=f"service.{service_name}",
                        routing_key=f"method.{request.method_name}",
                        priority=options.priority,
                        timeout=options.timeout or None,
                    )
                    return None

                response = await self._queue_client.send_and_receive(
                    **request.model_dump_message(),
                    exchange_name=f"service.{service_name}",
                    routing_key=f"method.{request.method_name}",
                    priority=options.priority,
                    timeout=options.timeout or None,
                    handler=Response.model_validate_message,
                )

                if response.error:
                    error_class = getattr(
                        errors, response.error.type, errors.UnknownError
                    )
                    raise error_class(response.error.message)

            except asyncio.CancelledError:
                if utils.get_current_timeout() != 0:
                    logger.warning(
                        "Wait was cancelled but not the request itself. "
                        "Pass `timeout` option instead of using `asyncio.wait_for` or similar"
                    )
                raise
            else:
                return response.result

            finally:
                elapsed += time.perf_counter()

                metrics.client_request_processed(
                    priority=options.priority or 0,
                    service=service_name,
                    method=method_name,
                    elapsed=elapsed,
                )


class RpcService:
    def __init__(self, client: RpcClient, service_name: str, options: Options) -> None:
        self._client = client
        self._service_name = service_name
        self._options = options

    def __getattr__(
        self,
        method_name: str,
        *args: Options,
        **kwargs: dict[str, Any],
    ) -> "RpcMethod":
        options = self._options.update(*args, **kwargs)
        return RpcMethod(self._client, self._service_name, method_name, options)

    get_method = __getattr__

    def __repr__(self) -> str:
        class_ = self.__class__
        return f"<{class_.__qualname__} `{self._service_name}`>"


class RpcMethod:
    def __init__(
        self,
        client: RpcClient,
        service_name: str,
        method_name: str,
        options: Options,
    ) -> None:
        self._client = client
        self._service_name = service_name
        self._method_name = method_name
        self._options = options

    def __repr__(self) -> str:
        class_ = self.__class__
        return (
            f"<{class_.__qualname__} `{self._method_name}` "
            "of service `{self._service_name}`>"
        )

    def __call__(self, *args: Options, **kwargs: Any) -> Any:
        options = self._options.update(*args)
        return self._client.call(
            service_name=self._service_name,
            method_name=self._method_name,
            arguments=kwargs,
            options=options,
        )
