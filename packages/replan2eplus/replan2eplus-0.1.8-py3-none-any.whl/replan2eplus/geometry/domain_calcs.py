from replan2eplus.geometry.contact_points import CardinalPoints, CornerPoints
from replan2eplus.geometry.coords import Coord
from dataclasses import dataclass
from replan2eplus.geometry.range import Range


# @dataclass(frozen=True)
@dataclass(frozen=True)
class BaseDomain:
    horz_range: Range
    vert_range: Range

def get_domain_shortcuts(domain: BaseDomain):
    n = domain.vert_range.max
    s = domain.vert_range.min
    e = domain.horz_range.max
    w = domain.horz_range.min
    return n, s, e, w


def calculate_corner_points(domain: BaseDomain) -> CornerPoints:
    n, s, e, w = get_domain_shortcuts(domain)
    return CornerPoints(
        NORTH_EAST=Coord(e, n),
        SOUTH_EAST=Coord(e, s),
        SOUTH_WEST=Coord(w, s),
        NORTH_WEST=Coord(w, n),
    )


def calculate_cardinal_points(domain: BaseDomain) -> CardinalPoints:
    n, s, e, w = get_domain_shortcuts(domain)
    mid_x = domain.horz_range.midpoint
    mid_y = domain.vert_range.midpoint
    return CardinalPoints(
        NORTH=Coord(mid_x, n),
        EAST=Coord(e, mid_y),
        SOUTH=Coord(mid_x, s),
        WEST=Coord(w, mid_y),
    )
