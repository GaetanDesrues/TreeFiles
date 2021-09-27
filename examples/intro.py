import treefiles as tf


def main():
    out = tf.Tree.from_file(__file__, "my_tree.tree")
    out.root = "/my/root"
    print(out)

    out = tf.Tree("/my-root")
    print(type(out), out.abs())

    print(out.file("file1.txt", file2="complicated filename.vtk"))
    print(out.file1)
    print(out.file2)
    print(out.get_files())

    print(out.dir(d="my-dir").file("example"))
    print(out.d.abs())
    print(out.example)

    print(out)


if __name__ == "__main__":
    main()
