from types import FunctionType
from typing import *

from preparse._processing.items import *
from preparse.core import warnings
from preparse.core.enums import *

__all__ = ["parse"]

PAOW = warnings.PreparseAmbiguousOptionWarning
PIOW = warnings.PreparseInvalidOptionWarning
PUAW = warnings.PreparseUnallowedArgumentWarning
PRAW = warnings.PreparseRequiredArgumentWarning


def parse(args: list[str], **kwargs: Any) -> list[Item]:
    return list(parse_generator(args, **kwargs))


def parse_generator(
    items: list[Positional],
    *,
    allowslong: bool,
    allowsshort: bool,
    expectsabbr: bool,
    expectsposix: bool,
    optdict: dict,
    prog: str,
    warn: FunctionType,
) -> Generator[Any, Any, Any]:
    broken: bool = not (allowslong or allowsshort)
    cause: FunctionType = parse_cause(prog=prog, warn=warn)
    last: Optional[Option] = None
    item: Positional
    for item in items:
        if broken:
            # if we are in the positional-only part
            yield item
            continue
        if last is not None:
            # if the last item hungers for a value
            last.right = item.value
            last.joined = False
            yield last
            last = None
            continue
        if item.value == "--":
            yield Special()
            broken = True
            continue
        if item.isobvious():
            # if the item is positional
            yield item
            broken = expectsposix
            continue
        last = parse_option(
            item.value,
            allowslong=allowslong,
            allowsshort=allowsshort,
            cause=cause,
            expectsabbr=expectsabbr,
            optdict=optdict,
        )
        if not last.ishungry():
            yield last
            last = None
    if last is None:
        # if the last item is not starved
        return
    if isinstance(last, Long):
        cause(PRAW, option=last.fullkey, islong=True)
    else:
        cause(PRAW, option=last.chars[-1], islong=False)
    yield last


def parse_cause(
    *,
    prog: str,
    warn: FunctionType,
) -> FunctionType:
    def ans(cls: type, **kwargs: Any) -> None:
        warn(cls(prog=prog, **kwargs))

    return ans


def parse_option(
    arg: str,
    *,
    cause: FunctionType,
    expectsabbr: bool,
    optdict: dict,
    **kwargs: Any,
) -> Option:
    if parse_islong(arg, **kwargs):
        return parse_long(
            arg,
            cause=cause,
            expectsabbr=expectsabbr,
            optdict=optdict,
        )
    else:
        return parse_bundling(
            arg,
            cause=cause,
            optdict=optdict,
        )


def parse_islong(
    arg: str,
    *,
    allowslong: bool,
    allowsshort: bool,
) -> bool:
    if allowslong and allowsshort:
        return arg.startswith("--")
    else:
        return not allowsshort


def parse_long(
    arg: str,
    *,
    cause: FunctionType,
    expectsabbr: bool,
    optdict: dict,
) -> Long:
    parts: list[str] = arg.split("=", 1)
    ans: Long = Long(fullkey=parts.pop(0))
    if len(parts):
        ans.joined = True
        ans.right = parts.pop()
    ans.abbrlen = len(ans.fullkey)
    if ans.fullkey in optdict.keys():
        ans.nargs = optdict[ans.fullkey]
        if (ans.nargs == Nargs.NO_ARGUMENT) and (ans.right is not None):
            cause(PUAW, option=ans.fullkey)
        return ans
    if expectsabbr:
        parts = parse_long_startswith(ans.abbr, keys=optdict.keys())
    else:
        parts = list()  # can be assumed
    if len(parts) == 0:
        ans.nargs = Nargs.OPTIONAL_ARGUMENT
        cause(PIOW, option=arg, islong=True)
        return ans
    if len(parts) >= 2:
        ans.nargs = Nargs.OPTIONAL_ARGUMENT
        cause(PAOW, option=arg, possibilities=parts)
        return ans
    (ans.fullkey,) = parts
    ans.nargs = optdict[ans.fullkey]
    return ans


def parse_long_startswith(
    abbr: str,
    *,
    keys: Iterable[str],
):
    x: str
    ans: list[str] = list()
    for x in keys:
        if x.startswith(abbr):
            ans.append(x)
    return ans


def parse_bundling(
    arg: str,
    *,
    cause: FunctionType,
    optdict: dict,
) -> Bundle:
    ans: Bundle = Bundle(chars="")
    for i, a in enumerate(arg):
        if i == 0:
            continue
        ans.chars += a
        try:
            ans.nargs = optdict["-" + a]
        except KeyError:
            cause(PIOW, option=a, islong=False)
            ans.nargs = Nargs.NO_ARGUMENT
        if ans.nargs == Nargs.NO_ARGUMENT:
            continue
        if ans.nargs == Nargs.OPTIONAL_ARGUMENT or i < len(arg) - 1:
            ans.joined = True
            ans.right = arg[i + 1 :]
        return ans
    return ans
