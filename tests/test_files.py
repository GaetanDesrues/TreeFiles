import pickle
import shutil
import unittest

import treefiles as tf


class TestFiles(unittest.TestCase):
    my_dir = tf.fTree(__file__, "foo")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.my_dir.abs())

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
        res = tf.start_oar(runme_str="runme.sh", do_run=False)
        _res = "oarsub --resource /host=1/core=1,walltime=00:01:00 --queue default runme.sh"
        self.assertIsInstance(res, list)
        self.assertEqual(" ".join(res), _res)

    def test_tree_parent_dir(self):
        _dir = tf.Tree.new(__file__, "foo")
        self.assertIsInstance(_dir.p, tf.Tree)
        self.assertEqual(_dir.p.abs(), tf.curDir(__file__))

    def test_temp_dir(self):
        root = tf.curDir(__file__)
        with tf.TmpDir(root) as tmp:
            self.assertTrue(tf.isDir(tmp.abs()))
            fname = tmp.abs()
        self.assertFalse(tf.isDir(fname))

    def test_tree_format(self):
        root = self.my_dir.dump().file("t.tree")
        root.dir(k="j").file(oui="non.txt")
        root.to_file(root.t)
        o = tf.Tree.from_file(self.my_dir.path("t.tree"))
        self.assertEqual(o.k.oui, self.my_dir.path("j/non.txt"))

    def test_str(self):
        aa = self.my_dir.path("oui")
        self.assertIsInstance(aa.parent, tf.Tree)
        self.assertEqual(aa.sibling("oui"), aa)


if __name__ == "__main__":
    unittest.main()
