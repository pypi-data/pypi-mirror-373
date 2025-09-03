from dataclasses import dataclass
from enum import IntEnum
from typing import Any, Self, TypeVar

import pydantic

__all__ = [
    "AbstractOptions",
    "Priority",
    "RequestContext",
]


TAbstractOptions = TypeVar("TAbstractOptions", bound="AbstractOptions")


class AbstractOptions(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid", frozen=True)

    def __init__(self, *args: "AbstractOptions", **kwargs: dict[str, Any]) -> None:
        if args:
            merged = {}
            self_class = type(self)
            for options in args:
                if not isinstance(options, self_class):
                    raise TypeError(
                        f"Positional arguments must be {self_class} instances"
                    )

                merged.update(options.model_dump(exclude_unset=True))
            merged.update(**kwargs)

            kwargs = merged

        return super().__init__(**kwargs)

    def update(self, *args: "TAbstractOptions", **kwargs: Any) -> Self:
        if not args and not kwargs:
            return self

        return self.__class__(self, *args, **kwargs)


class Priority(IntEnum):
    LOW = 0
    NORMAL = 1
    DEFAULT = 1
    HIGH = 2
    INTERACTIVE = 3
    SYSTEM = 4


@dataclass(frozen=True)
class RequestContext:
    deadline: float | None
    priority: Priority
