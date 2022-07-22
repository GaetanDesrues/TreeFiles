from typing import Callable

from treelib import Tree

from treefiles.commons import get_string


def get_extra(obj):
    return f" ({type(obj)})"


def get_extra_2(obj):
    exclude = {"Munch", "dict"}
    k = type(obj).__name__
    if k not in exclude:
        return f": {k}"
    return ""


def print_keys(dic, with_extra: bool = False, callback: Callable = get_extra):
    """
    Pretty print the keys of a nested dictionnary (not sorted)
    dico = {"key1": {"SubKey1": 1234, "SubKey3": [1, 2, 3]}, "Key2": None}
    tf.print_keys(dico)
            dict.keys
            ├── Key2
            └── key1
                ├── SubKey1
                └── SubKey3

    'with_extra' can help to display types:
    from treefiles.dictkeys import get_extra_2
    tf.print_keys(dico, with_extra=True, callback=get_extra_2)
            dict.keys
            ├── Key2: NoneType
            └── key1
                ├── SubKey1: int
                └── SubKey3: list
    """
    tree = Tree()
    tree.create_node("dict.keys", "root")

    def walk_dict(d, anchor="root"):
        for k, v in d.items():
            anc = get_string()
            extra = callback(v) if with_extra else ""
            tree.create_node(f"{k}{extra}", anc, parent=anchor)
            if isinstance(v, dict):
                walk_dict(v, anchor=anc)

    walk_dict(dic)
    tree.show()
