import asyncio
import collections
import contextlib
import contextvars
import inspect
import logging
import os
from typing import Callable, cast

logger = logging.getLogger(__name__)


def assert_handler_is_coroutine(handler: Callable) -> None:
    if not inspect.iscoroutinefunction(handler):
        raise TypeError(f"{handler!r} must be coroutine functions")


def assert_handler_kwargs_only(handler: Callable) -> None:
    positional_only = []
    positional_or_keyword = []

    for parameter_name, parameter in inspect.signature(handler).parameters.items():
        if parameter.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
            positional_or_keyword.append(parameter_name)

        elif parameter.kind in {
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.VAR_POSITIONAL,
        }:
            positional_only.append(parameter_name)

    if positional_only:
        raise TypeError(
            f"{handler!r} has positional-only parameters {positional_only} that are not supported"
        )

    if positional_or_keyword:
        logger.warning(
            "%s has positional parameters %s, only keyword parameters are supported",
            handler,
            positional_or_keyword,
        )


_timeout_contextvar: contextvars.ContextVar[asyncio.Timeout | None] = (
    contextvars.ContextVar("_timeout_contextvar", default=None)
)


def get_current_timeout() -> float | None:
    current_context_timeout = _timeout_contextvar.get()
    if not current_context_timeout:
        return None

    deadline = cast(float, current_context_timeout.when())

    return max(deadline - asyncio.get_running_loop().time(), 0)


@contextlib.asynccontextmanager
async def timeout(timeout: float | None = None) -> collections.abc.AsyncGenerator:
    if timeout is None:
        # timeout is None, no timeout needed,
        # so we do nothing and emulate nullcontext
        yield
        return

    timeout_obj = asyncio.timeout(timeout)
    current_timeout_obj = _timeout_contextvar.get()
    if current_timeout_obj and (
        cast(float, current_timeout_obj.when()) <= cast(float, timeout_obj.when())
    ):
        # timeout had been already set, so
        # we compare new incoming and existing timeout,
        # when new timeout is bigger we do noting and emulate nullcontext
        yield
        return

    async with timeout_obj:
        # we enforce and set timeout
        token = _timeout_contextvar.set(timeout_obj)

        try:
            yield
        finally:
            _timeout_contextvar.reset(token)


def max_timeout() -> asyncio.Timeout:
    ack_timeout = int(os.getenv("DELPHAI_RPC_RABBITMQ_ACK_TIMEOUT_SECONDS") or 30 * 60)

    # Should be at least 1 minute less than the RabbitMQ `consumer_timeout` value.
    # Reference: https://www.rabbitmq.com/docs/consumers#acknowledgement-timeout
    # Default is 29 minutes, while RabbitMQ `consumer_timeout` defaults to 30 minutes.
    max_timeout = max(ack_timeout - 60, 0)

    return asyncio.timeout(max_timeout)
