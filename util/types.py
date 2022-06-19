from types import UnionType
from typing import Final


Number = int | float | complex


def const(__t: type) -> type:
    return Final[__t]


def nullable(__t: type) -> UnionType:
    return __t | None
