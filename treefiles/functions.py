import numpy as np

try:
    from matplotlib import pyplot as plt
    from scipy.stats import beta
except:
    pass

import treefiles as tf


def minmax_(x):
    return (x - np.min(x)) / np.max(x - np.min(x))


def beta_(a, b, x=None):
    d = beta(a, b)
    if x is not None:
        return d.cdf(x)
    return d


def plot_beta_example():
    x = np.linspace(0, 1, 100)
    with tf.SPlot():
        fig, axs = plt.subplots(nrows=2, figsize=(3, 6))

        ab = list(zip([0.5, 1, 2], [0.5, 1, 2])) + list(zip([0.5, 1, 2], [2, 1, 0.5]))
        for a, b in ab:
            s = f"a={a}, b={b}"
            axs[0].plot(x, beta_(a, b, x), label=s)
            axs[0].plot(x, x, "k--", alpha=0.3)
            axs[0].plot(x, 1 - x, "k--", alpha=0.3)
            axs[0].legend()

        # ab = [(1, 5), (3, 5), (5, 5), (15, 15), (3, 3), (10, 3)]
        ab = [(6, 5), (6, 13), (5, 5)]
        for a, b in ab:
            s = f"a={a}, b={b}"
            axs[1].plot(x, beta_(a, b, x), label=s)
            axs[1].plot(x, x, "k--", alpha=0.3)
            axs[1].plot(x, 1 - x, "k--", alpha=0.3)
            axs[1].legend()

        tf.despine(fig)
        fig.suptitle("Beta distribution")
        fig.tight_layout()


# plot_beta_example()
