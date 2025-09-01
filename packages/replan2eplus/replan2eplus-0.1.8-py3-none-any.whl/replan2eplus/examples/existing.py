from replan2eplus.examples.defaults import PATH_TO_IDD, PATH_TO_SAMPLE_IDF
from replan2eplus.ezcase.main import EZCase
from replan2eplus.ezcase.read import ExistCase


def get_example_idf():
    case = EZCase(PATH_TO_IDD, PATH_TO_SAMPLE_IDF)
    return case.initialize_idf()


def read_example_case():
    case = ExistCase(PATH_TO_IDD, PATH_TO_SAMPLE_IDF)
    case.initialize_idf()
    case.get_objects()
    return case
