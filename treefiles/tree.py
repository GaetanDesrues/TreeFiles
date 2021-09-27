import glob
import os
import shutil
from typing import TypeVar, List, Union, Optional, Callable

from treefiles.tree_format import parse_lines, set_parents, get_lines

T = TypeVar("T", bound="Tree")
S = TypeVar("S", bound="Str")
TS = Union[S, T, str]


class Tree:
    """
    Creates a tree instance

    :param name: root of the current tree
    :param parent: parent tree if current tree is not the main root
    """

    def __init__(self, name: TS = None, parent: T = None):
        if name is not None:
            if isinstance(name, Tree):
                name = name.abs()
        else:
            name = "root"
        self.parent = parent
        self._name = Str(name)
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

    def abs(self, path="") -> S:
        """
        Returns the absolute path of a tree root

        :param path: recursion parameter
        """
        if self.parent is None:
            return Str(os.path.abspath(self._name))
        return Str(os.path.join(self.parent.abs(path), self._name))

    @property
    def root(self) -> S:
        return self._name

    @root.setter
    def root(self, x: TS):
        if isinstance(x, Tree):
            x = x.abs()
        self._name = Str(x)

    @property
    def p(self) -> T:
        """
        Returns the parent directory (path only)
        """
        dirs = self.abs().split(os.sep)
        return type(self)(os.sep.join(dirs[:-1]))

    def copy(self, root=None, parent=None):
        c = type(self)(self.root if root is None else root)
        c.dirs = [x.copy(parent=c) for x in self.dirs]
        c.ndirs = {k: x.copy(parent=c) for k, x in self.ndirs.items()}
        c.files = dict(self.files)
        c.parent = parent
        return c

    def __getattr__(self, att) -> Optional[TS]:
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
            return Str(os.path.join(self.abs(), self.files[att]))
        for d in self.dirs:
            if d.root == att:
                return d
        for d in self.dirs:
            found = getattr(d, att)
            if found is not None:
                return found
        for alias, d in self.ndirs.items():
            if alias == att:
                return d
        for d in self.ndirs.values():
            found = getattr(d, att)
            if found is not None:
                return found
        if self.parent is None:
            raise AttributeError(f"Attribute {att!r} not found in {self._name}")

    def __repr__(self, i=2):
        """
        Pretty prints th current tree

        :param i: recursion parameter
        """
        s = f"{self._name}"
        if i == 2 and self.abs() != self._name:
            s += f" ({self.abs()})"
        s += "\n"
        for al, f in self.files.items():
            kk = ""
            if al != os.path.splitext(f)[0]:
                kk = f" [{al}]"
            s += f"{' '*i}\u2514{kk} {f}\n"
        for d in self.dirs:
            s += f"{' '*i}\u2514 {d.__repr__(i+2)}\n"
        for al, d in self.ndirs.items():
            s += f"{' '*i}\u2514 [{al}] {d.__repr__(i+2)}\n"
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
        if len(names) > 0:
            return self.dirs[-1]
        if len(named_dirs) > 0:
            return self.ndirs[list(named_dirs.keys())[-1]]

    def jdir(self, path: str, sep: str = "/") -> T:
        """
        Create directory by joining path on sep

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

    def file(self, *args: str, **kwargs: str) -> T:
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
        return self

    def path(self, *args: str) -> S:
        """
        Creates a path starting from parent

        :param args: paths to join
        :return: the joined absolute path
        """
        return Str(os.path.join(self.abs(), *args))

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

    def glob(self, pattern: str) -> List[S]:
        """
        Return a list of paths matching a pathname pattern, see <glob.glob>
        """
        from treefiles.commons import natural_sort

        return [Str(x) for x in natural_sort(glob.glob(self.path(pattern)))]

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

    @classmethod
    def from_str(cls, lines: Union[str, List[str]], fname: str = None, **envs):
        for k, v in envs.items():
            os.environ[k] = str(v)

        if isinstance(lines, str):
            lines = lines.split("\n")

        l = parse_lines(lines)
        set_parents(l)

        # If root absolute path is different from the given root,
        # the dirname is considered parent
        c0 = cls(l[0].value)
        if c0.abs() != l[0].value:
            dn = os.path.dirname(fname) if fname else ""
            c0.root = os.path.join(dn, l[0].value)

        objs = [c0]
        for x in l[1:]:
            parent = objs[x.parent_line]
            parent = x.callback(parent)
            objs.append(parent)

        return objs[0]

    @classmethod
    def from_file(cls, *args: S, ensure_ext: bool = True, **envs):
        lines, fname = get_lines(*args, ensure_ext=ensure_ext)
        return cls.from_str(lines, fname=fname, **envs)

    def to_file(self, *args: S, comment=None, ensure_ext: bool = True):
        fname = args[0]
        if fname.endswith(".py"):
            fname = os.path.join(os.path.dirname(os.path.abspath(fname)), *args[1:])

        if ensure_ext:
            from treefiles import ensure_ext as ee

            fname = ee(fname, "tree")

        with open(fname, "w") as f:
            f.write(self.pprint(comment=comment))

    def pprint(self, comment=None, i=2):
        """
        Export the current tree to file with the `tree` format

        :param comment: File header
        :param i: recursion parameter
        """
        s = ""
        if i == 2:
            # s += f"# File generated by the treefiles package, see https://github.com/GaetanDesrues/TreeFiles\n"
            if comment:
                for x in comment.split("\n"):
                    s += f"# {x}\n"
            s += ". "
        s += f"{self.root}\n"
        for d in self.dirs:
            s += f"{' '*i}. {d.pprint(i=i+2)}\n"
        for al, d in self.ndirs.items():
            s += f"{' '*i}. {al}: {d.pprint(i=i+2)}\n"
        for al, f in self.files.items():
            s += f"{' '*i}- {al}: {f}\n"
        return s.strip()

    def get_files(self) -> List[str]:
        all_files = []
        for x in self.files.values():
            all_files.append(self.path(x))
        for x in self.dirs:
            all_files.extend(x.get_files())
        for x in self.ndirs.values():
            all_files.extend(x.get_files())
        return all_files


def jTree(*args) -> T:
    from treefiles.commons import join

    return Tree(join(*args))


def fTree(file: str, *args: str, dump: bool = False, clean: bool = False) -> T:
    return Tree.new(file, *args, dump=dump, clean=clean)


class Str(str):
    def __new__(cls, value):
        obj = str.__new__(cls, value)
        return obj

    def f(self, *a, **k) -> S:
        return Str(self.format(*a, **k))

    @property
    def parent(self) -> T:
        return Tree(os.path.dirname(os.path.abspath(self)))

    @property
    def sibling(self) -> Callable:
        return self.parent.path
