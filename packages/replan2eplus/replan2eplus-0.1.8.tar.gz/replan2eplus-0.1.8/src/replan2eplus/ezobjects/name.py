import re
from typing import Literal, NamedTuple

SurfaceTypes = Literal["Wall", "Floor", "Roof"]


class IDFName(NamedTuple):
    # zone_name: str
    plan_name: str
    # storey_name: str
    # surface_type: SurfaceTypes | str
    n_direction: str
    n_position: str
    # object_type: str

    # @property
    # def zone_number(self):
    #     assert self.zone_name
    #     return int(self.zone_name.split(" ")[1])

    @property
    def direction_number(self):
        assert self.n_direction
        return int(self.n_direction)

    @property
    def position_number(self):
        if self.n_position:
            return int(self.n_position.split("_")[1])
        else:
            return ""

    @property
    def full_number(self):
        if self.position_number:
            return f"{self.direction_number}_{self.position_number}"
        else:
            return str(self.direction_number)

    # @property
    # def recreate_zone_name(self):
    #     return " ".join([self.zone_name, self.plan_name, self.storey_name]) # TODO redundnat with method on Zone?

    # @property
    # def plan_name_alone(self):
    #     return self.plan_name.replace("`", "")


# TODO this should be part of the object above as a class method?
def decompose_idf_name(name: str):
    def match(pattern: re.Pattern[str]):
        m = pattern.search(name)
        if m:
            return m.group()
        else:
            return ""

    # TODO write tests..
    # block = re.compile(r"Block \d{2}")
    plan_name = re.compile(r"`(.*)`")
    storey = re.compile(r"Storey \d{0,2}")
    surface_type = re.compile(r"(Wall|Floor|Roof)")
    n_direction = re.compile(r"\d{4}")
    n_position = re.compile(r"_\d{1,2}\b")
    object_type = re.compile(r"(Window|Door)")

    # s = IDFName(
    #     # zone_name=match(block),
    #     plan_name=match(plan_name).replace("`", ""),
    #     # storey_name=match(storey),
    #     # surface_type=match(surface_type),
    #     match(n_direction),
    #     match(n_position),
    #     # match(object_type),
    # )
    s = IDFName(
        match(plan_name).replace("`", ""),
        match(n_direction),
        match(n_position),
    )

    return s
