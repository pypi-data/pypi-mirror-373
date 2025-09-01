# functions used in other parts of the code!

# def filter_subsurfaces():
#     # TODO: for now use dummy hash, later add some sort of ordering..
#     # do want to keep in the edge order though..
#     pass
from replan2eplus.ezobjects.subsurface import Subsurface


def get_unique_subsurfaces(subsurfaces: list[Subsurface]):
    return [i for i in subsurfaces if i.edge.space_a in i.surface.zone_name]
