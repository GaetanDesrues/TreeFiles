import collections
import ctypes
import glob
import inspect
import io
import json
import logging
import os
import random
import re
import shutil
import string
import sys
import tempfile
import time
from contextlib import contextmanager
from os.path import join, isfile, basename, isdir
from typing import List, Union
from zipfile import ZipFile

from treefiles.tree import Tree, Str, S, T, TS

try:
    try:
        import yaml
        from yaml import CLoader as Loader, CDumper as Dumper
    except ImportError:
        from yaml import Loader, Dumper
    YAML = True
except:
    YAML = False
# `pip install PyYAML` to install yaml


def join(*paths: TS) -> S:
    """Wrapper of `os.path.join`"""
    x = map(lambda y: y.abs() if isinstance(y, Tree) else y, paths)
    return Str(os.path.join(*x))


def isDir(path: TS):
    """Wrapper of `os.path.isdir`"""
    if isinstance(path, Tree):
        return isdir(path.abs())
    return isdir(path)


def load_yaml(fname: str, **kwargs):
    """Loads a yaml file with `yaml.load`"""
    if not YAML:
        logging.error("You must install yaml: `pip install PyYAML`")
    if not isfile(fname):
        logging.critical(f"{fname!r} has not been found")
    with open(fname, "r") as f:
        kwargs.update({"Loader": kwargs.get("Loader", Loader)})
        return yaml.load(f, **kwargs)


if YAML:

    class NoAliasDumper(yaml.SafeDumper):
        def ignore_aliases(self, *_):
            return True


def dump_yaml(fname: str, data, **kwargs):
    """Dumps a dict to a yaml file with `yaml.dump`"""
    if not YAML:
        logging.error("You must install yaml")
    with open(fname, "w") as f:
        kwargs.update({"Dumper": kwargs.get("Dumper", Dumper)})  # NoAliasDumper
        f.write(yaml.dump(data, **kwargs))


def load_json(filename: str, force_ext: bool = True, munch: bool = False, **kwargs):
    """Loads a json file with `json.load`

    :return: dict
    """
    if force_ext:
        filename = ensure_ext(filename, "json")
    with open(filename, "r") as f:
        if munch:
            from munch import munchify

            return munchify(json.load(f, **kwargs))
        else:
            return json.load(f, **kwargs)


def dump_json(filename: str, data, force_ext: bool = True, **kwargs):
    """Dumps a dict to a json file with `json.dump`

    :param data: dict
    """
    if force_ext:
        filename = ensure_ext(filename, "json")
    kwargs["indent"] = kwargs.get("indent", 4)
    with open(filename, "w") as f:
        json.dump(data, f, **kwargs)


def load_str(filename: str, method="read") -> str:
    """Loads a file to string"""
    with open(filename, "r") as f:
        return getattr(f, method)()


def dump_str(filename: str, data):
    """Dumps `str(data)` to file"""
    with open(filename, "w") as f:
        f.write(str(data))  # .encode("utf-8")


def pprint_json(data: dict):
    """Returns a pretty printed dict"""
    return json.dumps(data, indent=4)


def curDir(file: str = None):
    """Absolute path of current directory"""
    return os.getcwd() if file is None else os.path.dirname(os.path.abspath(file))


def curDirs(file: str, *paths: str) -> S:
    """Absolute path of current directory joined with `*paths`"""
    return Str(join(curDir(file), *paths))


def removeIfExists(fname: str):
    """Remove `fname` if it exists"""
    if os.path.exists(fname):
        os.remove(fname)


def remove(*args: str):
    """Remove files in globs `*args` if they exist"""
    for t in args:
        for f in glob.glob(t):
            removeIfExists(f)


def move(arg: str, dest: str):
    """Move files in glob `arg` to `dest` with `shutil.move`"""
    for f in glob.glob(arg):
        removeIfExists(join(dest, os.path.basename(f)))
        shutil.move(f, Str(dest))


def copyfile(arg: str, dest: TS):
    """Copy a file in glob `arg` to `dest` with `shutil.copyfile`

    `dest` is a directory path, later joined with args' basenames
    """
    if isinstance(dest, Tree):
        dest = dest.abs()
    for f in glob.glob(arg):
        shutil.copyfile(f, join(dest, os.path.basename(f)))


def copyFile(src: str, dst: str):
    """Copy a file `src` to `dst` with `shutil.copyfile`

    dst is a file, the file path of the copied file
    """
    shutil.copyfile(src, dst)


def link(in_fname: str, out_dir: T):
    """
    Will create a sym link from `in_fname` to the directory out_dir
    :param in_fname str: Filename of the file
    :param out_dir Tree: Tree instance representing the directory where to save the link
    :return: filename of the created link
    """
    quick_link = out_dir.path(basename(in_fname))
    removeIfExists(quick_link)
    os.symlink(in_fname, quick_link)
    return quick_link


def dump_txt(fname: str, data, delimiter=" "):
    fname = ensure_ext(fname, "txt")
    with open(fname, "w") as f:
        for line in data:
            f.write(str(delimiter).join(map(str, get_iterable(line))) + "\n")


def load_txt(fname: str, delimiter=" "):
    fname = ensure_ext(fname, "txt")
    with open(fname, "r") as f:
        data = f.readlines()
    return [x.rstrip().split(delimiter) if delimiter in x else x.rstrip() for x in data]


def find_new_dir(temp: str, start=0):
    """Return new directory name indexed as the first `start` index available in `temp` formattable path"""
    while isdir(temp.format(start)):
        start += 1
    return temp.format(start)


def greedy_download(*fnames: str, force: bool = False):
    if force:
        return True
    for x in fnames:
        if not os.path.isfile(x):
            return True
    return False


def natural_sort(l: List[str]) -> List[str]:
    """
    Sorts a list of paths in a natural way
    """
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split(r"(\d+)", key)]
    return sorted(l, key=alphanum_key)


def listdir(root: Union[T, str]) -> List[S]:
    """
    Returns a list of files and folders in directory
    """
    if isinstance(root, str):
        root = Tree(root)

    l = os.listdir(root.abs())
    l = natural_sort(l)
    return [Str(root.path(x)) for x in l]


def load_zip(file_name: str):
    """
    Extract a zip file

    :param file_name: path to the zip file
    """
    with ZipFile(file_name, "r") as z:
        z.extractall(path=curDir(file_name))


def dump_zip(file_name: str, paths: Union[str, Tree, List[str]], name: str = None):
    """
    Writes a bunch of files to a zip file

    :param file_name: path to the zip file
    :param paths: either a directory path (in this case all files under it
        are included in the zip file), or a list of files. The tree structure is respected
        only if a directory path is given. If a list is given, all files are zipped under
        the common directory name `name`.
    :param name: common directory name in zip file
    """
    removeIfExists(file_name)

    if isinstance(paths, (str, Tree)):
        pa = Tree(paths)
        cdir = os.path.basename(pa.p.abs())
        paths = get_all_file_paths(pa.abs())
        aname = [x.split(cdir)[1] for x in paths]
        if name is not None:
            cad = os.path.basename(pa.abs())
            aname = [x.replace(cad, name) for x in aname]

    else:
        if name is None:
            name = "zipped_files"
        aname = [os.path.join(name, os.path.basename(x)) for x in paths]

    with ZipFile(file_name, "w") as z:
        for file, name in zip(paths, aname):
            z.write(file, arcname=name)


def get_all_file_paths(directory) -> List[str]:
    file_paths = []
    for root, _, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)
    return file_paths


def get_timestamp(fmt: str = "%d%m%Y_%H%M%S") -> str:
    """
    Return timestamp: 25122021_151240
    """
    from datetime import datetime

    return datetime.now().strftime(fmt)


def insert_before(src: str, sub: str, data) -> str:
    """
    >>> insert_before("long_filename.mha", ".mha", "_newfile")
    long_filename_newfile.mha
    """
    i = src.find(sub)
    return Str(f"{src[:i]}{data}{src[i:]}")


def flatten_dict(d, parent_key="", sep="_"):
    """
    Flatten a dictionnary
    """
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if v and isinstance(v, collections.MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def update_dict(fname: str, **kw):
    d = load_json(fname)
    d.update(kw)
    dump_json(fname, d)


def ensure_ext(fname: str, ext: str) -> S:
    if not fname.endswith(f".{ext}"):
        fname += f".{ext}"
    return Str(fname)


class redirect_stdout:
    """
    Usage:
        with tf.redirect_stdout(fname: str):
            ...
    """

    def __init__(self, fname: str):
        self.old_target = sys.stdout
        sys.stdout = open(fname, "w")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self.old_target


class redirect_stderr:
    """
    Usage:
        with tf.redirect_stderr(fname: str):
            ...
    """

    def __init__(self, fname: str):
        self.old_target = sys.stderr
        sys.stderr = open(fname, "w")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stderr.close()
        sys.stderr = self.old_target


class no_stdout:
    """
    Usage:
        with tf.no_stdout(is_enabled: bool):
            ...
    """

    def __init__(self, enable: bool):
        self.enable = enable
        if enable:
            self.old_target = sys.stdout
            sys.stdout = open(os.devnull, "w")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.enable:
            sys.stdout.close()
            sys.stdout = self.old_target


libc = ctypes.CDLL(None)
c_stdout = ctypes.c_void_p.in_dll(libc, "stdout")
c_stderr = ctypes.c_void_p.in_dll(libc, "stderr")


@contextmanager
def stdout_redirector(stream):
    # The original fd stdout points to. Usually 1 on POSIX systems.
    original_stdout_fd = sys.stdout.fileno()

    def _redirect_stdout(to_fd):
        """Redirect stdout to the given file descriptor."""
        # Flush the C-level buffer stdout
        libc.fflush(c_stdout)
        # Flush and close sys.stdout - also closes the file descriptor (fd)
        sys.stdout.close()
        # Make original_stdout_fd point to the same file as to_fd
        os.dup2(to_fd, original_stdout_fd)
        # Create a new sys.stdout that points to the redirected fd
        sys.stdout = io.TextIOWrapper(os.fdopen(original_stdout_fd, "wb"))

    # Save a copy of the original stdout fd in saved_stdout_fd
    saved_stdout_fd = os.dup(original_stdout_fd)
    try:
        # Create a temporary file and redirect stdout to it
        tfile = tempfile.TemporaryFile(mode="w+b")
        _redirect_stdout(tfile.fileno())
        # Yield to caller, then redirect stdout back to the saved fd
        yield
        _redirect_stdout(saved_stdout_fd)
        # Copy contents of temporary file to the given stream
        tfile.flush()
        tfile.seek(0, io.SEEK_SET)
        stream.write(tfile.read())
    finally:
        tfile.close()
        os.close(saved_stdout_fd)


@contextmanager
def stderr_redirector(stream):
    # The original fd stderr points to. Usually 1 on POSIX systems.
    original_stderr_fd = sys.stderr.fileno()

    def _redirect_stderr(to_fd):
        """Redirect stderr to the given file descriptor."""
        # Flush the C-level buffer stderr
        libc.fflush(c_stderr)
        # Flush and close sys.stderr - also closes the file descriptor (fd)
        sys.stderr.close()
        # Make original_stderr_fd point to the same file as to_fd
        os.dup2(to_fd, original_stderr_fd)
        # Create a new sys.stderr that points to the redirected fd
        sys.stderr = io.TextIOWrapper(os.fdopen(original_stderr_fd, "wb"))

    # Save a copy of the original stderr fd in saved_stderr_fd
    saved_stderr_fd = os.dup(original_stderr_fd)
    try:
        # Create a temporary file and redirect stderr to it
        tfile = tempfile.TemporaryFile(mode="w+b")
        _redirect_stderr(tfile.fileno())
        # Yield to caller, then redirect stderr back to the saved fd
        yield
        _redirect_stderr(saved_stderr_fd)
        # Copy contents of temporary file to the given stream
        tfile.flush()
        tfile.seek(0, io.SEEK_SET)
        stream.write(tfile.read())
    finally:
        tfile.close()
        os.close(saved_stderr_fd)


def none(var, default_value):
    """Quick 'if is None'"""
    return default_value if var is None else var


def get_iterable(x):
    """Ensure x is iterable"""
    from collections.abc import Iterable

    if isinstance(x, str):
        return (x,)
    elif isinstance(x, Iterable):
        return x
    else:
        return (x,)


def print_link(file=None, line=None):
    """
    Print a link in PyCharm to a line in file
    Defaults to line where this function was called
    """
    if file is None:
        file = inspect.stack()[1].filename
    if line is None:
        line = inspect.stack()[1].lineno
    string = f'File "{file}", line {max(line, 1)}'
    return string


def print_link_to_obj(obj):
    """
    Print a link in PyCharm to a module, function, class, method or property
    """
    if isinstance(obj, property):
        obj = obj.fget
    file = inspect.getfile(obj)
    line = inspect.getsourcelines(obj)[1]
    return print_link(file=file, line=line)


def unique(x: List):
    """
    Return a copy of x with copies removed
    """
    z = []
    for y in x:
        if not y in z:
            z.append(y)
    return z


def is_abs(path: TS) -> bool:
    return Tree(path).abs() == path


def get_string(size=6, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


def copy_tree(src, dst, dirs_exist_ok=True, **kw):
    if isinstance(src, Tree):
        src = src.abs()
    if isinstance(dst, Tree):
        dst = dst.abs()
    return shutil.copytree(src, dst, dirs_exist_ok=dirs_exist_ok, **kw)


def dump(dst: TS, clean: bool = False) -> T:
    return Tree(dst).dump(clean)


class Timer:
    """
    Basic timer with context

    .. code-block::

        with Timer() as t:
            time.sleep(1.46)
        print(t.secs)  # 1.460746487020515

    """

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time.perf_counter()
        self.secs = end_time - self.start_time  # seconds


def logf(fname):
    fname = Str(fname)
    logging.info(f"Wrote {fname.basename!r} to file://{fname.parent}")


def logd(dname):
    dname = Str(dname)
    logging.info(f"Directory path: file://{dname}")


def breaklines(x: str, k: int = 50, bc: str = "\n"):
    """Will return a copy of the string x with breaklines
    between words if line lenght is greater than k"""
    x = str(none(x, ""))
    x_ = x.split()
    groups = [""]
    for y in x_:
        if len(groups[-1]) + len(y) < k:
            groups[-1] += " " + y
        else:
            groups.append(y)
    groups[0] = groups[0][1:]
    return bc.join(groups)
