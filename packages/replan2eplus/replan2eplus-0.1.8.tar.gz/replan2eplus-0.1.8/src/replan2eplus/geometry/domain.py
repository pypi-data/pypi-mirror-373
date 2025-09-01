from dataclasses import dataclass
from replan2eplus.geometry.coords import Coord
from replan2eplus.geometry.nonant import Nonant
from typing import Literal, NamedTuple
from replan2eplus.geometry.domain_calcs import (
    BaseDomain,
    calculate_cardinal_points,
    calculate_corner_points,
)
from replan2eplus.geometry.range import compute_multirange, expand_range


AXIS = Literal["X", "Y", "Z"]


class Plane(NamedTuple):
    axis: AXIS
    location: float


@dataclass(frozen=True)
class Domain(BaseDomain):
    plane: Plane | None = None

    # def __eq__(self, value: object) -> bool:
    #     return super().__eq__(value)

    @property
    def area(self):
        return self.horz_range.size * self.vert_range.size

    @property
    def aspect_ratio(self):
        return self.horz_range.size / self.vert_range.size

    @property
    def centroid(self):
        return Coord(self.horz_range.midpoint, self.vert_range.midpoint)

    @property
    def cardinal(self):
        return calculate_cardinal_points(self) 

    @property
    def corner(self):  
        return calculate_corner_points(self) 

    @property
    def nonant(self):
        return Nonant(self.horz_range.trirange, self.vert_range.trirange)

def expand_domain(domain: Domain, factor: float):
    horz_range = expand_range(domain.horz_range, factor)
    vert_range = expand_range(domain.vert_range, factor)
    return Domain(horz_range, vert_range)


def compute_multidomain(domains: list[Domain]):
    horz_range = compute_multirange([i.horz_range for i in domains])
    vert_range = compute_multirange([i.vert_range for i in domains])
    return Domain(horz_range, vert_range)


# TODO: This probably belong in the domain -> really just a helper for a test ..
def calculate_cardinal_domain(
    domains: list[Domain], cardinal_expansion_factor: float = 1.1
):
    total_domain = compute_multidomain(domains)

    cardinal_domain = expand_domain(total_domain, cardinal_expansion_factor)

    return cardinal_domain
