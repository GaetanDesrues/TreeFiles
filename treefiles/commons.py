import collections
import glob
import inspect
import json
import logging
import os
import re
import shutil
import sys
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


def load_json(filename: str, force_ext: bool = True, **kwargs):
    """Loads a json file with `json.load`

    :return: dict
    """
    if force_ext:
        filename = ensure_ext(filename, "json")
    with open(filename, "r") as f:
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
        shutil.move(f, dest)


def copyfile(arg: str, dest: str):
    """Copy a file in glob `arg` to `dest` with `shutil.copyfile`

    `dest` is a directory path, later joined with args' basenames
    """
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
            f.write(str(delimiter).join(map(str, line)) + "\n")


def load_txt(fname: str, delimiter=" "):
    fname = ensure_ext(fname, "txt")
    with open(fname, "r") as f:
        data = f.read().split("\n")
    while data[-1] == "":
        data = data[:-1]
    return list(map(lambda x: x.rstrip().split(delimiter), data))


def find_new_dir(temp: str, start=0):
    """Return new directory name indexed as the first `start` index available in `temp` formattable path"""
    while isdir(temp.format(start)):
        start += 1
    return temp.format(start)


def greedy_download(fname: str, force: bool = False):
    return not os.path.isfile(fname) or force


def natural_sort(l: List[str]) -> List[str]:
    """
    Sorts a list of paths in a natural way
    """
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split("(\d+)", key)]
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
    return f"{src[:i]}{data}{src[i:]}"


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


def none(var, default_value):
    """Quick 'if is None'"""
    return default_value if var is None else var


def get_iterable(x):
    """Ensure x is iterable"""
    from collections.abc import Iterable

    if isinstance(x, Iterable):
        return x
    else:
        return [x]


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
