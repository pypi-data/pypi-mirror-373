from enum import IntEnum
from typing import Literal


class WallNormal(IntEnum):
    """
    [Direction of outward normal of a surface](https://eppy.readthedocs.io/en/latest/eppy.geometry.html#eppy.geometry.surface.azimuth)
    """

    NORTH = 0
    EAST = 90
    SOUTH = 180
    WEST = 270
    UP = 1
    DOWN = -1
    # TODO => if anything iterates over this it will throw an error

    def __getitem__(self, i):
        return getattr(self, i)

    @classmethod
    def keys(cls):
        return list(cls.__members__.keys())


WallNormalLiteral = Literal["NORTH", "EAST", "SOUTH", "WEST", "UP", "DOWN"]
WallNormalNamesList = ["NORTH", "EAST", "SOUTH", "WEST", "UP", "DOWN"]
