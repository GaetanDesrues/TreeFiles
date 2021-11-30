import matplotlib.pyplot as plt
from treefiles.pyplot import despine


class SimplePlot:
    """
    Cleanly plot a figure with matplotlib.pyplot
    fig, ax = plt.subplots()
    """

    def __init__(self, fname: str = None, show: bool = True, save: bool = None):
        """
        :param fname: figure filename
        :param show: if `plt.show` must be called
        :param save: if `fig.savefig` must be called
        """
        self._fname = fname
        self._save = fname is not None if save is None else save
        self._show = show

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Get the current figure, save/show it if specified and finally close the figure properly
        """
        fig = plt.gcf()

        if self._fname is not None and self._save:
            fig.savefig(self._fname)

        if self._show:
            plt.show()

        plt.close(fig)

    def save(self, fname):
        """Give a filename to save the figure"""
        self._fname = fname
        self._save = True


class APlot(SimplePlot):
    def __enter__(self):
        fig, ax = plt.subplots()
        return fig, ax

    def __exit__(self, exc_type, exc_val, exc_tb):
        fig = plt.gcf()

        fig.legend()
        despine(fig)
        fig.tight_layout()

        if self._fname is not None and self._save:
            fig.savefig(self._fname)

        if self._show:
            plt.show()

        plt.close(fig)
