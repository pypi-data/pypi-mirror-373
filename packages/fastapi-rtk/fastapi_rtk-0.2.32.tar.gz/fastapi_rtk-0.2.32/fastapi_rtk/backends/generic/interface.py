import datetime
import typing
from enum import Enum

from pydantic import EmailStr

from ...bases.db import DBQueryParams
from ...bases.interface import AbstractInterface
from ...utils import T, lazy_self
from .column import GenericColumn
from .db import GenericQueryBuilder
from .filters import GenericFilterConverter, GenericFilterGlobal
from .model import GenericModel
from .session import GenericSession

__all__ = ["GenericInterface"]


class lazy(lazy_self["GenericInterface", T]): ...


class GenericInterface(AbstractInterface[GenericModel, GenericSession, GenericColumn]):
    """
    Represents an interface for a Generic model (Based on pydantic).
    """

    # Overloaded attributes
    filter_converter = GenericFilterConverter()
    global_filter_class = GenericFilterGlobal

    # Query builders
    query = lazy(lambda self: GenericQueryBuilder(self, self.session))
    query_count = lazy(lambda self: GenericQueryBuilder(self, self.session))

    def __init__(
        self, obj: typing.Type[GenericModel], session: typing.Type[GenericSession]
    ):
        super().__init__(obj)
        if not isinstance(session, type):
            raise ValueError("session must be a class, do not instantiate it")
        self.session = session

    """
    --------------------------------------------------------------------------------------------------------
        DEPENDENCIES METHODS
    --------------------------------------------------------------------------------------------------------
    """

    def get_session_factory(self):
        return self.session

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
        return statement.count()

    async def get_many(self, session, params=None):
        statement = await self.query.build_query(params)
        return statement.all()

    async def get_one(self, session, params=None):
        statement = await self.query.build_query(params)
        return statement.first()

    async def yield_per(self, session, params=None):
        relevant_params = params.copy() if params else DBQueryParams()
        relevant_params.pop("page", None)
        page_size = relevant_params.pop("page_size", 100)

        statement = await self.query.build_query(relevant_params)
        items = statement.yield_per(page_size)
        while True:
            chunk = items[:page_size]
            items = items[page_size:]
            if not chunk:
                break
            yield chunk

    async def add(self, session, item, *, flush=True, commit=True, refresh=True):
        session.add(item)
        if flush:
            session.flush()
        if commit:
            session.commit()
        if (flush or commit) and refresh:
            session.refresh(item)
        return item

    async def edit(self, session, item, *, flush=True, commit=True, refresh=False):
        result = session.merge(item)
        if flush:
            session.flush()
        if commit:
            session.commit()
        if (flush or commit) and refresh:
            session.refresh(result)
        return result

    async def delete(self, session, item, *, flush=True, commit=True):
        session.delete(item)
        if flush:
            session.flush()
        if commit:
            session.commit()

    """
    --------------------------------------------------------------------------------------------------------
        SESSION METHODS - to be implemented
    --------------------------------------------------------------------------------------------------------
    """

    async def commit(self, session):
        return session.commit()

    async def close(self, session):
        return session.close()

    """
    --------------------------------------------------------------------------------------------------------
        GET METHODS
    --------------------------------------------------------------------------------------------------------
    """

    def get_add_column_list(self):
        return self.get_user_column_list()

    def get_edit_column_list(self):
        return self.get_user_column_list()

    def get_order_column_list(self, list_columns):
        return [x for x in list_columns if x not in self.get_property_column_list()]

    def get_search_column_list(self, list_columns):
        return [
            x
            for x in list_columns
            if x not in self.get_property_column_list()
            and not self.is_pk(x)
            and not self.is_relation(x)
        ]

    def get_type(self, col):
        return self.list_properties[col].col_type

    def get_type_name(self, col) -> str:
        if self.is_string(col):
            return "String"
        if self.is_integer(col):
            return "Integer"
        if self.is_boolean(col):
            return "Boolean"
        if self.is_date(col):
            return "DateTime"
        return "Raw"

    def get_enum_value(self, col_name):
        return self.get_type(col_name)

    """
    --------------------------------------------------------------------------------------------------------
        RELATED MODEL METHODS
    --------------------------------------------------------------------------------------------------------
    """

    def get_related_model(self, col_name):
        if self.is_relation(col_name):
            return self.list_properties[col_name].__class__

        raise ValueError(f"{col_name} is not a relation")

    """
    --------------------------------------------------------------------------------------------------------
        INIT METHODS
    --------------------------------------------------------------------------------------------------------
    """

    def init_list_columns(self):
        return {k: self.list_properties[k] for k in self.obj.__mapper__.columns}

    def init_list_properties(self):
        return self.obj.__mapper__.properties

    """
    --------------------------------------------------------------------------------------------------------
        IS METHODS
    --------------------------------------------------------------------------------------------------------
    """

    def is_pk(self, col_name):
        try:
            return self.list_properties[col_name].primary_key
        except KeyError:
            return False

    def is_nullable(self, col_name):
        try:
            return self.list_properties[col_name].nullable
        except KeyError:
            return False

    def is_unique(self, col_name):
        try:
            return self.list_properties[col_name].unique
        except KeyError:
            return False

    def is_string(self, col_name):
        try:
            return (
                self.list_properties[col_name].col_type is str
                or self.list_properties[col_name].col_type == EmailStr
            )
        except KeyError:
            return False

    def is_text(self, col_name):
        return self.is_string(col_name)

    def is_integer(self, col_name):
        try:
            return self.list_properties[col_name].col_type is int
        except KeyError:
            return False

    def is_numeric(self, col_name):
        return self.is_integer(col_name)

    def is_float(self, col_name):
        return self.is_integer(col_name)

    def is_boolean(self, col_name):
        try:
            return self.list_properties[col_name].col_type is bool
        except KeyError:
            return False

    def is_date(self, col_name):
        try:
            return self.list_properties[col_name].col_type == datetime.date
        except KeyError:
            return False

    def is_datetime(self, col_name):
        try:
            return self.list_properties[col_name].col_type == datetime.datetime
        except KeyError:
            return False

    def is_enum(self, col_name):
        try:
            return self.list_properties[col_name].col_type == Enum
        except KeyError:
            return False

    def is_json(self, col_name):
        try:
            return self.list_properties[col_name].col_type is dict
        except KeyError:
            return False

    def is_jsonb(self, col_name):
        return self.is_json(col_name)

    def is_relation(self, col_name):
        return self.is_relation_one_to_one(col_name) or self.is_relation_one_to_many(
            col_name
        )

    def is_relation_one_to_one(self, col_name):
        try:
            return isinstance(self.list_properties[col_name], GenericModel)
        except KeyError:
            False

    def is_relation_one_to_many(self, col_name):
        try:
            if not isinstance(self.list_properties[col_name], list):
                return False
            for prop in self.list_properties[col_name]:
                if not isinstance(prop, GenericModel):
                    return False
        except KeyError:
            return False

        return True

    def is_relation_many_to_one(self, col_name):
        # TODO: AS OF NOW, cant detect
        return False

    def is_relation_many_to_many(self, col_name):
        # TODO: AS OF NOW, cant detect
        return False

    """
    --------------------------------------------------------------------------------------------------------
        LIFESPAN METHODS
    --------------------------------------------------------------------------------------------------------
    """

    async def on_shutdown(self):
        self.session().save_data()
