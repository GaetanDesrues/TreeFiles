import glob
import json
import logging
import os
import re
import shutil
from os.path import join, isfile, basename, isdir
from typing import TypeVar, List

from treefiles.tree import Tree

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


T = TypeVar("T", bound=Tree)


def isDir(path: [str, T]):
    """ Wrapper of `os.path.isdir` """
    if isinstance(path, Tree):
        return isdir(path.abs())
    return isdir(path)


def load_yaml(fname: str, **kwargs):
    """ Loads a yaml file with `yaml.load`

    :return: dict
    """
    if not YAML:
        logging.error("You must install yaml: `pip install PyYAML`")
    if not isfile(fname):
        logging.critical(f"{fname!r} has not been found")
    with open(fname, "r") as f:
        kwargs.update({"Loader": kwargs.get("Loader", Loader)})
        return yaml.load(f, **kwargs)


def dump_yaml(fname: str, data, **kwargs):
    """ Dumps a dict to a yaml file with `yaml.dump`

    :param data: dict
    """
    if not YAML:
        logging.error("You must install yaml")
    with open(fname, "w") as f:
        kwargs.update({"Dumper": kwargs.get("Dumper", Dumper)})
        f.write(yaml.dump(data, **kwargs))


def load_json(filename: str, **kwargs):
    """ Loads a json file with `json.load`

    :return: dict
    """
    with open(filename, "r") as f:
        return json.load(f, **kwargs)


def dump_json(filename: str, data, **kwargs):
    """ Dumps a dict to a json file with `json.dump`

    :param data: dict
    """
    kwargs["indent"] = kwargs.get("indent", 4)
    with open(filename, "w") as f:
        json.dump(data, f, **kwargs)


def pprint_json(data: dict):
    """ Returns a pretty printed dict """
    return json.dumps(data, indent=4)


def curDir(file: str = None):
    """ Absolute path of current directory """
    return os.getcwd() if file is None else os.path.dirname(os.path.abspath(file))


def curDirs(file: str, *paths: str):
    """ Absolute path of current directory joined with `*paths` """
    return join(curDir(file), *paths)


def removeIfExists(fname: str):
    """ Remove `fname` if it exists """
    if os.path.exists(fname):
        os.remove(fname)


def remove(*args: str):
    """ Remove files in globs `*args` if they exist """
    for t in args:
        for f in glob.glob(t):
            removeIfExists(f)


def move(arg: str, dest: str):
    """ Move files in glob `arg` to `dest` with `shutil.move` """
    for f in glob.glob(arg):
        removeIfExists(join(dest, os.path.basename(f)))
        shutil.move(f, dest)


def copyfile(arg: str, dest: str):
    """ Copy a file in glob `arg` to `dest` with `shutil.copyfile`

    `dest` is a directory path, later joined with args' basenames
    """
    for f in glob.glob(arg):
        shutil.copyfile(f, join(dest, os.path.basename(f)))


def copyFile(src: str, dst: str):
    """ Copy a file `src` to `dst` with `shutil.copyfile`

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
    with open(fname, "w") as f:
        for line in data:
            f.write(str(delimiter).join(map(str, line)) + "\n")


def load_txt(fname: str, delimiter=" "):
    with open(fname, "r") as f:
        data = f.read().split("\n")
    while data[-1] == "":
        data = data[:-1]
    return list(map(lambda x: x.rstrip().split(delimiter), data))


def find_new_dir(temp: str, start=0):
    """ Return new directory name indexed as the first `start` index available in `temp` formattable path """
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


def listdir(root: [T, str]) -> List[str]:
    """
    Returns a list of files and folders in directory
    """
    if isinstance(root, str):
        root = Tree(root)

    l = os.listdir(root.abs())
    l = natural_sort(l)
    return list(map(root.path, l))
