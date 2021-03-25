from os.path import isdir

import treefiles as tf


def find_new_dir(temp, start=0):
    while isdir(temp.format(start)):
        start += 1
    return temp.format(start)


@tf.timer
def main():
    dir = tf.Tree.new(__file__, "foo")
    dir.file("test1.txt", ca="test2.vtk")
    second = dir.dir("bar", "second")
    second.file("Hello_second.txt")
    dir.bar.file("Hello_bar.txt")

    print(dir)
    # <path-to-examples>/foo
    #     └ bar
    #         └ Hello_bar.txt
    #     └ second
    #         └ Hello_second.txt
    #     └ test1.txt
    #     └ test2.vtk

    dir.dump()
    dir.remove_empty()

    kk = find_new_dir(dir.path("test_{}"))
    tf.Tree(kk).dump()
    print(kk)


if __name__ == "__main__":
    main()
