import logging
import os
import re
from dataclasses import dataclass
from typing import List


@dataclass
class Line:
    indent: int
    comment: str = None
    name: str = None
    value: str = None
    entry_type: str = None
    parent_line: int = None

    def callback(self, parent):
        m = getattr(parent, self.entry_type)
        if self.name:
            return m(**{self.name: self.value})
        else:
            return m(self.value)

    def __repr__(self):
        s = f"[{self.name}]" if self.name else ""
        s = f"{s}{self.value}"
        return (
            f"{' '*self.indent}{self.entry_type}: {s} - parent line {self.parent_line}"
        )


def split_lin(x):
    name, value = None, None
    r = x.split(":")
    clean = lambda x: x.replace('"', "").replace("'", "").strip()

    if len(r) == 1:
        value = clean(r[0])
    elif len(r) == 2:
        name, value = clean(r[0]), clean(r[1])

    return name, value


def parse_lines(lines, dirname=None) -> List[Line]:
    _lines = []

    def is_in(*x):
        for i in x[:-1]:
            if i in x[-1]:
                return True
        return False

    for x in lines:
        y = Line(len(x) - len(x.lstrip()))
        x = x.strip()

        # skip comments
        if is_in("#", x):
            s = x.split("#")
            x = s[0]
            if len(s) > 1:
                y.comment = " ".join(s[1:]).strip()

        # Replace env variables
        while is_in("${", x):
            m = re.search(r"\${(\w+)}", x)
            d = f"{m.group(1)!r}NotFound"
            x = x[: m.span()[0]] + os.environ.get(m.group(1), d) + x[m.span()[1] :]

        # Read file or dir entry
        if is_in(".", "-", ":", "<", x):
            key, x = x[0], x[1:]
            if key == ".":
                y.entry_type = "dir"
                y.name, y.value = split_lin(x)
            elif key == "-":
                y.entry_type = "file"
                y.name, y.value = split_lin(x)
            elif key == "<":
                name, value = split_lin(x)
                import_lines, _ = get_lines(value, dirname=dirname)
                new_branch = parse_lines(import_lines)
                for x in new_branch:
                    x.indent += y.indent
                if name:
                    new_branch[0].value = name
                _lines.extend(new_branch)

        if y.entry_type:
            _lines.append(y)

    return _lines


def set_parents(lines):
    indents = [x.indent for x in lines]
    assert indents[0] == 0
    assert indents[1] > 0
    di = indents[1]

    for i, x in enumerate(lines):
        assert x.indent % di == 0
        k = 0
        for j, y in enumerate(lines[i::-1]):
            if x.indent == y.indent + di:
                k = i - j
                break
        x.parent_line = k


def get_lines(*args, ensure_ext: bool = True, dirname=None):
    fname = args[0]
    if fname.endswith(".py"):
        fname = os.path.join(os.path.dirname(os.path.abspath(fname)), *args[1:])

    if ensure_ext:
        from treefiles import ensure_ext as ee

        fname = ee(fname, "tree")

    if not os.path.isfile(fname) and dirname is not None:
        fname = os.path.join(dirname, fname)
        if not os.path.isfile(fname):
            log.error(f"File {fname} not found")

    with open(fname) as f:
        lines = f.readlines()

    return lines, fname


log = logging.getLogger(__name__)
