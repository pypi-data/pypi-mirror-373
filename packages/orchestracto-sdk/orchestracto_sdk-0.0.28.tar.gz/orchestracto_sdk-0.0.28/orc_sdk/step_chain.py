import dataclasses
from typing import Iterable, Any
from typing_extensions import Self


each = type("Each", (), {})()


@dataclasses.dataclass
class RetValWrapper:
    value: Any
    sci: "StepChainItem"
    name: str


@dataclasses.dataclass
class StepChainItem:
    step_id: str

    _for_each: Iterable[Any] | RetValWrapper | None = dataclasses.field(default=None)

    _first: list["StepChainItem"] = dataclasses.field(init=False)
    _next_steps: list["StepChainItem"] = dataclasses.field(init=False)
    _prev_steps: list["StepChainItem"] = dataclasses.field(init=False)

    def __post_init__(self):
        self._first = [self]
        self._next_steps = []
        self._prev_steps = []

    def __rshift__(self, other: Self | list[Self]) -> Self:
        self.set_downstream(other)
        return other

    def __lshift__(self, other: Self | list[Self]) -> Self | list[Self]:
        self.set_upstream(other)
        return other

    def __rrshift__(self, other: Self | list[Self]) -> Self:
        self.__lshift__(other)
        return self

    def __rlshift__(self, other: Self | list[Self]):
        self.__rrshift__(other)
        return self

    def set_downstream(self, other: Self | list[Self]):
        if isinstance(other, list):
            for sro in other:
                sro._first = self._first
                self._next_steps.append(sro)
                sro._prev_steps.append(self)
        else:
            other._first = self._first
            self._next_steps.append(other)
            other._prev_steps.append(self)

    def set_upstream(self, other: Self | list[Self]):
        if isinstance(other, list):
            for sro in other:
                sro._next_steps.append(self)
                self._prev_steps.append(sro)
            self._first = other[0]._first
        else:
            other._next_steps.append(self)
            self._first = other._first
            self._prev_steps.append(other)

    def with_id(self, step_id: str) -> Self:
        self.step_id = step_id
        return self

    def for_each(self, iterable: Iterable[Any] | RetValWrapper):
        self._for_each = iterable
        return self
