from treefiles.tree import Tree, jTree, fTree, Str, S, T, TS
from treefiles.decorators import debug, timer
from treefiles.pdf import PDFMerger
from treefiles.logs import get_logger, stream_csv_handler, get_csv_logger
from treefiles.oar import start_oar, walltime, NotifyOar, Queue, Program
from treefiles.temp import TmpDir, TmpFile, tmp_
from treefiles.tables import Table
from treefiles.sofa import Viewer, run_sofa
from treefiles.mails import send_mail, register_treemails
from treefiles.poolception import NestablePool


f = fTree


try:
    from treefiles.baseio_.baseio_ import TValue, BaseIO, Bases, IOEncoder
    from treefiles.baseio_.param import Param, Params, TParams
except ImportError:
    pass


try:
    from tqdm import tqdm
except ImportError:
    pass

try:
    import matplotlib.pyplot as plt
except ImportError:
    pass
else:
    from treefiles.pyplot import get_color_cycle, despine, move_legend
    from treefiles.splot import SimplePlot as SPlot, APlot

try:
    import pyvista as pv
    from MeshObject import Object
except ImportError:
    pass
else:
    from treefiles.pyvista_plot import PvPlot, Themes


try:
    import numpy as np
except ImportError:
    pass
else:
    from treefiles.np import (
        NumpyEncoder,
        NpArray,
        normalize,
        project_vector_on_vector,
        project_vector_on_plane,
    )
    from treefiles.functions import beta_, minmax_


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
    load_str,
    dump_str,
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
    no_stdout,
    none,
    get_iterable,
    print_link,
    print_link_to_obj,
    unique,
    is_abs,
    get_string,
    copy_tree,
    dump,
    Timer,
    logf,
    breaklines,
)


# Debug mode
# if tf.DEBUG:
#   ...
DEBUG = False


def set_debug(active: bool = True):
    global DEBUG
    DEBUG = active


def rge(arr):
    return np.min(arr), np.max(arr)