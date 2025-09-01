# EPBunch helpers -> not worth it to have a class..
from dataclasses import fields
from eppy.bunch_subclass import EpBunch
from typing import Any, Callable, Dict, Iterable, List, TypeVar, Union
from itertools import groupby
from itertools import chain

T = TypeVar("T")


def get_epbunch_key(epbunch: EpBunch):
    return epbunch.key


def create_dict_from_fields(epbunch: EpBunch):
    res = {field: epbunch[field] for field in epbunch.objls if field != "key"}
    return {k: v for k, v in res.items() if v}


def classFromArgs(className, argDict):
    # TODO this is a temp solution! -> removes data that might be there!
    fieldSet = {f.name for f in fields(className) if f.init}
    filteredArgDict = {k: v for k, v in argDict.items() if k in fieldSet}
    return className(**filteredArgDict)


def sort_and_group_objects(lst: Iterable[T], fx: Callable[[T], Any]) -> list[list[T]]:
    sorted_objs = sorted(lst, key=fx)
    return [list(g) for _, g in groupby(sorted_objs, fx)]


# TODO move to utils4plans..
def sort_and_group_objects_dict(
    lst: Iterable[T], fx: Callable[[T], Any]
) -> dict[Any, list[T]]:
    sorted_objs = sorted(lst, key=fx)
    d = {}
    for k, g in groupby(sorted_objs, fx):
        d[k] = [i for i in list(g)]
    return d


def chain_flatten(lst: Iterable[Iterable[T]]) -> list[T]:
    return list(chain.from_iterable(lst))


def set_difference(a: Iterable[T], b: Iterable[T]) -> list[T]:
    return list(set(a).difference(set(b)))


def filter_list(function: Callable[[T], Any], iterable: Iterable[T]):
    return filter(function, iterable)
