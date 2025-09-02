import enum
import typing
from datetime import datetime

import sqlalchemy
import sqlalchemy.types as sa_types
from fastapi import HTTPException
from sqlalchemy import Column, Select, and_, cast, func, or_, select

from ...bases.filter import AbstractBaseFilter
from ...const import logger
from .model import Model

__all__ = [
    "BaseFilter",
    "BaseFilterTextContains",
    "BaseFilterRelationOneToOneOrManyToOne",
    "BaseFilterRelationOneToManyOrManyToMany",
    "FilterTextContains",
    "FilterEqual",
    "FilterNotEqual",
    "FilterStartsWith",
    "FilterNotStartsWith",
    "FilterEndsWith",
    "FilterNotEndsWith",
    "FilterContains",
    "FilterNotContains",
    "FilterGreater",
    "FilterSmaller",
    "FilterGreaterEqual",
    "FilterSmallerEqual",
    "FilterIn",
    "FilterBetween",
    "FilterRelationOneToOneOrManyToOneEqual",
    "FilterRelationOneToOneOrManyToOneNotEqual",
    "FilterRelationOneToManyOrManyToManyIn",
    "FilterRelationOneToManyOrManyToManyNotIn",
    "FilterGlobal",
    "SQLAFilterConverter",
]


class BaseFilter(AbstractBaseFilter[Select[Model]]):
    def _get_column(self, col_name: str) -> Column:
        """
        Get the column from the datamodel object.

        Args:
            col_name (str): The name of the column to get.

        Returns:
            Column: The column from the datamodel object.
        """
        return getattr(self.datamodel.obj, col_name)

    def _cast_col_and_value(self, col: str, value: typing.Any):
        """
        Cast the column and value to the correct type.

        Args:
            col (str): The column name.
            value (typing.Any): The value to cast.

        Returns:
            Tuple[Column, typing.Any]: A tuple containing the column and value casted to the correct type.
        """
        cast_col = self._cast_column(col, value)
        cast_value = self._cast_value(col, value)
        return cast_col, cast_value

    def _cast_column(self, col: str, value=None):
        """
        Get the column and cast it to the correct type.

        Args:
            col (str): The column name.
            value (Any, optional): The value to cast. Defaults to None.

        Returns:
            Column: The column casted to the correct type.
        """
        col_obj = self._get_column(col)
        try:
            if self.datamodel.is_jsonb(col):
                return cast(col_obj, sa_types.String)
            return col_obj
        except Exception:
            return col_obj

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


class BaseFilterTextContains(BaseFilter):
    def _handle_relation_contains(self, col: str, value: str):
        sub_col = ""
        if "." in col:
            col, sub_col = col.split(".", 1)
        rel_interface = self.datamodel.get_related_interface(col)
        filter = (
            getattr(self.datamodel.obj, col).any
            if self.datamodel.is_relation_one_to_many(col)
            or self.datamodel.is_relation_many_to_many(col)
            else getattr(self.datamodel.obj, col).has
        )
        if sub_col:
            # If it is a relation, recursively filter it through the related interface
            if "." in sub_col:
                return filter(
                    self.__class__(rel_interface)._handle_relation_contains(
                        sub_col, value
                    )
                )
            else:
                # Otherwise, we filter only the sub-column
                rel_cols = [sub_col]
        else:
            # If there is no sub-column, we filter all columns in the relation
            rel_cols = rel_interface.list_columns.keys()
        concat = []
        rel_obj = rel_interface.obj
        rel_pks = rel_interface.get_pk_attrs()
        for col_name in rel_cols:
            col_obj = getattr(rel_obj, col_name)
            concat.append(sqlalchemy.cast(col_obj, sa_types.String))
            concat.append(" ")
        rel_statements = [
            select(getattr(rel_obj, pk)).filter(
                func.concat(*concat).ilike("%" + value + "%")
            )
            for pk in rel_pks
        ]
        rel_statements = [
            getattr(rel_obj, pk).in_(statement)
            for pk, statement in zip(rel_pks, rel_statements)
        ]
        return filter(*rel_statements)

    def _handle_text_contains(self, col: str, value: str):
        """
        Handle text contains for a column.

        Args:
            col (str): The column name.
            value (str): The value to filter by.

        Returns:
            sqlalchemy.sql.elements.BinaryExpression: The SQLAlchemy expression for the filter.
        """
        value = value.strip().lower()
        if self.datamodel.is_relation(col) or "." in col:
            return self._handle_relation_contains(col, value)
        elif self.datamodel.is_boolean(col):
            true_keywords = ["true", "1"]
            false_keywords = ["false", "0"]
            if any(value in keywords for keywords in true_keywords + false_keywords):
                return self._get_column(col).is_(
                    True
                    if any(value in keywords for keywords in true_keywords)
                    else False
                )
        return cast(self._cast_column(col), sa_types.String).ilike("%" + value + "%")


class BaseFilterRelationOneToOneOrManyToOne(BaseFilter):
    def _get_rel_value(self, col: str, value: typing.Any):
        if isinstance(value, Model):
            return value
        rel_interface = self.datamodel.get_related_interface(col)
        pk_attrs = rel_interface.get_pk_attrs()
        if isinstance(value, str):
            value = value.split(",")
        elif not isinstance(value, list):
            value = [value]

        new_value = {}
        for pk_attr in pk_attrs:
            new_value[pk_attr] = value.pop(0)
        datamodel = self.datamodel
        try:
            self.datamodel = rel_interface
            statements = [
                self._get_column(pk_attr) == self._cast_value(pk_attr, val)
                for pk_attr, val in new_value.items()
            ]
        finally:
            self.datamodel = datamodel
        return and_(*statements)


class BaseFilterRelationOneToManyOrManyToMany(BaseFilterRelationOneToOneOrManyToOne):
    def _get_rel_value(self, col: str, value: typing.Any):
        if not isinstance(value, list):
            value = [value]

        if all(isinstance(val, Model) for val in value):
            return value

        return [super()._get_rel_value(col, val) for val in value]


class FilterTextContains(BaseFilterTextContains):
    name = "Text contains"
    arg_name = "tc"

    def apply(self, statement, col: str, value):
        from ...setting import Setting

        SEPARATOR = Setting.TEXT_FILTER_SEPARATOR
        value = [v for v in value.split(SEPARATOR) if v]
        filters = []

        for val in value:
            filters.append(self._handle_text_contains(col, val))
        return statement.filter(and_(*filters))


class FilterEqual(BaseFilter):
    name = "Equal to"
    arg_name = "eq"

    def apply(self, statement, col: str, value):
        col, value = self._cast_col_and_value(col, value)
        return statement.filter(col == value)


class FilterNotEqual(BaseFilter):
    name = "Not Equal to"
    arg_name = "neq"

    def apply(self, statement, col: str, value):
        col, value = self._cast_col_and_value(col, value)
        return statement.filter(col != value)


class FilterStartsWith(BaseFilter):
    name = "Starts with"
    arg_name = "sw"

    def apply(self, statement, col: str, value):
        col, value = self._cast_col_and_value(col, value)
        return statement.filter(col.ilike(value + "%"))


class FilterNotStartsWith(BaseFilter):
    name = "Not Starts with"
    arg_name = "nsw"

    def apply(self, statement, col: str, value):
        col, value = self._cast_col_and_value(col, value)
        return statement.filter(~col.ilike(value + "%"))


class FilterEndsWith(BaseFilter):
    name = "Ends with"
    arg_name = "ew"

    def apply(self, statement, col: str, value):
        col, value = self._cast_col_and_value(col, value)
        return statement.filter(col.ilike("%" + value))


class FilterNotEndsWith(BaseFilter):
    name = "Not Ends with"
    arg_name = "new"

    def apply(self, statement, col: str, value):
        col, value = self._cast_col_and_value(col, value)
        return statement.filter(~col.ilike("%" + value))


class FilterContains(BaseFilter):
    name = "Contains"
    arg_name = "ct"

    def apply(self, statement, col: str, value):
        col, value = self._cast_col_and_value(col, value)
        return statement.filter(col.ilike("%" + value + "%"))


class FilterNotContains(BaseFilter):
    name = "Not Contains"
    arg_name = "nct"

    def apply(self, statement, col: str, value):
        col, value = self._cast_col_and_value(col, value)
        return statement.filter(~col.ilike("%" + value + "%"))


class FilterGreater(BaseFilter):
    name = "Greater than"
    arg_name = "gt"

    def apply(self, statement, col: str, value):
        col, value = self._cast_col_and_value(col, value)
        return statement.filter(col > value)


class FilterSmaller(BaseFilter):
    name = "Smaller than"
    arg_name = "lt"

    def apply(self, statement, col: str, value):
        col, value = self._cast_col_and_value(col, value)
        return statement.filter(col < value)


class FilterGreaterEqual(BaseFilter):
    name = "Greater equal"
    arg_name = "ge"

    def apply(self, statement, col: str, value):
        col, value = self._cast_col_and_value(col, value)
        return statement.filter(col >= value)


class FilterSmallerEqual(BaseFilter):
    name = "Smaller equal"
    arg_name = "le"

    def apply(self, statement, col: str, value):
        col, value = self._cast_col_and_value(col, value)
        return statement.filter(col <= value)


class FilterIn(BaseFilter):
    name = "One of"
    arg_name = "in"

    def apply(self, statement, col: str, value):
        col, value = self._cast_col_and_value(col, value)
        return statement.filter(col.in_(value))


class FilterBetween(BaseFilter):
    name = "Between"
    arg_name = "bw"

    def apply(self, statement, col: str, value):
        if not value:
            return statement

        if len(value) != 2:
            raise HTTPException(400, "Between filter requires two values")

        value = [self._cast_value(col, v) for v in value]
        if value[0] is None or value[1] is None:
            return statement

        col = self._cast_column(col, value)
        return statement.filter(col.between(value[0], value[1]))


class FilterRelationOneToOneOrManyToOneEqual(
    BaseFilterRelationOneToOneOrManyToOne, FilterEqual
):
    arg_name = "rel_o_m"

    def apply(self, statement, col: str, value):
        if not value:
            return statement

        rel_val = self._get_rel_value(col, value)
        if isinstance(rel_val, Model):
            return super().apply(statement, col, rel_val)
        col = self._get_column(col)
        return statement.filter(col.has(rel_val))


class FilterRelationOneToOneOrManyToOneNotEqual(
    BaseFilterRelationOneToOneOrManyToOne, FilterNotEqual
):
    arg_name = "nrel_o_m"

    def apply(self, statement, col: str, value):
        if not value:
            return statement

        rel_val = self._get_rel_value(col, value)
        if isinstance(rel_val, Model):
            return super().apply(statement, col, rel_val)
        col = self._get_column(col)
        return statement.filter(~col.has(rel_val))


class FilterRelationOneToManyOrManyToManyIn(BaseFilterRelationOneToManyOrManyToMany):
    name = "In"
    arg_name = "rel_m_m"

    def apply(self, statement, col: str, value):
        if not value:
            return statement

        rel_val = self._get_rel_value(col, value)
        col = self._get_column(col)
        for val in rel_val:
            if isinstance(val, Model):
                statement = statement.filter(col.contains(val))
            else:
                statement = statement.filter(col.any(val))
        return statement


class FilterRelationOneToManyOrManyToManyNotIn(BaseFilterRelationOneToManyOrManyToMany):
    name = "Not In"
    arg_name = "nrel_m_m"

    def apply(self, statement, col: str, value):
        if not value:
            return statement

        rel_val = self._get_rel_value(col, value)
        col = self._get_column(col)
        for val in rel_val:
            if isinstance(val, Model):
                statement = statement.filter(col.contains(val))
            else:
                statement = statement.filter(~col.any(val))
        return statement


class FilterGlobal(BaseFilterTextContains):
    name = "Global Filter"
    arg_name = "global"

    def apply(self, statement, cols: list[str], value):
        from ...setting import Setting

        SEPARATOR = Setting.TEXT_FILTER_SEPARATOR
        value = [v for v in value.split(SEPARATOR) if v]
        filters = []

        for val in value:
            concat_arr = []
            rel_filter_arr = []
            for col in cols:
                if (
                    self.datamodel.is_relation(col)
                    or "." in col
                    or self.datamodel.is_boolean(col)
                ):
                    rel_filter_arr.append(self._handle_text_contains(col, val))
                elif col in self.datamodel.list_columns:
                    concat_arr.extend(
                        [cast(self._cast_column(col), sa_types.String), " "]
                    )
            params = [*rel_filter_arr]
            if concat_arr:
                val = val.strip().lower()
                params.append(func.concat(*concat_arr).ilike("%" + val + "%"))
            filters.append(or_(*params))
        return statement.filter(and_(*filters))


class SQLAFilterConverter:
    """
    Helper class to get available filters for a column type.
    """

    conversion_table = (
        (
            "is_relation_one_to_one",
            [
                FilterRelationOneToOneOrManyToOneEqual,
                FilterRelationOneToOneOrManyToOneNotEqual,
                FilterTextContains,
            ],
        ),
        (
            "is_relation_many_to_one",
            [
                FilterRelationOneToOneOrManyToOneEqual,
                FilterRelationOneToOneOrManyToOneNotEqual,
                FilterTextContains,
            ],
        ),
        (
            "is_relation_one_to_many",
            [
                FilterRelationOneToManyOrManyToManyIn,
                FilterRelationOneToManyOrManyToManyNotIn,
                FilterTextContains,
            ],
        ),
        (
            "is_relation_many_to_many",
            [
                FilterRelationOneToManyOrManyToManyIn,
                FilterRelationOneToManyOrManyToManyNotIn,
                FilterTextContains,
            ],
        ),
        (
            "is_enum",
            [
                FilterTextContains,
                FilterEqual,
                FilterNotEqual,
                FilterIn,
            ],
        ),
        (
            "is_boolean",
            [
                FilterEqual,
                FilterNotEqual,
                FilterTextContains,
            ],
        ),
        (
            "is_text",
            [
                FilterTextContains,
                FilterEqual,
                FilterNotEqual,
                FilterStartsWith,
                FilterNotStartsWith,
                FilterEndsWith,
                FilterNotEndsWith,
                FilterContains,
                FilterNotContains,
                FilterIn,
            ],
        ),
        (
            "is_binary",
            [
                FilterTextContains,
                FilterEqual,
                FilterNotEqual,
                FilterStartsWith,
                FilterNotStartsWith,
                FilterEndsWith,
                FilterNotEndsWith,
                FilterContains,
                FilterNotContains,
                FilterIn,
            ],
        ),
        (
            "is_string",
            [
                FilterTextContains,
                FilterEqual,
                FilterNotEqual,
                FilterStartsWith,
                FilterNotStartsWith,
                FilterEndsWith,
                FilterNotEndsWith,
                FilterContains,
                FilterNotContains,
                FilterIn,
            ],
        ),
        (
            "is_json",
            [
                FilterTextContains,
                FilterEqual,
                FilterNotEqual,
                FilterStartsWith,
                FilterNotStartsWith,
                FilterEndsWith,
                FilterNotEndsWith,
                FilterContains,
                FilterNotContains,
                FilterIn,
            ],
        ),
        (
            "is_integer",
            [
                FilterBetween,
                FilterTextContains,
                FilterEqual,
                FilterNotEqual,
                FilterGreater,
                FilterSmaller,
                FilterGreaterEqual,
                FilterSmallerEqual,
                FilterIn,
            ],
        ),
        (
            "is_float",
            [
                FilterBetween,
                FilterTextContains,
                FilterEqual,
                FilterNotEqual,
                FilterGreater,
                FilterSmaller,
                FilterGreaterEqual,
                FilterSmallerEqual,
                FilterIn,
            ],
        ),
        (
            "is_numeric",
            [
                FilterBetween,
                FilterTextContains,
                FilterEqual,
                FilterNotEqual,
                FilterGreater,
                FilterSmaller,
                FilterGreaterEqual,
                FilterSmallerEqual,
                FilterIn,
            ],
        ),
        (
            "is_date",
            [
                FilterBetween,
                FilterTextContains,
                FilterEqual,
                FilterNotEqual,
                FilterGreater,
                FilterSmaller,
                FilterGreaterEqual,
                FilterSmallerEqual,
                FilterIn,
            ],
        ),
        (
            "is_datetime",
            [
                FilterBetween,
                FilterTextContains,
                FilterEqual,
                FilterNotEqual,
                FilterGreater,
                FilterSmaller,
                FilterGreaterEqual,
                FilterSmallerEqual,
                FilterIn,
            ],
        ),
    )
