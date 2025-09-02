from typing import *

from datahold import OkayABC, OkayList

from v440.core.VersionError import VersionError


class Base:

    def __eq__(self: Self, other: Any) -> bool:
        ans: bool
        try:
            opp: Self = type(self)(other)
        except VersionError:
            ans = False
        else:
            ans = self._data == opp._data
        return ans

    def __ge__(self: Self, other: Any, /) -> bool:
        ans: bool
        try:
            opp: Self = type(self)(other)
        except:
            ans = self.data >= other
        else:
            ans = opp <= self
        return ans

    __gt__ = OkayList.__gt__
    __hash__ = OkayABC.__hash__

    def __le__(self: Self, other: Any, /) -> bool:
        ans: bool
        try:
            opp: Self = type(self)(other)
        except:
            ans = self.data <= other
        else:
            ans = self._data <= opp._data
        return ans

    __lt__ = OkayList.__lt__
    __ne__ = OkayABC.__ne__
    __repr__ = OkayABC.__repr__

    def __setattr__(self: Self, name: str, value: Any) -> None:
        if name.startswith("_"):
            object.__setattr__(self, name, value)
            return
        cls: type = type(self)
        attr: Any = getattr(cls, name)
        if type(attr) is not property:
            e = "%r is not a property"
            e %= name
            e = AttributeError(e)
            raise e
        try:
            object.__setattr__(self, name, value)
        except VersionError:
            raise
        except:
            e = "%r is an invalid value for %r"
            e %= (value, cls.__name__ + "." + name)
            raise VersionError(e)
