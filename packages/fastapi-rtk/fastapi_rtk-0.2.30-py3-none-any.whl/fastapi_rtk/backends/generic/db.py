import typing

from fastapi import HTTPException

from ...bases.db import AbstractQueryBuilder
from ...utils import lazy
from .session import GenericSession

if typing.TYPE_CHECKING:
    from .interface import GenericInterface

__all__ = ["GenericQueryBuilder"]


class GenericQueryBuilder(AbstractQueryBuilder[GenericSession]):
    datamodel: "GenericInterface"

    def __init__(self, datamodel, statement: typing.Type[GenericSession]):
        self._statement = statement()
        type(self).statement = lazy(
            lambda self: self._statement.query(self.datamodel.obj), cache=False
        )
        type(self).statement.__set_name__(type(self), "statement")
        super().__init__(datamodel)

    def apply_list_columns(self, statement, list_columns):
        # Nothing to be loaded, since everything is loaded by default
        return statement

    def apply_pagination(self, statement, page, page_size):
        return statement.offset(page * page_size).limit(page_size)

    def apply_order_by(self, statement, order_column, order_direction):
        col = order_column.lstrip().rstrip()

        #! If the order column comes from a request, it will be in the format ClassName.column_name
        if col.startswith(self.datamodel.obj.__class__.__name__) or col.startswith(
            self.datamodel.obj.__name__
        ):
            col = col.split(".", 1)[1]

        return statement.order_by(col, order_direction)

    def apply_where(self, statement, column, value):
        return statement.equal(column, value)

    def apply_where_in(self, statement, column, values):
        return statement.in_(column, values)

    def apply_filter(self, statement, filter):
        filter_classes = self.datamodel.filters.get(filter.col)
        filter_class = None
        for f in filter_classes:
            if f.arg_name == filter.opr:
                filter_class = f
                break
        if not filter_class:
            raise HTTPException(
                status_code=400, detail=f"Invalid filter opr: {filter.opr}"
            )

        col = filter.col
        value = filter.value

        return self.apply_filter_class(statement, col, filter_class, value)

    def apply_filter_class(self, statement, col, filter_class, value):
        return filter_class.apply(statement, col, value)

    def apply_global_filter(self, statement, columns, global_filter):
        return self.apply_filter_class(
            statement,
            columns,
            self.datamodel.global_filter_class(self.datamodel),
            global_filter,
        )
