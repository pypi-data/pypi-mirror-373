from dataclasses import dataclass
from replan2eplus.geometry.coords import Coord

from typing import Literal, NamedTuple

from replan2eplus.geometry.nonant import NonantEntries


CardinalEntries = Literal["NORTH", "EAST", "SOUTH", "WEST"]


@dataclass
class CardinalPoints:
    NORTH: Coord
    EAST: Coord
    SOUTH: Coord
    WEST: Coord

    def __getitem__(self, item: CardinalEntries) -> Coord:
        return getattr(self, item)

    @property
    def dict_(self):
        return {
            "NORTH": self.NORTH,
            "EAST": self.EAST,
            "SOUTH": self.SOUTH,
            "WEST": self.WEST,
        }


CornerEntries = Literal["NORTH_EAST", "SOUTH_EAST", "SOUTH_WEST", "NORTH_WEST"]


@dataclass
class CornerPoints:
    NORTH_EAST: Coord
    SOUTH_EAST: Coord
    SOUTH_WEST: Coord
    NORTH_WEST: Coord

    def __getitem__(self, item: CornerEntries) -> Coord:
        return getattr(self, item)

    @property
    def coord_list(self):
        # this is clock wise not counter clockwise
        # return [self.NORTH_EAST, self.SOUTH_EAST, self.SOUTH_WEST, self.NORTH_WEST]
        return [self.NORTH_EAST, self.NORTH_WEST, self.SOUTH_WEST, self.SOUTH_EAST]

    @property
    def tuple_list(self):
        return [i.as_tuple for i in self.coord_list]
