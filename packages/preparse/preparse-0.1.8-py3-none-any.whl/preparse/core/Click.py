import dataclasses
import functools
import types
from typing import *

import overloadable

__all__ = ["Click"]


@dataclasses.dataclass
class Click:

    parser: Any
    cmd: Any = True
    ctx: Any = True

    @overloadable.Overloadable
    def __call__(self: Self, target: Any) -> Any:
        "This magic method implements self(target)."
        if isinstance(target, types.FunctionType):
            return "function"
        if isinstance(target, types.MethodType):
            return "method"
        return "other"

    @__call__.overload("function")
    def __call__(self: Self, target: types.FunctionType) -> types.FunctionType:
        @functools.wraps(target)
        def ans(cmd: Any, ctx: Any, args: Any) -> Any:
            p = self.parser.copy()
            if self.cmd:
                p.reflectClickCommand(cmd)
            if self.ctx:
                p.reflectClickContext(ctx)
            return target(cmd, ctx, p.parse_args(args))

        return ans

    @__call__.overload("method")
    def __call__(self: Self, target: types.MethodType) -> types.MethodType:
        func = self(target.__func__)
        ans = types.MethodType(func, target.__self__)
        return ans

    @__call__.overload("other")
    def __call__(self: Self, target: Any) -> Any:
        target.parse_args = self(target.parse_args)
        return target
