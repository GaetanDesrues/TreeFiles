import logging
from typing import Tuple, List, Union

from treefiles.baseio.baseio import TValue, BaseIO, Bases

_Bounds = Tuple[TValue, TValue]


class Param(BaseIO):
    def __init__(
        self, *args, initial_value: TValue = None, bounds: _Bounds = None, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.initial_value = initial_value
        self.bounds = bounds

        self.registered.add("initial_value")
        self.registered.add("bounds")

    @property
    def table(self):
        return Params(self).table


class Params(Bases[str, Param]):
    def build_table(self) -> Tuple[Bases.THeader, Bases.TData]:
        header = ["Name", "Baseline", "Value", "Bounds", "Unit"]
        data = [
            [x.name, x.initial_value, r(x.value), x.bounds, x.unit]
            for x in self.values()
        ]
        return header, data

    @property
    def bounds(self):
        return [x.bounds for x in self.values()]


def r(x, k=2):
    if isinstance(x, str):
        return x
    elif isinstance(x, (int, float)):
        return round(x, k)


TParams = Union[List[Param], Params]

log = logging.getLogger(__name__)
