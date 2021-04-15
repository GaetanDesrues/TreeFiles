import logging
import shutil
import string
import tempfile
import random
import treefiles as tf


class TmpDir:
    def __init__(self, root=tempfile.gettempdir()):
        self.root = tf.Tree(root)

    def find_new(self):
        new_name = self.root.path(
            "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        )
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


log = logging.getLogger(__name__)
