from dataclasses import dataclass

from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

from replan2eplus.errors import IDFMisunderstandingError

from replan2eplus.ezobjects.subsurface import Edge

from replan2eplus.ezobjects.zone import Zone
from replan2eplus.ezobjects.zone import get_zones
from replan2eplus.geometry.contact_points import CardinalPoints
from replan2eplus.geometry.coords import Coord
from replan2eplus.geometry.directions import WallNormalNamesList
from replan2eplus.geometry.domain import (
    Domain,
    Plane,
)
from replan2eplus.geometry.range import Range
from typing import NamedTuple

EXPANSION_FACTOR = 1.3


class MPlData(NamedTuple):
    xdata: list[float]
    ydata: list[float]


def split_coords(coords: list[Coord]):
    return MPlData([i.x for i in coords], [i.y for i in coords])


@dataclass
class Line:
    # TODO feels like this logic should be in geometry folder
    start: Coord
    end: Coord
    plane: Plane

    @property
    def to_line2D(self):
        return Line2D(
            *split_coords([self.start, self.end])
        ) 

    @property
    def centroid(self):
        return (
            Range(self.start.x, self.end.x).midpoint,
            Range(self.start.y, self.end.y).midpoint,
        )


def domain_to_rectangle(domain: Domain):
    return Rectangle(
        (domain.horz_range.min, domain.vert_range.min),
        domain.horz_range.size,
        domain.vert_range.size,
        fill=False,
    )


# TODO write tests for this! and potentially move to geometry folder ..
def domain_to_line(domain: Domain):
    assert domain.plane
    plane = domain.plane
    if plane.axis == "Z":
        raise IDFMisunderstandingError("Can't flatten a domain in the Z Plane!")
    else:
        min_ = domain.horz_range.min
        max_ = domain.horz_range.max
    if plane.axis == "X":
        start = Coord(plane.location, min_)
        end = Coord(plane.location, max_)
    else:
        assert plane.axis == "Y"
        start = Coord(min_, plane.location)
        end = Coord(max_, plane.location)
    return Line(start, end, plane)


# this is a pretty generic fx -> utils4plans -> filter, get1 throw error
def subsurface_to_connection_line(
    domain: Domain,
    edge: Edge,
    zones: list[Zone],
    cardinal_coords: CardinalPoints,
):
    space_a, space_b = edge

    middle_coord = Coord(*domain_to_line(domain).centroid)

    zone_a = get_zones(space_a, zones)
    coord_a = zone_a.domain.centroid
    if space_b in WallNormalNamesList:
        coord_b = cardinal_coords.dict_[space_b]
    else:
        zone_b = get_zones(space_b, zones)
        coord_b = zone_b.domain.centroid

    points = [coord_a, middle_coord, coord_b]
    return Line2D(*split_coords(points))


# TODO this is kind of its own thing!
