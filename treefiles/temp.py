import logging
import os
import random
import shutil
import string
import tempfile

import treefiles as tf


def rand(k=8):
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=k))


class TmpDir:
    def __init__(self, root=tempfile.gettempdir()):
        self.root = tf.Tree(root)

    def find_new(self):
        new_name = self.root.path(rand())
        if tf.isDir(new_name):
            return self.find_new()
        else:
            return tf.Tree(new_name)

    def __enter__(self):
        self.root = self.find_new()
        return self.root.dump()

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.root.abs())
        log.debug(f"Deleting {self.root.abs()}")


class TmpFile:
    def __init__(self, mode="w+", suffix=None):
        self.mode = mode
        self.suffix = suffix
        self.fname = None

    def find_new(self):
        new_name = rand()
        return self.find_new() if tf.isfile(new_name) else new_name

    def __enter__(self):
        new_name = self.find_new()
        if self.suffix is not None:
            new_name += self.suffix
        self.fname = os.path.join(tempfile.gettempdir(), new_name)
        self.f = open(self.fname, mode=self.mode)
        return self.f

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.f.close()
        tf.removeIfExists(self.fname)


log = logging.getLogger(__name__)
