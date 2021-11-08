import logging

import pyvista as pv
import treefiles as tf
from MeshObject import Object
from pyvista import themes


# Add callback to print camera position
#  -->  p.add_key_event("c", lambda: print(p.camera_position))


class Themes:
    paraview = themes.ParaViewTheme()
    doc = themes.DocumentTheme()

    # test = themes.DefaultTheme()
    # test.color = "black"
    # test.show_edges = True
    # test.edge_color = "k"
    # test.background = "w"
    # test.transparent_background = True


class PvPlot(pv.Plotter):
    T = Themes()

    def __init__(
        self,
        theme=T.paraview,
        fname: str = None,
        show: bool = True,  # prefer `off_screen=True`
        save: bool = None,
        transparent: bool = True,
        **kwargs,
    ):
        kwargs = {**kwargs, "theme": theme}
        super().__init__(**kwargs)

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
            if isinstance(x, (tuple, list)):
                self.add_mesh(x[0], **x[1])
            elif isinstance(x, dict):
                assert "mesh" in x
                x = dict(x)
                self.add_mesh(x.pop("mesh"), **x)
            else:
                self.add_mesh(x)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._fname is not None and self._save:
            log.debug(f"Figure saved to file://{self._fname}")
            self.screenshot(
                filename=self._fname, transparent_background=self._transparent
            )

        if self._show:
            self.show()

        self.close()

    def save(self, fname):
        """Give a filename to save the figure"""
        self._fname = fname
        self._save = True


log = logging.getLogger(__name__)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    log = tf.get_logger()

    m = Object.Sphere()
    m2 = m.copy()
    m2.transform(translate=[2, 0, 0])

    with PvPlot() as plotter:  # off_screen=True
        plotter.add_meshes([[m2, {"show_edges": True}], m])
        # plotter.save(tf.curDirs(__file__, "plot.png"))
