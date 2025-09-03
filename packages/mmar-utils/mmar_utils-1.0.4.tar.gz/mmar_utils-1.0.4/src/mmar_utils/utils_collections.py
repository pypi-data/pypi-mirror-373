from collections.abc import Callable, Iterable
from typing import TypeVar


T = TypeVar("T")


def edit_object(obj: any, editor: Callable[[T], T | None]):
    """assumed there is no null's inside obj"""
    obj_fix = editor(obj)
    if obj_fix is not None:
        return obj_fix
    if isinstance(obj, tuple):
        return tuple(edit_object(el, editor) for el in obj)
    if isinstance(obj, list):
        return list(edit_object(el, editor) for el in obj)
    return obj


def flatten(xss: Iterable[Iterable[T]]) -> list[T]:
    return [x for xs in xss for x in xs]
