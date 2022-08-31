import re
from dataclasses import dataclass

from treefiles.tree import Str


@dataclass
class KStringResult:
    idx: int
    preffix: str
    match: str
    suffix: str

    def __truediv__(self, other) -> Str:
        return Str(self.preffix + self.match + self.suffix) / other


class K(Str):
    def __new__(cls, value, idx=None):
        obj = super().__new__(cls, value)
        if idx is not None:
            obj += f"_{idx}"
        return obj

    def re(self, pat):
        m = re.search(rf"(.+)?{pat}_(\d+)(.+)?", self)
        if m:
            a, b, c = m[1], type(self)(pat, m[2]), m[3]
            return KStringResult(m[2], a, b, c)


if __name__ == "__main__":
    ss = Str("aze/aze")
    i = 19
    s = K(ss / K("Patient", i) / "oui")
    print(s)

    aze = s.re("Patient")
    print(aze / f"non_{aze.idx}" / K("habon", aze.idx))
