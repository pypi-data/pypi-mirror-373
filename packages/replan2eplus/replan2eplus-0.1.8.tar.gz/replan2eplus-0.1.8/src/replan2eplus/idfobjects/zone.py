# TODO move to Eppy constants
from typing import TypedDict


class GeomeppyBlock(TypedDict):
    name: str
    coordinates: list[tuple[float, float]]
    height: float
