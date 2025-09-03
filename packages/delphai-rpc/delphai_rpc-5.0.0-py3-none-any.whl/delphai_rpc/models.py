import contextlib
import logging
import uuid
from typing import Any, ClassVar, Self

import msgpack
import pydantic

from . import errors

logger = logging.getLogger(__name__)


class BaseModel(pydantic.BaseModel):
    type: ClassVar[str]

    def model_dump_msgpack(self, **kwargs: Any) -> bytes:
        kwargs.setdefault("exclude_defaults", True)
        data = self.model_dump(**kwargs)
        return msgpack.dumps(data, datetime=True, default=_msgpack_default)

    def model_dump_message(self, **kwargs: Any) -> dict[str, Any]:
        return {
            "body": self.model_dump_msgpack(**kwargs),
            "content_type": "application/msgpack",
            "type": self.type,
        }

    @classmethod
    def model_validate_msgpack(cls, body: bytes) -> Self:
        try:
            return cls.model_validate(
                msgpack.loads(
                    body,
                    timestamp=3,
                    ext_hook=_msgpack_ext_hook,
                    strict_map_key=False,
                )
            )
        except ValueError as error:
            raise errors.BadMessageError(f"Message deserialization failed: `{error!r}`")

    @classmethod
    def model_validate_message(
        cls,
        body: bytes,
        message_type: str,
        content_type: str | None = None,
        **kwargs: Any,
    ) -> Self:
        if message_type != cls.type:
            raise errors.BadMessageError(f"Wrong message type `{message_type}`")

        if content_type != "application/msgpack":
            raise errors.BadMessageError(
                f"Got a message with unknown content type: {content_type}"
            )

        return cls.model_validate_msgpack(body=body)


class Request(BaseModel):
    type = "rpc.request"
    method_name: str
    arguments: dict[str, Any] = {}
    context: Any | None = None
    timings: list[tuple[str, float]] = []


class ResponseError(pydantic.BaseModel):
    type: str
    message: str | None = None


class Response(BaseModel):
    type = "rpc.response"
    result: Any | None = None
    error: ResponseError | None = None
    context: Any = None
    timings: list[tuple[str, float]] = []

    @classmethod
    def build_from_error(cls, error: Exception) -> Self:
        if isinstance(error, errors.RpcError):
            return cls(
                error=ResponseError(
                    type=type(error).__name__,
                    message=error.args[0],
                )
            )

        return cls(
            error=ResponseError(
                type="UnhandledError",
                message=repr(error),
            )
        )


ObjectId: Any = None
with contextlib.suppress(ImportError):
    from bson import ObjectId


MSGPACK_EXT_TYPE_OBJECT_ID = 1
MSGPACK_EXT_TYPE_UUID = 2


def _msgpack_default(obj: Any) -> msgpack.ExtType:
    if ObjectId and isinstance(obj, ObjectId):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_OBJECT_ID, obj.binary)

    if isinstance(obj, uuid.UUID):
        return msgpack.ExtType(MSGPACK_EXT_TYPE_UUID, obj.bytes)

    raise TypeError(f"Cannot serialize {obj!r}")


def _msgpack_ext_hook(code: int, data: bytes) -> Any:
    if code == MSGPACK_EXT_TYPE_OBJECT_ID:
        if ObjectId is None:
            raise RuntimeError("Install `bson` package to support `ObjectId` type")

        return ObjectId(data)

    if code == MSGPACK_EXT_TYPE_UUID:
        return uuid.UUID(bytes=data)

    return msgpack.ExtType(code, data)
