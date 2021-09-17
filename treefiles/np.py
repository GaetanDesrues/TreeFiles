import json

import numpy as np


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, range):
            value = list(obj)
            return [value[0], value[-1] + 1]
        return super().default(obj)


def a(*w, **k):
    return np.array(*w, **k)
