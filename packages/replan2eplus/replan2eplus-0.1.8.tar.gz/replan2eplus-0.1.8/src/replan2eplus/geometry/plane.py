from geomeppy.geom.polygons import Polygon3D
from replan2eplus.geometry.coords import Coord, Coordinate3D
from replan2eplus.geometry.domain import Domain, Plane, AXIS
from replan2eplus.geometry.range import Range

# TODO: move?


def get_location_of_fixed_plane(plane: AXIS, coords: list[Coordinate3D]):
    plane_locs = [coord.get_plane_axis_location(plane.lower()) for coord in coords]
    unique_loc = set(plane_locs)
    assert len(unique_loc) == 1
    return plane_locs[0]


def create_domain_from_coords_list(coords: list[Coord]):
    xs = sorted(set([i.x for i in coords]))
    ys = sorted(set([i.y for i in coords]))
    horz_range = Range(xs[0], xs[-1])
    vert_range = Range(ys[0], ys[-1])
    return Domain(horz_range, vert_range)


def create_domain_from_coords(normal_axis: AXIS, coords: list[Coordinate3D]):
    def get_2D_coords(l1, l2):
        return [coord.get_pair(l1, l2) for coord in coords]

    match normal_axis:
        case "X":
            pair = ("y", "z")

        case "Y":
            pair = ("x", "z")

        case "Z":
            pair = ("x", "y")
        case _:
            raise Exception("Invalid Direction!")

    coords_2D = get_2D_coords(*pair)
    domain = create_domain_from_coords_list(coords_2D)

    location_of_fixed_plane = get_location_of_fixed_plane(normal_axis, coords)
    # TODO set plane function.. 
    # domain.plane = Plane(normal_axis, location_of_fixed_plane)

    return Domain(
        domain.horz_range,
        domain.vert_range,
        plane=Plane(normal_axis, location_of_fixed_plane),
    )


def compute_unit_normal(coords: list[tuple[float, float, float]]) -> AXIS:
    vector_map: dict[tuple[int, int, int], AXIS] = {
        (1, 0, 0): "X",
        (0, 1, 0): "Y",
        (0, 0, 1): "Z",
    }
    polygon = Polygon3D(coords)
    normal_vector = polygon.normal_vector
    nv = tuple([abs(int(i)) for i in normal_vector])
    assert len(nv) == 3

    try:
        return vector_map[nv]
    except:
        assert polygon.vertices
        flipped_vertices = reversed(polygon.vertices)

        print(f"There is something wrong with these vertices! switching them around. Original: {polygon.vertices}. New: {flipped_vertices}")
        normal_vector = polygon.normal_vector
        nv = tuple([abs(round(i)) for i in normal_vector])
        assert len(nv) == 3
        return vector_map[nv]


