import collections
import enum
import json
import typing
from datetime import date, datetime
from typing import Annotated, List, Literal, Type

import fastapi
import marshmallow_sqlalchemy
import sqlalchemy
from pydantic import (
    AfterValidator,
    BeforeValidator,
)
from sqlalchemy import Column
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Session, SynonymProperty, class_mapper
from sqlalchemy.orm.properties import ColumnProperty, RelationshipProperty
from sqlalchemy.sql import sqltypes as sa_types

from ...bases.db import DBQueryParams
from ...bases.interface import AbstractInterface
from ...db import get_session_factory as _get_session_factory
from ...schemas import (
    DatetimeUTC,
)
from ...types import FileColumn, ImageColumn
from ...utils import T, is_sqla_type, lazy_import, lazy_self, safe_call, smart_run
from .db import SQLAQueryBuilder
from .filters import BaseFilter, FilterGlobal, SQLAFilterConverter
from .model import Model

__all__ = ["SQLAInterface"]

if typing.TYPE_CHECKING:
    from .extensions.geoalchemy2 import GeometryConverter


class lazy(lazy_self["SQLAInterface", T]): ...


class SQLAInterface(AbstractInterface[Model, Session | AsyncSession, Column]):
    """
    Datamodel interface for SQLAlchemy models.
    """

    filter_converter = SQLAFilterConverter()
    global_filter_class = FilterGlobal

    # Query builders
    query = lazy(lambda self: SQLAQueryBuilder(self, sqlalchemy.select(self.obj)))
    query_count = lazy(
        lambda self: SQLAQueryBuilder(
            self, sqlalchemy.select(sqlalchemy.func.count()).select_from(self.obj)
        )
    )
    geometry_converter: "GeometryConverter" = lazy_import(
        "fastapi_rtk.backends.sqla.extensions.geoalchemy2",
        lambda mod: mod.GeometryConverter(),
    )

    _cache_field: dict[str, str] = {}
    """
    Internal cache for column types and names.
    """

    """
    --------------------------------------------------------------------------------------------------------
        DEPENDENCIES METHODS
    --------------------------------------------------------------------------------------------------------
    """

    def get_session_factory(self):
        return _get_session_factory(getattr(self.obj, "__bind_key__", None))

    """
    --------------------------------------------------------------------------------------------------------
        COUNT AND CRUD METHODS
    --------------------------------------------------------------------------------------------------------
    """

    async def count(self, session, params=None):
        relevant_params = params.copy() if params else DBQueryParams()
        relevant_params.pop("list_columns", None)
        relevant_params.pop("page", None)
        relevant_params.pop("page_size", None)
        relevant_params.pop("order_column", None)
        relevant_params.pop("order_direction", None)

        statement = await self.query_count.build_query(relevant_params)
        result = await smart_run(session.scalars, statement)
        return result.one()

    async def get_many(self, session, params=None):
        statement = await self.query.build_query(params)
        result = await smart_run(session.scalars, statement)
        return list(result.all())

    async def get_one(self, session, params=None):
        statement = await self.query.build_query(params)
        result = await smart_run(session.scalars, statement)
        return result.first()

    async def yield_per(self, session, params=None):
        relevant_params = params.copy() if params else DBQueryParams()
        relevant_params.pop("page", None)
        page_size = relevant_params.pop("page_size", 100)

        statement = await self.query.build_query(relevant_params)
        statement = statement.execution_options(stream_results=True)
        if isinstance(session, AsyncSession):
            result = await session.stream(statement)
            result = result.scalars()
        else:
            result = session.scalars(statement)
        while True:
            chunk = await smart_run(result.fetchmany, page_size)
            if not chunk:
                break
            yield chunk
        await safe_call(self.close(session))

    async def add(self, session, item, *, flush=True, commit=True, refresh=True):
        await smart_run(session.add, item)
        if flush:
            await smart_run(session.flush)
        if commit:
            await smart_run(session.commit)
        if (flush or commit) and refresh:
            await smart_run(session.refresh, item)
        return item

    async def edit(self, session, item, *, flush=True, commit=True, refresh=False):
        result: Model = await smart_run(session.merge, item)
        if flush:
            await smart_run(session.flush)
        if commit:
            await smart_run(session.commit)
        if (flush or commit) and refresh:
            await smart_run(session.refresh, result)
        return result

    async def delete(self, session, item, *, flush=True, commit=True):
        await smart_run(session.delete, item)
        if flush:
            await smart_run(session.flush)
        if commit:
            await smart_run(session.commit)

    """
    --------------------------------------------------------------------------------------------------------
        SESSION METHODS - to be implemented
    --------------------------------------------------------------------------------------------------------
    """

    async def commit(self, session):
        return await smart_run(session.commit)

    async def close(self, session):
        return await smart_run(session.close)

    """
    --------------------------------------------------------------------------------------------------------
        GET METHODS
    --------------------------------------------------------------------------------------------------------
    """

    def get_add_column_list(self):
        return self.get_user_column_list()

    def get_edit_column_list(self):
        return self.get_user_column_list()

    def get_order_column_list(self, list_columns: List[str], *, depth=0, max_depth=-1):
        """
        Get all columns that can be used for ordering

        Args:
            list_columns (List[str]): Columns to be used for ordering.
            depth (int, optional): Depth of the relation. Defaults to 0. Used for recursive calls.
            max_depth (int, optional): Maximum depth of the relation. When set to -1, it will be ignored. Defaults to -1.

        Returns:
            List[str]: List of columns that can be used for ordering
        """
        unique_order_columns: set[str] = set()
        for col_name in list_columns:
            # Split the column name into the main column and sub-column if it is a relation
            if "." in col_name:
                col_name, sub_col_name = col_name.split(".", 1)
            else:
                sub_col_name = ""

            if self.is_relation(col_name):
                # Ignore relations that are one-to-many or many-to-many since ordering is not possible
                if (
                    (max_depth != -1 and depth >= max_depth)
                    or self.is_relation_one_to_many(col_name)
                    or self.is_relation_many_to_many(col_name)
                ):
                    continue

                # Get the related interface and its order columns for the sub-column
                if sub_col_name:
                    related_interface = self.get_related_interface(col_name)
                    sub_order_columns = related_interface.get_order_column_list(
                        [sub_col_name], depth=depth + 1, max_depth=max_depth
                    )
                    if sub_col_name:
                        sub_order_columns = [
                            x for x in sub_order_columns if x == sub_col_name
                        ]
                    unique_order_columns.update(
                        [f"{col_name}.{sub_col}" for sub_col in sub_order_columns]
                    )
            elif self.is_property(col_name) and not self.is_hybrid_property(col_name):
                continue

            # Allow the column to be used for ordering by default
            unique_order_columns.add(col_name)

        # Only take the columns that are in the list_columns
        result = [x for x in unique_order_columns if x in list_columns]

        # Order our result by the order of the list_columns
        return sorted(result, key=lambda x: list_columns.index(x))

    def get_search_column_list(self, list_columns):
        unique_search_columns: set[str] = set()
        for col_name in list_columns:
            # Split the column name into the main column and sub-column if it is a relation
            if "." in col_name:
                col_name, sub_col_name = col_name.split(".", 1)
            else:
                sub_col_name = ""

            if self.is_relation(col_name):
                # Get the related interface and its search columns for the sub-column
                if sub_col_name:
                    related_interface = self.get_related_interface(col_name)
                    sub_search_columns = related_interface.get_search_column_list(
                        [sub_col_name]
                    )
                    if sub_col_name:
                        sub_search_columns = [
                            x for x in sub_search_columns if x == sub_col_name
                        ]
                    unique_search_columns.update(
                        [f"{col_name}.{sub_col}" for sub_col in sub_search_columns]
                    )
            elif self.is_property(col_name) and not self.is_hybrid_property(col_name):
                continue

            # Allow the column to be used for searching by default
            unique_search_columns.add(col_name)

        # Only take the columns that are in the list_columns and only has 1 dot in it
        result = [
            x for x in unique_search_columns if x in list_columns and x.count(".") <= 1
        ]

        # Order our result by the order of the list_columns
        return sorted(result, key=lambda x: list_columns.index(x))

    def get_file_column_list(self):
        return [
            i.name
            for i in self.obj.__mapper__.columns
            if isinstance(i.type, FileColumn)
        ]

    def get_image_column_list(self):
        return [
            i.name
            for i in self.obj.__mapper__.columns
            if isinstance(i.type, ImageColumn)
        ]

    def get_type(self, col):
        if self.is_enum(col):
            col_type = None
            enum_val = self.get_enum_value(col)
            enum_values = list(enum_val)

            for val in enum_values:
                new_val = Literal[val]
                if isinstance(val, enum.Enum):
                    value_type = type(val.value)
                    new_val = (
                        new_val
                        | Annotated[
                            Literal[str(val.value)],
                            AfterValidator(lambda x: enum_val(value_type(x))),
                        ]
                    )
                if col_type is None:
                    col_type = new_val
                else:
                    col_type = col_type | new_val
            return col_type
        elif self.is_geometry(col):
            geo_col = self.list_columns[col]

            return Annotated[
                dict[str, typing.Any] | str,
                BeforeValidator(
                    self.geometry_converter.two_way_converter_generator(
                        geo_col.type.geometry_type
                    )
                ),
            ]
        elif self.is_file(col) or self.is_image(col):
            return (
                fastapi.UploadFile
                | typing.Annotated[
                    str | None, BeforeValidator(lambda x: None if x == "null" else x)
                ]
            )
        elif self.is_date(col):
            return date
        elif self.is_datetime(col):
            return DatetimeUTC | datetime
        elif self.is_text(col) or self.is_string(col):
            return str
        elif (
            self.is_integer(col_name=col) or self.is_numeric(col) or self.is_float(col)
        ):
            return int | float
        elif self.is_boolean(col):
            return bool
        elif self.is_json or self.is_jsonb(col):
            #! At the bottom, because everything is a subclass of the JSON type

            def validator_func(data):
                try:
                    return json.loads(data)
                except Exception:
                    return data

            return typing.Annotated[
                typing.Any,
                AfterValidator(validator_func),
            ]
        elif self.is_relation(col_name=col):
            raise Exception(
                f"Column '{col}' is a relation. Use 'get_relation_type' instead."
            )
        else:
            return typing.Any

    def get_type_name(self, col):
        cache_key = f"{self.obj.__name__}.{col}"
        if not self._cache_field.get(cache_key):
            try:
                # Check for geometry
                if self.is_geometry(col):
                    self._cache_field[cache_key] = "Geometry"
                elif self.is_enum(col):
                    self._cache_field[cache_key] = "Enum"
                elif self.is_hybrid_property(col):
                    self._cache_field[cache_key] = marshmallow_sqlalchemy.column2field(
                        Column(
                            col, getattr(self.obj, col).expression.type, nullable=True
                        )
                    ).__class__.__name__
                else:
                    self._cache_field[cache_key] = marshmallow_sqlalchemy.field_for(
                        self.obj, col
                    ).__class__.__name__
            except Exception:
                self._cache_field[cache_key] = "Unknown"
        return self._cache_field[cache_key]

    def get_enum_value(self, col_name) -> enum.EnumType | list[str]:
        col_type = self.list_columns[col_name].type
        if isinstance(col_type.python_type, enum.EnumType):
            return col_type.python_type
        return col_type.enums

    """
    --------------------------------------------------------------------------------------------------------
        RELATED MODEL METHODS
    --------------------------------------------------------------------------------------------------------
    """

    def get_related_model(self, col_name) -> typing.Type[Model]:
        return self.list_properties[col_name].mapper.class_

    """
    --------------------------------------------------------------------------------------------------------
        INIT METHODS
    --------------------------------------------------------------------------------------------------------
    """

    def init_list_columns(self):
        result = dict[str, Column]()
        for col_name in self.obj.__mapper__.columns.keys():
            if col_name in self.list_properties:
                result[col_name] = self.obj.__mapper__.columns[col_name]

        return result

    def init_list_properties(self):
        result = dict[str, Column]()
        for prop in class_mapper(self.obj).iterate_properties:
            if type(prop) is not SynonymProperty:
                result[prop.key] = prop

        return result

    """
    --------------------------------------------------------------------------------------------------------
        IS METHODS
    --------------------------------------------------------------------------------------------------------
    """

    def is_pk_composite(self):
        return len(self.obj.__mapper__.primary_key) > 1

    def is_pk(self, col_name):
        try:
            return self.list_columns[col_name].primary_key
        except KeyError:
            return False

    def is_fk(self, col_name):
        try:
            return self.list_columns[col_name].foreign_keys
        except KeyError:
            return False

    def is_nullable(self, col_name):
        if self.is_relation_many_to_one(col_name):
            col = self.get_relation_fk(col_name)
            return col.nullable
        elif self.is_relation_many_to_many(col_name) or self.is_relation_one_to_many(
            col_name
        ):
            return True
        try:
            return self.list_columns[col_name].nullable
        except KeyError:
            return False

    def is_unique(self, col_name):
        try:
            return self.list_columns[col_name].unique is True
        except KeyError:
            return False

    def is_image(self, col_name):
        try:
            return is_sqla_type(self.list_columns[col_name].type, ImageColumn)
        except KeyError:
            return False

    def is_file(self, col_name):
        try:
            return is_sqla_type(self.list_columns[col_name].type, FileColumn)
        except KeyError:
            return False

    def is_string(self, col_name):
        try:
            return is_sqla_type(
                self.list_columns[col_name].type, sa_types.String
            ) or is_sqla_type(self.list_columns[col_name].type, sa_types.UUID)
        except KeyError:
            return False

    def is_text(self, col_name):
        try:
            return is_sqla_type(self.list_columns[col_name].type, sa_types.Text)
        except KeyError:
            return False

    def is_binary(self, col_name):
        try:
            return is_sqla_type(self.list_columns[col_name].type, sa_types.LargeBinary)
        except KeyError:
            return False

    def is_integer(self, col_name):
        try:
            return is_sqla_type(self.list_columns[col_name].type, sa_types.Integer)
        except KeyError:
            return False

    def is_numeric(self, col_name):
        try:
            return is_sqla_type(self.list_columns[col_name].type, sa_types.Numeric)
        except KeyError:
            return False

    def is_float(self, col_name):
        try:
            return is_sqla_type(self.list_columns[col_name].type, sa_types.Float)
        except KeyError:
            return False

    def is_boolean(self, col_name):
        try:
            return is_sqla_type(self.list_columns[col_name].type, sa_types.Boolean)
        except KeyError:
            return False

    def is_date(self, col_name):
        try:
            return is_sqla_type(self.list_columns[col_name].type, sa_types.Date)
        except KeyError:
            return False

    def is_datetime(self, col_name):
        try:
            return is_sqla_type(self.list_columns[col_name].type, sa_types.DateTime)
        except KeyError:
            return False

    def is_enum(self, col_name):
        try:
            return is_sqla_type(self.list_columns[col_name].type, sa_types.Enum)
        except KeyError:
            return False

    def is_json(self, col_name):
        try:
            return is_sqla_type(self.list_columns[col_name].type, sa_types.JSON)
        except KeyError:
            return False

    def is_jsonb(self, col_name):
        try:
            return is_sqla_type(self.list_columns[col_name].type, postgresql.JSONB)
        except KeyError:
            return False

    def is_relation(self, col_name):
        try:
            return isinstance(self.list_properties[col_name], RelationshipProperty)
        except KeyError:
            return False

    def is_relation_one_to_one(self, col_name):
        try:
            if self.is_relation(col_name):
                relation = self.list_properties[col_name]
                return self.list_properties[col_name].direction.name == "ONETOONE" or (
                    relation.direction.name == "ONETOMANY" and relation.uselist is False
                )
            return False
        except KeyError:
            return False

    def is_relation_one_to_many(self, col_name):
        try:
            if self.is_relation(col_name):
                relation = self.list_properties[col_name]
                return relation.direction.name == "ONETOMANY" and relation.uselist
            return False
        except KeyError:
            return False

    def is_relation_many_to_one(self, col_name):
        try:
            if self.is_relation(col_name):
                return self.list_properties[col_name].direction.name == "MANYTOONE"
            return False
        except KeyError:
            return False

    def is_relation_many_to_many(self, col_name):
        try:
            if self.is_relation(col_name):
                relation = self.list_properties[col_name]
                return relation.direction.name == "MANYTOMANY"
            return False
        except KeyError:
            return False

    def get_max_length(self, col_name):
        try:
            if self.is_enum(col_name):
                return -1
            col = self.list_columns[col_name]
            if col.type.length:
                return col.type.length
            else:
                return -1
        except Exception:
            return -1

    """
    --------------------------------------------------------------------------------------------------------
        OVERLOADED METHODS - EXTRA LOGIC NEEDED FOR SQLAINTERFACE
    --------------------------------------------------------------------------------------------------------
    """

    def init_filters(self):
        result = collections.defaultdict[str, list[BaseFilter]](list)
        for col in self.list_properties.keys():
            for func_attr, filters in self.filter_converter.conversion_table:
                if getattr(self, func_attr)(col):
                    result[col] = [f(self) for f in filters]
                    break

        for col in self.get_property_column_list():
            if self.is_hybrid_property(col):
                self.list_columns[col] = Column(
                    col, getattr(self.obj, col).expression.type, nullable=True
                )
                try:
                    for func_attr, filters in self.filter_converter.conversion_table:
                        if getattr(self, func_attr)(col):
                            result[col] = [f(self) for f in filters]
                            break
                finally:
                    del self.list_columns[col]

        return result

    """
    --------------------------------------------------------------------------------------------------------
        SQLA RELATED METHODS - ONLY IN SQLAInterface
    --------------------------------------------------------------------------------------------------------
    """

    def get_related_fk(self, model: Type[Model]):
        for col_name in self.list_properties.keys():
            if self.is_relation(col_name):
                if model == self.get_related_model(col_name):
                    return col_name
        return None

    def get_related_fks(self):
        return [
            self.get_related_fk(model)
            for model in self.list_properties.values()
            if self.is_relation(model)
        ]

    def get_fk_column(self, relationship_name: str) -> str:
        """
        Get the foreign key column for the specified relationship.

        Args:
            relationship_name (str): The name of the relationship.

        Raises:
            Exception: If no foreign key is found for the specified relationship.

        Returns:
            str: The name of the foreign key column.
        """
        # Get the relationship property from the model's mapper
        relationship_prop = class_mapper(self.obj).relationships[relationship_name]

        # Iterate through the columns involved in the relationship
        for local_column, _ in relationship_prop.local_remote_pairs:
            # Check if the local column is the foreign key
            if local_column.foreign_keys:
                return local_column.name

        raise Exception(
            f"No foreign key found for relationship '{relationship_name}' in model '{self.obj.__name__}'."
        )

    def get_info(self, col_name: str):
        if col_name in self.list_properties:
            return self.list_properties[col_name].info
        return {}

    def get_property_first_col(self, col_name: str) -> ColumnProperty:
        # support for only one col for pk and fk
        return self.list_properties[col_name].columns[0]

    def get_relation_fk(self, col_name: str) -> Column:
        # support for only one col for pk and fk
        return list(self.list_properties[col_name].local_columns)[0]

    def is_hybrid_property(self, col_name: str) -> bool:
        try:
            attr = getattr(self.obj, col_name)
            descriptor = getattr(attr, "descriptor")
            return isinstance(descriptor, hybrid_property)
        except AttributeError:
            return False

    def is_geometry(self, col_name: str) -> bool:
        try:
            from geoalchemy2 import Geometry

            return is_sqla_type(self.list_columns[col_name].type, Geometry)
        except KeyError:
            return False
        except ImportError:
            return False

    def is_relation_many_to_many_special(self, col_name: str) -> bool:
        try:
            if self.is_relation(col_name):
                relation = self.list_properties[col_name]
                return relation.direction.name == "ONETOONE" and relation.uselist
            return False
        except KeyError:
            return False
