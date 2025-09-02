import typing

from .utils import T

__all__ = ["raise_exception", "FastAPIReactToolkitException", "RolesMismatchException"]


def raise_exception(message: str, return_type: typing.Type[T] | None = None) -> T:
    """
    Raise a FastAPIReactToolkitException with the given message.

    Args:
        message (str): The error message.
        return_type (typing.Type[T] | None, optional): The expected return type. Defaults to None.

    Raises:
        FastAPIReactToolkitException: Always raised.

    Returns:
        T: The return value.
    """
    raise FastAPIReactToolkitException(message)


class FastAPIReactToolkitException(Exception):
    """Base exception for FastAPI React Toolkit errors."""


class RolesMismatchException(FastAPIReactToolkitException):
    """Exception raised when the roles do not match the expected roles."""
