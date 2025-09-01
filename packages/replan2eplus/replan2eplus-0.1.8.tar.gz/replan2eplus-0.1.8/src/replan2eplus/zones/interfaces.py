from dataclasses import dataclass

from replan2eplus.errors import IDFMisunderstandingError
from replan2eplus.geometry.domain import Domain
from replan2eplus.idfobjects.zone import GeomeppyBlock
from typing import NamedTuple


@dataclass
class Room:
    name: str
    domain: Domain
    height: float  # TODO add default # notify that height is in meters!

    @property
    def coords(self):
        return self.domain.corner.tuple_list # NOTE: this translation ensures that the domain is in the correct order, but should I have another check? 

    @property
    def room_name(self):
        return f"`{self.name}`"

    def geomeppy_block(self):
        return GeomeppyBlock(
            {
                "name": self.room_name,
                "coordinates": self.coords,
                "height": self.height,
            }
        )


class RoomZonePair(NamedTuple):
    room_name: str  # name in the plan
    zone_name: str


@dataclass
class RoomMap:
    items: list[RoomZonePair]

    @property
    def room_names(self):
        return [i.room_name for i in self.items]

    def validate_room(self, name: str):
        try:
            assert name in self.room_names
        except AssertionError:
            raise IDFMisunderstandingError(f"Invalid room name: `{name}` is not in []")

    # TODO also handle directions -> NORTH EAST etc..  -> should be validate name, not validate room?
