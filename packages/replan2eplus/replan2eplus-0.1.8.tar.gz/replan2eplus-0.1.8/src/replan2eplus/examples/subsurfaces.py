from replan2eplus.idfobjects.subsurface import SubsurfaceObject
from replan2eplus.subsurfaces.interfaces import (
    ZoneEdge,
    ZoneDirectionEdge,
    Details,
    Location,
    SubsurfaceInputs,
)
from replan2eplus.examples.minimal import get_minimal_case_with_rooms, test_rooms
from replan2eplus.geometry.directions import WallNormal
from replan2eplus.geometry.domain_create import Dimension
from dataclasses import dataclass
from replan2eplus.ezobjects.subsurface import Edge

FACTOR = 4

room1, room2 = test_rooms

val = 0.5
random_surface_name = "Block `room1` Storey 0 Wall 0003"
subsurface_object = SubsurfaceObject("Test", random_surface_name, val, val, val, val)


# TODO probably a good idea to put these in classes..?
zone_edge = ZoneEdge(room1.name, room2.name)
zone_drn_edge = ZoneDirectionEdge(room1.name, WallNormal.WEST)
zone_drn_edge_room2 = ZoneDirectionEdge(room2.name, WallNormal.EAST)

location = Location("mm", "SOUTH_WEST", "SOUTH_WEST")
location_bl = Location("bl", "SOUTH_WEST", "SOUTH_WEST")
dimension = Dimension(
    room1.domain.horz_range.size / FACTOR, room1.domain.vert_range.size / FACTOR
)
door_details = Details(dimension, location, "Door")
window_details = Details(dimension, location, "Window")
window_details_bl = Details(dimension, location_bl, "Window")


# testing actual implementation..


@dataclass
class TestInputs:
    edges: list[Edge]
    details: list[Details]
    map_: dict[int, list[int]]

    def to_dict(self, lst: list):
        return {ix: i for ix, i in enumerate(lst)}

    @property
    def inputs(self):
        return SubsurfaceInputs(
            self.to_dict(self.edges), self.to_dict(self.details), self.map_
        )


e0 = Edge(room1.name, room2.name)
e1 = Edge(room1.name, "WEST")
e2 = Edge(room1.name, "NORTH")
e3 = Edge(room2.name, "SOUTH")

simple_subsurface_inputs = TestInputs(
    [e0, e1],
    [door_details, window_details],
    {0: [0], 1: [1]},
)

airboundary_subsurface_inputs = TestInputs(
    [e1, e2], [door_details, window_details], {0: [0], 1: [1]}
)

three_details_subsurface_inputs = TestInputs(
    [e0, e1, e2, e3],
    [door_details, window_details, window_details_bl],
    {0: [0], 1: [1, 2], 2: [3]},
)


def get_minimal_case_with_subsurfaces():
    case = get_minimal_case_with_rooms()
    case.add_subsurfaces(simple_subsurface_inputs.inputs)
    return case
