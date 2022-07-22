from treelib import Tree

from treefiles.commons import get_string


def print_keys(dic):
    """
    Pretty print the keys of a nested dictionnary (not sorted)
    dico = {"key1": {"SubKey1": 1234, "SubKey3": [1, 2, 3]}, "Key2": None}
    tf.print_keys(dico)
            dict.keys
            ├── Key2
            └── key1
                ├── SubKey1
                └── SubKey3
    """
    tree = Tree()
    tree.create_node("dict.keys", "root")

    def walk_dict(d, anchor="root"):
        for k, v in d.items():
            anc = get_string()
            tree.create_node(k, anc, parent=anchor)
            if isinstance(v, dict):
                walk_dict(v, anchor=anc)

    walk_dict(dic)
    tree.show()
