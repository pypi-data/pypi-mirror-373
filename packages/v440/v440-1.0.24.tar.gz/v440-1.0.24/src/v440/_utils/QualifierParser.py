from __future__ import annotations

import dataclasses
from typing import *

from v440._utils import utils
from v440._utils.Pattern import Pattern


@dataclasses.dataclass(frozen=True)
class QualifierParser:
    keysforlist: tuple = ()
    keysforstr: tuple = ()
    phasedict: dict = dataclasses.field(default_factory=dict)
    allow_len_1: bool = False

    @utils.digest
    class __call__:
        def byInt(self: Self, value: int) -> Any:
            if self.phasedict:
                raise TypeError
            value = int(value)
            if value < 0:
                raise ValueError
            return value

        def byList(self: Self, value: list) -> Any:
            value = [utils.segment(x) for x in value]
            if self.phasedict:
                l, n = value
                if [l, n] == [None, None]:
                    return [None, None]
                l = self.phasedict[l]
                if not isinstance(n, int):
                    raise TypeError
                return [l, n]
            else:
                n = self.nbylist(value)
                if isinstance(n, str):
                    raise TypeError
                return n

        def byNone(self: Self) -> Optional[list]:
            if self.phasedict:
                return [None, None]

        def byStr(self: Self, value: str) -> Optional[int | list]:
            v: str = value
            v = v.replace("_", ".")
            v = v.replace("-", ".")
            if self.phasedict and v == "":
                return [None, None]
            m: Any = Pattern.PARSER.bound.search(v)
            l, n = m.groups()
            if self.phasedict:
                l = self.phasedict[l]
                n = 0 if (n is None) else int(n)
                return [l, n]
            if l not in self.keysforstr:
                raise ValueError
            if n is None:
                return None
            else:
                return int(n)

    def __post_init__(self: Self) -> None:
        if type(self.phasedict) is not dict:
            raise TypeError
        pd = self.phasedict
        pd = list(pd.keys()) + list(pd.values())
        pd = set(type(x) for x in pd)
        if not (pd <= {str}):
            raise TypeError
        if type(self.allow_len_1) is not bool:
            raise TypeError
        if type(self.keysforlist) is not tuple:
            raise TypeError
        if type(self.keysforstr) is not tuple:
            raise TypeError
        keys = self.keysforlist + self.keysforstr
        for k in keys:
            if k is None:
                continue
            if type(k) is str:
                continue
            raise TypeError

    def nbylist(self: Self, value: Any, /) -> Any:
        if len(value) == 2:
            l, n = value
            if l not in self.keysforlist:
                raise ValueError
            return n
        if len(value) == 1:
            n = value[0]
            if not self.allow_len_1:
                raise ValueError
            return n
        raise ValueError


POST = QualifierParser(
    keysforlist=("post", "rev", "r", ""),
    keysforstr=(None, "post", "rev", "r"),
    allow_len_1=True,
)
DEV = QualifierParser(
    keysforlist=("dev",),
    keysforstr=(None, "dev"),
)
PRE = QualifierParser(
    phasedict=dict(
        alpha="a",
        a="a",
        beta="b",
        b="b",
        preview="rc",
        pre="rc",
        c="rc",
        rc="rc",
    ),
)
