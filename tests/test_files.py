import pickle
import shutil
import unittest

import treefiles as tf


class TestFiles(unittest.TestCase):
    my_dir = tf.Tree(tf.curDirs(__file__, "foo"))

    def test_dir(self):
        self.my_dir.dump()
        self.assertTrue(tf.isDir(self.my_dir))

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


if __name__ == "__main__":
    unittest.main()
