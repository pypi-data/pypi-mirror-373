import inspect
import typing

import pydantic
from pydantic import (
    BaseModel,
    Field,
    ValidationError,
    create_model,
)

from ...utils import T
from .exceptions import ColumnInvalidTypeException, GenericColumnException

if typing.TYPE_CHECKING:
    from .model import GenericModel

__all__ = ["GenericColumn"]


class _CapitalClass:
    def __repr__(self) -> str:
        return self.__class__.__name__.lstrip("_").upper()


class _PKAutoIncrement(_CapitalClass): ...


class _Unset(_CapitalClass): ...


PK_AUTO_INCREMENT = _PKAutoIncrement()
UNSET = _Unset()


class GenericColumn(typing.Generic[T]):
    """
    A generic column for `GenericModel`. This works similar to a SQLAlchemy column.

    Args:
        col_type (typing.Type[T]): The type of the column.
        primary_key (bool, optional): Whether the column is a primary key. Defaults to False.
        auto_increment (bool, optional): Whether the column is auto incremented. Only works if the column is a primary key. Defaults to False.
        unique (bool, optional): Whether the column is unique. Defaults to False.
        nullable (bool, optional): Whether the column is nullable. Defaults to True.
        default (T | typing.Callable[[], T] | typing.Callable[[GenericModel], T] | NoDefault, optional): The default value of the column. Will be used if the column is not set by the user. Defaults to NoDefault (no default value).
    """

    col_type: typing.Type[T]
    primary_key: bool
    auto_increment: bool
    unique: bool
    nullable: bool
    default: T | typing.Callable[["GenericModel"], T] | _Unset

    _validation_model: BaseModel = None
    _col_name: str = None

    def __init__(
        self,
        col_type: typing.Type[T],
        *,
        primary_key: bool = False,
        auto_increment: bool = False,
        unique: bool = False,
        nullable: bool = True,
        default: T
        | typing.Callable[[], T]
        | typing.Callable[["GenericModel"], T]
        | _Unset = UNSET,
    ):
        """
        Initializes a GenericColumn instance.

        Args:
            col_type (typing.Type[T]): The type of the column.
            primary_key (bool, optional): Whether the column is a primary key. Defaults to False.
            auto_increment (bool, optional): Whether the column is auto incremented. Only works if the column is a primary key. Defaults to False.
            unique (bool, optional): Whether the column is unique. Defaults to False.
            nullable (bool, optional): Whether the column is nullable. Defaults to True.
            default (T | typing.Callable[[], T] | typing.Callable[["GenericModel"], T] | _NoDefaultValue, optional): The default value of the column. Will be used if the column is not set by the user. Defaults to UNSET (no default value).

        Raises:
            GenericColumnException: If auto increment is set on a non-primary key column or if the column type is not int when auto increment is set.
            GenericColumnException: If auto increment is set on a non-integer column type.
        """
        self.col_type = col_type
        self.primary_key = primary_key
        self.auto_increment = auto_increment
        self.unique = unique
        self.nullable = nullable
        self.default = default

        if self.primary_key:
            self.unique = True
            self.nullable = False

        # Check if default is a function
        if inspect.isfunction(self.default):
            # If the function takes no parameters, convert it to a function that needs the instance
            if inspect.signature(self.default).parameters == {}:
                self.default = lambda instance, func=self.default: func()

        if not self.primary_key and self.auto_increment:
            raise GenericColumnException(
                self, "Auto increment can only be set on primary key columns"
            )

        if self.auto_increment and self.col_type is not int:
            raise GenericColumnException(
                self, "Primary key with auto increment must be of type int"
            )

        # TODO: Handle self.unique

    @typing.overload
    def __get__(
        self, instance: None, owner: typing.Type["GenericModel"]
    ) -> "GenericColumn": ...
    @typing.overload
    def __get__(
        self, instance: "GenericModel", owner: typing.Type["GenericModel"]
    ) -> T | None: ...
    def __get__(
        self,
        instance: typing.Optional["GenericModel"],
        owner: typing.Type["GenericModel"],
    ):
        if not instance:
            return self

        default_value = self.default
        if callable(default_value):
            default_value = default_value(instance)

        value: T | _Unset = instance.__dict__.get(f"_{self._col_name}", default_value)

        if value is default_value:
            if self.nullable and value is UNSET:
                return None
            elif self.primary_key and self.auto_increment:
                return PK_AUTO_INCREMENT

        return value

    def __set__(self, instance: "GenericModel", value: T | _Unset) -> None:
        try:
            validated = self._validation_model.model_validate({self._col_name: value})
        except ValidationError as e:
            raise ColumnInvalidTypeException(
                instance, f"Invalid type for column {self._col_name}, {str(e)}"
            )
        instance.__dict__[f"_{self._col_name}"] = getattr(validated, self._col_name)

    def __set_name__(self, owner: typing.Type["GenericModel"], name: str) -> None:
        self._col_name = name

        # Create pydantic model for validation
        validation_type = self.col_type
        if self.nullable:
            validation_type = validation_type | None
        if self.default is not UNSET:
            validation_type = validation_type | type(self.default)
            validation_field = Field(default=self.default)
        else:
            validation_field = Field

        self._validation_model = create_model(
            f"{owner.__name__}{self._col_name.capitalize()}Validation",
            __config__=pydantic.ConfigDict(arbitrary_types_allowed=True),
            **{name: (validation_type, validation_field)},
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({';'.join([f'{k}={getattr(v, "__name__", v)}' for k, v in vars(self).items() if not k.startswith('_')])})"

    def is_column_set(self, instance: "GenericModel") -> bool:
        """
        Check if the column is set in the instance.

        Args:
            instance (GenericModel): The instance to check.

        Returns:
            bool: True if the column is set, False otherwise.
        """
        return (
            f"_{self._col_name}" in instance.__dict__
            and getattr(instance, f"_{self._col_name}") is not UNSET
        )
