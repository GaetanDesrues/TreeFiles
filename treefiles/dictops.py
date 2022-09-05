import logging
from collections import defaultdict


def analyse(d):
    # Analyse a list of dict
    from munch import munchify

    r = defaultdict(list)
    for x in d:
        for k, v in x.items():
            r[k].append(v)
    return munchify(r)


def query(d, **kw):
    # Query a list of dict
    xkeep = []
    for x in d:
        cond = True
        for k, v in kw.items():
            if x.get(k) != v:
                cond = False
                break
        if cond:
            xkeep.append(x)
    return xkeep


log = logging.getLogger(__name__)
