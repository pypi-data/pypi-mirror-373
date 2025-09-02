import typing

from ...bases.model import BasicModel
from ...utils import T, lazy
from .column import UNSET, GenericColumn, _PKAutoIncrement
from .exceptions import (
    ColumnNotSetException,
    MultipleColumnsException,
    PKMissingException,
    PKMultipleException,
)

if typing.TYPE_CHECKING:
    from .session import Table

__all__ = ["GenericModel"]


class Mapper(typing.Generic[T]):
    """
    Mapper class that contains a model's definitions.
    """

    pk: str = None
    """
    The primary key of the model.
    - If a model is missing a primary key, it will raise a `PKMissingException`.
    - If a model has multiple primary keys, it will raise a `PKMultipleException`.
    """
    properties: dict[str, T] = None
    """
    A dictionary of properties of the model.
    """
    columns: list[str] = None
    """
    A list of columns of the model excluding the relationships.
    """

    def __init__(self):
        self.properties = {}
        self.columns = []


class GenericModel(BasicModel):
    """
    GenericModel is a base class for all models that does not use SQLAlchemy, but want to behave like one.
    """

    __mapper__: Mapper[GenericColumn] = lazy(
        lambda: Mapper[GenericColumn](), only_instance=False
    )
    """
    A mapper that contains the primary key, properties, and columns of the model.
    """
    __ignore_init__ = False
    """
    If set to True, the `__init_subclass__` method will not run for this class.

    Useful for subclasses that should work as a model.
    """
    __table__: "Table | None" = None
    """
    The table object that can be used as a way to check whether the model is queried from a table.
    """

    def __init_subclass__(cls) -> None:
        if getattr(cls, "__ignore_init__", False):
            # If the child class defines '__ignore_init__', skip the parent's logic
            return

        # Take all the columns from the base classes, this allow the use of multiple inheritance
        base_list = list(cls.__bases__)
        base_list.append(cls)
        self_attr = {}
        for base in base_list:
            self_attr.update(
                {k: v for k, v in vars(base).items() if isinstance(v, GenericColumn)}
            )

        for key, value in self_attr.items():
            if isinstance(value, GenericColumn):
                cls.__mapper__.properties[key] = value
                cls.__mapper__.columns.append(key)

                if value.primary_key:
                    if cls.__mapper__.pk and cls.__mapper__.pk != key:
                        raise PKMultipleException(
                            cls.__name__, "Only one primary key is allowed"
                        )
                    cls.__mapper__.pk = key

        if not cls.__mapper__.pk:
            raise PKMissingException(cls.__name__, "Primary key is missing")

    def __init__(self, **kwargs):
        if not kwargs:
            return
        for key, value in kwargs.items():
            if key not in self.__mapper__.properties.keys():
                continue
            setattr(self, key, value)
        self.is_model_valid()

    def get_pk(self) -> str | int | _PKAutoIncrement:
        """
        Get the primary key of the model.

        Returns:
            str | int | _PKAutoIncrement: The primary key of the model.
        """
        return getattr(self, self.__mapper__.pk)

    def set_pk(self, value: str | int):
        """
        Set the primary key of the model.

        Args:
            value (str | int): The value to set as the primary key.
        """
        setattr(self, self.__mapper__.pk, value)

    def get_col_type(self, col_name: str):
        return self.__mapper__.properties[col_name].col_type

    def update(self, data):
        super().update(data)

        # Check if the model is valid
        self.is_model_valid()

    def is_model_valid(self):
        """
        Check if the model is valid. A model is valid if all the columns are set.

        Raises:
            MultipleColumnsException: If any column is not set.
        """
        errors: list[Exception] = []
        for key in self.__mapper__.properties.keys():
            if getattr(self, key) is UNSET:
                errors.append(ColumnNotSetException(self, f"Column {key} is not set"))

        if errors:
            # Rollback to last valid state
            last_valid_data = getattr(self, "_last_valid_state", None)
            if last_valid_data is not None:
                self.update(last_valid_data)
            raise MultipleColumnsException(self, errors)

        # Save last valid state
        self._last_valid_state = {
            key: getattr(self, key) for key in self.__mapper__.properties.keys()
        }

    @classmethod
    def get_pk_attrs(cls):
        return [cls.__mapper__.pk]

    def __repr__(self):
        return f"{self.__class__.__name__}({';'.join([f'{col}={getattr(self, col)}' for col in self.__mapper__.properties.keys()])})"
