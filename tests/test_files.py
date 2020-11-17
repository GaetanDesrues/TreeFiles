import unittest
from treefiles import Tree, curDirs, isDir, join, dump_json, isfile
import shutil


class TestFiles(unittest.TestCase):
    dir = Tree(curDirs(__file__, "foo"))

    def test_dir(self):
        self.dir.dump()
        self.assertTrue(isDir(self.dir))

    def test_files(self):
        _dir = self.dir.dump()
        _dir.file("test1.txt", ca="test2.vtk")
        self.assertEqual(_dir.test1, join(_dir.abs(), "test1.txt"))
        self.assertEqual(_dir.ca, join(_dir.abs(), "test2.vtk"))

    def test_commons(self):
        _dir = self.dir.dump(clean=True)
        _dir.file("test3.json")

        data = {"test": True}
        dump_json(_dir.test3, data)

        self.assertTrue(isfile(_dir.test3))

    def test_rm(self):
        shutil.rmtree(self.dir.abs())


if __name__ == "__main__":
    unittest.main()
