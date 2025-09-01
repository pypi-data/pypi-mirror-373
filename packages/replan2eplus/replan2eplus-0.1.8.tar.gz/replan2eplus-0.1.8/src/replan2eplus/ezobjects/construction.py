from replan2eplus.ezobjects.base import EZObject
from dataclasses import dataclass
import replan2eplus.epnames.keys as epkeys
from utils4plans.lists import chain_flatten


@dataclass
class Construction(EZObject):
    expected_key: str = epkeys.CONSTRUCTION

    @property
    def construction_name(self):
        return self._epbunch.Name


@dataclass
class BaseConstructionSet:
    # default: Construction
    interior: str
    exterior: str

    # def __post_init__(self):
    #     if not self.interior:
    #         self.interior = self.default
    #     if not self.exterior:
    #         self.exterior = self.default


@dataclass
class EPConstructionSet:
    wall: BaseConstructionSet
    roof: BaseConstructionSet
    floor: BaseConstructionSet
    window: BaseConstructionSet
    door: BaseConstructionSet

    # TODO validate?

    @property
    def sets(self):
        return [self.wall, self.roof, self.floor, self.window, self.door]

    @property
    def names(self):
        return chain_flatten([[i.interior, i.exterior] for i in self.sets])
