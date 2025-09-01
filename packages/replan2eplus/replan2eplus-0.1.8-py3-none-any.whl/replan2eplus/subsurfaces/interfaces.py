from dataclasses import dataclass
from typing import NamedTuple, Literal, TypeVar
from replan2eplus.ezobjects.subsurface import Subsurface
from replan2eplus.ezobjects.subsurface import Edge
from replan2eplus.ezobjects.zone import Zone
from replan2eplus.geometry.contact_points import CornerEntries
from replan2eplus.geometry.directions import WallNormal
from replan2eplus.geometry.domain_create import Dimension
from replan2eplus.geometry.nonant import NonantEntries



# NOTE: these are given in room names!
class ZoneDirectionEdge(NamedTuple):
    space_a: str
    space_b: WallNormal


class ZoneEdge(NamedTuple):
    space_a: str
    space_b: str


class Location(NamedTuple):
    nonant_loc: NonantEntries
    nonant_contact_loc: CornerEntries
    subsurface_contact_loc: CornerEntries


class Details(NamedTuple):
    # edge: Edge
    dimension: Dimension
    location: Location
    type_: Literal["Door", "Window"]


T = TypeVar("T")


# TODO move to utils4plans
def flatten_dict_map(dict_map: dict[int, list[int]]) -> list[tuple[int, int]]:
    res = []
    for k, v in dict_map.items():
        res.extend([(k, input) for input in v])
    return res


class IndexPair(NamedTuple):
    detail_ix: int
    edge_ix: int


@dataclass
class SubsurfaceInputs:
    edges: dict[int, Edge]
    details: dict[int, Details]
    map_: dict[int, list[int]]  # TODO -> is there a better way to do this?

    @property
    def _index_pairs(self):
        flattened_map = flatten_dict_map(self.map_)
        return (IndexPair(*i) for i in flattened_map)

    @property
    def _zone_edges(self):
        return {
            k: ZoneEdge(*v) for k, v in self.edges.items() if not v.is_directed_edge
        }

    @property
    def _zone_drn_edges(self):
        return {
            k: ZoneDirectionEdge(*v.sorted_directed_edge)
            for k, v in self.edges.items()
            if v.is_directed_edge
        }

    def _replace_indices(self, edge_dict: dict[int, T]):
        return [
            (edge_dict[i.edge_ix], self.details[i.detail_ix])
            for i in self._index_pairs
            if i.edge_ix in edge_dict.keys()
        ]

    @property
    def zone_pairs(self):
        return self._replace_indices(self._zone_edges)

    @property
    def zone_drn_pairs(self):
        return self._replace_indices(self._zone_drn_edges)
