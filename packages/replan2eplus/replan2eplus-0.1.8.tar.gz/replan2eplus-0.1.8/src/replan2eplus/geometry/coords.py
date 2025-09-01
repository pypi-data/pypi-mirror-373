from matplotlib.text import Text
from replan2eplus.geometry.directions import WallNormalLiteral


from dataclasses import dataclass


# TODO organize classes -> dunder methods, then class methods, then properties, then other things..

from dataclasses import fields


def dataclass_as_dict(dataclass):
    return {field.name: getattr(dataclass, field.name) for field in fields(dataclass)}


@dataclass(frozen=True)
class Coord:
    x: float
    y: float

    def __getitem__(self, i):
        return (self.x, self.y)[i]

    @property
    def as_tuple(self):
        return (self.x, self.y)


@dataclass(frozen=True)
class Coordinate3D(Coord):
    z: float

    def get_pair(self, l1, l2):
        return Coord(self.__dict__[l1], self.__dict__[l2])

    def get_plane_axis_location(self, axis: str):
        # TODO check that all coords return the same value..
        return self.__dict__[axis]

    @property
    def as_three_tuple(self):
        return (self.x, self.y, self.z)
