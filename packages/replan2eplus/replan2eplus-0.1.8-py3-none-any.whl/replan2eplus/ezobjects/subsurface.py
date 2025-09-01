from typing import NamedTuple, get_args
from replan2eplus.ezobjects.base import EZObject
from dataclasses import dataclass
import replan2eplus.epnames.keys as epkeys
from replan2eplus.ezobjects.epbunch_utils import get_epbunch_key
from replan2eplus.ezobjects.zone import Zone
from replan2eplus.geometry.directions import WallNormal, WallNormalNamesList
from replan2eplus.geometry.domain import Domain
from eppy.bunch_subclass import EpBunch
from typing import Literal

from replan2eplus.geometry.range import Range
from replan2eplus.ezobjects.surface import Surface

subsurface_options = [
    "DOOR",
    "WINDOW",
    "DOOR:INTERZONE",
]  # TODO arg thing since now have literal..

display_map = {"DOOR": "Door", "WINDOW": "Window", "DOOR:INTERZONE": "Door"}


class Edge(NamedTuple):
    space_a: str
    space_b: str

    @property
    def is_directed_edge(self):
        return (
            self.space_a in WallNormalNamesList or self.space_b in WallNormalNamesList
        )

    @property
    def as_tuple(self):
        return (self.space_a, self.space_b)

    @property
    def sorted_directed_edge(self):
        if self.is_directed_edge:
            zone, drn = sorted(
                [self.space_a, self.space_b], key=lambda x: x in WallNormalNamesList
            )  # NOTE: order is (false=0, true=1)
            return (zone, WallNormal[drn])
        else:
            raise Exception("This is not a directed edge!")
        # need the surface its on..

    # TODO properties to add: surface, partner obj, connecting zones, "driving zones" (for the purpose of the AFN )


SubsurfaceOptions = Literal["DOOR", "WINDOW", "DOOR:INTERZONE"]


@dataclass
class Subsurface(EZObject):
    _epbunch: EpBunch
    expected_key: SubsurfaceOptions
    surface: Surface
    edge: Edge

    @classmethod
    def from_epbunch_and_key(
        cls,
        _epbunch: EpBunch,
        zones: list[Zone],
        surfaces: list[Surface],
    ):
        # NOTE: this is being created based on reading an IDF
        # TODO clean up!
        expected_key = get_epbunch_key(_epbunch)

        surface_name = _epbunch.Building_Surface_Name

        surface = [i for i in surfaces if i.surface_name == surface_name][0]
        zone = [i for i in zones if i.zone_name == surface.zone_name][0]
        if surface.boundary_condition == "outdoors":
            edge = Edge(zone.zone_name, surface.direction.name)
        else:
            nb_surface = [i for i in surfaces if i.surface_name == surface.neighbor][0]
            nb_zone = [i for i in zones if i.zone_name == nb_surface.zone_name][0]
            edge = Edge(zone.zone_name, nb_zone.zone_name)

        return cls(_epbunch, expected_key, surface, edge)  # type: ignore #TODO => get epbunch for subsurface..

    def __post_init__(self):
        assert self.expected_key in get_args(SubsurfaceOptions)

    # def set_edge(self, edge: tuple[str, str]):
    #     self.edge = edge

    def __eq__(self, other):
        if isinstance(other, Subsurface):
            if other.edge == self.edge:
                return True
            # later could include domain.. if have two subsurfaces on one location..
        return False

    @property
    def subsurface_name(self):
        return self._epbunch.Name

    @property
    def display_name(self):
        type_ = display_map[self.expected_key]
        return f"{type_}_{self.surface.display_name}"

    @property
    def is_door(self):
        return "DOOR" in self.expected_key

    @property
    def is_window(self):
        return "WINDOW" in self.expected_key

    @property
    def domain(self):
        surf_domain = self.surface.domain
        surface_min_horz = surf_domain.horz_range.min
        surface_min_vert = surf_domain.vert_range.min

        horz_min = surface_min_horz + float(self._epbunch.Starting_X_Coordinate)
        width = float(self._epbunch.Length)

        vert_min = surface_min_vert + float(self._epbunch.Starting_Z_Coordinate)
        height = float(self._epbunch.Height)

        horz_range = Range(horz_min, horz_min + width)
        vert_range = Range(vert_min, vert_min + height)

        return Domain(horz_range, vert_range, surf_domain.plane)
