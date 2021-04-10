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

    print(root)
    # <path-to-examples>/foo
    #     └ bar
    #         └ Hello_bar.txt
    #     └ second
    #         └ Hello_second.txt
    #     └ test1.txt
    #     └ test2.vtk

    print(root.p)
    # <path-to-examples>/hello.txt

    # dir.dump()
    # dir.remove_empty()




if __name__ == "__main__":
    main()
