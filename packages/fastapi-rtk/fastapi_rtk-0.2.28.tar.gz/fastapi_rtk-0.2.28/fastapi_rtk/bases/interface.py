import abc
import asyncio
import collections
import enum
import inspect
import typing

import pydantic

from ..exceptions import raise_exception
from ..globals import g
from ..schemas import PRIMARY_KEY, ColumnEnumInfo, ColumnInfo, ColumnRelationInfo
from ..utils import AsyncTaskRunner, C, T, deep_merge, lazy_self, smart_run
from .db import DBQueryParams
from .filter import AbstractBaseFilter

CT = typing.TypeVar("CT")

filter_converter_type = None

if typing.TYPE_CHECKING:
    from ..backends.sqla.filters import SQLAFilterConverter

    filter_converter_type = SQLAFilterConverter


class PydanticGenerationSchema(typing.TypedDict):
    """
    Schema for generating Pydantic models.
    """

    __config__: pydantic.ConfigDict
    __async_columns__: list[str]
    __columns__: list[str] | None
    __with_id__: bool
    __with_name__: bool
    __with_property__: bool
    __optional__: bool
    __hide_sensitive_columns__: bool
    __with_fk__: bool
    __name__: str | None

    id_: tuple[type[PRIMARY_KEY], pydantic.Field] | None
    name_: tuple[type[str], pydantic.Field] | None


class lazy(lazy_self["AbstractInterface", T]): ...


class AbstractInterface(abc.ABC, typing.Generic[T, C, CT]):
    """
    Abstract base class for datamodel interfaces.

    This class provides a common interface for interacting with data models, including methods for CRUD operations, schema generation, and type checking.

    Type parameters:
    - T: The type of the model being interfaced with.
    - C: The type of the session (e.g., SQLAlchemy Session or AsyncSession).
    - CT: The type of the columns or properties in the model (e.g., SQLAlchemy Column).

    Example usage:
    ```python

    class SQLAInterface(AbstractInterface[Model, Session | AsyncSession, Column]):
        # Implementation of the SQLAInterface class
    ```
    """

    filter_converter = lazy(
        lambda: raise_exception(
            "filter_converter must be set in the subclass", filter_converter_type
        )
    )
    global_filter_class = lazy(
        lambda: raise_exception(
            "global_filter_class must be set in the subclass",
            typing.Type[AbstractBaseFilter],
        )
    )
    """
    Filter class to be used for global filtering.
    """

    id_schema = lazy(lambda self: self.init_id_schema())
    """
    The pydantic schema for the primary key of the model. If the primary key is composite or a string, it will be set to str, otherwise int or float.
    """
    schema = lazy(lambda self: self.init_schema())
    """
    The pydantic schema for the model. This is the standard schema. If the field is optional, it will be set to None as default.
    """
    schema_optional = lazy(lambda self: self.init_schema(optional=True))
    """
    The pydantic schema for the model. This is the standard schema, but all fields are optional. Useful for POST and PUT requests.
    """
    list_properties: lazy[dict[str, CT]] = lazy(
        lambda self: self.init_list_properties()
    )
    """
    A dictionary of all model's columns and relationships.
    """
    list_columns: lazy[dict[str, CT]] = lazy(lambda self: self.init_list_columns())
    """
    A dictionary of all model's columns.
    """
    filters = lazy(lambda self: self.init_filters())
    """
    A dictionary of filters for the model's columns. The keys are the column names and the values are lists of filters.
    """
    exclude_filters = lazy(lambda: collections.defaultdict[str, list[str]](list))
    """
    A dictionary of filters to exclude from the model's columns when filtering. The keys are the column names and the values are lists of filter `arg_name`.

    Automatically filled by `ModelRestApi`.
    """

    _cache_schema: dict[str, typing.Type[pydantic.BaseModel]] = {}

    def __init__(self, obj: typing.Type[T], with_fk=True):
        super().__init__()
        self.obj = obj
        self.with_fk = with_fk

    """
    --------------------------------------------------------------------------------------------------------
        DEPENDENCIES METHODS - to be implemented
    --------------------------------------------------------------------------------------------------------
    """

    @abc.abstractmethod
    def get_session_factory(self) -> typing.Callable[[], C]:
        """
        Returns the session factory for the model's database connection.
        """
        raise NotImplementedError(
            "This method should be implemented by subclasses to return a session factory."
        )

    """
    --------------------------------------------------------------------------------------------------------
        COUNT AND CRUD METHODS - to be implemented
    --------------------------------------------------------------------------------------------------------
    """

    @abc.abstractmethod
    async def count(self, session: C, params: DBQueryParams | None = None) -> int:
        """
        Counts the number of items in the database based on the provided parameters.

        Args:
            session (C): The session to use for the query.
            params (DBQueryParams, optional): Parameters for the query, such as filters, pagination, and sorting. Defaults to None.

        Returns:
            int: The count of items in the database.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    @abc.abstractmethod
    async def get_many(
        self,
        session: C,
        params: DBQueryParams | None = None,
    ) -> list[T]:
        """
        Retrieves multiple items from the database based on the provided parameters.

        Args:
            session (C): The session to use for the query.
            params (DBExecuteParams, optional): Parameters for the query, such as filters, pagination, and sorting. Defaults to None.

        Returns:
            List[T]: A list of items retrieved from the database.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    @abc.abstractmethod
    async def get_one(
        self,
        session: C,
        params: DBQueryParams | None = None,
    ) -> T | None:
        """
        Retrieves a single item from the database based on the provided parameters.

        Args:
            session (C): The session to use for the query.
            params (DBQueryParams | None, optional): Parameters for the query, such as filters, pagination, and sorting. Defaults to None.

        Returns:
            T | None: The item retrieved from the database, or None if no item matches the query.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    @abc.abstractmethod
    async def yield_per(
        self,
        session: C,
        params: DBQueryParams | None = None,
    ) -> typing.Generator[typing.Sequence[T], None, None]:
        """
        Executes the database query using the provided session and yields results in batches of the specified size.

        Note: PLEASE ALWAYS CLOSE THE SESSION AFTER USING THIS METHOD

        Args:
            session (Session | AsyncSession): The session to use for the query.
            params (DBExecuteParams, optional): Parameters for the query, such as filters, pagination, and sorting. Defaults to None.

        Returns:
            typing.AsyncGenerator[typing.Sequence[T], None, None]: A generator that yields results in batches of the specified size.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    @abc.abstractmethod
    async def add(
        self, session: C, item: T, *, flush=True, commit=True, refresh=True
    ) -> T:
        """
        Adds an item to the session and commits the changes.

        Args:
            session (C): The session to which the item will be added.
            item (T): The item to be added.
            flush (bool, optional): Whether to flush the session after adding the item. Defaults to True.
            commit (bool, optional): Whether to commit the session after adding the item. Defaults to True.
            refresh (bool, optional): Whether to refresh the item after adding it. Defaults to True.

        Returns:
            T: The added item.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    @abc.abstractmethod
    async def edit(
        self, session: C, item: T, *, flush=True, commit=True, refresh=False
    ) -> T:
        """
        Edits an item in the session and commits the changes.

        Args:
            session (C): The session in which the item will be edited.
            item (T): The item to be edited.
            flush (bool, optional): Whether to flush the session after editing the item. Defaults to True.
            commit (bool, optional): Whether to commit the session after editing the item. Defaults to True.
            refresh (bool, optional): Whether to refresh the item after editing it. Defaults to False.

        Returns:
            T: The edited item.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    @abc.abstractmethod
    async def delete(self, session: C, item: T, *, flush=True, commit=True) -> None:
        """
        Deletes an item from the session and commits the changes.

        Args:
            session (C): The session from which the item will be deleted.
            item (T): The item to be deleted.
            flush (bool, optional): Whether to flush the session after deleting the item. Defaults to True.
            commit (bool, optional): Whether to commit the session after deleting the item. Defaults to True.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    """
    --------------------------------------------------------------------------------------------------------
        SESSION METHODS - to be implemented
    --------------------------------------------------------------------------------------------------------
    """

    @abc.abstractmethod
    async def commit(self, session: C) -> None:
        """
        Commits the current transaction in the session.

        Args:
            session (C): The session in which the transaction will be committed.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    @abc.abstractmethod
    async def close(self, session: C) -> None:
        """
        Closes the session.

        Args:
            session (C): The session to be closed.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    """
    --------------------------------------------------------------------------------------------------------
        GET METHODS - to be implemented
    --------------------------------------------------------------------------------------------------------
    """

    @abc.abstractmethod
    def get_add_column_list(self) -> list[str]:
        """
        Returns the list of columns that can be used for adding new items.

        Returns:
            list[str]: A list of columns that can be used for adding new items.
        """
        raise NotImplementedError(
            "This method should be implemented by subclasses to return a list of columns that can be used for adding new items."
        )

    @abc.abstractmethod
    def get_edit_column_list(self) -> list[str]:
        """
        Returns the list of columns that can be used for editing items.

        Returns:
            list[str]: A list of columns that can be used for editing items.
        """
        raise NotImplementedError(
            "This method should be implemented by subclasses to return a list of columns that can be used for editing items."
        )

    @abc.abstractmethod
    def get_order_column_list(self, list_columns: list[str]) -> list[str]:
        """
        Returns the list of columns that can be used for ordering items.

        Args:
            list_columns (list[str]): The list of columns to consider for ordering.

        Returns:
            list[str]: A list of columns that can be used for ordering items.
        """
        raise NotImplementedError(
            "This method should be implemented by subclasses to return a list of columns that can be used for ordering."
        )

    @abc.abstractmethod
    def get_search_column_list(self, list_columns: list[str]) -> list[str]:
        """
        Returns the list of columns that can be used for searching items.

        Args:
            list_columns (list[str]): The list of columns to consider for searching.

        Returns:
            list[str]: A list of columns that can be used for searching items.
        """
        raise NotImplementedError(
            "This method should be implemented by subclasses to return a list of columns that can be used for searching."
        )

    def get_file_column_list(self) -> list[str]:
        """
        Returns all model's columns that are files.

        Returns:
            list[str]: A list of columns that are files.
        """
        return []

    def get_image_column_list(self) -> list[str]:
        """
        Returns all model's columns that are images.

        Returns:
            list[str]: A list of columns that are images.
        """
        return []

    @abc.abstractmethod
    def get_type(self, col: str) -> type:
        """
        Get the Python type corresponding to the specified column name.

        Used to build the schema for the pydantic model.

        Args:
            col (str): The name of the column.

        Returns:
            type: The Python type of the column.
        """
        raise NotImplementedError(
            "This method should be implemented by subclasses to return the Python type of the specified column."
        )

    @abc.abstractmethod
    def get_type_name(self, col: str) -> str:
        """
        Get the name of the type corresponding to the specified column name.

        Used when retrieving the column information for the `_info` endpoint.

        Args:
            col (str): The name of the column.

        Returns:
            str: The name of the type of the column.
        """
        raise NotImplementedError(
            "This method should be implemented by subclasses to return the name of the type of the specified column."
        )

    @abc.abstractmethod
    def get_enum_value(self, col_name: str) -> enum.EnumType | list[str]:
        """
        Get the enum values for the specified column name.
        """
        raise NotImplementedError(
            "This method should be implemented by subclasses to return the enum values for the specified column."
        )

    """
    --------------------------------------------------------------------------------------------------------
        RELATED MODEL METHODS - to be implemented
    --------------------------------------------------------------------------------------------------------
    """

    @abc.abstractmethod
    def get_related_model(self, col_name: str) -> typing.Type[T]:
        """
        Gets the related model for a given column name.

        Args:
            col_name (str): The name of the column for which to get the related model.

        Returns:
            typing.Type[T]: The related model class for the specified column name.
        """
        raise NotImplementedError(
            "This method should be implemented by subclasses to return the related model class for a given column name."
        )

    """
    --------------------------------------------------------------------------------------------------------
        INIT METHODS - to be implemented
    --------------------------------------------------------------------------------------------------------
    """

    def init_list_columns(self) -> dict[str, CT]:
        """
        Initializes a dictionary of all model's columns.

        Returns:
            dict[str, CT]: A dictionary where keys are column names and values are their corresponding SQLAlchemy Column objects or other relevant types.
        """
        raise NotImplementedError(
            "This method should be implemented by subclasses to return a dictionary of all model's columns."
        )

    def init_list_properties(self) -> dict[str, CT]:
        """
        Initializes a dictionary of all model's columns and relationships

        Returns:
            dict[str, CT]: A dictionary where keys are property names and values are their corresponding SQLAlchemy Column objects or other relevant types.
        """
        raise NotImplementedError(
            "This method should be implemented by subclasses to return a dictionary of all model's columns and relationships."
        )

    """
    --------------------------------------------------------------------------------------------------------
        IS METHODS - to be implemented
    --------------------------------------------------------------------------------------------------------
    """

    def is_pk_composite(self) -> bool:
        return False

    def is_pk(self, col_name: str) -> bool:
        return False

    def is_fk(self, col_name: str) -> bool:
        return False

    def is_nullable(self, col_name: str) -> bool:
        return False

    def is_unique(self, col_name: str) -> bool:
        return False

    def is_image(self, col_name: str) -> bool:
        return False

    def is_file(self, col_name: str) -> bool:
        return False

    def is_string(self, col_name: str) -> bool:
        return False

    def is_text(self, col_name: str) -> bool:
        return False

    def is_binary(self, col_name: str) -> bool:
        return False

    def is_integer(self, col_name: str) -> bool:
        return False

    def is_numeric(self, col_name: str) -> bool:
        return False

    def is_float(self, col_name: str) -> bool:
        return False

    def is_boolean(self, col_name: str) -> bool:
        return False

    def is_date(self, col_name: str) -> bool:
        return False

    def is_datetime(self, col_name: str) -> bool:
        return False

    def is_enum(self, col_name: str) -> bool:
        return False

    def is_json(self, col_name: str) -> bool:
        return False

    def is_jsonb(self, col_name: str) -> bool:
        return False

    def is_relation(self, col_name: str) -> bool:
        return False

    def is_relation_one_to_one(self, col_name: str) -> bool:
        return False

    def is_relation_one_to_many(self, col_name: str) -> bool:
        return False

    def is_relation_many_to_one(self, col_name: str) -> bool:
        return False

    def is_relation_many_to_many(self, col_name: str) -> bool:
        return False

    def get_max_length(self, col_name: str) -> int:
        return -1

    def get_min_length(self, col_name: str) -> int:
        return -1

    """
    --------------------------------------------------------------------------------------------------------
        LIFESPAN METHODS - can be implemented
    --------------------------------------------------------------------------------------------------------
    """

    async def on_startup(self):
        """
        Method to run on startup.

        This will be called by `FastAPIReactToolkit` when the application starts.
        """
        pass

    async def on_shutdown(self):
        """
        Method to run on shutdown.

        This will be called by `FastAPIReactToolkit` when the application shuts down.
        """
        pass

    """
    --------------------------------------------------------------------------------------------------------
        DEPENDENCIES METHODS - implemented
    --------------------------------------------------------------------------------------------------------
    """

    def get_download_session_factory(self) -> typing.Callable[[], C]:
        """
        Returns the session factory for the model's database connection.
        """
        return self.get_session_factory()

    """
    --------------------------------------------------------------------------------------------------------
        GET METHODS - implemented
    --------------------------------------------------------------------------------------------------------
    """

    def get_column_list(self):
        """
        Returns all model's columns on SQLA properties
        """
        return list(self.list_properties.keys())

    def get_user_column_list(self):
        """
        Returns all model's columns except pk or fk
        """
        return [
            col_name
            for col_name in self.get_column_list()
            if (not self.is_pk(col_name)) and (not self.is_fk(col_name))
        ]

    def get_property_column_list(self) -> list[str]:
        """
        Returns all model's columns that have @property decorator and is public
        """
        self_dict = vars(self.obj)
        return [
            key
            for key in self_dict.keys()
            if self.is_property(key) and not key.startswith("_")
        ]

    def get_columns_from_related_col(self, col: str, depth=1, prefix=""):
        """
        Returns all columns from a related model, including properties and user columns.

        Args:
            col (str): The name of the related column.
            depth (int, optional): Whether to take the related columns from the related model. 1 means only the columns from the related model, 2 means the columns from the related model and its related models, etc. Defaults to 1.
            prefix (str, optional): A prefix to add to the column names. Used recursively to build the full column names for nested relations. Defaults to "".

        Returns:
            List[str]: A list of column names from the related model, including properties and user columns.
        """
        prefix += f"{col}."
        interface = self.get_related_interface(col)
        columns = (
            interface.get_user_column_list() + interface.get_property_column_list()
        )
        columns = [f"{prefix}{sub_col}" for sub_col in columns]
        if depth > 1:
            related_cols = [
                x for x in interface.get_user_column_list() if interface.is_relation(x)
            ]
            for col in related_cols:
                columns += interface.get_columns_from_related_col(
                    col, depth - 1, prefix
                )
        return columns

    def get_pk_attr(self):
        """
        Returns the primary key attribute of the model.

        Returns:
            str: The name of the primary key attribute.
        """
        for key in self.list_columns.keys():
            if self.is_pk(key):
                return key

        raise Exception(
            f"Model '{self.obj.__name__}' does not have a primary key attribute."
        )

    def get_pk_attrs(self):
        """
        Returns the names of the primary key attributes for the object.

        Returns:
            List[str]: The names of the primary key attributes.
        """
        return [key for key in self.list_columns.keys() if self.is_pk(key)]

    async def get_column_info(
        self,
        col: str,
        session: C,
        session_count: C,
        *,
        params: DBQueryParams | None = None,
        description_columns: dict[str, str] | None = None,
        label_columns: dict[str, str] | None = None,
    ):
        """
        Get the information about a column in the model.

        Args:
            col (str): The name of the column.
            session (C): The SQLAlchemy session to use for retrieving related items.
            session_count (C): The SQLAlchemy session to use for counting related items.
            params (DBExecuteParams | None, optional): The parameters for the query. Defaults to None.
            description_columns (dict[str, str] | None, optional): Mapping of column names to their descriptions. Defaults to None.
            label_columns (dict[str, str] | None, optional): Mapping of column names to their labels. Defaults to None.

        Returns:
            ColumnInfo | ColumnRelationInfo | ColumnEnumInfo: The information about the column.
        """
        info_class = ColumnInfo
        params = params or DBQueryParams(page=0)
        description_columns = description_columns or {}
        label_columns = label_columns or {}
        column_info = {
            "description": description_columns.get(col, ""),
            "label": label_columns.get(col, ""),
            "name": col,
            "required": not self.is_nullable(col),
            "unique": self.is_unique(col),
            "type": self.get_type_name(col),
        }
        if self.is_relation(col):
            info_class = ColumnRelationInfo
            related_interface = self.get_related_interface(col)
            async with asyncio.TaskGroup() as tg:
                task_items = tg.create_task(
                    smart_run(related_interface.get_many, session, params)
                )
                task_count = tg.create_task(
                    smart_run(related_interface.count, session_count, params)
                )
            items, count = await task_items, await task_count
            values = []
            for item in items:
                id, item = related_interface.convert_to_result(item)
                values.append({"id": id, "value": str(item)})
            column_info["count"] = count
            column_info["values"] = values
        elif self.is_enum(col):
            info_class = ColumnEnumInfo
            column_info["values"] = self.get_enum_value(col)
        return info_class(**column_info)

    """
    --------------------------------------------------------------------------------------------------------
        RELATED MODEL METHODS - implemented
    --------------------------------------------------------------------------------------------------------
    """

    def get_related_interface(self, col_name: str, with_fk: bool | None = None):
        """
        Gets the related interface for a given column name.

        Args:
            col_name (str): The name of the column for which to get the related interface.
            with_fk (bool | None, optional): Whether to include foreign keys in the related interface. Defaults to None.

        Returns:
            typing.Self: The related interface for the specified column name.
        """
        return type(self)(self.get_related_model(col_name), with_fk)

    """
    --------------------------------------------------------------------------------------------------------
        IS METHODS - implemented
    --------------------------------------------------------------------------------------------------------
    """

    def is_property(self, col_name: str) -> bool:
        return hasattr(getattr(self.obj, col_name, None), "fget")

    def is_function(self, col_name: str) -> bool:
        return hasattr(getattr(self.obj, col_name, None), "__call__")

    """
    --------------------------------------------------------------------------------------------------------
        INIT METHODS - implemented
    --------------------------------------------------------------------------------------------------------
    """

    def init_id_schema(self):
        """
        Returns the type of the primary key attribute for the object.
        If the primary key is composite or a string, it returns str, otherwise int or float.

        Returns:
            type: The type of the primary key attribute.
        """
        pk_type = int | float
        pk_attr = self.get_pk_attr()
        if self.is_pk_composite() or self.is_string(pk_attr):
            pk_type = str
        return pk_type

    def init_schema(self, optional=False):
        """
        Generates the pydantic schema for the model. This is the standard schema. If the field is optional, it will be set to None as default.
        """
        cols = self.get_column_list() + self.get_property_column_list()
        if not self.with_fk:
            cols = [
                col for col in cols if not self.is_fk(col) and not self.is_relation(col)
            ]

        return self.generate_schema(cols, optional=optional)

    def init_filters(self):
        result = collections.defaultdict[str, list[AbstractBaseFilter]](list)
        for col in self.list_properties.keys():
            for func_attr, filters in self.filter_converter.conversion_table:
                if getattr(self, func_attr)(col):
                    result[col] = [f(self) for f in filters]
                    break

        return result

    """
    --------------------------------------------------------------------------------------------------------
         CONVERSION FUNCTIONS - implemented
    --------------------------------------------------------------------------------------------------------
    """

    @typing.overload
    def convert_to_result(self, data: T) -> tuple[PRIMARY_KEY, T]: ...
    @typing.overload
    def convert_to_result(self, data: list[T]) -> tuple[list[PRIMARY_KEY], list[T]]: ...
    def convert_to_result(self, data: T | list[T]):
        """
        Converts the given data to a result tuple.

        Args:
            data (T | List[T]): The data to be converted.

        Returns:
            tuple: A tuple containing the primary key(s) and the converted data.

        """
        if isinstance(data, list):
            pks: PRIMARY_KEY = (
                [getattr(item, self.get_pk_attr()) for item in data]
                if not self.is_pk_composite()
                else [
                    [str(getattr(item, key)) for key in self.get_pk_attrs()]
                    for item in data
                ]
            )
        else:
            pks: PRIMARY_KEY = (
                getattr(data, self.get_pk_attr())
                if not self.is_pk_composite()
                else [str(getattr(data, key)) for key in self.get_pk_attrs()]
            )

        return (pks, data)

    """
    --------------------------------------------------------------------------------------------------------
        SCHEMA GENERATION METHODS - implemented
    --------------------------------------------------------------------------------------------------------
    """

    def generate_schema(
        self,
        columns: list[str] | None = None,
        *,
        with_id=True,
        with_name=True,
        with_property=True,
        optional=False,
        name="",
        hide_sensitive_columns=True,
        related_kwargs: dict[str, typing.Any] | None = None,
    ):
        """
        Generate a pydantic schema for the model with the specified columns and options. If a column is a relation, the schema for the related model is generated as well.

        Args:
            columns (List[str] | None, optional): The list of columns to include in the schema. Defaults to None.
            with_id (bool, optional): Whether to include the id_ column. Defaults to True.
            with_name (bool, optional): Whether to include the name_ column. Defaults to True.
            with_property (bool, optional): Whether to include @property columns. Defaults to True.
            optional (bool, optional): Whether the columns should be optional. Defaults to False.
            name (str, optional): The name of the schema. If not specified, the name is generated based on the object's name and the specified options. Defaults to ''.
            hide_sensitive_columns (bool, optional): Whether to hide sensitive columns such as `password`. Defaults to True.
            related_kwargs (dict[str, typing.Any] | None, optional): Additional keyword arguments for schema generation of the related models. The options are the same as this function with `with_fk`. Defaults to None.

        Returns:
            type[BaseModel]: The Pydantic schema for the model.
        """
        if not name:
            name = self._generate_schema_name(
                columns,
                with_id=with_id,
                with_name=with_name,
                with_property=with_property,
                optional=optional,
                hide_sensitive_columns=hide_sensitive_columns,
            )
            if name in self._cache_schema:
                return self._cache_schema[name]

        return self._generate_schema_from_dict(
            self._generate_schema_from_columns(
                columns,
                with_id=with_id,
                with_name=with_name,
                with_property=with_property,
                optional=optional,
                name=name,
                hide_sensitive_columns=hide_sensitive_columns,
                related_kwargs=related_kwargs,
            )
        )

    def _generate_schema_from_dict(self, schema_dict: PydanticGenerationSchema):
        """
        Recursively generate a pydantic schema for the model from a dictionary created by `_generate_schema_from_columns`.

        Args:
            schema_dict (PydanticGenerationSchema): The dictionary created by `_generate_schema_from_columns`.

        Returns:
            type[BaseModel]: The Pydantic schema for the model.
        """
        async_columns = schema_dict.pop("__async_columns__")
        model_name = schema_dict.pop("__name__")
        optional = schema_dict.pop("__optional__")
        schema_dict.pop("__columns__", None)
        schema_dict.pop("__with_id__", None)
        schema_dict.pop("__with_name__", None)
        schema_dict.pop("__with_property__", None)
        schema_dict.pop("__hide_sensitive_columns__", None)
        schema_dict.pop("__with_fk__", None)

        if async_columns:

            async def fill_column(model, col: str):
                setattr(model, col, await getattr(model, col))

            def fill_columns(self):
                for col in async_columns:
                    AsyncTaskRunner.add_task(lambda: fill_column(self, col))
                return self

            decorated_func = pydantic.model_validator(mode="after")(fill_columns)
            schema_dict["__validators__"] = {fill_columns.__name__: decorated_func}

        if self.is_pk_composite():
            self.id_schema = str

        # Convert relationship schema to BaseModel
        for key, value in schema_dict.items():
            if key.startswith("__"):
                continue
            if isinstance(value, dict):
                sub_interface = self.get_related_interface(
                    key, bool(value.pop("__with_fk__", True))
                )
                params = {}
                type = sub_interface._generate_schema_from_dict(value) | None
                if self.is_relation_one_to_many(key) or self.is_relation_many_to_many(
                    key
                ):
                    type = list[type]
                if self.is_nullable(key) or optional:
                    params["default"] = None
                    type = type | None
                if self.get_max_length(key) != -1:
                    params["max_length"] = self.get_max_length(key)
                schema_dict[key] = (type, pydantic.Field(**params))

        self._cache_schema[model_name] = pydantic.create_model(
            model_name, **schema_dict
        )
        return self._cache_schema[model_name]

    def _generate_schema_from_columns(
        self,
        columns: list[str],
        *,
        with_id: bool,
        with_name: bool,
        with_property: bool,
        optional: bool,
        name: str,
        hide_sensitive_columns: bool,
        related_kwargs: dict[str, typing.Any] | None = None,
    ):
        """
        Recursively generate a pydantic schema for the model with the specified columns and options. If a column is a relation, the schema for the related model is generated as well.

        Args:
            columns (List[str] | None): The list of columns to include in the schema.
            with_id (bool): Whether to include the id_ column.
            with_name (bool): Whether to include the name_ column.
            with_property (bool): Whether to include @property columns.
            optional (bool): Whether the columns should be optional.
            name (str): The name of the schema. If not specified, the name is generated based on the object's name and the specified options.
            hide_sensitive_columns (bool): Whether to hide sensitive columns such as `password`.
            related_kwargs (dict[str, typing.Any] | None, optional): Additional keyword arguments for schema generation of the related models. The options are the same as this function with `with_fk`. Defaults to None.

        Returns:
            dict: The generated schema.
        """
        related_kwargs = related_kwargs or {}
        current_schema = PydanticGenerationSchema(
            __config__=pydantic.ConfigDict(from_attributes=True),
            __async_columns__=[],
            __columns__=columns,
            __with_name__=with_name,
            __with_id__=with_id,
            __with_property__=with_property,
            __optional__=optional,
            __hide_sensitive_columns__=hide_sensitive_columns,
            __with_fk__=self.with_fk,
        )

        current_schema["__name__"] = name

        if with_id:
            current_schema["id_"] = (PRIMARY_KEY, pydantic.Field())
        if with_name:
            current_schema["name_"] = (str, pydantic.Field())

        if hide_sensitive_columns:
            sensitive_columns = g.sensitive_data.get(self.obj.__name__, [])
            columns = [col for col in columns if col not in sensitive_columns]

        prop_dict = self.list_properties if self.with_fk else self.list_columns
        for col in columns:
            sub_col = ""
            if "." in col:
                col, sub_col = col.split(".", 1)

            if self.is_relation(col):
                current_schema[col] = current_schema.get(
                    col,
                    PydanticGenerationSchema(
                        __config__=pydantic.ConfigDict(from_attributes=True),
                        __async_columns__=[],
                    ),
                )

                sub_interface = self.get_related_interface(
                    col, related_kwargs.get("with_fk", bool(sub_col))
                )
                sub_columns = (
                    [
                        x
                        for x in sub_interface.get_column_list()
                        + sub_interface.get_property_column_list()
                        if not sub_interface.is_relation(x)
                        and not sub_interface.is_fk(x)
                    ]
                    if not sub_col
                    else [sub_col]
                )
                sub_with_id = current_schema[col].get(
                    "id_", related_kwargs.get("with_id", not bool(sub_col))
                )
                sub_with_name = current_schema[col].get(
                    "name_", related_kwargs.get("with_name", not bool(sub_col))
                )
                sub_with_property = current_schema[col].get(
                    "__with_property__",
                    related_kwargs.get("with_property", with_property),
                )
                sub_optional = current_schema[col].get(
                    "__optional__", related_kwargs.get("optional", optional)
                )
                sub_hide_sensitive_columns = current_schema[col].get(
                    "__hide_sensitive_columns__",
                    related_kwargs.get(
                        "hide_sensitive_columns", hide_sensitive_columns
                    ),
                )

                current_schema[col] = deep_merge(
                    current_schema[col],
                    sub_interface._generate_schema_from_columns(
                        sub_columns,
                        with_id=sub_with_id,
                        with_name=sub_with_name,
                        with_property=sub_with_property,
                        optional=sub_optional,
                        name=sub_interface._generate_schema_name(
                            sub_columns,
                            with_id=sub_with_id,
                            with_name=sub_with_name,
                            with_property=sub_with_property,
                            optional=sub_optional,
                            hide_sensitive_columns=sub_hide_sensitive_columns,
                        ),
                        hide_sensitive_columns=sub_hide_sensitive_columns,
                        related_kwargs=related_kwargs,
                    ),
                )
            else:
                # Get column from properties
                column = prop_dict.get(col, None)
                # If column is not found, check if it is a property
                if column is None:
                    if self.is_property(col) and with_property:
                        current_schema[col] = (typing.Any, pydantic.Field(default=None))
                        if inspect.iscoroutinefunction(
                            getattr(getattr(self.obj, col), "fget")
                        ):
                            current_schema["__async_columns__"].append(col)
                    continue

                params = {}
                type = self.get_type(col)

                if hasattr(column, "primary_key") and column.primary_key:
                    self.id_schema = type
                if self.is_nullable(col) or optional:
                    params["default"] = None
                    type = type | None
                # if self.get_max_length(col) != -1:
                #     params["max_length"] = self.get_max_length(col)
                current_schema[col] = (type, pydantic.Field(**params))

        return current_schema

    def _generate_schema_name(
        self,
        columns: list[str] | None = None,
        *,
        with_id: bool = False,
        with_name: bool = False,
        with_property: bool = False,
        optional: bool = False,
        hide_sensitive_columns: bool = True,
    ):
        """
        Generate a name for the schema based on the specified options.

        Args:
            columns (List[str] | None, optional): The list of columns to include in the schema. Defaults to None.
            with_id (bool, optional): Whether to include the id_ column. Defaults to False.
            with_name (bool, optional): Whether to include the name_ column. Defaults to False.
            with_property (bool, optional): Whether to include @property columns. Defaults to False.
            optional (bool, optional): Whether the columns should be optional. Defaults to False.
            hide_sensitive_columns (bool, optional): Whether to hide sensitive columns such as `password`. Defaults to True.

        Returns:
            str: The generated name for the schema.
        """
        name = f"{self.obj.__name__}-Schema"
        if columns:
            name += f"-{'-'.join(columns)}"
        if with_id:
            name += "-WithID"
        if with_name:
            name += "-WithName"
        if with_property:
            name += "-WithProperty"
        if self.with_fk:
            name += "-WithFK"
        if optional:
            name += "-Optional"
        if hide_sensitive_columns:
            name += "-HideSensitive"
        return name
