from dataclasses import dataclass

from replan2eplus.ezobjects.surface import Surface
from replan2eplus.ezobjects.subsurface import Edge


@dataclass
class Airboundary:
    surface: Surface
    edge: Edge

    @property
    def domain(self):
        return self.surface.domain


def get_unique_airboundaries(airboundaries: list[Airboundary]):
    return [i for i in airboundaries if i.edge.space_a in i.surface.zone_name]
