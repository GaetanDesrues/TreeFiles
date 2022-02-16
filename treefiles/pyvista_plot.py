import logging

import numpy as np
import pyvista as pv
import treefiles as tf
from MeshObject import Mesh
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
        show: bool = True,
        save: bool = None,
        transparent: bool = True,
        **kwargs,
    ):
        kwargs = {**kwargs, "theme": theme}
        if not show:
            kwargs.update({"off_screen": True})
        super().__init__(**kwargs)

        self._fname = fname
        self._save = fname is not None if save is None else save
        self._show = show
        self._transparent = transparent

    def add_mesh(self, mesh: Mesh, **kwargs):
        if isinstance(mesh, Mesh):
            if mesh.nbCells == 0:
                return self.add_pts(mesh.pts, **kwargs)
            mesh = mesh.pv

        v = kwargs.pop("vectors", None)
        if v:
            mesh.set_active_vectors(v)
            super().add_mesh(mesh.arrows, **kwargs)
        else:
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
            if self._show:
                self._on_first_render_request()
                self.render()
            self.screenshot(
                filename=self._fname, transparent_background=self._transparent
            )
            log.debug(f"Figure saved to file://{self._fname}")

        if self._show:
            self.show()

        self.close()

    def save(self, fname):
        """Give a filename to save the figure"""
        self._fname = fname
        self._save = True

    def label_point(self, p, label, **kwargs):
        poly = pv.PolyData([p])
        poly["txt"] = [label]
        self.add_point_labels(
            poly,
            "txt",
            point_size=20,
            font_size=36,
            render_points_as_spheres=True,
            **kwargs,
        )

    def vector(self, p, vec):
        poly = pv.PolyData([p])
        poly["vec"] = [vec]
        poly.set_active_vectors("vec")
        self.add_mesh(poly.arrows)

    def add_pts(self, pts, c=None, s=20, **kw):
        # if isinstance(pts, Mesh):
        #     log.warning("Calling 'add_pts' on a Mesh")
        #     return self.add_mesh(pts, color=c, **kw)
        m = pv.PolyData(pts)
        if isinstance(c, (list, np.ndarray)):
            m["c"] = c
            c = None
            kw["scalars"] = "c"
        self.add_mesh(m, render_points_as_spheres=True, point_size=s, color=c, **kw)


log = logging.getLogger(__name__)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    log = tf.get_logger()

    m = Mesh.Sphere()
    m2 = m.copy()
    m2.transform(translate=[2, 0, 0])

    with PvPlot() as plotter:  # off_screen=True
        plotter.add_meshes([[m2, {"show_edges": True}], m])
        # plotter.save(tf.curDirs(__file__, "plot.png"))
