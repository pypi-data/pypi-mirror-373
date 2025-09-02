import typing

import pydantic

__all__ = [
    "observable_state",
]


class observable_state(pydantic.BaseModel):
    _uri_: typing.ClassVar[str]
    _next_delay_seconds_: int = 0

    def __init_subclass__(klass) -> None:
        klass._uri_ = f"{klass.__module__}.{klass.__name__}"
        super().__init_subclass__()
