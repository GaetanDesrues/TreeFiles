import os
import re
from typing import List

import treefiles as tf


@tf.timer
def main():
    root = tf.Tree.new(__file__, "foo")
    root.file("test1.txt", ca="test2.vtk")
    second = root.dir("bar", "second")
    second.file("Hello_second.txt")
    root.bar.file("Hello_bar.txt")

    # print(root)
    # <path-to-examples>/foo
    #     └ bar
    #         └ Hello_bar.txt
    #     └ second
    #         └ Hello_second.txt
    #     └ test1.txt
    #     └ test2.vtk

    # print(root.p)
    # <path-to-examples>/hello.txt

    # dir.dump()
    # dir.remove_empty()

    def natural_sort(l: List) -> List:
        convert = lambda text: int(text) if text.isdigit() else text.lower()
        alphanum_key = lambda key: [convert(c) for c in re.split("(\d+)", key)]
        return sorted(l, key=alphanum_key)

    def ls(self):
        l = os.listdir(self.abs())
        l = natural_sort(l)
        l = list(map(self.path, l))
        return l

    print(ls(root))


if __name__ == "__main__":
    main()
