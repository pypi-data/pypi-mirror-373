from dataclasses import dataclass
from pathlib import Path

from replan2eplus.afn.presentation import create_afn_objects
from replan2eplus.airboundary.presentation import update_airboundary_constructions

# from replan2eplus.constructions import update_surfaces_with_construction_set
from replan2eplus.constructions.presentation import (
    add_constructions_from_other_idf,
)
from replan2eplus.ezobjects.afn import AirflowNetwork
from replan2eplus.ezobjects.airboundary import Airboundary, get_unique_airboundaries
from replan2eplus.ezobjects.construction import Construction, EPConstructionSet
from replan2eplus.ezobjects.material import Material
from replan2eplus.ezobjects.subsurface import Subsurface, Edge
from replan2eplus.ezobjects.surface import Surface
from replan2eplus.ezobjects.zone import Zone
from replan2eplus.idfobjects.idf import IDF
from replan2eplus.subsurfaces.interfaces import SubsurfaceInputs
from replan2eplus.subsurfaces.presentation import create_subsurfaces
from replan2eplus.zones.interfaces import Room
from replan2eplus.zones.presentation import create_zones
from replan2eplus.subsurfaces.utils import get_unique_subsurfaces

# TODO: need to be aware that these might be called out of order, so do rigorous checks!  -> can use decorators for this maybe?


@dataclass
class EZCase:
    path_to_idd: Path # TODO Sshould check that is v22.2 or at least that both match.. 
    path_to_initial_idf: Path

    # TODO: do these need to be initialized here?
    # path_to_weather: Path p
    # path_to_analysis_period: AnalysisPeriod
    def __post_init__(self):
        self.idf: IDF
        self.construction_set: EPConstructionSet

        self.zones: list[Zone] = []
        self.surfaces: list[Surface] = []
        self.airboundaries: list[Airboundary] = []
        self.subsurfaces: list[Subsurface] = []

        # -> may call add materials / constructions several times..
        self.materials: list[Material] = []
        self.constructions: list[Construction] = []

        self.airflownetwork = AirflowNetwork([], [], [])

    @property
    def unique_subsurfaces(self):
        return get_unique_subsurfaces(self.subsurfaces)

    @property
    def unique_airboundaries(self):
        return get_unique_airboundaries(self.airboundaries)

    def initialize_idf(self):
        self.idf = IDF(self.path_to_idd, self.path_to_initial_idf)
        return self.idf

    def add_zones(self, rooms: list[Room]):
        # TODO - check that idf exists!
        self.zones, self.surfaces = create_zones(self.idf, rooms)
        # when do constructuins, these surfaces will be updated..
        return self

    def add_airboundaries(self, edges: list[Edge]):
        # check that surfaces exist..
        self.airboundaries = update_airboundary_constructions(
            self.idf, edges, self.zones
        )
        return self

    def add_subsurfaces(self, inputs: SubsurfaceInputs):
        """
        edges: dict[int, Edge] -> u: name in the room plan, v: name in the room plan OR capitalized cardnal direction
        details: dict[int, Details]
        map_: dict[int, list[int]]

        """
        # TODO: check that zones exist
        self.subsurfaces = create_subsurfaces(
            inputs, self.zones, self.idf
        )  # TODO change so IDF comes first!
        return self

    # TODO: option to add constructions manually!

    def add_constructions_from_other_idf(
        self,
        paths_to_construction_idfs: list[Path],
        paths_to_material_idfs: list[Path],
        construction_set: EPConstructionSet,
    ):
        self.construction_set = construction_set

        new_materials, new_constructions = add_constructions_from_other_idf(
            self.idf,
            paths_to_construction_idfs,
            paths_to_material_idfs,
            self.path_to_idd,
            self.construction_set,
            self.surfaces,
            self.subsurfaces,
        )
        self.constructions.extend(new_constructions)
        self.materials.extend(new_materials)
        return self

    def add_airflownetwork(self):
        # TODO -> make an EZObject for AFN? Will be helpful for graphing..
        self.airflownetwork = create_afn_objects(
            self.idf, self.zones, self.subsurfaces, self.airboundaries, self.surfaces
        )
        return self

    def add_output_variables(self):
        return self  # use Munch!

    def save_and_run_case(self):
        return self  # compare to see if idf has changed or not -> interactive -> do you want to overwrite existing reults..
