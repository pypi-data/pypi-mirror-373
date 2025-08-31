import abc
import operator
from typing import *

from preparse._utils import *
from preparse.core.enums import *

__all__ = ["Item", "Option", "Bundle", "Long", "Special", "Positional"]


class Item(abc.ABC, BaseData):
    __slots__ = ("_data",)

    @abc.abstractmethod
    def deparse(self: Self) -> list[str]: ...

    @classmethod
    @abc.abstractmethod
    def sortkey(cls: type) -> int: ...


class Option(Item):

    def ishungry(self: Self) -> bool:
        return (self.right is None) and (self.nargs == Nargs.REQUIRED_ARGUMENT)

    @classmethod
    def sortkey(cls: type) -> int:
        return 0


class Bundle(Option):
    # slots
    @dataprop
    def chars(self: Self, x: Any) -> str:
        return str(x)

    @dataprop
    def joined(self: Self, x: SupportsIndex) -> bool:
        return bool(operator.index(x))

    @dataprop
    def right(self: Self, x: Any) -> Optional[str]:
        if x is not None:
            return str(x)

    @dataprop
    def nargs(self: Self, x: Any) -> Nargs:
        return Nargs(x)

    #

    def __init__(
        self: Self,
        *,
        chars: str,
        joined: bool = False,
        right: Optional[str] = None,
    ) -> None:
        self.chars = chars
        self.joined = joined
        self.right = right

    @classmethod
    def _split_allowslong(cls: type, chars: str) -> list[str]:
        ans: list[str] = list()
        x: str
        for x in chars:
            if x == "-":
                ans[-1].chars += "-"
            else:
                ans.append(x)
        return ans

    @classmethod
    def _split_shortonly(cls: type, chars: str) -> list[str]:
        ans: list[str] = list()
        x: str = chars
        while x:
            if x == "-":
                ans[0] = "-" + ans[0]
                x = ""
            elif x.endswith("-"):
                ans.insert(0, x[-2:])
                x = x[:-2]
            else:
                ans.insert(0, x[-1])
                x = x[:-1]
        return ans

    def deparse(self: Self) -> list[str]:
        if self.right is None:
            return ["-" + self.chars]
        elif self.joined:
            return ["-" + self.chars + self.right]
        else:
            return ["-" + self.chars, self.right]

    def split(self: Self, *, allowslong: bool) -> list[Item]:
        parts: list[str]
        if allowslong:
            parts = self._split_allowslong(self.chars)
        else:
            parts = self._split_shortonly(self.chars)
        ans: list[Self] = list()
        x: str
        for x in parts:
            ans.append(Bundle(chars=x))
        self.chars = ans[-1].chars
        ans[-1] = self
        return ans


class Long(Option):
    # slots
    @dataprop
    def fullkey(self: Self, x: Any) -> str:
        return str(x)

    @dataprop
    def abbrlen(self: Self, x: Optional[SupportsIndex]) -> Optional[int]:
        if x is not None:
            return operator.index(x)

    @dataprop
    def joined(self: Self, x: Any) -> bool:
        return operator.index(x)

    @dataprop
    def right(self: Self, x: Any) -> Optional[str]:
        if x is not None:
            return str(x)

    #
    def __init__(
        self: Self,
        *,
        fullkey: str,
        abbrlen: Optional[int] = None,
        joined: bool | str = False,
        right: Optional[str] = None,
    ) -> None:
        self.fullkey = fullkey
        self.abbrlen = abbrlen
        self.joined = joined
        self.right = right

    @property
    def abbr(self: Self) -> str:
        return self.fullkey[: self.abbrlen]

    def deparse(self: Self) -> list[str]:
        if self.right is None:
            return [self.abbr]
        elif self.joined:
            return [self.abbr + "=" + self.right]
        else:
            return [self.abbr, self.right]


class Special(Item):

    def deparse(self: Self) -> list[str]:
        return ["--"]

    @classmethod
    def sortkey(cls: type) -> int:
        return 1


class Positional(Item):
    # slots
    @dataprop
    def value(self: Self, x: Any) -> str:
        return str(x)

    #
    def __init__(self: Self, value: Any) -> None:
        self.value = value

    def deparse(self: Self) -> list[str]:
        return [self.value]

    def isobvious(self: Self) -> bool:
        return self.value == "-" or not self.value.startswith("-")

    @classmethod
    def sortkey(cls: type) -> int:
        return 2
