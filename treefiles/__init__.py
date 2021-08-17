from treefiles.tree import Tree, jTree, fTree
from treefiles.decorators import debug, timer
from treefiles.pdf import PDFMerger
from treefiles.splot import SimplePlot as SPlot
from treefiles.logs import get_logger, stream_csv_handler, get_csv_logger
from treefiles.oar import start_oar, walltime, NotifyOar, Queue, Program
from treefiles.temp import TmpDir, TmpFile
from treefiles.tables import Table
from treefiles.sofa import Viewer, run_sofa
from treefiles.mails import send_mail, register_treemails

try:
    import pyvista as pv
    from MeshObject import Object
except ImportError:
    pass
else:
    from treefiles.pyvista_plot import PvPlot


try:
    import numpy as np
except ImportError:
    pass
else:
    from treefiles.np import NumpyEncoder


from treefiles.commons import (
    join,
    isfile,
    basename,
    isDir,
    load_yaml,
    dump_yaml,
    load_json,
    dump_json,
    load_txt,
    dump_txt,
    pprint_json,
    curDir,
    curDirs,
    removeIfExists,
    remove,
    move,
    copyfile,
    copyFile,
    link,
    greedy_download,
    natural_sort,
    listdir,
    load_zip,
    dump_zip,
    get_timestamp,
    insert_before,
    flatten_dict,
    update_dict,
    ensure_ext,
)


# Debug mode
# if tf.DEBUG:
#   ...
DEBUG = False


def set_debug(active: bool):
    global DEBUG
    DEBUG = active
