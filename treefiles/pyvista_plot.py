import logging

import treefiles as tf

try:
    import pyvista as pv
    from MeshObject import Object
except ImportError:
    pass


class PvPlot(pv.Plotter):
    def __init__(
        self,
        theme="paraview",
        fname: str = None,
        show: bool = True,
        save: bool = None,
        transparent: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)
        pv.set_plot_theme(theme)

        self._fname = fname
        self._save = fname is not None if save is None else save
        self._show = show
        self._transparent = transparent

    def add_mesh(self, mesh, **kwargs):
        if isinstance(mesh, Object):
            mesh = pv.wrap(mesh.data)
        super().add_mesh(mesh, **kwargs)

    def add_meshes(self, meshes):
        for x in meshes:
            if isinstance(x, tuple) or isinstance(x, list):
                self.add_mesh(x[0], **x[1])
            else:
                self.add_mesh(x)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._fname is not None and self._save:
            log.debug(f"Figure saved to {self._fname}")
            self.screenshot(
                filename=self._fname, transparent_background=self._transparent
            )

        if self._show:
            self.show()

        self.close()

    def save(self, fname):
        """ Give a filename to save the figure """
        self._fname = fname
        self._save = True


log = logging.getLogger(__name__)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    log = tf.get_logger()

    m = Object.Sphere()
    m2 = m.copy()
    m2.transform(translate=[2, 0, 0])

    with PvPlot(off_screen=True) as plotter:
        plotter.add_meshes([[m2, {"show_edges": True}], m])
        plotter.save(tf.curDirs(__file__, "plot.png"))
