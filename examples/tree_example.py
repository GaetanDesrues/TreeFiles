from treefiles import Tree, curDirs


def main():
    dir = Tree(curDirs(__file__, "foo"))
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

    # dir.dump()
    # dir.remove_empty()


if __name__=="__main__":
    main()