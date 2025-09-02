import collections
import operator
import typing
from datetime import date, datetime

from ...bases.session import AbstractSession
from ...setting import Setting
from .column import PK_AUTO_INCREMENT
from .model import GenericModel

__all__ = ["GenericSession"]


class Table(dict[int | str, GenericModel]):
    latest_pk = 1

    def add(self, model: GenericModel):
        """
        Add a model to the table.

        Args:
            model (Model): The model to add.

        Raises:
            ValueError: If the model's primary key already exists in the table.
        """
        pk = model.get_pk()

        # If the model is queried from this table, then update the model in the table.
        if model.__table__ == self:
            self[pk] = model
            return

        if pk is PK_AUTO_INCREMENT:
            # Generate a new primary key if the model has an auto-incrementing primary key.
            while self.latest_pk in self:
                self.latest_pk += 1

            # Set the primary key of the model to the new value, add it to the table, and increment the latest_pk.
            model.set_pk(self.latest_pk)
            pk = self.latest_pk
            self.latest_pk += 1

        if pk not in self:
            self[pk] = model
            model.__table__ = self
        else:
            raise ValueError(f"Model with pk {pk} already exists")


class Database(collections.defaultdict[typing.Type[GenericModel], Table]):
    def __missing__(self, key):
        """
        If the key is not found, create a new table for the model
        """
        self[key] = Table()
        return self[key]


class GenericSession(AbstractSession):
    """
    A generic session for a generic data source. This works similar to a SQLAlchemy session.

    This class can be used as is for a simple in-memory data source.

    But, if you have an external data source, you should override the following methods:

    - **get**: Get a model from the database.
    - **add**: Add a model to the database.
    - **delete**: Delete a model from the database.
    - **count**: Return the total length of the items after applying all filters and orders.
    - **first**: Return the first item after applying all filters and orders.
    - **all**: Return all items after applying all filters and orders.
    - **load_data**: Load data to the session. This will be called when the session class is initialized.
    - **save_data**: Save data to other sources. This will be called when FastAPI is shutting down.
    """

    # Class variable to hold the database instance
    database: Database = None

    # Instance variable to hold the session instance for orm-like behavior
    _query: typing.Type[GenericModel] | None = None
    _order_by: tuple[str, typing.Literal["asc", "desc"]] | None = None
    _filters: (
        list[
            tuple[
                typing.Callable[[GenericModel, str, typing.Any], bool],
                str,
                typing.Any,
            ]
        ]
        | None
    ) = None
    _offset: int | None = None
    _limit: int | None = None

    def __init_subclass__(cls):
        cls.database = Database()
        cls.load_data(cls())

    def __init__(self):
        self.reset_query()

    def reset_query(self):
        """
        Reset the query parameters to their default values.
        """
        self._query = None
        self._order_by = None
        self._filters = []
        self._offset = None
        self._limit = None
        return self

    """
    -----------------------------------------
         CRUD FUNCTIONS
    -----------------------------------------
    """

    def get(self, model: GenericModel, pk: int | str):
        """
        Get a model from the database.

        Args:
            model (Model): The model to get.
            pk (int | str): The primary key of the model.

        Returns:
            Model | None: The model if found, otherwise None.
        """
        return self.database[model.__class__].get(pk)

    def add(self, model: GenericModel):
        """
        Add a model to the database.

        Args:
            model (Model): The model to add.
        """
        self.database[model.__class__].add(model)

    def merge(self, model: GenericModel):
        """
        Merge a model into the database.

        This is similar to add, but it will update the model if it already exists.

        Args:
            model (Model): The model to merge.
        """
        pk = model.get_pk()
        if pk in self.database[model.__class__]:
            self.database[model.__class__][pk] = model
        else:
            self.add(model)
        return model

    def delete(self, model: GenericModel):
        """
        Delete a model from the database.

        Args:
            model (Model): The model to delete.
        """
        del self.database[model.__class__][model.get_pk()]

    """
    -----------------------------------------
         SESSION FUNCTIONS
    -----------------------------------------
    """

    def query(self, model_class: typing.Type[GenericModel]):
        """
        Set the model for the session.

        This also resets the query parameters.

        Args:
            model_class (typing.Type[GenericModel]): The model to set.

        Returns:
            GenericSession: The session instance.
        """
        self.reset_query()
        self._query = model_class
        return self

    def count(self):
        """
        Count the number of models in the database.

        Returns:
            int: The number of models.
        """
        return len(self.all())

    def first(self):
        """
        Get the first model from the database.

        Applies filters, orders, limits, and offsets.

        Resets the query parameters after executing the query.

        Raises:
            ValueError: If no model is set for the session.

        Returns:
            GenericModel | None: The model if found, otherwise None.
        """
        items = self.all()
        return items[0] if items else None

    def all(self):
        """
        Get all models from the database.

        Applies filters, orders, limits, and offsets.

        Resets the query parameters after executing the query.

        Args:
            model (GenericModel): The model to get.

        Raises:
            ValueError: If no model is set for the session.

        Returns:
            List[GenericModel]: The models.
        """
        # Get the items from the database
        if self._query is None:
            raise ValueError(
                "No model set for the session. Use query() to set a model."
            )

        model_class = self._query
        items = list(self.database[model_class].values())

        # Filter the items based on the filters
        if self._filters:
            items = [
                item
                for item in items
                if all(
                    filter_cmd[0](item, filter_cmd[1], filter_cmd[2])
                    for filter_cmd in self._filters
                )
            ]

        # Sort the items based on the order_by
        if self._order_by:
            items = self._order_by_func(items)

        # Apply the offset
        if self._offset is not None:
            items = items[self._offset :]

        # Apply the limit
        if self._limit is not None:
            items = items[: self._limit]

        self.reset_query()
        return items

    def yield_per(self, _: int):
        """
        Should actually yield results in batches of size **yield_per**. But this is not needed in this case.
        """
        return self.all()

    def commit(self): ...

    def flush(self): ...

    def refresh(self, item): ...

    def close(self): ...

    """
    -----------------------------------------
         ORDER AND LIMIT FUNCTIONS
    -----------------------------------------
    """

    def order_by(self, column: str, direction: typing.Literal["asc", "desc"]):
        """
        Set the order by clause for the session.

        Args:
            column (str): The column to order by.
            direction (typing.Literal["asc", "desc"]): The direction to order by.

        Returns:
            GenericSession: The session instance.
        """
        self._order_by = (column, direction)
        return self

    def _order_by_func(self, data: list[GenericModel]):
        if not self._order_by:
            return data

        col_name, direction = self._order_by
        reverse_flag = direction == "desc"
        # patched as suggested by:
        # http://stackoverflow.com/questions/18411560/python-sort-list-with-none-at-the-end
        # and
        # http://stackoverflow.com/questions/5055942/sort-python-list-of-objects-by-date-when-some-are-none

        def col_name_if_not_none(data):
            """
            - sqlite sets to null unfilled fields.
            - sqlalchemy cast this to None
            - this is a killer if the datum is of type datetime.date:
            - it breaks a simple key=operator.attrgetter(col_name)
            approach.

            this function tries to patch the issue
            """
            op = operator.attrgetter(col_name)  # noqa
            missing = getattr(data, col_name) is not None
            return missing, getattr(data, col_name)

        return sorted(data, key=col_name_if_not_none, reverse=reverse_flag)

    def offset(self, offset: int):
        """
        Set the offset for the session.

        Args:
            offset (int): The offset to set.

        Returns:
            GenericSession: The session instance.
        """
        self._offset = offset
        return self

    def limit(self, limit: int):
        """
        Set the limit for the session.

        Args:
            limit (int): The limit to set.

        Returns:
            GenericSession: The session instance.
        """
        self._limit = limit
        return self

    """
    -----------------------------------------
         DATA FUNCTIONS
    -----------------------------------------
    """

    def load_data(self):
        """
        Override this method to load data when the session class is initialized.
        """
        pass

    def save_data(self):
        """
        Override this method to save data when the FastAPI app is shutting down.
        """
        pass

    """
    -----------------------------------------
         FILTER FUNCTIONS
    -----------------------------------------
    """

    def text_contains(self, col_name: str, value):
        self._filters.append((self._text_contains, col_name, value))
        return self

    def _text_contains(
        self, item: GenericModel, col_name: str, value, *, silent=True
    ) -> bool:
        try:
            col_value = str(getattr(item, col_name))
            col_value = col_value.lower()
            value = str(value)
            value = value.lower().strip()
            return value in col_value
        except Exception:
            if not silent:
                raise
            return False

    def starts_with(self, col_name: str, value):
        self._filters.append((self._starts_with, col_name, value))
        return self

    def _starts_with(
        self, item: GenericModel, col_name: str, value, *, silent=True
    ) -> bool:
        try:
            col_value = self._convert_value(item, col_name, getattr(item, col_name))
            col_value = col_value.lower()
            value = self._convert_value(item, col_name, value)
            value = value.lower()
            return col_value.startswith(value)
        except Exception:
            if not silent:
                raise
            return False

    def not_starts_with(self, col_name: str, value):
        self._filters.append((self._not_starts_with, col_name, value))
        return self

    def _not_starts_with(self, item: GenericModel, col_name: str, value):
        try:
            return not self._starts_with(item, col_name, value, silent=False)
        except Exception:
            return False

    def ends_with(self, col_name: str, value):
        self._filters.append((self._ends_with, col_name, value))
        return self

    def _ends_with(
        self, item: GenericModel, col_name: str, value, *, silent=True
    ) -> bool:
        try:
            col_value = self._convert_value(item, col_name, getattr(item, col_name))
            col_value = col_value.lower()
            value = self._convert_value(item, col_name, value)
            value = value.lower()
            return col_value.endswith(value)
        except Exception:
            if not silent:
                raise
            return False

    def not_ends_with(self, col_name: str, value):
        self._filters.append((self._not_ends_with, col_name, value))
        return self

    def _not_ends_with(self, item: GenericModel, col_name: str, value):
        try:
            return not self._ends_with(item, col_name, value, silent=False)
        except Exception:
            return False

    def greater(self, col_name: str, value):
        self._filters.append((self._greater, col_name, value))
        return self

    def _greater(self, item: GenericModel, col_name: str, value) -> bool:
        return self._compare(item, col_name, value, ">")

    def greater_equal(self, col_name: str, value):
        self._filters.append((self._greater_equal, col_name, value))
        return self

    def _greater_equal(self, item: GenericModel, col_name: str, value) -> bool:
        return self._compare(item, col_name, value, ">=")

    def smaller(self, col_name: str, value):
        self._filters.append((self._smaller, col_name, value))
        return self

    def _smaller(self, item: GenericModel, col_name: str, value):
        return self._compare(item, col_name, value, "<")

    def smaller_equal(self, col_name: str, value):
        self._filters.append((self._smaller_equal, col_name, value))
        return self

    def _smaller_equal(self, item: GenericModel, col_name: str, value):
        return self._compare(item, col_name, value, "<=")

    def like(self, col_name: str, value):
        self._filters.append((self._like, col_name, value))
        return self

    def _like(self, item: GenericModel, col_name: str, value, *, silent=True):
        try:
            col_value = str(
                self._convert_value(item, col_name, getattr(item, col_name))
            )
            value = self._convert_value(item, col_name, value)
            value = value.split(" ")
            return any(v in col_value for v in value)
        except Exception:
            if not silent:
                raise
            return False

    def not_like(self, col_name: str, value):
        self._filters.append((self._not_like, col_name, value))
        return self

    def _not_like(self, item: GenericModel, col_name: str, value):
        try:
            return not self._like(item, col_name, value, silent=False)
        except Exception:
            return False

    def ilike(self, col_name: str, value):
        self._filters.append((self._ilike, col_name, value))
        return self

    def _ilike(self, item: GenericModel, col_name: str, value):
        try:
            col_value = str(
                self._convert_value(item, col_name, getattr(item, col_name))
            )
            col_value = col_value.lower()
            value = self._convert_value(item, col_name, value)
            value = value.lower()
            value = value.split(" ")
            return any(v in col_value for v in value)
        except Exception:
            return False

    def equal(self, col_name: str, value):
        self._filters.append((self._equal, col_name, value))
        return self

    def _equal(self, item: GenericModel, col_name: str, value, *, silent=True) -> bool:
        try:
            col_value = self._convert_value(item, col_name, getattr(item, col_name))
            value = self._convert_value(item, col_name, value)
            return col_value == value
        except Exception:
            if not silent:
                raise
            return False

    def not_equal(self, col_name: str, value):
        self._filters.append((self._not_equal, col_name, value))
        return self

    def _not_equal(self, item: GenericModel, col_name: str, value):
        try:
            return not self._equal(item, col_name, value, silent=False)
        except Exception:
            return False

    def in_(self, col_name: str, value):
        self._filters.append((self._in, col_name, value))
        return self

    def _in(self, item: GenericModel, col_name: str, value):
        try:
            col_value = self._convert_value(item, col_name, getattr(item, col_name))
            value = self._convert_value(item, col_name, value)
            return col_value in value
        except Exception:
            return False

    def global_filter(self, list_columns: list[str], value):
        self._filters.append((self._global_filter, list_columns, value))
        return self

    def _global_filter(self, item: GenericModel, list_columns: list[str], value):
        if not value:
            return True

        SEPARATOR = Setting.TEXT_FILTER_SEPARATOR
        values = [v.strip() for v in value.split(SEPARATOR) if v]

        for value in values:
            for col_name in list_columns:
                is_true = self._text_contains(item, col_name, value)
                if is_true:
                    return True
        return False

    def _compare(
        self,
        item: GenericModel,
        col_name: str,
        value,
        operator_func: typing.Literal["<", "<=", ">", ">="],
    ):
        if value is None:
            return False

        try:
            col_value = getattr(item, col_name)

            # Convert the column value and the value to be compared to the same type
            col_value = self._convert_value(item, col_name, col_value)
            value = self._convert_value(item, col_name, value)

            # Compare the converted values
            if operator_func == "<":
                return col_value < value
            elif operator_func == "<=":
                return col_value <= value
            elif operator_func == ">":
                return col_value > value
            elif operator_func == ">=":
                return col_value >= value
        except Exception:
            return False

    def _convert_value(self, item: GenericModel, col_name: str, value):
        # If date, convert to unix timestamp
        if isinstance(value, date):
            return datetime.strptime(value, "%Y-%m-%d").timestamp()
        elif isinstance(value, datetime):
            return value.timestamp()

        # Convert to the type of the item class column
        col_type = item.get_col_type(col_name)
        if isinstance(value, list):
            return [col_type(v) for v in value]
        else:
            return col_type(value)
