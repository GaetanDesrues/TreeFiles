import matplotlib.pyplot as plt


class SimplePlot:
    def __init__(self, fname=None, show=True, save=None):
        self.fname = fname
        self.save = fname is not None if save is None else save
        self.show = show

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        fig = plt.gcf()

        if self.fname is not None and self.save:
            fig.savefig(self.fname)

        if self.show:
            plt.show()

        plt.close(fig)