import os
import shutil


class Tree:
    """
    Creates a tree instance

    :param name: root of the current tree
    :param parent: parent tree if current tree is not the main root
    """

    def __init__(self, name=None, parent=None):
        if name is not None:
            if isinstance(name, Tree):
                name = name.abs()
        else:
            name = "root"
        self.parent = parent
        self._name = name
        self.dirs = []
        self.files = dict()

    @classmethod
    def new(cls, file, *args):
        file = os.path.dirname(os.path.abspath(file))
        return cls(os.path.join(file, *args)).dump()

    def abs(self, path=""):
        """
        Returns the absolute path of a tree root

        :param path: recursion parameter
        """
        if self.parent is None:
            return os.path.abspath(self._name)
        return os.path.join(self.parent.abs(path), self._name)

    @property
    def root(self):
        return self._name

    @root.setter
    def root(self, x):
        if isinstance(x, Tree):
            self._name = x.abs()
        else:
            self._name = x

    def __getattr__(self, att):
        """
        Find an attribute

        :param att: the attribute name

        The order of preferences is:
            - look for files at current level
            - look for child at current level
            - look in children levels recursively
        """
        if att in self.files:
            return os.path.join(self.abs(), self.files[att])
        for d in self.dirs:
            if d._name == att:
                return d
        for d in self.dirs:
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
        s = f"{self._name}\n"
        for d in self.dirs:
            s += f"{' '*i}\u2514 {d.__repr__(i+2)}\n"
        for f in self.files.values():
            s += f"{' '*i}\u2514 {f}\n"
        return s.rstrip()

    def dir(self, *names):
        """
        Adds directories to the current level

        :param names: folder names
        :return: instance of the last child created
        """
        for name in names:
            self.dirs.append(type(self)(name, parent=self))
        return self.dirs[-1]

    def file(self, *args, **kwargs):
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

    def path(self, *args) -> str:
        """
        Creates a path starting from parent

        :param args: paths to join
        :return: the joined absolute path
        """
        return os.path.join(self.abs(), *args)

    def dump(self, clean=False):
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
