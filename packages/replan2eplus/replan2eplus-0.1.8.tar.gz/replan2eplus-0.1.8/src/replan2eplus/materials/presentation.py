from pathlib import Path
from re import L
from typing import Any, NamedTuple
import warnings

from utils4plans.sets import set_difference

from replan2eplus.ezobjects.epbunch_utils import classFromArgs
from replan2eplus.ezobjects.material import Material
import replan2eplus.materials.interfaces as mat_interfaces
from replan2eplus.errors import IDFMisunderstandingError
from replan2eplus.ezobjects.epbunch_utils import (
    create_dict_from_fields,
)
from replan2eplus.idfobjects.idf import IDF, EpBunch
from replan2eplus.materials.interfaces import (
    MaterialKey,
    MaterialObjectBase,
    material_keys,
)
from replan2eplus.ezobjects.constr_and_mat_utils import (
    get_possible_epbunches,
    warn_about_idf_comparison,
)

# TODO could also call logic?


class MaterialPair(NamedTuple):
    key: MaterialKey
    object_: MaterialObjectBase


def map_materials(key: MaterialKey, values: dict[str, Any]):
    match key:
        case "MATERIAL":
            return mat_interfaces.MaterialObject(**values)

        case "MATERIAL:NOMASS":
            return mat_interfaces.MaterialNoMassObject(**values)

        case "MATERIAL:AIRGAP":
            return mat_interfaces.MaterialAirGap(**values)

        case "WINDOWMATERIAL:GLAZING":  # TODO -> this is not the best, bc what if get more information? Its excluded!
            return classFromArgs(mat_interfaces.WindowMaterialGlazingObject, values)

        case "WINDOWMATERIAL:GAS":
            return classFromArgs(mat_interfaces.WindowMaterialGasObject, values)

        case "_":
            raise NotImplementedError("Don't have an object for this kind of material!")


def get_material_epbunch_key(epbunch: EpBunch) -> MaterialKey:
    val = epbunch.key.upper()
    assert val in material_keys
    return val  # type: ignore --- checked above


# TODO expose as a function that can be called..
def create_materials_from_other_idfs(
    path_to_idfs: list[Path], path_to_idd: Path, material_names: list[str] = []
):
    epbunches = get_possible_epbunches(
        path_to_idfs, path_to_idd, object_type="MATERIAL"
    )
    warn_about_idf_comparison(path_to_idfs, epbunches, material_names)

    if material_names:
        epbunches = [i for i in epbunches if i.Name in material_names]

    results: list[MaterialPair] = []
    for bunch in epbunches:
        bunch_dict = create_dict_from_fields(bunch)
        key = get_material_epbunch_key(bunch)
        object = map_materials(key, bunch_dict)
        results.append(MaterialPair(key, object))
    return results


# TODO can avoid need for material pair by adding key to the object itself..
def add_materials(idf: IDF, material_pairs: list[MaterialPair]):
    new_materials: list[Material] = []
    for mat_pair in material_pairs:
        (
            epbunch,
            key,
            mat_obj,
        ) = idf.add_material(mat_pair.key, mat_pair.object_)
        new_materials.append(Material(epbunch, key, mat_obj))
    return new_materials
