from __future__ import annotations

import dataclasses
from typing import *

import packaging.version
from datahold import OkayABC
from scaevola import Scaevola

from v440._utils import QualifierParser, utils
from v440._utils.Base import Base
from v440._utils.Pattern import Pattern
from v440.core.Local import Local
from v440.core.Pre import Pre
from v440.core.Release import Release
from v440.core.VersionError import VersionError

QUALIFIERDICT = dict(
    dev="dev",
    post="post",
    r="post",
    rev="post",
)


@dataclasses.dataclass(order=True)
class _Version:
    epoch: int = 0
    release: Release = dataclasses.field(default_factory=Release)
    pre: Pre = dataclasses.field(default_factory=Pre)
    post: Optional[int] = None
    dev: Optional[int] = None
    local: Local = dataclasses.field(default_factory=Local)

    def copy(self: Self) -> Self:
        return dataclasses.replace(self)

    def todict(self: Self) -> dict:
        return dataclasses.asdict(self)


class Version(Base):
    base: Self
    data: str
    dev: Optional[int]
    epoch: int
    local: Local
    post: Optional[int]
    pre: Pre
    public: Self
    release: Release

    def __bool__(self: Self) -> bool:
        return self._data != _Version()

    def __init__(self: Self, data: Any = "0", /, **kwargs: Any) -> None:
        object.__setattr__(self, "_data", _Version())
        self.data = data
        self.update(**kwargs)

    def __le__(self: Self, other: Any) -> bool:
        other = type(self)(other)
        return self._cmpkey() <= other._cmpkey()

    def __setattr__(self: Self, name: str, value: Any) -> None:
        a: dict = dict()
        b: dict = dict()
        x: Any
        y: Any
        for x, y in self._data.todict().items():
            try:
                a[x] = y.data
            except AttributeError:
                b[x] = y
        try:
            Base.__setattr__(self, name, value)
        except VersionError:
            for x, y in a.items():
                getattr(self._data, x).data = y
            for x, y in b.items():
                setattr(self._data, x, y)
            raise

    def __str__(self: Self) -> str:
        return self.data

    def _cmpkey(self: Self) -> tuple:
        ans = self._data.copy()
        if not ans.pre.isempty():
            ans.pre = tuple(ans.pre)
        elif ans.post is not None:
            ans.pre = "z", float("inf")
        elif ans.dev is None:
            ans.pre = "z", float("inf")
        else:
            ans.pre = "", -1
        if ans.post is None:
            ans.post = -1
        if ans.dev is None:
            ans.dev = float("inf")
        return ans

    @property
    def base(self: Self) -> Self:
        ans: Self = self.public
        ans.dev = None
        ans.pre = None
        ans.post = None
        return ans

    @base.setter
    @utils.digest
    class base:
        def byInt(self: Self, value: int) -> None:
            self.epoch = None
            self.release = value

        def byNone(self: Self) -> None:
            self.epoch = None
            self.release = None

        def byStr(self: Self, value: str) -> None:
            if "!" in value:
                self.epoch, self.release = value.split("!", 1)
            else:
                self.epoch, self.release = 0, value

    def clear(self: Self) -> None:
        self.data = None

    def copy(self: Self) -> Self:
        return type(self)(self)

    @property
    def data(self: Self) -> str:
        return self.format()

    @data.setter
    @utils.digest
    class data:
        def byInt(self: Self, value: int) -> None:
            self.public = value
            self.local = None

        def byNone(self: Self) -> None:
            self.public = None
            self.local = None

        def byStr(self: Self, value: str) -> None:
            if "+" in value:
                self.public, self.local = value.split("+", 1)
            else:
                self.public, self.local = value, None

    @property
    def dev(self: Self) -> Optional[int]:
        return self._data.dev

    @dev.setter
    def dev(self: Self, value: Any) -> None:
        self._data.dev = QualifierParser.DEV(value)

    @property
    def epoch(self: Self) -> int:
        return self._data.epoch

    @epoch.setter
    @utils.digest
    class epoch:
        def byInt(self: Self, value: int) -> None:
            if value < 0:
                raise ValueError
            self._data.epoch = value

        def byNone(self: Self) -> None:
            self._data.epoch = 0

        def byStr(self: Self, value: str) -> None:
            value = Pattern.EPOCH.bound.search(value)
            value = value.group("n")
            if value is None:
                self._data.epoch = 0
            else:
                self._data.epoch = int(value)

    def format(self: Self, cutoff: Any = None) -> str:
        ans: str = ""
        if self.epoch:
            ans += "%s!" % self.epoch
        ans += self.release.format(cutoff)
        ans += str(self.pre)
        if self.post is not None:
            ans += ".post%s" % self.post
        if self.dev is not None:
            ans += ".dev%s" % self.dev
        if self.local:
            ans += "+%s" % self.local
        return ans

    def isdevrelease(self: Self) -> bool:
        return self.dev is not None

    def isprerelease(self: Self) -> bool:
        return self.isdevrelease() or not self.pre.isempty()

    def ispostrelease(self: Self) -> bool:
        return self.post is not None

    @property
    def local(self: Self) -> Local:
        return self._data.local

    @local.setter
    def local(self: Self, value: Any) -> None:
        self._data.local.data = value

    def packaging(self: Self) -> packaging.version.Version:
        return packaging.version.Version(str(self))

    @property
    def post(self: Self) -> Optional[int]:
        return self._data.post

    @post.setter
    def post(self: Self, value: Any) -> None:
        self._data.post = QualifierParser.POST(value)

    @property
    def pre(self: Self) -> Pre:
        return self._data.pre

    @pre.setter
    def pre(self: Self, value: Any) -> None:
        self._data.pre.data = value

    @property
    def public(self: Self) -> Self:
        ans: Self = self.copy()
        ans.local = None
        return ans

    @public.setter
    @utils.digest
    class public:
        def byInt(self: Self, value: int) -> None:
            self.base = value
            self.pre = None
            self.post = None
            self.dev = None

        def byNone(self: Self) -> None:
            self.base = None
            self.pre = None
            self.post = None
            self.dev = None

        def byStr(self: Self, value: str) -> None:
            match = Pattern.PUBLIC.leftbound.search(value)
            self.base = value[: match.end()]
            value = value[match.end() :]
            self.pre = None
            self.post = None
            self.dev = None
            while value:
                m = Pattern.QUALIFIERS.leftbound.search(value)
                value = value[m.end() :]
                if m.group("N"):
                    self.post = m.group("N")
                else:
                    x = m.group("l")
                    y = m.group("n")
                    n = QUALIFIERDICT.get(x, "pre")
                    setattr(self, n, (x, y))

    @property
    def release(self: Self) -> Release:
        return self._data.release

    @release.setter
    def release(self: Self, value: Any) -> None:
        self._data.release.data = value

    def update(self: Self, **kwargs: Any) -> None:
        x: Any
        y: Any
        for x, y in kwargs.items():
            attr = getattr(type(self), x)
            if isinstance(attr, property):
                setattr(self, x, y)
                continue
            e = "%r is not a property"
            e %= x
            e = AttributeError(e)
            raise e
