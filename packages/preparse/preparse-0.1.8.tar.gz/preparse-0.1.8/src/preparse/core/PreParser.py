import os
import sys
import types
from typing import *

import click as cl
from tofunc import tofunc

from preparse._processing import *
from preparse.core.Click import *
from preparse.core.enums import *
from preparse.core.Optdict import *
from preparse.core.warnings import *

__all__ = ["PreParser"]


class BasePreParser(BaseData):

    __slots__ = ("_data",)

    def __init__(
        self: Self,
        *,
        allowslong: Any = True,
        allowsshort: Any = True,
        bundling: Any = Tuning.MAINTAIN,
        expandsabbr: Any = True,
        expectsabbr: Any = True,
        expectsposix: Any = False,
        optdict: Any = (),
        prog: Any = None,
        reconcilesorders: Any = True,
        special: Any = Tuning.MAINTAIN,
        warn: Callable = str,
    ) -> None:
        "This magic method initializes self."
        self.allowslong = allowslong
        self.allowsshort = allowsshort
        self.bundling = bundling
        self.expandsabbr = expandsabbr
        self.expectsabbr = expectsabbr
        self.expectsposix = expectsposix
        self.optdict = optdict
        self.prog = prog
        self.reconcilesorders = reconcilesorders
        self.special = special
        self.warn = warn

    @dataprop
    def allowslong(self: Self, value: Any) -> bool:
        return bool(value)

    @dataprop
    def allowsshort(self: Self, value: Any) -> bool:
        return bool(value)

    @dataprop
    def bundling(self: Self, value: Any) -> Tuning:
        "This property decides how to approach the bundling of short options."
        return Tuning(value)

    @dataprop
    def expandsabbr(self: Self, value: Any) -> bool:
        return bool(value)

    @dataprop
    def expectsabbr(self: Self, value: Any) -> bool:
        return bool(value)

    @dataprop
    def expectsposix(self: Self, value: Any) -> bool:
        if value == "infer":
            return bool(os.environ.get("POSIXLY_CORRECT"))
        else:
            return bool(value)

    @dataprop
    def optdict(self: Self, value: Any) -> Optdict:
        "This property gives a dictionary of options."
        if "optdict" not in self._data.keys():
            self._data["optdict"] = Optdict()
        dataA: Optdict = Optdict(value)
        self._data["optdict"].clear()
        self._data["optdict"].update(dataA)
        return self._data["optdict"]

    @dataprop
    def prog(self: Self, value: Any) -> str:
        "This property represents the name of the program."
        if value is None:
            value = os.path.basename(sys.argv[0])
        return str(value)

    @dataprop
    def reconcilesorders(self: Self, value: Any) -> bool:
        return bool(value)

    @dataprop
    def special(self: Self, value: Any) -> Tuning:
        "This Tuning property determines the approach towards the special argument."
        return Tuning(value)

    @dataprop
    def warn(self: Self, value: Callable) -> types.FunctionType:
        "This property gives a function that takes in the warnings."
        return tofunc(value)


class PreParser(BasePreParser):

    def click(self: Self, cmd: Any = True, ctx: Any = True) -> Click:
        "This method returns a decorator that infuses the current instance into parse_args."
        return Click(parser=self, cmd=cmd, ctx=ctx)

    def parse_args(
        self: Self,
        args: Optional[Iterable] = None,
    ) -> list[str]:
        "This method parses args."
        return process(args, **self.todict())

    def reflectClickCommand(self: Self, cmd: cl.Command) -> None:
        "This method causes the current instance to reflect a click.Command object."
        optdict = dict()
        for p in cmd.params:
            if not isinstance(p, cl.Option):
                continue
            if p.is_flag or p.nargs == 0:
                optn = Nargs.NO_ARGUMENT
            elif p.nargs == 1:
                optn = Nargs.REQUIRED_ARGUMENT
            else:
                optn = Nargs.OPTIONAL_ARGUMENT
            for o in p.opts:
                optdict[str(o)] = optn
        self.optdict.clear()
        self.optdict.update(optdict)

    def reflectClickContext(self: Self, ctx: cl.Context) -> None:
        "This method causes the current instance to reflect a click.Context object."
        self.prog = ctx.info_name
