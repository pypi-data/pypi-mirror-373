from pathlib import Path

from replan2eplus.constructions.interfaces import ConstructionsObject
from replan2eplus.errors import IDFMisunderstandingError
from replan2eplus.ezobjects.constr_and_mat_utils import (
    get_possible_epbunches,
    warn_about_idf_comparison,
)
from replan2eplus.ezobjects.construction import Construction
from replan2eplus.ezobjects.epbunch_utils import chain_flatten, create_dict_from_fields
from replan2eplus.idfobjects.idf import IDF
from replan2eplus.materials.presentation import (
    add_materials,
    create_materials_from_other_idfs,
)




def create_constructions_from_other_idfs(
    path_to_idfs: list[Path], path_to_idd: Path, construction_names: list[str] = []
):
    flat_epbunches = get_possible_epbunches(path_to_idfs, path_to_idd)
    warn_about_idf_comparison(path_to_idfs, flat_epbunches, construction_names)

    if construction_names:
        flat_epbunches = [i for i in flat_epbunches if i.Name in construction_names]

    constructions = [
        ConstructionsObject(**create_dict_from_fields(i)) for i in flat_epbunches
    ]

    return constructions


def check_materials_are_in_idf(const_object: ConstructionsObject, idf: IDF):
    idf_mats = idf.get_materials()
    idf_mat_names = [i.Name for i in idf_mats]
    for mat in const_object.materials:
        try:
            assert (
                mat in idf_mat_names
            )  # TODO: need try-except for assertion! have made this mistake elsewhere -> look for it and fix it!
        except AssertionError:
            raise IDFMisunderstandingError(
                f"`{mat}` needed for this construction is not in IDF materials: {sorted(idf_mat_names)}"
            )


def find_and_add_materials(
    idf: IDF,
    construction_objects: list[ConstructionsObject],
    path_to_material_idfs: list[Path],
    path_to_idd: Path,
):
    materials_to_find: list[str] = chain_flatten(
        [i.materials for i in construction_objects]
    )
    mat_pairs = create_materials_from_other_idfs(
        path_to_material_idfs, path_to_idd, materials_to_find
    )

    new_materials = add_materials(idf, mat_pairs)
    return new_materials


# TODO: when adding constructions to idf, fail if the constituent materials are not in the new idf..
def add_constructions(idf: IDF, construction_objects: list[ConstructionsObject]):
    results = []
    for const_object in construction_objects:
        check_materials_are_in_idf(const_object, idf)
        new_obj = idf.add_construction(const_object)
        results.append(Construction(new_obj))

    return results


# TODO: possibly one last function where pass in const names, names where consts are, and place to look for materials ->
