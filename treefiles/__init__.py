import os

from treefiles.tree import Tree, jTree, fTree, Str, S, T, TS, Container
from treefiles.decorators import debug, timer
from treefiles.pdf import PDFMerger
from treefiles.logs import get_logger, stream_csv_handler, get_csv_logger
from treefiles.oar import start_oar, walltime, NotifyOar, Queue, Program
from treefiles.temp import TmpDir, TmpFile, tmp_
from treefiles.tables import Table
from treefiles.sofa import Viewer, run_sofa
from treefiles.mails import send_mail, register_treemails
from treefiles.poolception import NestablePool
from treefiles.ctxman import timeout
from treefiles.jsonencoder import JsonEncoder

f = fTree


# def F(*a, **kw) -> S:
#     """Creates a filename <Str> while dumping the parent dir"""
#     obj = f(*a, **kw)
#     return obj.p.dump() / obj.basename
def file(fname: str):
    return Str(fname).parent.dump() / Str(fname).basename


def env(k: str, d: str = None):
    r = os.environ.get(k, d)
    if r is None:
        raise KeyError(f"Environment variable {k!r} not found")
    return Str(r)


from munch import munchify, Munch
from treefiles.dictops import analyse, query


def make_string(**kw):
    return "&".join([f"{k}={v}" for k, v in kw.items()])


def decode_string(s) -> Munch:
    return munchify({x.split("=")[0]: x.split("=")[1] for x in s.split("&")})


try:
    from dotenv import load_dotenv
except:
    print("dotenv not found, cannot define 'fenv' -> pip install python-dotenv")
else:

    def fenv(file: str, k: str):
        file = Str(file)
        if file.endswith(".py"):
            file = f(file)
        load_dotenv(file / ".env")
        return env(k)


try:
    from treefiles.baseio_.baseio_ import TValue, BaseIO, Bases, IOEncoder
    from treefiles.baseio_.param import Param, Params, TParams
    from treefiles.baseio_.paramiter import (
        ParamIter,
        LinearIter,
        LinearOneAtATimeIter,
        LHSParamIter,
        RandomSamplingParamIter,
    )
except ImportError:
    pass


try:
    from tqdm import tqdm
except ImportError:
    pass


try:
    from treefiles.dictkeys import print_keys
except ImportError as e:
    print(f"ERROR: {e}")


try:
    import matplotlib.pyplot as plt
except ImportError:
    pass
else:
    from treefiles.pyplot import get_color_cycle, despine, move_legend
    from treefiles.splot import SimplePlot as SPlot, APlot

# Deprecated
# try:
#     import pyvista as pv
#     from MeshObject import Object
# except ImportError:
#     pass
# else:
#     from treefiles.pyvista_plot import PvPlot, Themes


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
    logd,
    breaklines,
    redirect_stdout,
    redirect_stderr,
    redirect_std,
    stdout_redirector,
    stderr_redirector,
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


def glob(path):
    return Tree(curDir(path)).glob(basename(path))


EDSTIC = "#006a9b"


def expanduser(a="~"):
    return Str(os.path.expanduser(a))
