from typing import *

import datahold

from preparse.core.enums import *
from preparse.core.warnings import *

__all__ = ["Optdict"]


class Optdict(datahold.OkayDict):
    @property
    def data(self: Self) -> dict:
        return dict(self._data)

    @data.setter
    def data(self: Self, value: Any) -> None:
        if value is None:
            self._data = dict()
            return
        d: dict = dict()
        k: Any
        v: Any
        for k, v in value.items():
            d[str(k)] = Nargs(v)
        self._data = d
