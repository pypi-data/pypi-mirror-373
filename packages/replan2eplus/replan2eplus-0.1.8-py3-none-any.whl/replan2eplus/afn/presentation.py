from replan2eplus.afn.interfaces import AFNInputs
from replan2eplus.ezobjects.airboundary import Airboundary, get_unique_airboundaries
from replan2eplus.ezobjects.subsurface import Subsurface
from replan2eplus.ezobjects.surface import Surface
from replan2eplus.ezobjects.zone import Zone
from replan2eplus.idfobjects.afn import (
    AFNKeys,
)
from replan2eplus.idfobjects.idf import IDF
from replan2eplus.ezobjects.epbunch_utils import chain_flatten
from replan2eplus.subsurfaces.utils import get_unique_subsurfaces
from replan2eplus.ezobjects.afn import AirflowNetwork


def get_afn_subsurfaces(afn_zones: list[Zone], subsurfaces: list[Subsurface]):
    potential_subsurface_names = chain_flatten([i.subsurface_names for i in afn_zones])
    potential_subsurfaces = [
        i for i in subsurfaces if i.subsurface_name in potential_subsurface_names
    ]  # TODO filter function would help clean this up..
    afn_subsurfaces = get_unique_subsurfaces(potential_subsurfaces)
    return afn_subsurfaces


def get_afn_airboundaries(afn_zones: list[Zone], airboundaries: list[Airboundary]):
    afn_zone_names = [i.zone_name for i in afn_zones]
    possible_airboundaries = [
        i for i in airboundaries if i.surface.zone_name in afn_zone_names
    ]
    afn_airboundaries = get_unique_airboundaries(possible_airboundaries)
    return afn_airboundaries


def determine_anti_objects(
    zones: list[Zone], surfaces: list[Surface], afn_zones: list[Zone]
):
    anti_zones = [i for i in zones if i not in afn_zones]

    anti_surfaces_l1 = chain_flatten([i.surfaces for i in anti_zones])
    anti_surfaces_l2: list[str] = [i.neighbor for i in anti_surfaces_l1 if i.neighbor]
    anti_surfaces = [i.surface_name for i in anti_surfaces_l1] + anti_surfaces_l2

    anti_subsurfaces_l1 = chain_flatten([i.subsurface_names for i in anti_zones])
    # need to get the surfaces in neighbors..
    nb_surfs = [i for i in surfaces if i.surface_name in anti_surfaces_l2]
    anti_subsurfaces_l2 = chain_flatten([i.subsurface_names for i in nb_surfs])
    anti_subsurfaces = anti_subsurfaces_l1 + anti_subsurfaces_l2
    return anti_surfaces, anti_subsurfaces


def select_afn_objects(
    zones: list[Zone],
    subsurfaces: list[Subsurface],
    airboundaries: list[Airboundary],
    surfaces: list[Surface],
):
    afn_zones = [
        i for i in zones if len(i.potential_afn_surface_or_subsurface_names) >= 2
    ]
    anti_surfaces, anti_subsurfaces = determine_anti_objects(zones, surfaces, afn_zones)

    afn_subsurfaces = [
        i
        for i in get_afn_subsurfaces(afn_zones, subsurfaces)
        if i.subsurface_name not in anti_subsurfaces
    ]

    afn_airboundaries = [
        i
        for i in get_afn_airboundaries(afn_zones, airboundaries)
        if i.surface.surface_name not in anti_surfaces
    ]

    return AFNInputs(afn_zones, afn_subsurfaces, afn_airboundaries)


# TODO -> this should be the only thing in presentation
def create_afn_objects(
    idf: IDF,
    zones: list[Zone],
    subsurfaces: list[Subsurface],
    airboundaries: list[Airboundary],
    surfaces: list[Surface],
):
    inputs = select_afn_objects(zones, subsurfaces, airboundaries, surfaces)
    idf.add_afn_simulation_control(inputs.sim_control)

    for zone in inputs.zones:
        idf.add_afn_zone(zone)
        idf.print_idf()

    for pair in zip(*inputs.surfaces_and_openings):
        afn_surface, afn_opening = pair
        idf.add_afn_surface(afn_surface)
        idf.add_afn_opening(afn_opening)
    idf.print_idf()

    return AirflowNetwork(inputs.zones_, inputs.subsurfaces, inputs.airboundaires)
