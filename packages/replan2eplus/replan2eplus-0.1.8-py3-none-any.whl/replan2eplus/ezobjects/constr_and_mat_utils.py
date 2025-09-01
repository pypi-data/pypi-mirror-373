from typing import Literal
from utils4plans.sets import set_difference
from replan2eplus.ezobjects.epbunch_utils import EpBunch, chain_flatten
from replan2eplus.idfobjects.idf import IDF

import warnings
from pathlib import Path

# TODO -> move to materials.. 

def get_possible_epbunches(path_to_idfs: list[Path], path_to_idd: Path, object_type: Literal["MATERIAL","CONSTRUCTION"] = "CONSTRUCTION"):
    possible_epbunches = []
    for path in path_to_idfs:
        other_idf = IDF(path_to_idd, path)
        if object_type == "MATERIAL":
            epbunches = other_idf.get_materials()
        else:
            epbunches = other_idf.get_constructions()
        possible_epbunches.append(epbunches)

    return chain_flatten(possible_epbunches)


def warn_about_idf_comparison(
    path_to_idfs: list[Path], epbunches: list[EpBunch], names: list[str]
):
    differing_names = set_difference(names, [i.Name for i in epbunches])
    idf_names = [i.name for i in path_to_idfs]
    if differing_names:
        warnings.warn(
            f"{differing_names} cannot be found in these IDFs `{idf_names}`",
            UserWarning,
        )
