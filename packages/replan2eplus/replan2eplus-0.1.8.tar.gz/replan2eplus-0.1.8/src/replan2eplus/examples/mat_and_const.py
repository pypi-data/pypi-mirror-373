from pathlib import Path
from replan2eplus.paths import static_paths
from replan2eplus.ezobjects.construction import EPConstructionSet, BaseConstructionSet

PATH_TO_MAT_AND_CONST_IDF = (
    static_paths.inputs / "constructions/ASHRAE_2005_HOF_Materials.idf"
)

PATH_TO_WINDOW_CONST_IDF = static_paths.inputs / "constructions/WindowConstructs.idf"

PATH_TO_WINDOW_GLASS_IDF = (
    static_paths.inputs / "constructions/WindowGlassMaterials.idf"
)
PATH_TO_WINDOW_GAS_IDF = static_paths.inputs / "constructions/WindowGasMaterials.idf"

material_idfs = [
    PATH_TO_MAT_AND_CONST_IDF,
    PATH_TO_WINDOW_GLASS_IDF,
    PATH_TO_WINDOW_GAS_IDF,
]


CONST_IN_EXAMPLE = "Medium Exterior Wall"
TEST_CONSTRUCTIONS = ["Light Exterior Wall", "Light Roof/Ceiling"]
TEST_CONSTRUCTIONS_WITH_WINDOW = [
    "Light Exterior Wall",
    "Light Roof/Ceiling",
    "Sgl Clr 6mm",
]


BAD_CONSTRUCTION_SET = EPConstructionSet(
    wall=BaseConstructionSet("Medium Roof/Ceiling", "Medium Roof/Ceiling"),
    floor=BaseConstructionSet("Medium Partitions", "Medium Furnishings"),
    roof=BaseConstructionSet("Medium Furnishings", "Medium Furnishings"),
    window=BaseConstructionSet("Sgl Clr 6mm", "Sgl Clr 6mm"),
    door=BaseConstructionSet("Medium Partitions", "Medium Partitions"),
)


SAMPLE_CONSTRUCTION_SET = EPConstructionSet(
    # interior then exterior
    # TODO should be able to specify a tuple, and just one object if its the same.., trim white space
    wall=BaseConstructionSet("Medium Partitions", "Medium Exterior Wall"),
    floor=BaseConstructionSet("Medium Floor", "Medium Floor"),
    roof=BaseConstructionSet("Medium Roof/Ceiling", "Medium Roof/Ceiling"),
    window=BaseConstructionSet("Sgl Clr 6mm", "Sgl Clr 6mm"),
    door=BaseConstructionSet("Medium Furnishings", "Medium Furnishings"),
)  # TODO -> could one quicly change the names of these?
