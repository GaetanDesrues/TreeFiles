import pickle
import shutil
import unittest
from datetime import time

import treefiles as tf


class TestFiles(unittest.TestCase):
    my_dir = tf.Tree(tf.curDirs(__file__, "foo"))

    def test_dir(self):
        self.my_dir.dir("test").dump()
        self.assertTrue(tf.isDir(self.my_dir.test))

    def test_files(self):
        _dir = self.my_dir.dump()
        _dir.file("test1.txt", ca="test2.vtk")
        self.assertEqual(_dir.test1, tf.join(_dir.abs(), "test1.txt"))
        self.assertEqual(_dir.ca, tf.join(_dir.abs(), "test2.vtk"))

    def test_commons(self):
        _dir = self.my_dir.dump(clean=True)
        _dir.file("test3.json", "test_yaml.yaml")

        data = {"test": True}
        tf.dump_json(_dir.test3, data)

        self.assertTrue(tf.isfile(_dir.test3))

        tf.dump_yaml(_dir.test_yaml, data)
        self.assertTrue(tf.isfile(_dir.test_yaml))
        d = tf.load_yaml(_dir.test_yaml)
        self.assertEqual(d, data)

    def test_rm(self):
        shutil.rmtree(self.my_dir.abs())

    def test_pickle(self):
        d = pickle.dumps(self.my_dir)
        my_dir = pickle.loads(d)
        self.assertIs(type(my_dir), tf.Tree)
        self.assertEqual(self.my_dir.abs(), my_dir.abs())

    def test_oar(self):
        res = tf.start_oar(runme_str="runme.sh",)
        _res = "oarsub --resource /host=1/core=4,walltime=00:10:00 -J --queue default runme.sh"
        self.assertIs(type(res), str)
        self.assertEqual(res, _res)


if __name__ == "__main__":
    unittest.main()
