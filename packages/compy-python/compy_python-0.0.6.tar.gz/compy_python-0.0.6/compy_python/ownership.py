from typing import Annotated


def mov[T](obj: T) -> T:
    return obj


class PassByValue:
    pass


def Valu[T](typ: T) -> Annotated[T, PassByValue()]:
    return Annotated[typ, PassByValue()]


class TypeIsARef:
    pass


def Ref[T](typ: T) -> Annotated[T, TypeIsARef()]:
    return Annotated[typ, TypeIsARef()]
