from typing import *

__all__ = ["VersionError"]


class VersionError(ValueError):
    def __init__(self: Self, *args: Any) -> None:
        super().__init__(*args)
