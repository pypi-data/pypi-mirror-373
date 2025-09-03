from __future__ import annotations

import operator
import string
from typing import *

from keyalias import keyalias
from overloadable import overloadable

from v440._utils import utils
from v440._utils.VList import VList


@keyalias(major=0, minor=1, micro=2, patch=2)
class Release(VList):
    data: list[int]
    major: int
    minor: int
    micro: int
    patch: int

    def __add__(self: Self, other: Any, /) -> Self:
        opp: Self = type(self)(other)
        ans: Self = self.copy()
        ans._data += opp._data
        return ans

    @overloadable
    def __delitem__(self: Self, key: Any) -> bool:
        return type(key) is slice

    @__delitem__.overload(False)
    def __delitem__(self: Self, key: SupportsIndex) -> None:
        i: int = operator.index(key)
        if i < len(self):
            del self._data[i]

    @__delitem__.overload(True)
    def __delitem__(self: Self, key: Any) -> None:
        key = utils.torange(key, len(self))
        key = [k for k in key if k < len(self)]
        key.sort(reverse=True)
        for k in key:
            del self._data[k]

    @overloadable
    def __getitem__(self: Self, key: Any) -> bool:
        return type(key) is slice

    @__getitem__.overload(False)
    def __getitem__(self: Self, key: Any) -> int:
        i: int = operator.index(key)
        ans: int = self._getitem_int(i)
        return ans

    @__getitem__.overload(True)
    def __getitem__(self: Self, key: Any) -> list:
        r: range = utils.torange(key, len(self))
        m: map = map(self._getitem_int, r)
        ans: list = list(m)
        return ans

    @overloadable
    def __setitem__(self: Self, key: Any, value: Any) -> bool:
        return type(key) is slice

    @__setitem__.overload(False)
    def __setitem__(self: Self, key: SupportsIndex, value: Any) -> Any:
        i: int = operator.index(key)
        self._setitem_int(i, value)

    @__setitem__.overload(True)
    def __setitem__(self: Self, key: SupportsIndex, value: Any) -> Any:
        key = utils.torange(key, len(self))
        self._setitem_range(key, value)

    def __str__(self: Self) -> str:
        return self.format()

    def _getitem_int(self: Self, key: int) -> int:
        if key < len(self):
            return self._data[key]
        else:
            return 0

    def _setitem_int(self: Self, key: int, value: Any) -> Any:
        value = utils.numeral(value)
        length = len(self)
        if length > key:
            self._data[key] = value
            return
        if value == 0:
            return
        self._data.extend([0] * (key - length))
        self._data.append(value)

    @overloadable
    def _setitem_range(self: Self, key: range, value: Any) -> Any:
        return key.step == 1

    @_setitem_range.overload(False)
    def _setitem_range(self: Self, key: range, value: Any) -> Any:
        key = list(key)
        value = self._tolist(value, slicing=len(key))
        if len(key) != len(value):
            e = "attempt to assign sequence of size %s to extended slice of size %s"
            e %= (len(value), len(key))
            raise ValueError(e)
        maximum = max(*key)
        ext = max(0, maximum + 1 - len(self))
        data = self.data
        data += [0] * ext
        for k, v in zip(key, value):
            data[k] = v
        while len(data) and not data[-1]:
            data.pop()
        self._data = data

    @_setitem_range.overload(True)
    def _setitem_range(self: Self, key: range, value: Any) -> Any:
        data = self.data
        ext = max(0, key.start - len(data))
        data += ext * [0]
        value = self._tolist(value, slicing="always")
        data = data[: key.start] + value + data[key.stop :]
        while len(data) and not data[-1]:
            data.pop()
        self._data = data

    @staticmethod
    def _tolist(value: Any, *, slicing: Any) -> list:
        if value is None:
            return []
        if isinstance(value, int):
            return [utils.numeral(value)]
        if not isinstance(value, str):
            if hasattr(value, "__iter__"):
                return [utils.numeral(x) for x in value]
            slicing = "never"
        value = str(value)
        if value == "":
            return list()
        if "" == value.strip(string.digits) and slicing in (len(value), "always"):
            return [int(x) for x in value]
        value = value.lower().strip()
        value = value.replace("_", ".")
        value = value.replace("-", ".")
        if value.startswith("v") or value.startswith("."):
            value = value[1:]
        value = value.split(".")
        if "" in value:
            raise ValueError
        value = [utils.numeral(x) for x in value]
        return value

    def bump(self: Self, index: SupportsIndex = -1, amount: SupportsIndex = 1) -> None:
        i: int = operator.index(index)
        a: int = operator.index(amount)
        x: int = self._getitem_int(i) + a
        self._setitem_int(i, x)
        if i != -1:
            self.data = self.data[: i + 1]

    @property
    def data(self: Self) -> list:
        return list(self._data)

    @data.setter
    def data(self: Self, value: Any) -> None:
        value = self._tolist(value, slicing="always")
        while value and value[-1] == 0:
            value.pop()
        self._data = value

    def format(self: Self, cutoff: Any = None) -> str:
        s: str = str(cutoff) if cutoff else ""
        i: Optional[int] = int(s) if s else None
        ans = self[:i]
        if len(ans) == 0:
            ans += [0]
        ans = [str(x) for x in ans]
        ans = ".".join(ans)
        return ans
