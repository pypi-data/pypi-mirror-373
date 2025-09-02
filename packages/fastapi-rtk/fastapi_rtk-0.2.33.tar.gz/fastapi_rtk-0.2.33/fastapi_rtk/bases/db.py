import abc
import typing

import fastapi

from ..const import logger
from ..schemas import PRIMARY_KEY, FilterSchema
from ..utils import T, safe_call, use_default_when_none
from .filter import AbstractBaseFilter

if typing.TYPE_CHECKING:
    from .interface import AbstractInterface

BUILD_STEPS = typing.Literal[
    "list_columns",
    "page|page_size",
    "order_column|order_direction",
    "where",
    "where_in",
    "where_id",
    "where_id_in",
    "filters",
    "filter_classes",
    "global_filter",
]
DEFAULT_ORDER = [
    "list_columns",
    "page|page_size",
    "order_column|order_direction",
    "where",
    "where_in",
    "where_id",
    "where_id_in",
    "filters",
    "filter_classes",
    "global_filter",
]


class DBQueryParams(typing.TypedDict):
    list_columns: list[str] | None
    page: int | None
    page_size: int | None
    order_column: str | None
    order_direction: typing.Literal["asc", "desc"] | None
    where: tuple[str, typing.Any] | list[tuple[str, typing.Any]] | None
    where_in: tuple[str, list[typing.Any]] | None
    where_id: PRIMARY_KEY | None
    where_id_in: list[PRIMARY_KEY] | None
    filters: list[FilterSchema] | None
    filter_classes: list[tuple[str, AbstractBaseFilter, typing.Any]] | None
    global_filter: tuple[list[str], str] | None


class AbstractQueryBuilder(abc.ABC, typing.Generic[T]):
    """
    An abstract base class for a helper class that builds queries based on the provided parameters.
    """

    datamodel: "AbstractInterface" = None
    statement: T = None

    build_steps: BUILD_STEPS = DEFAULT_ORDER
    """
    A list of steps to build the query. Each step corresponds to a method that will be called in order.

    Duplications in the `build_steps` list will be removed automatically when the query is built for the first time.

    ***If you want to change the order of the steps, override this attribute in the subclass like this:***

    ```python
    class MyQueryBuilderClass(AbstractQueryBuilder):
        # Handle pagination and sorting first, then apply the default order
        build_steps = ['page|page_size', 'order_column|order_direction'] + AbstractQueryBuilder.DEFAULT_ORDER
    ```
    """

    DEFAULT_BUILD_STEPS = DEFAULT_ORDER
    """
    Default build steps for reference.

    DO NOT MODIFY.
    """

    _duplicates_removed = False
    """
    A flag to indicate whether duplicates have been removed from the `build_steps` list.
    """

    def __init__(self, datamodel: "AbstractInterface", statement: T | None = None):
        super().__init__()
        self.datamodel = use_default_when_none(datamodel, self.datamodel)
        if statement is not None:
            self.statement = statement
        if self.statement is None:
            raise RuntimeError(
                "The statement must be provided or initialized in the subclass."
            )

    async def build_query(
        self,
        params: DBQueryParams = None,
        **kwargs,
    ):
        """
        BuBuilds a SQLAlchemy query based on the provided parameters and the initial statement.

        Args:
            params (DBExecuteParams, optional): Parameters for the query, such as filters, pagination, and sorting. Defaults to None.

        Returns:
            T: The built SQLAlchemy query statement.
        """
        statement = self.statement
        params = params or DBQueryParams()
        params = DBQueryParams(**params, **kwargs)

        if not self._duplicates_removed:
            # Remove duplicates from build_steps if not already done
            self._duplicates_removed = True
            self.build_steps = list(dict.fromkeys(self.build_steps))

        for step in self.build_steps:
            if step not in self.DEFAULT_BUILD_STEPS:
                raise Exception(
                    f"Unknown build step: {step}. Please check the build_steps configuration. The available steps are: {', '.join(self.build_steps)}."
                )

            if step == "list_columns" and params.get("list_columns"):
                statement = await safe_call(
                    self.apply_list_columns(statement, params["list_columns"])
                )
            elif (
                step == "page|page_size"
                and params.get("page") is not None
                and params.get("page_size") is not None
            ):
                statement = await safe_call(
                    self.apply_pagination(
                        statement, params["page"], params["page_size"]
                    )
                )
            elif (
                step == "order_column|order_direction"
                and params.get("order_column")
                and params.get("order_direction")
            ):
                statement = await safe_call(
                    self.apply_order_by(
                        statement,
                        params["order_column"],
                        params["order_direction"],
                    )
                )
            elif step == "where" and params.get("where"):
                where = params["where"]
                if not isinstance(where, list):
                    where = [where]
                for w in where:
                    statement = await safe_call(self.apply_where(statement, *w))
            elif step == "where_in" and params.get("where_in"):
                statement = await safe_call(
                    self.apply_where_in(statement, *params["where_in"])
                )
            elif step == "where_id" and params.get("where_id"):
                statement = await safe_call(
                    self.apply_where_id(statement, params["where_id"])
                )
            elif step == "where_id_in" and params.get("where_id_in"):
                statement = await safe_call(
                    self.apply_where_id_in(statement, params["where_id_in"])
                )
            elif step == "filters" and params.get("filters"):
                for filter in params["filters"]:
                    statement = await safe_call(self.apply_filter(statement, filter))
            elif step == "filter_classes" and params.get("filter_classes"):
                for filter_class in params["filter_classes"]:
                    statement = await safe_call(
                        self.apply_filter_class(statement, *filter_class)
                    )
            elif step == "global_filter" and params.get("global_filter"):
                columns, global_filter = params["global_filter"]
                statement = await safe_call(
                    self.apply_global_filter(statement, columns, global_filter)
                )

        logger.debug(f"{self.__class__.__name__}: build_query: {statement}")
        return statement

    """
    --------------------------------------------------------------------------------------------------------
        APPLY METHODS - to be implemented
    --------------------------------------------------------------------------------------------------------
    """

    @abc.abstractmethod
    async def apply_list_columns(self, statement: T, list_columns: list[str]) -> T:
        """
        Handles the selection of specific columns in the query.

        Args:
            statement (T): The SQLAlchemy query statement to modify.
            list_columns (list[str]): A list of column names to select.

        Returns:
            T: The modified SQLAlchemy query statement with the specified columns selected.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    @abc.abstractmethod
    async def apply_pagination(self, statement: T, page: int, page_size: int) -> T:
        """
        Handles pagination of the query results.

        Args:
            statement (T): The SQLAlchemy query statement to modify.
            page (int): The page number to retrieve.
            page_size (int): The number of items per page.

        Returns:
            T: The modified SQLAlchemy query statement with pagination applied.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    @abc.abstractmethod
    async def apply_order_by(
        self,
        statement: T,
        order_column: str,
        order_direction: typing.Literal["asc", "desc"],
    ) -> T:
        """
        Handles the ordering of the query results.

        Args:
            statement (T): The SQLAlchemy query statement to modify.
            order_column (str): The column to order by.
            order_direction (typing.Literal["asc", "desc"]): The direction of the order ('asc' or 'desc').

        Returns:
            T: The modified SQLAlchemy query statement with ordering applied.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    @abc.abstractmethod
    async def apply_where(self, statement: T, column: str, value) -> T:
        """
        Handles the WHERE clause of the query.

        Args:
            statement (T): The SQLAlchemy query statement to modify.
            column (str): The column to filter by.
            value: The value to filter the column by.

        Returns:
            T: The modified SQLAlchemy query statement with the WHERE clause applied.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    @abc.abstractmethod
    async def apply_where_in(
        self, statement: T, column: str, values: list[typing.Any]
    ) -> T:
        """
        Handles the WHERE IN clause of the query.

        Args:
            statement (T): The SQLAlchemy query statement to modify.
            column (str): The column to filter by.
            values (list[typing.Any]): A list of values to filter the column by.

        Returns:
            T: The modified SQLAlchemy query statement with the WHERE IN clause applied.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    @abc.abstractmethod
    async def apply_filter(self, statement: T, filter: FilterSchema) -> T:
        """
        Handles the filtering of the query based on a FilterSchema.

        Args:
            statement (T): The SQLAlchemy query statement to modify.
            filter (FilterSchema): The filter schema to apply.

        Returns:
            T: The modified SQLAlchemy query statement with the filter applied.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    @abc.abstractmethod
    async def apply_filter_class(
        self,
        statement: T,
        col: str,
        filter_class: AbstractBaseFilter[T],
        value,
    ) -> T:
        """
        Handles the filtering of the query using a filter class.

        Args:
            statement (T): The SQLAlchemy query statement to modify.
            col (str): The column to filter by.
            filter_class (AbstractBaseFilter[T]): The filter class to apply.
            value: The value to filter the column by.

        Returns:
            T: The modified SQLAlchemy query statement with the filter class applied.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    @abc.abstractmethod
    async def apply_global_filter(
        self, statement: T, columns: list[str], global_filter: str
    ) -> T:
        """
        Handles the filtering of the query using a global filter.

        Args:
            statement (T): The SQLAlchemy query statement to modify.
            columns (list[str]): The columns to apply the global filter on.
            global_filter (str): The global filter to apply.

        Returns:
            T: The modified SQLAlchemy query statement with the global filter applied.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    """
    --------------------------------------------------------------------------------------------------------
        APPLY METHODS - implemented
    --------------------------------------------------------------------------------------------------------
    """

    async def apply_where_id(self, statement: T, value: PRIMARY_KEY):
        """
        Handles the WHERE ID clause of the query.

        Args:
            statement (T): The SQLAlchemy query statement to modify.
            value (PRIMARY_KEY): The primary key value to filter by.

        Returns:
            T: The modified SQLAlchemy query statement with the WHERE ID clause applied.
        """
        pk_dict = self._convert_id_into_dict(value)
        for col, val in pk_dict.items():
            statement = self.apply_where(statement, col, val)
        return statement

    async def apply_where_id_in(self, statement: T, values: list[PRIMARY_KEY]):
        """
        Handles the WHERE ID IN clause of the query.

        Args:
            statement (T): The SQLAlchemy query statement to modify.
            values (list[PRIMARY_KEY]): A list of primary key values to filter by.

        Returns:
            T: The modified SQLAlchemy query statement with the WHERE ID IN clause applied.
        """
        to_apply_dict = {}
        for id in self.datamodel.get_pk_attrs():
            to_apply_dict[id] = []

        pk_dicts = [self._convert_id_into_dict(id) for id in values]
        for pk_dict in pk_dicts:
            for col, val in pk_dict.items():
                to_apply_dict[col].append(val)

        for col, vals in to_apply_dict.items():
            statement = self.apply_where_in(statement, col, vals)
        return statement

    """
    --------------------------------------------------------------------------------------------------------
        HELPER METHODS
    --------------------------------------------------------------------------------------------------------
    """

    def _convert_id_into_dict(self, id: PRIMARY_KEY) -> dict[str, typing.Any]:
        """
        Converts the given ID into a dictionary format.

        Args:
            id (PRIMARY_KEY): The ID to be converted.

        Returns:
            dict[str, typing.Any]: The converted ID in dictionary format.

        Raises:
            HTTPException: If the ID is invalid.
        """
        pk_dict = {}
        if self.datamodel.is_pk_composite():
            try:
                # Assume the ID is a string, split the string to ','
                id = id.split(",") if isinstance(id, str) else id
                if len(id) != len(self.datamodel.get_pk_attrs()):
                    raise fastapi.HTTPException(
                        status_code=400,
                        detail=f"Invalid ID: {id}, expected {len(self.datamodel.get_pk_attrs())} values",
                    )
                for pk_key in self.datamodel.get_pk_attrs():
                    pk_dict[pk_key] = id.pop(0)
            except Exception:
                raise fastapi.HTTPException(status_code=400, detail="Invalid ID")
        else:
            pk_dict[self.datamodel.get_pk_attr()] = id

        return pk_dict
