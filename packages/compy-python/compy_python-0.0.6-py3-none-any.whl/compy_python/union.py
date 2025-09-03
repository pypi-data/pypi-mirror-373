from typing import Any


class Uni[*Ts]:
    def __init__(self, value: Any):
        self._value = value


def isinst[*Ts, T](obj: Uni[*Ts], _type: type[T]) -> bool:
    return isinstance(obj._value, _type)


def is_none[*Ts](obj: Uni[*Ts]) -> bool:
    return obj._value is None


def ug[*Ts, T](obj: Uni[*Ts], _type: type[T]) -> Any:
    return obj._value
