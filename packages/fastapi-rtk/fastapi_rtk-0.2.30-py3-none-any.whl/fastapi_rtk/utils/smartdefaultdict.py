import collections
import typing

__all__ = ["smartdefaultdict"]

_KT = typing.TypeVar("_KT")
_VT = typing.TypeVar("_VT")


class smartdefaultdict(collections.defaultdict[_KT, _VT]):
    """
    Subclass of `collections.defaultdict` with extended functionalities.

    - the `default_factory` can be a callable that takes the key as an argument.
    """

    default_factory: typing.Callable[[_KT], _VT] | None

    def __init__(self, default_factory: typing.Callable[[_KT], _VT] | None, /):
        return super().__init__(default_factory)

    def __missing__(self, key):
        self[key] = self.default_factory(key)
        return self[key]
