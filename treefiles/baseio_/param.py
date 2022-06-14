import logging
from typing import Tuple, List, Union

from treefiles import Str
from treefiles.baseio_.baseio_ import TValue, BaseIO, Bases

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

    def __truediv__(self, other):
        return Str(Str(self.value) / other)

    def __call__(self, value=None, **kwargs):
        self.value = value
        for k, v in kwargs.items():
            if k in self.registered:
                setattr(self, k, v)
        return self

    def __eq__(self, other):
        if isinstance(other, Param):
            return self.value == other.value
        return self.value == other


# class Params(Bases[str, Param]):  # python >= 3.9
class Params(Bases):
    inner_class = Param  # python < 3.9

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

    @classmethod
    def from_dict(cls, d):
        return cls([cls.inner_class(k, v) for k, v in d.items()])


def r(x, k=2):
    if x is None:
        return
    try:
        y = round(x, k)
    except:
        y = x
    return y


TParams = Union[List[Param], Params]

log = logging.getLogger(__name__)
