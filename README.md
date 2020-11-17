# TreeFiles

### A sympathic way of dealing with filenames

```bash
>>> dir = Tree(curDirs(__file__, "foo"))
>>> dir.file("test1.txt", ca="test2.vtk")

>>> bar = dir.dir("bar")
>>> bar.file("Hello_bar.txt")

>>> print(dir)
<path-to-directory>/foo
    └ bar
        └ Hello_bar.txt
    └ test1.txt
    └ test2.vtk
```


```python
>>> dir.dump()  # Create tree
>>> dir.remove_empty()  # Clean tree from empty dirs
```