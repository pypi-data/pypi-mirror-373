from typing import *

from preparse._processing.items import *

__all__ = ["deparse"]


def deparse(items: list[Item]) -> list[str]:
    ans: list[str] = list()
    item: Item
    for item in items:
        ans += item.deparse()
    return ans
