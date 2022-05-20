from __future__ import annotations

import inspect
import logging
from copy import deepcopy
from typing import Union, TypeVar, Set, List, Tuple, Dict, get_args

import numpy as np

from treefiles.commons import get_iterable
from treefiles.np import NumpyEncoder
from treefiles.tables import Table

TValue = Union[int, float, np.ndarray]
TRegistered = Set[str]


class BaseIO:
    def __init__(
        self, name: str, value: TValue = None, pretty_name: str = None, unit: str = None
    ):
        self.name = name
        self.pretty_name = pretty_name
        self.value = value
        self.unit = unit

        self.registered: TRegistered = {"name", "pretty_name", "value", "unit"}

    @property
    def _class_name(self) -> str:
        return type(self).__name__

    @property
    def dict(self) -> dict:
        return self.to_dict()

    def get_pname(self) -> str:
        return self.name if self.pretty_name is None else self.pretty_name

    def __repr__(self):
        v = str(self.value)
        s = "..." if len(v) > 50 else ""
        v = v[: min(50, len(v))]
        return f"<{self._class_name}.{self.name}={v}{s}>"

    def to_dict(self) -> dict:
        return {k: getattr(self, k) for k in self.registered}

    def copy(self):
        return deepcopy(self)

    @classmethod
    def from_dict(cls, d: dict) -> T:
        d, s = dict(d), dict()

        keys = []
        for base_class in reversed(cls.mro()):
            sig = inspect.signature(base_class.__init__)
            keys.extend(sig.parameters.keys())
        keys = [k for k in keys if k not in ["self", "args", "kwargs"]]

        for k in keys:
            if k not in d:
                d[k] = None
                # msg = f"Cannot cast dict to <{cls.__name__}>: {k!r} not present"
                # log.critical(msg)
                # raise TypeError(msg)

        s = {k: d.pop(k) for k in keys}

        c = cls(**s)
        for k in c.registered:
            if not hasattr(c, k):
                setattr(c, k, d.get(k))
        return c


class IOEncoder(NumpyEncoder):
    def default(self, obj):
        if isinstance(obj, BaseIO):
            return obj.to_dict()
        return super().default(obj)


# class Bases(Dict[str, BaseIO]):  # python >= 3.9
class Bases(dict):
    __orig_bases__ = None
    inner_class = BaseIO  # python < 3.9

    # python >= 3.9:
    # @classmethod
    # @property
    # def inner_class(cls):
    #     return get_args(cls.__orig_bases__[0])[1]

    def add(self, *args, **kwargs):
        c = self.inner_class(*args, **kwargs)
        self[c.name] = c
        # return self
        return self[c.name]

    def __init__(self, *items: Union[T, List[T], Bases, dict]):
        # # if len(items)>0:
        # #     breakpoint()
        # def l_(x):
        #     if isinstance(x, BaseIO):
        #         return x
        #     elif isinstance(x, dict):
        #         return self.inner_class.from_dict(x)
        #     else:
        #         breakpoint()
        #
        # its = []
        # for z in get_iterable(items):
        #     if isinstance(z, dict):
        #         z = [z]
        #     for x in get_iterable(z):
        #         if isinstance(x, dict):
        #             y = next(iter(x.values()))
        #             if isinstance(y, BaseIO):
        #                 its.extend(l_(k) for k in l_(x.values()))
        #         else:
        #             its.append(l_(x))
        # # if len(its) > 0:
        # #     breakpoint()
        # items = its
        # # items = [l_(x) for z in get_iterable(items) for x in get_iterable(z)]
        # # print(x)
        # # if isinstance(x, dict):
        # #     y = next(iter(x.values()))
        # #     if isinstance(y, BaseIO):
        # #         items = list(x.values())
        # #     # else:
        # #     elif isinstance(y, dict):
        # #
        # #     else:
        # #     #     breakpoint()
        ln = len(items)
        if ln > 0:
            if ln == 1:
                x = items[0]
                if isinstance(x, BaseIO):
                    items = [x]
                elif len(x) == 0:
                    items = []
                elif isinstance(x, list):
                    items = []
                    for z in x:
                        if isinstance(z, dict):
                            items.append(self.inner_class.from_dict(z))
                        else:
                            items.append(z)
                elif isinstance(x, dict):
                    y = list(x.values())[0]
                    if isinstance(y, BaseIO):
                        items = list(x.values())
                    elif isinstance(y, dict):
                        items = [self.inner_class.from_dict(z) for z in x.values()]
                elif len(x) > 0:
                    if isinstance(x[0], BaseIO):
                        items = x
        super().__init__({k.name: k for k in items})

    @property
    def elems(self) -> List[T]:
        return list(self.values())

    @property
    def names(self) -> List[str]:
        return list(self.keys())

    def copy(self) -> TBases:
        return type(self)({k: v.copy() for k, v in self.items()})

    @property
    def table(self) -> Table:
        h, d = self.build_table()
        return Table(header=h, rows=d)

    show = table
    THeader = List[str]
    TData = List[List[TValue]]

    def build_table(self) -> Tuple[THeader, TData]:
        raise NotImplementedError

    def assign(self, values: Union[np.ndarray, List[TValue]], att: str = "value"):
        cop = self.copy()
        for x, v in zip(cop.values(), values):
            setattr(x, att, v)
        return cop

    @property
    def vals(self):
        return [x.value for x in self.values()]

    def print(self):
        return f"{type(self).__name__}:\n{self.table()}"

    def to_dict(self):
        return {k: v.to_dict() for k, v in self.items()}

    def __add__(self, other):
        if not isinstance(other, dict):
            other = {x.name: x for x in get_iterable(other)}
        return type(self)(*{**self, **other}.values())

    def __getattr__(self, item):
        if item in self:
            return self[item]
        return super().__getattribute__(item)

    def __setattr__(self, key, value):
        if key in self:
            self[key] = value
        else:
            super().__setattr__(key, value)


T = TypeVar("T", bound=BaseIO)
TBases = TypeVar("TBases", bound=Bases)


log = logging.getLogger(__name__)
