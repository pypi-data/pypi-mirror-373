import typing

T = typing.TypeVar("T")

__all__ = ["use_default_when_none"]


def use_default_when_none(value: T, default: T) -> T:
    """
    Returns the value if it is not None, otherwise returns the default value.

    Args:
        value (T): The value to check.
        default (T): The default value to return if `value` is None.

    Returns:
        T: The original value or the default value.
    """
    return value if value is not None else default
