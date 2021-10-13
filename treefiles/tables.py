import logging

import treefiles as tf


class Table:
    def __init__(
        self,
        header=None,
        rows=None,
        orient: str = "r",
        head_sep: [None, str] = "-",
        col_pad: str = " ",
        col_sep: str = " ",
    ):
        self.header = header
        self.rows = [] if rows is None else list(rows)
        self.col_sep = col_sep
        self.col_pad = col_pad
        self.head_sep = head_sep
        self.orient = ORIENT[orient]

    def add_row(self, *row):
        self.rows.append(row)

    def replace_none(self, s=""):
        g = lambda x: tf.none(x, s)
        self.rows = [list(map(g, x)) for x in self.rows]

    def _find_template(self):
        if self.header is not None:
            n_cols = len(self.header)
        elif len(self.rows) > 0:
            n_cols = len(self.rows[0])
            self.header = [f"Col {i}" for i in range(n_cols)]
        else:
            raise EmptyData

        self.header = list(map(str, self.header))
        self.rows = [list(map(str, x)) for x in self.rows]

        self.lens = [0] * n_cols
        self._rows = list(self.rows)
        self._rows.insert(0, self.header)
        for x in self._rows:
            for j, k in enumerate(x):
                self.lens[j] = max(self.lens[j], len(k))

        self._tformat = (
            self.col_sep.join(
                [
                    f"{self.col_pad}{{:{self.orient}{i}}}{self.col_pad}"
                    for i in self.lens
                ]
            )
            + "\n"
        )

    def __call__(self):
        self._find_template()

        if self.head_sep is not None:
            head_sep = [self.head_sep * i for i in self.lens]
            self._rows.insert(1, head_sep)

        s = ""
        for x in self._rows:
            s += self._tformat.format(*x)
        return s

    @classmethod
    def from_dict(cls, data, **kwargs):
        c = cls(header=data.keys(), **kwargs)
        n = len(next(iter(data.values())))
        for i in range(n):
            c.add_row(*[x[i] for x in data.values()])
        return c


ORIENT = dict(l="<", r=">", c="^")


class EmptyData(Exception):
    pass


log = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    log = tf.get_logger()

    t = Table()
    t.add_row(1, 2, 3)
    print(t())
