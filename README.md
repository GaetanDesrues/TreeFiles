# TreeFiles

### A sympathic way of dealing with filenames, and more...

Documentation: [here](https://www-sop.inria.fr/members/Gaetan.Desrues/treefiles/).

```python
import treefiles as tf

dir = tf.Tree.new(__file__, "foo")
dir.file("test1.txt", ca="test2.vtk")

bar = dir.dir("bar")
bar.file("Hello_bar.txt")

print(dir)
# Output:
# <path-to-directory>/foo
#     └ bar
#         └ Hello_bar.txt
#     └ test1.txt
#     └ test2.vtk
```


```python
dir.dump()  # Create directory with os.makedirs
dir.remove_empty()  # Delete empty directories
```