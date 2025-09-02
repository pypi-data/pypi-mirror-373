import collections
import typing

import sqlalchemy
from fastapi import HTTPException
from sqlalchemy import (
    Column,
    Select,
    select,
)
from sqlalchemy.orm import (
    defer,
    joinedload,
    load_only,
    selectinload,
)
from sqlalchemy.orm.strategy_options import _AbstractLoad

from ...bases.db import AbstractQueryBuilder
from ...const import logger
from ...utils import T, deep_merge, prettify_dict, safe_call, smart_run
from .filters import BaseFilter

__all__ = ["SQLAQueryBuilder"]

LOAD_TYPE_MAPPING = {
    "defer": 0,
    "some": 1,
    "all": 2,
}


class LoadColumn(typing.TypedDict):
    statement: Select[tuple[T]] | _AbstractLoad
    type: typing.Literal["defer", "some", "all"]
    columns: list[str]
    related_columns: collections.defaultdict[str, "LoadColumn"]


def create_load_column(statement: Select[tuple[T]] | _AbstractLoad | None = None):
    return LoadColumn(
        statement=statement,
        type="defer",
        columns=[],
        related_columns=collections.defaultdict(create_load_column),
    )


class SQLAQueryBuilder(AbstractQueryBuilder[Select[tuple[T]]]):
    """
    A class that builds SQLAlchemy queries based on the provided parameters.

    Usage:
    ```python
    # E.g how to query the user with name and email
    interface = SQLAInterface(User)
    query = await QueryBuilder(interface).build_query(
        list_columns=["name", "email"],
        where=[("name", "John Doe")],
        order_column="email",
        order_direction="asc",
        # Additional parameters can be passed as needed
    )
    ```
    """

    _load_options_cache: dict[str, list[list[_AbstractLoad] | _AbstractLoad]] = {}

    def __init__(self, datamodel, statement=None):
        if self.statement is None:
            self.statement = sqlalchemy.select(datamodel.obj)
        super().__init__(datamodel, statement)

    def apply_list_columns(self, statement, list_columns):
        """
        Load specified columns into the given SQLAlchemy statement.
        This method processes the provided list of columns, orders them, and
        determines the appropriate loading strategy for each column. It supports
        loading both direct columns and related columns (one-to-one, many-to-one,
        and select-in relationships). The method also handles nested column
        relationships by recursively calling itself.

        Args:
            statement (Select[tuple[T]]): The SQLAlchemy statement to which the
                columns will be loaded.
            columns (list[str]): A list of column names to be loaded.

        Returns:
            The modified SQLAlchemy statement with the specified columns loaded.
        """
        # Order the columns first, so that related columns are loaded before their sub-columns
        list_columns = sorted(list_columns)

        # Check if the columns have been loaded before
        cache_key = f"{self.datamodel.obj.__name__}-{list_columns}"
        if cache_key in self._load_options_cache:
            logger.debug(f"Loading columns from cache: {cache_key}")
            for cache_option in self._load_options_cache[cache_key]:
                if isinstance(cache_option, list):
                    statement = statement.options(*cache_option)
                else:
                    statement = statement.options(cache_option)
            return statement

        load_column = self._load_columns_recursively(statement, list_columns)
        logger.debug(f"Load Column:\n{prettify_dict(load_column)}")
        return self._load_columns_from_dictionary(statement, load_column, list_columns)

    def apply_pagination(self, statement, page, page_size):
        return statement.offset(page * page_size).limit(page_size)

    def apply_order_by(self, statement, order_column, order_direction):
        col = order_column

        #! If the order column comes from a request, it will be in the format ClassName.column_name
        if col.startswith(self.datamodel.obj.__class__.__name__):
            col = col.split(".", 1)[1]

        statement, col = self._retrieve_column(statement, col)
        if order_direction == "asc":
            statement = statement.order_by(col)
        else:
            statement = statement.order_by(col.desc())
        return statement

    def apply_where(self, statement, column, value):
        column = getattr(self.datamodel.obj, column)
        return statement.where(column == value)

    def apply_where_in(self, statement, column, values):
        column = getattr(self.datamodel.obj, column)
        return statement.where(column.in_(values))

    async def apply_filter(self, statement, filter):
        col = filter.col
        if "." in col:
            col, rel_col = col.split(".", 1)
            rel_interface = self.datamodel.get_related_interface(col)
            rel_interface.filters[rel_col].extend(
                self.datamodel.filters.get(filter.col, [])
            )
            rel_interface.filters[rel_col] = [
                f
                for f in rel_interface.filters[rel_col]
                if f.arg_name not in self.datamodel.exclude_filters.get(filter.col, [])
            ]
            filter_classes = rel_interface.filters.get(rel_col, [])
        else:
            filter_classes = self.datamodel.filters.get(col, [])
        filter_class = None
        for f in filter_classes:
            if f.arg_name == filter.opr:
                filter_class = f
                break
        if not filter_class:
            raise HTTPException(
                status_code=400, detail=f"Invalid filter opr: {filter.opr}"
            )

        if "." in filter.col:
            return await self._filter_relation(
                statement, filter.col, filter_class, filter.value
            )

        return await self._filter(filter_class, statement, filter.col, filter.value)

    async def apply_filter_class(self, statement, col, filter_class, value):
        # If there is . in the column name, it means it should filter on a related table
        if "." in col:
            return await self._filter_relation(statement, col, filter_class, value)

        return await self._filter(filter_class, statement, col, value)

    async def apply_global_filter(self, statement, columns, global_filter):
        return await self.apply_filter_class(
            statement,
            columns,
            self.datamodel.global_filter_class(self.datamodel),
            global_filter,
        )

    """
    -------------
     HELPER METHODS
    -------------
    """

    def _retrieve_column(
        self, statement: Select[tuple[T]], col: str
    ) -> tuple[Select[tuple[T]], Column]:
        """
        Retrieves the column from the datamodel based on the provided column name.

        - If the column is a relation, it will join the relation and return the primary key of the related datamodel.
        - If the column is not a relation, it will return the column directly.
        - If the column is a nested relation (e.g., 'relation.sub_relation.column'), it will recursively join the relations until it reaches the specified column.

        Args:
            statement (Select[tuple[T]]): The SQLAlchemy Select statement to which the column will be retrieved and joined.
            col (str): The column name to retrieve, which can be a relation or a nested relation in the format 'relation.column'.

        Returns:
            tuple[Select[tuple[T]], Column]: The updated SQLAlchemy Select statement and the specified column.
        """
        cols = col.split(".")
        datamodel = self.datamodel

        logger.debug(f"Retrieving column: {col} from model: {datamodel.obj.__name__}")

        for c in cols:
            col = c
            if datamodel.is_relation(c):
                rel_datamodel = datamodel.get_related_interface(c)
                rel_pk = rel_datamodel.get_pk_attr()
                fk = datamodel.get_fk_column(c)
                statement = statement.join(
                    rel_datamodel.obj,
                    getattr(datamodel.obj, fk) == getattr(rel_datamodel.obj, rel_pk),
                    isouter=True,
                )
                logger.debug(
                    f"Joining column: {c} with foreign key: {fk} in model: {datamodel.obj.__name__}"
                )
                datamodel = rel_datamodel
                col = rel_pk

        return statement, getattr(datamodel.obj, col)

    async def _filter_relation(
        self,
        statement: Select[tuple[T]],
        col: str,
        filter_class: BaseFilter,
        value,
    ):
        col, rel_col = col.split(".")
        rel_obj = filter_class.datamodel.obj
        rel_pks = filter_class.datamodel.get_pk_attrs()
        rel_statements = [select(getattr(rel_obj, pk)) for pk in rel_pks]
        rel_statements = [
            await safe_call(self._filter(filter_class, statement, rel_col, value))
            for statement in rel_statements
        ]
        rel_statements = [
            getattr(rel_obj, pk).in_(statement)
            for pk, statement in zip(rel_pks, rel_statements)
        ]
        func = (
            getattr(self.datamodel.obj, col).any
            if self.datamodel.is_relation_one_to_many(col)
            or self.datamodel.is_relation_many_to_many(col)
            else getattr(self.datamodel.obj, col).has
        )
        return statement.filter(func(*rel_statements))

    async def _filter(
        self,
        cls: BaseFilter,
        statement: Select[tuple[T]],
        col: str,
        value: typing.Any,
    ):
        """
        Helper method to apply a filter class.

        Args:
            cls (BaseFilter): The filter class to apply.
            statement (Select[tuple[T]]): The SQLAlchemy Select statement to which the filter will be applied.
            col (str): The column name to apply the filter on.
            value (typing.Any): The value to filter by.

        Returns:
            Select[tuple[T]]: The SQLAlchemy Select statement with the filter applied.
        """
        if cls.is_heavy:
            return await smart_run(cls.apply, statement, col, value)

        return await safe_call(cls.apply(statement, col, value))

    def _load_columns_from_dictionary(
        self,
        statement: Select[tuple[T]] | _AbstractLoad,
        load_column: LoadColumn,
        columns: list[str] | None = None,
    ):
        """
        Load specified columns into the given SQLAlchemy statement. This method processes the provided dictionary of columns and related columns, and loads them into the statement.

        Args:
            statement (Select[tuple[T]] | _AbstractLoad): The SQLAlchemy statement to which the columns will be loaded.
            load_column (LoadColumn): The dictionary of columns to load.
            columns (list[str] | None, optional): A list of column names to be cached. If none, the columns are not cached. Defaults to None.

        Returns:
            Select[tuple[T]] | _AbstractLoad: The modified SQLAlchemy statement with the specified columns loaded.
        """
        cache_key = ""
        if columns:
            cache_key = f"{self.datamodel.obj.__name__}-{columns}"
            self._load_options_cache[cache_key] = []
        if load_column["type"] == "defer":
            defers = [
                defer(getattr(self.datamodel.obj, col))
                for col in [
                    x
                    for x in self.datamodel.get_user_column_list()
                    if not self.datamodel.is_relation(x)
                ]
            ]
            statement = statement.options(*defers)
            if cache_key:
                self._load_options_cache[cache_key].append(defers)
        elif load_column["type"] == "some":
            load_onlys = [
                getattr(self.datamodel.obj, col) for col in load_column["columns"]
            ]
            statement = statement.options(load_only(*load_onlys))
            if cache_key:
                self._load_options_cache[cache_key].append(load_only(*load_onlys))

        for col, load_dict in load_column["related_columns"].items():
            interface = self.datamodel.get_related_interface(col)
            load_dict["statement"] = interface.query._load_columns_from_dictionary(
                load_dict["statement"], load_dict
            )
            statement = statement.options(load_dict["statement"])
            if cache_key:
                self._load_options_cache[cache_key].append(load_dict["statement"])

        return statement

    def _load_columns_recursively(
        self, statement: Select[tuple[T]] | _AbstractLoad, columns: list[str]
    ):
        """
        Load specified columns into the given SQLAlchemy statement. This returns a dictionary that can be used with the `load_columns_from_dictionary` method.

        Args:
            statement (Select[tuple[T]] | _AbstractLoad): The SQLAlchemy statement to which the columns will be loaded.
            columns (list[str]): A list of column names to be loaded.

        Returns:
            dict: A dictionary that can be used with the `load_columns_from_dictionary` method.
        """
        load_column = create_load_column(statement)
        for col in columns:
            sub_col = ""
            if "." in col:
                col, sub_col = col.split(".", 1)

            # If it is not a relation, load only the column if it is in the user column list, else skip
            if not self.datamodel.is_relation(col):
                if col in self.datamodel.get_user_column_list():
                    load_column["columns"].append(col)
                    load_column["type"] = "some"
                continue

            if self.datamodel.is_relation_one_to_one(
                col
            ) or self.datamodel.is_relation_many_to_one(col):
                load_column["related_columns"][col]["statement"] = load_column[
                    "related_columns"
                ][col]["statement"] or joinedload(self.datamodel.obj.load_options(col))
            else:
                load_column["related_columns"][col]["statement"] = load_column[
                    "related_columns"
                ][col]["statement"] or selectinload(
                    self.datamodel.obj.load_options(col)
                )

            interface = self.datamodel.get_related_interface(col)

            # If there is a . in the sub column, it means it is a relation column, so we need to load it
            if "." in sub_col or interface.is_relation(sub_col):
                load_column["related_columns"][col] = deep_merge(
                    load_column["related_columns"][col],
                    interface.query._load_columns_recursively(
                        load_column["related_columns"][col]["statement"], [sub_col]
                    ),
                    rules={
                        "type": lambda x1, x2: LOAD_TYPE_MAPPING[x2]
                        > LOAD_TYPE_MAPPING[x1]
                    },
                )

            # If load_type is all, we do not need handle sub columns, since it will be loaded anyway
            if load_column["related_columns"][col]["type"] == "all":
                continue

            # If the sub_col is not specified, assume that we want to load all columns of the relation
            if not sub_col:
                load_column["related_columns"][col]["type"] = "all"
                continue

            # Skip if the sub column is not in the user column list or if it is a relation
            if sub_col not in interface.get_user_column_list() or interface.is_relation(
                sub_col
            ):
                continue

            load_column["related_columns"][col]["columns"].append(sub_col)
            load_column["related_columns"][col]["type"] = "some"

        return load_column
