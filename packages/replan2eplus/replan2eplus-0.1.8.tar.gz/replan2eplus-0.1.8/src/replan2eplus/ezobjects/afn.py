from dataclasses import dataclass
from replan2eplus.ezobjects.airboundary import Airboundary
from replan2eplus.ezobjects.subsurface import Subsurface
from replan2eplus.ezobjects.surface import Surface
from replan2eplus.ezobjects.zone import Zone
from utils4plans.sets import set_difference, set_intersection


@dataclass
class AirflowNetwork:
    zones: list[Zone]
    subsurfaces: list[Subsurface]
    airboundaries: list[Airboundary]

    @property
    def surfacelike_objects(self):
        return self.subsurfaces + self.airboundaries


    def non_afn_airboundaries(self, airboundaries: list[Airboundary]):
        return [i for i in airboundaries if i not in self.airboundaries]

    def non_afn_subsurfaces(self, subsurfaces: list[Subsurface]):
        return [i for i in subsurfaces if i not in self.subsurfaces]
