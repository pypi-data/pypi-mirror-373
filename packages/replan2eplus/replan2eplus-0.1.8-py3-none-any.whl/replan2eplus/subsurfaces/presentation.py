from replan2eplus.ezobjects.epbunch_utils import chain_flatten

from replan2eplus.errors import IDFMisunderstandingError
from replan2eplus.idfobjects.idf import IDF
from replan2eplus.ezobjects.subsurface import SubsurfaceOptions, Subsurface, Edge
from replan2eplus.ezobjects.zone import Zone
from replan2eplus.geometry.domain import Domain
from replan2eplus.geometry.domain_create import place_domain
from replan2eplus.idfobjects.subsurface import SubsurfaceKey, SubsurfaceObject
from replan2eplus.subsurfaces.interfaces import (
    Details,
    SubsurfaceInputs,
    ZoneDirectionEdge,
    ZoneEdge,
)
from replan2eplus.subsurfaces.logic import (
    get_surface_between_zone_and_direction,
    get_surface_between_zones,
)


# TODO this goes to logic! TODO number files in logic _04_indiv_subsurf
def prepare_object(surface_name: str, domain: Domain, detail: Details):
    def create_ss_name(surface_name: str):
        return f"{detail.type_}__{surface_name}"

    coords = domain.corner.SOUTH_WEST.as_tuple
    dims = detail.dimension.as_tuple

    return SubsurfaceObject(create_ss_name(surface_name), surface_name, *coords, *dims)


def create_subsurface_for_interior_edge(
    edge: ZoneEdge, detail: Details, zones: list[Zone], idf: IDF
) -> tuple[Subsurface, Subsurface]:
    key: SubsurfaceKey = (f"{detail.type_}:Interzone").upper()  # type: ignore #TODO verify!

    main_surface, nb_surface = get_surface_between_zones(edge, zones)
    if main_surface.is_airboundary or nb_surface.is_airboundary:
        main_name = f"Main: {main_surface.surface_name}"
        nb_name = f"Nb: {nb_surface.surface_name}"
        assert main_surface.is_airboundary and nb_surface.is_airboundary, (
            f"Matching surfaces should be airboundaries!!! \n {main_name}' constr: {main_surface.construction_name}\n {nb_name}' constr: {nb_surface.construction_name}"
        )
        raise IDFMisunderstandingError(
            f"{main_name} and {nb_name} are airboundaries! They cannot have surfaces placed on them! "
        )
    subsurf_domain = place_domain(
        main_surface.domain, *detail.location, detail.dimension
    )

    main_obj = idf.add_subsurface(
        key, prepare_object(main_surface.surface_name, subsurf_domain, detail)
    )
    nb_obj = idf.add_subsurface(
        key, prepare_object(nb_surface.surface_name, subsurf_domain, detail)
    )

    return Subsurface(main_obj, key, main_surface, Edge(*edge)), Subsurface(
        nb_obj, key, nb_surface, Edge(*edge)
    )


def create_subsurface_for_exterior_edge(
    edge: ZoneDirectionEdge, detail: Details, zones: list[Zone], idf: IDF
):
    key: SubsurfaceOptions = detail.type_.upper()  # type: ignore #TODO verify!

    surface = get_surface_between_zone_and_direction(edge, zones)
    subsurf_domain = place_domain(surface.domain, *detail.location, detail.dimension)
    obj = idf.add_subsurface(
        key, prepare_object(surface.surface_name, subsurf_domain, detail)
    )
    return Subsurface(obj, key, surface, Edge(edge.space_a, edge.space_b.name))


# TODO this should be dealing w/ different APIs..
def create_subsurfaces(
    inputs: SubsurfaceInputs,
    zones: list[Zone],
    idf: IDF,
):
    # TODO fix chain_flatten in utils4plans to use typevar
    interior_subsurfaces: list[Subsurface] = chain_flatten(
        [
            create_subsurface_for_interior_edge(edge, detail, zones, idf)
            for edge, detail in inputs.zone_pairs
        ]
    )
    exterior_subsurfaces = [
        create_subsurface_for_exterior_edge(edge, detail, zones, idf)
        for edge, detail in inputs.zone_drn_pairs
    ]

    return interior_subsurfaces + exterior_subsurfaces
