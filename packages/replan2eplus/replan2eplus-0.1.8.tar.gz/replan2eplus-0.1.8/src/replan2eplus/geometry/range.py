from dataclasses import dataclass
from enum import Enum
from typing import Callable, Literal, NamedTuple
import numpy as np


class InvalidRangeException(Exception):
    def __init__(self, min, max) -> None:
        super().__init__(self)
        print(f"{min:.2f} cannot be less than {max:.2f}")


@dataclass
class TriRange:
    min: float
    mid1: float
    mid2: float
    max: float

    def __post_init__(self):
        try:
            # TODO np assert a list of numbers are close..
            assert np.isclose(self.mid1 - self.min, self.mid2 - self.mid1)
            # assert np.isclose(self.max - self.min, self.mid2 - self.mid1)
        except AssertionError:
            raise InvalidRangeException(self.min, self.max)

    @property
    def dist_between(self):
        return self.mid1 - self.min


@dataclass(frozen=True)
class Range:
    min: float
    max: float

    def __post_init__(self):
        try:
            assert self.min <= self.max
        except AssertionError:
            raise InvalidRangeException(self.min, self.max)

    def __repr__(self) -> str:
        return f"[{self.min:.2f}, {self.max:.2f}]"

    def __eq__(self, other) -> bool:
        return np.isclose(self.min, other.min) and np.isclose(self.max, other.max)

    @property
    def as_tuple(self):
        return (self.min, self.max)

    @property
    def midpoint(self):
        return (self.min + self.max) / 2

    @property
    def size(self):
        return abs(self.max - self.min)

    @property
    def trirange(self):
        result = np.linspace(self.min, self.max, num=4)
        return TriRange(*[i.item() for i in result])


def expand_range(base: Range, factor: float):
    assert factor >= 1, NotImplementedError(
        "Have not handled shrinking!"
    )  # TODO not sure about this..
    new_size = base.size * factor
    delta = (new_size - base.size) / 2
    return Range(base.min - delta, base.max + delta)


def compute_multirange(ranges: list[Range]):
    smallest_min = min([i.min for i in ranges])
    largest_max = max([i.max for i in ranges])
    return Range(smallest_min, largest_max)

    # return [self.north.pair, self.south.pair, self.west.pair, self.east.pair]

    # @classmethod
    # def from_list_of_coords(cls, coords:list[Coord]):


# @dataclass
# class Dimensions:  # TODO why is this different from a Domain?
#     width: float
#     height: float

#     def __getitem__(self, i):
#         return (self.width, self.height)[i]

#     @property
#     def area(self):
#         return self.width * self.height

#     def modify(self, fx: Callable[[float], float]):
#         return self.__class__(fx(self.width), fx(self.height))

#     def modify_area(self, factor: float):
#         # preserves aspect ratio
#         sqrt_val = factor ** (1 / 2)
#         return self.__class__.modify(self, lambda x: sqrt_val * x)


# # TODO -> convert these to be associated with the EPBUnch, https://eppy.readthedocs.io/en/latest/_modules/eppy/bunch_subclass.html#addfunctions


# # def __lt__(self):
# #     return
