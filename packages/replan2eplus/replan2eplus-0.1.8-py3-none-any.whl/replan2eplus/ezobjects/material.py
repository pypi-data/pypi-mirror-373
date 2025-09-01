from replan2eplus.ezobjects.base import EZObject
from dataclasses import dataclass
import replan2eplus.epnames.keys as epkeys
from replan2eplus.materials.interfaces import (
    MaterialKey,
    MaterialObjectBase,
)  # TODO potential circular import


@dataclass
class Material(EZObject):
    expected_key: MaterialKey
    material_object: MaterialObjectBase


