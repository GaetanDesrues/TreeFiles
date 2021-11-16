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


class NpArray(np.ndarray):
    """
    An array with extra attributes, being passed on to views and results of
    ufuncs.
    """

    def __new__(cls, array, *args, **kwargs):
        """
        Some magic stolen from numpy docs.

        https://docs.scipy.org/doc/numpy/user/basics.subclassing.html
        """
        # Input array is an already formed ndarray instance
        # We first cast to be our class type
        obj = np.asarray(array).view(cls)
        # add the new attributes to the created instance
        for key, value in kwargs.items():
            setattr(obj, key, value)
        # Finally, we must return the newly created object:
        return obj

    def __array_finalize__(self, obj):
        """
        This function ensures that attributes are present in all ways instances
        are created, including views on the array.
        """
        if type(obj) is not np.ndarray:
            for key, value in vars(obj).items():
                setattr(self, key, value)

    def __array_wrap__(self, obj, context=None):
        """Ensure that scalar type is returned instead of 0D array"""
        if obj.shape == ():
            return obj[()]  # if ufunc output is scalar, return it
        else:
            return np.ndarray.__array_wrap__(self, obj)
