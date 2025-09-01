from replan2eplus.ezobjects.surface import Surface
from replan2eplus.zones.interfaces import Room
from replan2eplus.idfobjects.idf import IDF
from replan2eplus.ezobjects.zone import Zone
# from replan2eplus.ezcase.examples import get_minimal_idf

# TODO: logic!
# Tests to do on rooms -> no duplicates..
# -> Domains should be hashed -> no dup domains,
# no duplicate room names..


# TODO may need a different home..
def get_zone_surfaces(zone: Zone, surfaces: list[Surface]):
    return [i for i in surfaces if i.zone_name == zone.zone_name]


def assign_zone_surfaces(zones: list[Zone], surfaces: list[Surface]):
    for zone in zones:
        z_surfaces = get_zone_surfaces(zone, surfaces)
        zone.surfaces = z_surfaces
        assert len(zone.surfaces) >= 6
    return zones


def create_zones(idf: IDF, rooms: list[Room]):
    # TODO move to logic!
    for room in rooms:
        idf.add_geomeppy_block(room.geomeppy_block())

    idf.intersect_match()
    # now get the zones from the idf..
    zones = [Zone(_epbunch=i) for i in idf.get_zones()]
    surfaces = [Surface(i) for i in idf.get_surfaces()]
    updates_zones = assign_zone_surfaces(zones, surfaces)

    # figure out zone surfaces..
    # room_map = RoomMap([RoomZonePair(i.room_name, i.zone_name) for i in zones])
    return updates_zones, surfaces  # oom_map
