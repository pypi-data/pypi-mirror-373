from dataclasses import dataclass
from typing import Literal

from replan2eplus.geometry.coords import Coord
from replan2eplus.geometry.range import TriRange


NonantEntries = Literal[
    # "horz_trirange",  # TODO not sure these should be here..
    # "vert_trirange",
    "bl",
    "ml",
    "tl",
    "bm",
    "mm",
    "tm",
    "br",
    "mr",
    "tr",
]


@dataclass
class Nonant:  # effectively a quadrant, but 9
    horz_trirange: TriRange
    vert_trirange: TriRange

    def __getitem__(self, item: NonantEntries):
        return getattr(self, item)

    # left
    @property
    def bl(self):
        return Coord(self.horz_trirange.min, self.vert_trirange.min)

    @property
    def ml(self):
        return Coord(self.horz_trirange.min, self.vert_trirange.mid1)

    @property
    def tl(self):
        return Coord(self.horz_trirange.min, self.vert_trirange.mid2)

    # middle
    @property
    def bm(self):
        return Coord(self.horz_trirange.mid1, self.vert_trirange.min)

    @property
    def mm(self):
        return Coord(self.horz_trirange.mid1, self.vert_trirange.mid1)

    @property
    def tm(self):
        return Coord(self.horz_trirange.mid1, self.vert_trirange.mid2)

    # right
    @property
    def br(self):
        return Coord(self.horz_trirange.mid2, self.vert_trirange.min)

    @property
    def mr(self):
        return Coord(self.horz_trirange.mid2, self.vert_trirange.mid1)

    @property
    def tr(self):
        return Coord(self.horz_trirange.mid2, self.vert_trirange.mid2)
