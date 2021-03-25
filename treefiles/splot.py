try:
    import matplotlib.pyplot as plt
except ImportError:
    pass


class SimplePlot:
    def __init__(self, fname=None, show=True, save=None):
        self._fname = fname
        self._save = fname is not None if save is None else save
        self._show = show

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        fig = plt.gcf()

        if self._fname is not None and self._save:
            fig.savefig(self._fname)

        if self._show:
            plt.show()

        plt.close(fig)

    def save(self, fname):
        self._fname = fname
        self._save = True