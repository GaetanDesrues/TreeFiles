import glob
import os
import shutil
from typing import TypeVar, List, Union

T = TypeVar("T", bound="Tree")


class Tree:
    """
    Creates a tree instance

    :param name: root of the current tree
    :param parent: parent tree if current tree is not the main root
    """

    def __init__(self, name: [str, T] = None, parent: T = None):
        if name is not None:
            if isinstance(name, Tree):
                name = name.abs()
        else:
            name = "root"
        self.parent = parent
        self._name = name
        self.dirs = []
        self.ndirs = {}
        self.files = dict()

    @classmethod
    def new(cls, file: str, *args: str, dump: bool = True, clean: bool = False) -> T:
        file = os.path.dirname(os.path.abspath(file))
        c = cls(os.path.join(file, *args))
        if dump:
            c.dump(clean=clean)
        return c

    def abs(self, path="") -> str:
        """
        Returns the absolute path of a tree root

        :param path: recursion parameter
        """
        if self.parent is None:
            return os.path.abspath(self._name)
        return os.path.join(self.parent.abs(path), self._name)

    @property
    def root(self) -> str:
        return self._name

    @root.setter
    def root(self, x: Union[T, str]):
        if isinstance(x, Tree):
            self._name = x.abs()
        else:
            self._name = x

    @property
    def p(self) -> T:
        """
        Returns the parent directory (path only)
        """
        dirs = self.abs().split(os.sep)
        return type(self)(os.sep.join(dirs[:-1]))

    def __getattr__(self, att) -> [str, T]:
        """
        Finds an attribute

        :param att: the attribute name

        The order of preferences is:
            - look for files at current level
            - look for child at current level
            - look in children levels recursively
        """
        if att in self.files:
            if self.files[att] is None:
                return
            return os.path.join(self.abs(), self.files[att])
        for d in self.dirs:
            if d._name == att:
                return d
        for d in self.dirs:
            found = getattr(d, att)
            if found is not None:
                return found
        for alias, d in self.ndirs.items():
            if alias == att:
                return d
        if self.parent is None:
            raise AttributeError(f"Attribute {att!r} not found in {self._name}")

    def __repr__(self, i=2):
        """
        Pretty prints th current tree

        :param i: recursion parameter
        """
        s = f"{self._name}"
        if i == 2:
            s += f" ({self.abs()})"
        s += "\n"
        for d in self.dirs:
            s += f"{' '*i}\u2514 {d.__repr__(i+2)}\n"
        for al, d in self.ndirs.items():
            s += f"{' '*i}\u2514 [{al}] {d.__repr__(i+2)}\n"
        for al, f in self.files.items():
            s += f"{' '*i}\u2514 [{al}] {f}\n"
        return s.rstrip()

    def dir(self, *names: str, **named_dirs: str) -> T:
        """
        Adds directories to the current level

        :param names: folder names
        :return: instance of the last child created
        """
        for name in names:
            self.dirs.append(type(self)(name, parent=self))
        for alias, name in named_dirs.items():
            self.ndirs[alias] = type(self)(name, parent=self)
        if len(self.dirs) > 0:
            return self.dirs[-1]
        if len(self.ndirs) > 0:
            return self.ndirs[list(named_dirs.keys())[-1]]

    def jdir(self, path: str, sep: str = "/") -> T:
        """
        Create directory joining path

        :param sep: separator used in `path`
        :param path: folder path, sperated by `sep`, joined to self.abs()
        """
        path, o = path.split(sep), self
        for i in path:
            if i == "..":
                o = o.p
            else:
                o = o.dir(i)
        return o

    def file(self, *args: str, **kwargs: str):
        """
        Saves a filename at the current tree level

        :param args: filenames, attributes are the files basename
        :param kwargs: filenames, attributes are the kwargs key
        """
        for arg in args:
            name, _ = os.path.splitext(arg)
            self.files[name] = arg
        for k, v in kwargs.items():
            self.files[k] = v

    def path(self, *args: str) -> str:
        """
        Creates a path starting from parent

        :param args: paths to join
        :return: the joined absolute path
        """
        return os.path.join(self.abs(), *args)

    def dump(self, clean: bool = False) -> T:
        """
        Create tree as root (create folder and children)

        :param clean: remove root before recreating it if exists
        :return: root instance
        """
        if clean and os.path.isdir(self.abs()):
            shutil.rmtree(self.abs())

        for d in self.dirs:
            d.dump()
        os.makedirs(self.abs(), exist_ok=True)
        return self

    def remove_empty(self):
        """
        Deletes empty children
        """
        for d in self.dirs:
            d.remove_empty()

        if os.path.isdir(self.abs()) and len(os.listdir(self.abs())) == 0:
            os.rmdir(self.abs())

    def __getstate__(self):
        """
        Pickles an object.

        Because of recursion on __getstate__, only the absolute path is saved when pickling for the moment.
        You can override this method if it does not meet your needs, PR are welcomed.
        """

        # if self.parent is not None:
        #     d.update({"parent": self.parent.__getstate__()})
        # d.update({"dirs": [x.__getstate__() for x in self.dirs]})

        return {"_name": self.abs()}

    def __setstate__(self, state):
        """
        Unpickles an object.
        """
        self.__dict__.update(
            {"_name": state.get("_name"), "parent": None, "dirs": [], "files": {}}
        )

    def glob(self, pattern: str) -> List[str]:
        """
        Return a list of paths matching a pathname pattern, see <glob.glob>
        """
        from treefiles.commons import natural_sort

        return natural_sort(glob.glob(self.path(pattern)))

    @property
    def ls(self):
        """
        Returns a sorted list of the folder contents
        """
        from treefiles.commons import listdir

        return listdir(self)

    @property
    def basename(self):
        return os.path.basename(self.abs())

    def to_dict(self) -> dict:
        return dict(
            name=self._name,
            dirs=[x.to_dict() for x in self.dirs],
            ndirs={al: x.to_dict() for al, x in self.ndirs.items()},
            files={al: x for al, x in self.files.items()},
        )

    @classmethod
    def from_dict(cls, d: dict, parent: T = None):
        c = cls(d["name"])
        c.parent = parent
        c.files = d.get("files", [])
        c.dirs = [cls.from_dict(x, c) for x in d.get("dirs", [])]
        c.ndirs = {al: cls.from_dict(x, c) for al, x in d.get("ndirs", {}).items()}
        return c


def jTree(*args) -> T:
    from treefiles.commons import join

    return Tree(join(*args))


def fTree(file: str, *args: str, dump: bool = False, clean: bool = False) -> T:
    return Tree.new(file, *args, dump=dump, clean=clean)


# class FTree(Tree):
#     # def __init__(self, file: str, *args: str):
#     #     super().new(file, *args, dump=False)
#
#     def __new__(cls, file: str, *args: str) -> T:
#         ins = super().__new__(cls)
#         file = os.path.dirname(os.path.abspath(file))
#         ins.__init__(os.path.join(file, *args))
#         return ins


# if __name__ == "__main__":
#     aa = FTree(__file__, "dd", "test.py")
#     print(type(aa))
#     print(aa.root)
