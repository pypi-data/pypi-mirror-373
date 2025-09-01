from dataclasses import dataclass
from typing import Any, Literal
from eppy.bunch_subclass import EpBunch
from replan2eplus.ezobjects.epbunch_utils import get_epbunch_key
from replan2eplus.errors import InvalidEpBunchError
from replan2eplus.ezobjects.name import decompose_idf_name


@dataclass
class EZObject:
    _epbunch: EpBunch
    expected_key: Any # str  # TODO does this mess things up? -> want it to be parent of typed and any literal.. 
    # TODO idf name stuff

    def __post_init__(self):
        actual_key = get_epbunch_key(self._epbunch)
        try:
            assert actual_key == self.expected_key
        except AssertionError:
            raise InvalidEpBunchError(self.expected_key, actual_key)

    @property
    def _idf_name(self):
        return str(self._epbunch.Name)

    @property
    def _dname(self):
        return decompose_idf_name(self._idf_name)
