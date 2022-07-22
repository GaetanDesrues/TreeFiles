from treelib import Tree

from treefiles.commons import get_string


def print_keys(dic):
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
