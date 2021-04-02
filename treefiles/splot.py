try:
    import matplotlib.pyplot as plt
except ImportError:
    pass


class SimplePlot:
    """
    Cleanly plot a figure with matplotlib.pyplot
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
        """ Give a filename to save the figure """
        self._fname = fname
        self._save = True
