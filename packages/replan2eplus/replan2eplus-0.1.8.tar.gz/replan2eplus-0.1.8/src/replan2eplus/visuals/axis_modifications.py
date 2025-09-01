from typing import NamedTuple

from matplotlib.axes import Axes

from replan2eplus.ezobjects.subsurface import Edge
from replan2eplus.ezobjects.zone import Zone
from replan2eplus.geometry.contact_points import CardinalPoints
from replan2eplus.geometry.coords import Coord
from replan2eplus.geometry.domain import Domain
from replan2eplus.visuals.transformations import (
    domain_to_line,
    domain_to_rectangle,
    subsurface_to_connection_line,
)
from replan2eplus.visuals.styles.artists import (
    LineStyles,
    RectangleStyles,
    AnnotationStyles,
)


def add_rectangles(domains: list[Domain], style: RectangleStyles, axes: Axes):
    for domain in domains:
        rectangle = domain_to_rectangle(domain)
        rectangle.set(**style.values)
        axes.add_artist(rectangle)
    return axes


def add_surface_lines(domains: list[Domain], style: LineStyles, axes: Axes):
    for ix, domain in enumerate(domains):
        if ix != 0:
            style.label = ""
        line = domain_to_line(domain).to_line2D
        line.set(**style.values)
        axes.add_artist(line)
    return axes


def add_connection_lines(
    domains: list[Domain],
    edges: list[Edge],
    zones: list[Zone],
    cardinal_coords: CardinalPoints,
    style: LineStyles,
    axes: Axes,
):
    for domain, edge in zip(domains, edges):
        line = subsurface_to_connection_line(domain, edge, zones, cardinal_coords)
        line.set(**style.values)
        axes.add_artist(line)
    return axes


class AnnotationPair(NamedTuple):
    coord: Coord
    name: str


def add_annotations(
    annotation_pair: list[AnnotationPair],
    style: AnnotationStyles,
    axes: Axes,
):
    for coord, name in annotation_pair:
        axes.text(*coord.as_tuple, s=name, **style.values)
    return axes
