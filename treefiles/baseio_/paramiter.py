import logging
from typing import Union, List

import numpy as np
import treefiles as tf
from smt.sampling_methods import LHS


"""
See example: https://github.com/GaetanDesrues/TreeFiles/blob/master/examples/example_params.ipynb
"""


class ParamIter:
    """
    Class intended to provide methods to iterate over several sets
    of parameters
    """

    def __init__(
        self,
        *ps: Union[tf.Params, List[tf.Param], tf.Param],
        defaults: Union[tf.Params, List[tf.Param]] = None,
        n: int = None,
    ):
        all_p = []
        for x in tf.get_iterable(ps):
            x = tf.get_iterable(x)
            if isinstance(x, tf.Bases):
                x = x.values()
            for y in x:
                all_p.append(y)
        self.params = all_p
        self.defaults = tf.Params(tf.none(defaults, {}))
        self.n = n

    def __len__(self):
        return len(self.params)

    @property
    def gen(self):
        for x in self.params:
            d = self.defaults.copy()
            for y in tf.get_iterable(x):
                d.setdefault(y.name, y)
                d[y.name].value = y.value
            yield d

    def save(self, fname: str):
        tf.f(fname).dump()
        tf.dump_json(
            fname,
            {
                "n": self.n,
                "N": len(self),
                "varying": self.params,
                "defaults": self.defaults.to_dict(),
            },
            cls=tf.IOEncoder,
        )
        return self

    @classmethod
    def load(cls, fname: str):
        data = tf.load_json(fname)
        return cls(
            tf.Params(data["varying"]),
            n=data["n"],
            defaults=tf.Params(data["defaults"]),
        )


class LinearIter(ParamIter):
    def __len__(self):
        return self.n

    @property
    def gen(self):
        """
        Return self.n sets of parameters, each parameter has n values
        varying linearly between its bounds
        """
        bds = [np.linspace(*x.bounds, self.n) for x in self.params]
        for i in range(self.n):
            d = self.defaults.copy()
            for j, x in enumerate(self.params):
                d.setdefault(x.name, x)
                d[x.name].value = bds[j][i]
            yield d


class LinearOneAtATimeIter(ParamIter):
    def __len__(self):
        return self.n * len(self.params)

    @property
    def gen(self):
        """
        Return self.n*len(self.params) sets of parameters, each parameter has n values
        varying linearly between its bounds while the other are set to default
        """
        for x in self.params:
            self.defaults.setdefault(x.name, x)
        for x in self.params:
            bds = x.bounds
            for val in np.linspace(*bds, self.n):
                d = self.defaults.copy()
                d[x.name].value = val
                yield d

    @property
    def gen_infos(self):
        for x in self.params:
            bds = x.bounds
            for i, val in enumerate(np.linspace(*bds, self.n)):
                d = self.defaults.copy()
                # d.setdefault(y.name, tf.Param(y.name))
                d[x.name].value = val
                yield {"i": i, "varying": d[x.name]}


class LHSParamIter(ParamIter):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        ps = tf.Params(self.params)
        sampling = LHS(xlimits=np.array(ps.bounds), criterion="ese")
        self.params = [ps.assign(x).values() for x in sampling(self.n)]

    def __len__(self):
        return self.n

    @property
    def gen(self):
        for x in self.params:
            d = self.defaults.copy()
            for y in tf.get_iterable(x):
                d.setdefault(y.name, y)
                d[y.name].value = y.value
            yield d


log = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    log = tf.get_logger()

    coef_V3 = tf.Param("coef_V3", bounds=(0.5, 3))
    apd = tf.Param("apd_mid", unit="ms", bounds=(250, 350))
    print(coef_V3, apd)
    print(coef_V3.table())
    print(tf.Params(coef_V3, apd).table())

    # ParamIter
    defs = [tf.Param("constant_param", 1, unit="mm")]
    it = ParamIter([coef_V3.copy()(i) for i in range(4)], defaults=defs)
    log.info(f"ParamIter ({len(it)})")
    for i, x in enumerate(it.gen):
        print(x.table())

    # LinearIter
    it = LinearIter(coef_V3, apd, n=5)
    log.info(f"LinearIter ({len(it)})")
    for i, x in enumerate(it.gen):
        print(x.table())

    # LinearOneAtATimeIter
    it = LinearOneAtATimeIter(coef_V3, apd(210, bounds=(200, 250)), n=5)
    log.info(f"LinearOneAtATimeIter ({len(it)})")
    for i, x in enumerate(it.gen):
        print(x.table())

    # LHSParamIter
    defs = [tf.Param("patient_id", 12)]
    it = LHSParamIter(coef_V3, apd, n=3, defaults=defs)
    log.info(f"LHSParamIter ({len(it)})")
    for i, x in enumerate(it.gen):
        print(x.table())
