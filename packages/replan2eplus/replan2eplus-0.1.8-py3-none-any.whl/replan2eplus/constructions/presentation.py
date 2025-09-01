from pathlib import Path

from replan2eplus.constructions.logic.update import (
    update_surfaces_with_construction_set,
)
from replan2eplus.constructions.logic.utils import (
    add_constructions,
    create_constructions_from_other_idfs,
    find_and_add_materials,
)
from replan2eplus.ezobjects.construction import EPConstructionSet
from replan2eplus.ezobjects.surface import Surface
from replan2eplus.idfobjects.idf import IDF, Subsurface


def add_constructions_from_other_idf(
    idf: IDF,
    paths_to_construction_idfs: list[Path],
    paths_to_material_idfs: list[Path],
    path_to_idd: Path,
    construction_set: EPConstructionSet,
    surfaces: list[Surface],
    subsurfaces: list[Subsurface],
):
    construction_objects = create_constructions_from_other_idfs(
        paths_to_construction_idfs, path_to_idd, construction_set.names
    )

    new_materials = []
    if paths_to_material_idfs:
        new_materials = find_and_add_materials(
            idf,
            construction_objects,
            paths_to_material_idfs,
            path_to_idd,
        )

    new_constructions = add_constructions(idf, construction_objects)

    update_surfaces_with_construction_set(idf, construction_set, surfaces, subsurfaces)
    return new_materials, new_constructions
