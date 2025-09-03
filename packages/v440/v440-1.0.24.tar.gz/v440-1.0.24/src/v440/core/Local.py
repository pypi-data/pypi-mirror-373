from __future__ import annotations

import functools
from typing import *

from v440._utils import utils
from v440._utils.VList import VList

__all__ = ["Local"]


class Local(VList):

    data: list[int | str]

    def __le__(self: Self, other: Iterable) -> bool:
        try:
            other = type(self)(other)
        except ValueError:
            pass
        else:
            return self._cmpkey() <= other._cmpkey()
        return self.data <= other

    def __str__(self: Self) -> str:
        return ".".join(map(str, self))

    def _cmpkey(self: Self) -> list:
        return [self._sortkey(x) for x in self]

    @staticmethod
    def _sortkey(value: Any) -> Tuple[bool, Any]:
        return type(value) is int, value

    @property
    def data(self: Self) -> list[int | str]:
        return list(self._data)

    @data.setter
    @utils.digest
    class data:
        def byInt(self: Self, value: int) -> None:
            self._data = [value]

        def byList(self: Self, value: list) -> None:
            value = [utils.segment(x) for x in value]
            if None in value:
                raise ValueError
            self._data = value

        def byNone(self: Self) -> None:
            self._data = list()

        def byStr(self: Self, value: str) -> None:
            if value.startswith("+"):
                value = value[1:]
            value = value.replace("_", ".")
            value = value.replace("-", ".")
            value = value.split(".")
            value = [utils.segment(x) for x in value]
            if None in value:
                raise ValueError
            self._data = value

    @functools.wraps(VList.sort)
    def sort(self: Self, /, *, key: Any = None, **kwargs: Any) -> None:
        if key is None:
            key = self._sortkey
        self._data.sort(key=key, **kwargs)
