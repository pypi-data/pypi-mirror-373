import abc
import typing

from ..utils import T

if typing.TYPE_CHECKING:
    from .interface import AbstractInterface


class AbstractBaseFilter(abc.ABC, typing.Generic[T]):
    """
    Abstract base class to apply filters to select statements.
    """

    name: str
    arg_name: str
    datamodel: "AbstractInterface"

    is_heavy = False
    """
    If set to true, will run the filter in a separate thread. Useful for heavy filters that take a long time to execute. Default is False.

    Only works when `apply` function is async.
    """

    def __init__(self, datamodel: "AbstractInterface"):
        super().__init__()
        self.datamodel = datamodel

    @abc.abstractmethod
    def apply(self, statement: T, col: str, value) -> T:
        """
        Apply the filter to the given SQLAlchemy Select statement.

        Args:
            statement (T): The SQLAlchemy query statement to modify.
            col (str): The column to filter by.
            value: The value to filter the column by.

        Returns:
            T: The modified SQLAlchemy query statement.
        """
        raise NotImplementedError("Subclasses must implement this method.")
