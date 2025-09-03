from caerp.utils.compat import Iterable
import itertools
from typing import (
    Any,
    Tuple,
)


def groupby(elements: Iterable, attrname: str) -> Tuple[Any, Iterable]:
    """
    Specialized version of itertools.groupby grouping on attribute

    Note that for this to work, elements should be already ordered to allow
    grouping ; see itertools.groupby doc.
    """

    def f(x):
        try:
            return getattr(x, attrname)
        except AttributeError:
            raise ValueError(f"Attempted to groupby {x} on inexistant attr {attrname}")

    return itertools.groupby(elements, f)
