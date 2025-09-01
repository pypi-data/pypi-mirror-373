from collections.abc import MutableSet
from typing import Any, Dict, Iterable, Iterator


class OrderedSet(MutableSet):
    """Something akin to a `set` that keeps the order of insertion.

    The correctness of this class relies upon Python 3.7 where `dict`s
    started respecting order of insertion.
    """
    def __init__(self, iterable: Iterable = ()):
        self._values: Dict[Any, None] = {v: None for v in iterable}

    def __len__(self) -> int:
        return len(self._values)

    def __iter__(self) -> Iterator[Any]:
        return iter(self._values)

    def __contains__(self, x: Any) -> bool:
        return self._values.__contains__(x)

    def add(self, value: Any) -> None:
        self._values[value] = None

    def discard(self, value: Any) -> None:
        self._values.pop(value)

    def intersection(self, other: Iterable[Any]):
        # Python 3.11+ has typing.Self, which is a better way of typing this.
        #  https://peps.python.org/pep-0673/
        # There is supposedly a way of doing this with TypeVars, but it's unclear how to make mypy happy.
        other_set = set(other)
        return OrderedSet(i for i in self if i in other_set)
