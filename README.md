# TreeFiles

### A sympathic way of dealing with filenames, and more...

Documentation: [here](https://treefiles.doc.kerga.fr).

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

## Introducing the `tree` format

Each folder is considered a Tree object. Each file is a leaf.
Each Tree has a root, either a dirname or an absolute path. If no root is specified, `os.getcwd` is used.


**Tree's main methods**
- `abs`: return the absolute path, recursively calling `parent.abs`
- `path`: concatenate a filename and return the absolute path
- `file`: register a list of files for the current Tree
- `dir`: register a list of directories for the current Tree


**Tree instanciation**
- The natural way to create a Tree instance is by calling the `tf.Tree` constructor. In this case, pass the root as te `name` argument.
- Another way is by using `tf.fTree`, which concatenates the dirname of the first argument and the other arguments.
- Similarly, `tf.jTree` joins all the arguments and create a Tree with the joined name.


**Retrieve Tree attributes**

To get a dir or file path, just call this object as an attribute.
For example:
```python
import treefiles as tf

out = tf.Tree("/my-root")
print(type(out), out.abs())
# <class 'treefiles.tree.Tree'> /my-root

print(out.file("file1.txt", file2="complicated filename.vtk"))
# root (/my-root)
#   └ file1.txt
#   └ [file2] complicated filename.vtk
print(out.file1)
# '/my-root/file1.txt'
print(out.file2)
# '/my-root/complicated filename.vtk'
print(out.get_files())
# ['/my-root/file1.txt', '/my-root/complicated filename.vtk']
print(out.dir(d='my-dir').file('example'))
# my-dir (/my-root/my-dir)
# └ example
print(out.d.abs())
# /my-root/my-dir
print(out.example)
# /my-root/my-dir/example

print(out)
# /my-root
#   └ file1.txt
#   └ [file2] complicated filename.vtk
#   └ [d] my-dir
#     └ example
```


### Create a Tree object from file
Create the file `my_tree.tree`:
```
.  # Main directory root
	. folder_A
		- a: b.vtk
	. b: folder_B
		- some_file.txt
		- id: some other file.txt
```
```bash
>>> import treefiles as tf
>>> out = tf.Tree.from_file(__file__, 'my_tree.tree')
>>> out
/my/root
  └ folder_A
    └ [a] b.vtk
  └ [b] folder_B
    └ some_file.txt
    └ [id] some other file.txt
```

You can now retrieve your filename: 
```bash
>>> out.some_file
/my/root/folder_B/some_file.txt
>>> out.a
/my/root/folder_A/b.vtk
```
Browse all files: 
```bash
>>> out.b.get_files()
['/my/root/folder_B/some_file.txt', '/my/root/folder_B/some other file.txt']
```

### Includes
Change your `tree` file to add the `<` keyword, importing a tree from another file:
```
.  # Main directory root
	. folder_A
		- a: b.vtk
	. b: folder_B
		- some_file.txt
		- id: some other file.txt
		< nested: my_nested_tree.tree
```
Create the `my_nested_tree.tree` file:
```
.
	. folder_C
		- b.vtk
	. folder_D
		- nested_file: some_file.txt
		- id2: some other (other) file.txt
```
Now print the tree:
```bash
>>> out = tf.Tree.from_file(__file__, 'my_tree.tree')
>>> out
/my/root
  └ folder_A
    └ [a] b.vtk
  └ [b] folder_B
    └ some_file.txt
    └ [id] some other file.txt
    └ nested
      └ folder_C
        └ b.vtk
      └ folder_D
        └ nested_file: some_file.txt
        └ [id2] some other (other) file.txt
>>> out.folder_D.abs()
/my/root/folder_B/nested/folder_D
>>> out.nested_file
/my/root/folder_B/nested/folder_D/some_file.txt
```