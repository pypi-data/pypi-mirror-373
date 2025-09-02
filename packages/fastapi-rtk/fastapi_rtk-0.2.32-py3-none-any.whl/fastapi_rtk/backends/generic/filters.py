import enum
import typing
from datetime import date, datetime

from ...bases.filter import AbstractBaseFilter
from ...const import logger
from .session import GenericSession

if typing.TYPE_CHECKING:
    from .interface import GenericInterface

__all__ = [
    "GenericBaseFilter",
    "GenericFilterTextContains",
    "GenericFilterEqual",
    "GenericFilterNotEqual",
    "GenericFilterStartsWith",
    "GenericFilterNotStartsWith",
    "GenericFilterEndsWith",
    "GenericFilterNotEndsWith",
    "GenericFilterContains",
    "GenericFilterIContains",
    "GenericFilterNotContains",
    "GenericFilterGreater",
    "GenericFilterSmaller",
    "GenericFilterGreaterEqual",
    "GenericFilterSmallerEqual",
    "GenericFilterIn",
    "GenericFilterGlobal",
    "GenericFilterConverter",
]


class GenericBaseFilter(AbstractBaseFilter[GenericSession]):
    datamodel: "GenericInterface"

    def _cast_value(self, col: str, value: typing.Any):
        """
        Cast the value to the correct type.

        Args:
            col (str): The column name.
            value (typing.Any): The value to cast.

        Returns:
            typing.Any: The value casted to the correct type.
        """
        try:
            if isinstance(value, list):
                return [self._cast_value(col, val) for val in value]
            if value == "NULL":
                return None
            if self.datamodel.is_enum(col):
                enum_val = self.datamodel.get_enum_value(col)
                if isinstance(enum_val, enum.EnumType):
                    return enum_val(value)
                return value
            if self.datamodel.is_string(col):
                return str(value)
            if self.datamodel.is_integer(col):
                return int(value)
            if self.datamodel.is_float(col):
                return float(value)
            if self.datamodel.is_boolean(col):
                return value == 1 or value.lower() in ["true", "1"]
            if self.datamodel.is_date(col):
                return datetime.fromisoformat(value).date()
            if self.datamodel.is_datetime(col):
                return datetime.fromisoformat(value).replace(tzinfo=None)
            return value
        except Exception as e:
            logger.warning(
                f"Failed to cast value {value} to the correct type for column {col}: {e}"
            )
            return value


class GenericFilterTextContains(GenericBaseFilter):
    name = "Text contains"
    arg_name = "tc"

    def apply(self, statement, col, value):
        return statement.text_contains(col, value)


class GenericFilterEqual(GenericBaseFilter):
    name = "Equal to"
    arg_name = "eq"

    def apply(
        self,
        statement,
        col: str,
        value: str | bool | int | date | datetime,
    ):
        value = self._cast_value(col, value)
        return statement.equal(col, value)


class GenericFilterNotEqual(GenericBaseFilter):
    name = "Not Equal to"
    arg_name = "neq"

    def apply(
        self,
        statement,
        col: str,
        value: str | bool | int | date | datetime,
    ):
        value = self._cast_value(col, value)
        return statement.not_equal(col, value)


class GenericFilterStartsWith(GenericBaseFilter):
    name = "Starts with"
    arg_name = "sw"

    def apply(self, statement, col: str, value):
        value = self._cast_value(col, value)
        return statement.starts_with(col, value)


class GenericFilterNotStartsWith(GenericBaseFilter):
    name = "Not Starts with"
    arg_name = "nsw"

    def apply(self, statement, col: str, value):
        value = self._cast_value(col, value)
        return statement.not_starts_with(col, value)


class GenericFilterEndsWith(GenericBaseFilter):
    name = "Ends with"
    arg_name = "ew"

    def apply(self, statement, col: str, value):
        value = self._cast_value(col, value)
        return statement.ends_with(col, value)


class GenericFilterNotEndsWith(GenericBaseFilter):
    name = "Not Ends with"
    arg_name = "new"

    def apply(self, statement, col: str, value):
        value = self._cast_value(col, value)
        return statement.not_ends_with(col, value)


class GenericFilterContains(GenericBaseFilter):
    name = "Contains"
    arg_name = "ct"

    def apply(self, statement, col: str, value):
        value = self._cast_value(col, value)
        return statement.like(col, value)


class GenericFilterIContains(GenericBaseFilter):
    name = "Contains (insensitive)"
    arg_name = "ict"

    def apply(self, statement, col: str, value):
        value = self._cast_value(col, value)
        return statement.ilike(col, value)


class GenericFilterNotContains(GenericBaseFilter):
    name = "Not Contains"
    arg_name = "nct"

    def apply(self, statement, col: str, value):
        value = self._cast_value(col, value)
        return statement.not_like(col, value)


class GenericFilterGreater(GenericBaseFilter):
    name = "Greater than"
    arg_name = "gt"

    def apply(self, statement, col: str, value: int | date | datetime):
        value = self._cast_value(col, value)
        return statement.greater(col, value)


class GenericFilterSmaller(GenericBaseFilter):
    name = "Smaller than"
    arg_name = "lt"

    def apply(self, statement, col: str, value: int | date | datetime):
        value = self._cast_value(col, value)
        return statement.smaller(col, value)


class GenericFilterGreaterEqual(GenericBaseFilter):
    name = "Greater equal"
    arg_name = "ge"

    def apply(self, statement, col: str, value: int | date | datetime):
        value = self._cast_value(col, value)
        return statement.greater_equal(col, value)


class GenericFilterSmallerEqual(GenericBaseFilter):
    name = "Smaller equal"
    arg_name = "le"

    def apply(self, statement, col: str, value: int | date | datetime):
        value = self._cast_value(col, value)
        return statement.smaller_equal(col, value)


class GenericFilterIn(GenericBaseFilter):
    name = "One of"
    arg_name = "in"

    def apply(self, statement, col: str, value: list[str | bool | int]):
        value = self._cast_value(col, value)
        return statement.in_(col, value)


class GenericFilterGlobal(GenericBaseFilter):
    name = "Global Filter"
    arg_name = "global"

    def apply(self, statement, col: str, value: str):
        value = self._cast_value(col, value)
        return statement.global_filter(col, value)


class GenericFilterConverter:
    """
    Helper class to get available filters for a generic column type.
    """

    conversion_table = (
        (
            "is_enum",
            [
                GenericFilterTextContains,
                GenericFilterEqual,
                GenericFilterNotEqual,
                GenericFilterIn,
            ],
        ),
        (
            "is_boolean",
            [GenericFilterEqual, GenericFilterNotEqual, GenericFilterTextContains],
        ),
        (
            "is_text",
            [
                GenericFilterTextContains,
                GenericFilterStartsWith,
                GenericFilterNotStartsWith,
                GenericFilterEndsWith,
                GenericFilterNotEndsWith,
                GenericFilterContains,
                GenericFilterIContains,
                GenericFilterNotContains,
                GenericFilterEqual,
                GenericFilterNotEqual,
                GenericFilterIn,
            ],
        ),
        (
            "is_string",
            [
                GenericFilterTextContains,
                GenericFilterStartsWith,
                GenericFilterNotStartsWith,
                GenericFilterEndsWith,
                GenericFilterNotEndsWith,
                GenericFilterContains,
                GenericFilterIContains,
                GenericFilterNotContains,
                GenericFilterEqual,
                GenericFilterNotEqual,
                GenericFilterIn,
            ],
        ),
        (
            "is_integer",
            [
                GenericFilterTextContains,
                GenericFilterEqual,
                GenericFilterNotEqual,
                GenericFilterGreater,
                GenericFilterSmaller,
                GenericFilterGreaterEqual,
                GenericFilterSmallerEqual,
                GenericFilterIn,
            ],
        ),
        (
            "is_date",
            [
                GenericFilterTextContains,
                GenericFilterEqual,
                GenericFilterNotEqual,
                GenericFilterGreater,
                GenericFilterSmaller,
                GenericFilterGreaterEqual,
                GenericFilterSmallerEqual,
                GenericFilterIn,
            ],
        ),
        (
            "is_datetime",
            [
                GenericFilterTextContains,
                GenericFilterEqual,
                GenericFilterNotEqual,
                GenericFilterGreater,
                GenericFilterSmaller,
                GenericFilterGreaterEqual,
                GenericFilterSmallerEqual,
                GenericFilterIn,
            ],
        ),
    )
