from replan2eplus.airboundary.interfaces import (
    DEFAULT_AIRBOUNDARY_OBJECT,
    AirboundaryConstructionObject,
)
from replan2eplus.ezobjects.surface import Surface
from replan2eplus.ezobjects.zone import Zone
from replan2eplus.idfobjects.idf import IDF
from replan2eplus.subsurfaces.interfaces import ZoneEdge
from replan2eplus.subsurfaces.logic import get_surface_between_zones
from replan2eplus.ezobjects.airboundary import Airboundary
from replan2eplus.ezobjects.subsurface import Edge


def add_airboundary_construction(idf: IDF, object_: AirboundaryConstructionObject):
    idf.add_airboundary_construction(object_)


def update_airboundary_constructions(
    idf: IDF,
    edges: list[Edge],
    zones: list[Zone],
):
    zone_edges = [ZoneEdge(*i) for i in edges if not i.is_directed_edge]
    assert edges == zone_edges, (
        f"All airboundary edges need to be between zones! Instead have {edges}"
    )

    add_airboundary_construction(idf, DEFAULT_AIRBOUNDARY_OBJECT)

    airboundaries: list[Airboundary] = []

    for zone_edge, edge in zip(zone_edges, edges):
        main_surface, nb_surface = get_surface_between_zones(zone_edge, zones)
        idf.update_construction(main_surface, DEFAULT_AIRBOUNDARY_OBJECT.Name)
        idf.update_construction(nb_surface, DEFAULT_AIRBOUNDARY_OBJECT.Name)

        airboundaries.extend(
            [Airboundary(main_surface, edge), Airboundary(nb_surface, edge)]
        )

    return airboundaries
