import os
import shutil
from os.path import join, isfile, basename, isdir
import json
import glob
import logging
from .tree import Tree

try:
    try:
        import yaml
        from yaml import CLoader as Loader, CDumper as Dumper
    except ImportError:
        from yaml import Loader, Dumper
    YAML = True
except:
    YAML = False


def isDir(path):
    if isinstance(path, Tree):
        return isdir(path.abs())
    return isdir(path)


def load_yaml(fname):
    if not YAML:
        logging.error("You must install yaml")
    if not isfile(fname):
        logging.critical(f"{fname!r} has not been found")
    with open(fname, "r") as f:
        return yaml.load(f, Loader=Loader)


def dump_yaml(fname, data):
    if not YAML:
        logging.error("You must install yaml")
    with open(fname, "w") as f:
        f.write(yaml.dump(data, Dumper=Dumper))


def load_json(filename, **kwargs):
    with open(filename, "r") as f:
        return json.load(f, **kwargs)


def dump_json(filename, data, **kwargs):
    kwargs["indent"] = kwargs.get("indent", 4)
    with open(filename, "w") as f:
        json.dump(data, f, **kwargs)


def pprint_json(data):
    return json.dumps(data, indent=4)


def curDir(file=None):
    return os.getcwd() if file is None else os.path.dirname(os.path.abspath(file))


def curDirs(file, *paths):
    return join(curDir(file), *paths)


def removeIfExists(fname):
    if os.path.exists(fname):
        os.remove(fname)


def remove(*args):
    for t in args:
        for f in glob.glob(t):
            removeIfExists(f)


def move(arg, dest):
    for f in glob.glob(arg):
        removeIfExists(join(dest, os.path.basename(f)))
        shutil.move(f, dest)


def copyfile(arg, dest):
    for f in glob.glob(arg):
        shutil.copyfile(f, join(dest, os.path.basename(f)))


def copyFile(src, dst):
    shutil.copyfile(src, dst)


def link(in_fname, out_dir):
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
