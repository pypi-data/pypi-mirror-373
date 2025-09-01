from dataclasses import dataclass
from eppy.bunch_subclass import EpBunch
from replan2eplus.airboundary.interfaces import AirboundaryConstructionObject
from replan2eplus.constructions.interfaces import ConstructionsObject
import replan2eplus.epnames.keys as epkeys
from geomeppy import IDF as geomeppyIDF
from pathlib import Path
from eppy.modeleditor import IDDAlreadySetError

from replan2eplus.errors import IDFMisunderstandingError
from replan2eplus.ezobjects.subsurface import Subsurface
from replan2eplus.ezobjects.surface import Surface
from replan2eplus.idfobjects.subsurface import SubsurfaceKey, SubsurfaceObject
from replan2eplus.idfobjects.zone import GeomeppyBlock
from replan2eplus.idfobjects.afn import (
    AFNKeys,
    AFNSimulationControl,
    AFNZone,
    AFNSurface,
    AFNSimpleOpening,
)
from utils4plans.lists import chain_flatten

from replan2eplus.materials.interfaces import (
    MaterialKey,
    material_keys,
    MaterialObjectBase,
)

from ladybug.analysisperiod import AnalysisPeriod
from ladybug.epw import EPW
from replan2eplus.paths import WEATHER_FILE

# TODO --> move stuff in idfobjects into the interfaces files of their folder!

SAMPLE_EPW = EPW(WEATHER_FILE)


def update_idf_location(idf: geomeppyIDF, epw: EPW = SAMPLE_EPW):
    loc = idf.newidfobject("SITE:LOCATION")
    loc.Name = epw.location.city
    loc.Latitude = epw.location.latitude
    loc.Longitude = epw.location.longitude
    loc.Time_Zone = epw.location.time_zone
    loc.Elevation = epw.location.elevation
    return idf


def update_idf_run_period(
    idf: geomeppyIDF,
    ap: AnalysisPeriod = AnalysisPeriod(
        st_month=7, st_day=1, end_month=7, end_day=1, timestep=4
    ),
):
    rp = idf.newidfobject("RUNPERIOD")
    rp.Name = "Summer"
    rp.Begin_Month = ap.st_month
    rp.End_Month = ap.end_month
    rp.Begin_Day_of_Month = ap.st_day
    rp.End_Day_of_Month = ap.end_day
    return idf


@dataclass
class IDF:
    path_to_idd: Path
    path_to_idf: Path

    def __post_init__(self):
        try:
            geomeppyIDF.setiddname(self.path_to_idd)
        except IDDAlreadySetError:
            pass  # TODO log IDD already set, especially if the one they try to set is different..

        self.idf = geomeppyIDF(idfname=self.path_to_idf)
        self.idf = update_idf_location(self.idf)
        self.idf = update_idf_run_period(self.idf)
        self.idf.epw = WEATHER_FILE

    def print_idf(self):
        self.idf.printidf()  # TOOD make sure works?

    def view_idf_3d(self):
        self.idf.view_model()

    # TODO this is a property, unless adding filters later..
    def get_zones(self) -> list[EpBunch]:
        return [
            i for i in self.idf.idfobjects[epkeys.ZONE]
        ]  # TODO could put EzBunch on top here.. => maybe if things get out of hand..

    def get_surfaces(self) -> list[EpBunch]:
        return [i for i in self.idf.idfobjects[epkeys.SURFACE]]

    def get_subsurfaces(self) -> list[EpBunch]:
        return self.idf.getsubsurfaces()

    def get_materials(self) -> list[EpBunch]:
        materials = []
        for key in material_keys:
            materials.extend([self.idf.idfobjects[key]])

        return chain_flatten(materials)

    def get_constructions(self) -> list[EpBunch]:
        true_const: list[EpBunch] = self.idf.idfobjects[epkeys.CONSTRUCTION]
        airboundary_const: list[EpBunch] = self.idf.idfobjects[
            epkeys.AIRBOUNDARY_CONSTRUCTION
        ]
        return chain_flatten([true_const, airboundary_const])

    def get_afn_objects(self) -> list[EpBunch]:
        objects_ = []
        for key in AFNKeys:
            objects_.extend([self.idf.idfobjects[key]])
        return chain_flatten(objects_)

    ##################################################
    ########## ------ ADDING TO IDF ------ ##########
    ##################################################

    def add_geomeppy_block(self, block: GeomeppyBlock):
        self.idf.add_block(
            **block
        )  # TODO: think named tuple is just as good for this? good for consistency? not sure bc its a slightly different API

    def intersect_match(self):
        self.idf.intersect_match()

    def add_subsurface(self, key: SubsurfaceKey, subsurface_object: SubsurfaceObject):
        # TODO is this check needed / should it be hapening elsewhere? just to
        surface_names = [i.Name for i in self.get_surfaces()]
        assert subsurface_object.Building_Surface_Name in surface_names
        obj0 = self.idf.newidfobject(key.upper(), **subsurface_object._asdict())

        return obj0

    def add_afn_simulation_control(self, object_: AFNSimulationControl):
        obj0 = self.idf.newidfobject(AFNKeys.SIM_CONTROL, **object_._asdict())
        return obj0

    def add_afn_zone(self, object_: AFNZone):
        obj0 = self.idf.newidfobject(AFNKeys.ZONE, **object_._asdict())
        return obj0

    def add_afn_opening(self, object_: AFNSimpleOpening):
        obj0 = self.idf.newidfobject(AFNKeys.OPENING, **object_._asdict())
        return obj0

    def add_afn_surface(self, object_: AFNSurface):
        obj0 = self.idf.newidfobject(
            AFNKeys.SURFACE, **object_._asdict()
        )  # TODO some repetition here, could pull out
        return obj0

    def add_material(self, key: MaterialKey, object_: MaterialObjectBase):
        obj0 = self.idf.newidfobject(key, **object_.__dict__)
        return (
            obj0,
            key,
            object_,
        )  # NOTE: this is special!

    def add_construction(self, object_: ConstructionsObject):
        obj0 = self.idf.newidfobject(epkeys.CONSTRUCTION, **object_.valid_dict)
        return obj0

    def add_airboundary_construction(self, object_: AirboundaryConstructionObject):
        obj0 = self.idf.newidfobject(
            epkeys.AIRBOUNDARY_CONSTRUCTION, **object_.__dict__
        )
        return obj0

    def update_construction(
        self, surface_or_subsurface: Surface | Subsurface, construction_name: str
    ):
        const_names = [i.Name for i in self.get_constructions()]
        try:
            assert construction_name in const_names
        except AssertionError:
            raise IDFMisunderstandingError(
                f"`{construction_name}` has not been added to this IDF. The constructions exosting are: {const_names}"
            )
        surface_or_subsurface._epbunch.Construction_Name = construction_name
