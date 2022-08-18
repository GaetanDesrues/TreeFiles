import logging
from typing import Tuple, List, Union

from treefiles import Str
from treefiles.baseio_.baseio_ import TValue, BaseIO, Bases

_Bounds = Tuple[TValue, TValue]


class Param(BaseIO):
    """
    A ``Param`` is a dictionary that contains a fixed set of keys, defined in ``self.registered``:
        - name (required)
        - value
        - pretty_name
        - unit
        - initial_value
        - ref
        - bounds

    .. code-block:: python

        >>> param = Param("some_param", 10)
        >>> param
        <Param.some_param=10>
        >>> param.value  # get value
        10
        >>> param(-7)  # assign value
        <Param.some_param=-7>

    """

    def __init__(
        self,
        *args,
        initial_value: TValue = None,
        bounds: _Bounds = None,
        ref=None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.initial_value = initial_value
        self.bounds = bounds
        self.ref = ref

        self.registered.add("initial_value")
        self.registered.add("ref")
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

    def build_table_old(self) -> Tuple[Bases.THeader, Bases.TData]:
        header = ["Name", "Ref", "Baseline", "Value", "Bounds", "Unit"]
        data = [
            [x.name, r(x.ref), x.initial_value, r(x.value), x.bounds, x.unit]
            for x in self.values()
        ]
        return header, data

    def build_table(self) -> Tuple[Bases.THeader, Bases.TData]:
        import numpy as np

        header, data = self.build_table_old()
        datab = np.array([[y is None for y in x] for x in data])
        hd, dataT = [], []
        d = np.array(data, dtype=object)
        for i, h in enumerate(header):
            if not datab[:, i].all():
                hd.append(h)
                dataT.append(d[:, i])
        return hd, np.array(dataT).T

    @property
    def bounds(self):
        return [x.bounds for x in self.values()]

    @classmethod
    def from_dict(cls, d):
        return cls([cls.inner_class(k, v) for k, v in d.items()])


def r(x):
    if x is None:
        return
    try:
        k = 3 if x > 1e3 else 6
        y = round(x, k)
    except:
        y = x
    return y


TParams = Union[List[Param], Params]

log = logging.getLogger(__name__)
