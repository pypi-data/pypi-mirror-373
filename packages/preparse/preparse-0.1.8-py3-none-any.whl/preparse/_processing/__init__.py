from types import FunctionType
from typing import *

from preparse._processing.deparsing import *
from preparse._processing.digesting import *
from preparse._processing.items import *
from preparse._processing.parsing import *
from preparse._processing.pulling import *
from preparse._utils import *
from preparse.core.enums import *

__all__ = ["BaseData", "dataprop", "process"]


def process(
    args: Optional[Iterable] = None,
    *,
    allowslong: bool,
    allowsshort: bool,
    bundling: Tuning,
    expandsabbr: bool,
    expectsabbr: bool,
    expectsposix: bool,
    optdict: dict,
    prog: str,
    reconcilesorders: bool,
    special: Tuning,
    warn: FunctionType,
) -> list[str]:
    "This method parses args."
    items: list[Item] = pull(args)
    items = parse(
        items,
        allowslong=allowslong,
        allowsshort=allowsshort,
        expectsabbr=expectsabbr,
        expectsposix=expectsposix,
        optdict=optdict,
        prog=prog,
        warn=warn,
    )
    items = digest(
        items,
        allowslong=allowslong,
        bundling=bundling,
        expandsabbr=expandsabbr,
        expectsposix=expectsposix,
        reconcilesorders=reconcilesorders,
        special=special,
    )
    ans: list[str] = deparse(items)
    return ans
