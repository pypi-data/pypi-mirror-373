import datetime
import typing

import gremlin_python.process.graph_traversal
import gremlin_python.process.traversal

from ...const import logger

try:
    import janusgraph_python.process.traversal
except ImportError:
    logger.warning(
        "janusgraph_python is not installed. Some Gremlin features may not work as expected."
    )
    janusgraph_python = None

from ...bases.filter import AbstractBaseFilter

if typing.TYPE_CHECKING:
    from .interface import GremlinInterface

__all__ = [
    "GremlinBaseFilter",
    "GremlinBaseFilterRelationOneToOneOrManyToOne",
    "GremlinBaseFilterRelationOneToManyOrManyToMany",
    "GremlinFilterTextContains",
    "GremlinFilterEqual",
    "GremlinFilterNotEqual",
    "GremlinFilterStartsWith",
    "GremlinFilterNotStartsWith",
    "GremlinFilterEndsWith",
    "GremlinFilterNotEndsWith",
    "GremlinFilterContains",
    "GremlinFilterNotContains",
    "GremlinFilterGreater",
    "GremlinFilterSmaller",
    "GremlinFilterGreaterEqual",
    "GremlinFilterSmallerEqual",
    "GremlinFilterIn",
    "GremlinFilterBetween",
    "GremlinFilterRelationOneToOneOrManyToOneEqual",
    "GremlinFilterRelationOneToManyOrManyToManyIn",
    "GremlinFilterConverter",
]


class GremlinBaseFilter(
    AbstractBaseFilter[gremlin_python.process.graph_traversal.GraphTraversal]
):
    datamodel: "GremlinInterface"

    def _apply(
        self,
        statement: gremlin_python.process.graph_traversal.GraphTraversal,
        col: str,
        args: tuple[str, typing.Any],
    ):
        func = statement.has
        if col.lower() == self.datamodel.obj.__mapper__.pk:
            func = statement.hasId
            args = args[1:]
        elif col.lower() == self.datamodel.obj.__mapper__.lk:
            func = statement.hasLabel
            args = args[1:]
        return func(*args)


class GremlinBaseFilterRelationOneToOneOrManyToOne(GremlinBaseFilter):
    def _rel_apply(self, col: str, value: str):
        match self.datamodel.list_properties[col].direction:
            case "both":
                statement = gremlin_python.process.graph_traversal.__.bothE()
            case "in":
                statement = gremlin_python.process.graph_traversal.__.inE()
            case "out":
                statement = gremlin_python.process.graph_traversal.__.outE()
            case _:
                raise ValueError(
                    f"Invalid direction for relation: {col}, must be 'both', 'in' or 'out'."
                )
        if self.datamodel.list_properties[col].properties:
            for key, val in self.datamodel.list_properties[col].properties.items():
                statement = statement.has(key, val)
        statement = statement.otherV()
        if self.datamodel.list_properties[col].obj_properties:
            for key, val in self.datamodel.list_properties[col].obj_properties.items():
                statement = statement.has(key, val)
        return statement.hasId(value)


class GremlinBaseFilterRelationOneToManyOrManyToMany(
    GremlinBaseFilterRelationOneToOneOrManyToOne
):
    def _rel_apply(self, col, value: list[str]):
        return [super()._rel_apply(col, v) for v in value] if value else []


class GremlinFilterTextContains(GremlinBaseFilter):
    name = "Text contains"
    arg_name = "tc"

    def apply(self, statement, col, value):
        value_func = (
            janusgraph_python.process.traversal.Text.text_contains
            if janusgraph_python
            else gremlin_python.process.traversal.TextP.containing
        )

        statement = self._apply(statement, col, (col, value_func(value)))
        if janusgraph_python:
            statement = statement.fold().unfold()
        return statement


class GremlinFilterEqual(GremlinBaseFilter):
    name = "Equal to"
    arg_name = "eq"

    def apply(self, statement, col, value):
        return self._apply(statement, col, [col, value])


class GremlinFilterNotEqual(GremlinBaseFilter):
    name = "Not equal to"
    arg_name = "neq"

    def apply(self, statement, col, value):
        return self._apply(
            statement, col, [col, gremlin_python.process.traversal.P.neq(value)]
        )


class GremlinFilterStartsWith(GremlinBaseFilter):
    name = "Starts with"
    arg_name = "sw"

    def apply(self, statement, col, value):
        return self._apply(
            statement,
            col,
            (col, gremlin_python.process.traversal.TextP.startingWith(value)),
        )


class GremlinFilterNotStartsWith(GremlinBaseFilter):
    name = "Not starts with"
    arg_name = "nsw"

    def apply(self, statement, col, value):
        return self._apply(
            statement,
            col,
            (col, gremlin_python.process.traversal.TextP.notStartingWith(value)),
        )


class GremlinFilterEndsWith(GremlinBaseFilter):
    name = "Ends with"
    arg_name = "ew"

    def apply(self, statement, col, value):
        return self._apply(
            statement,
            col,
            (col, gremlin_python.process.traversal.TextP.endingWith(value)),
        )


class GremlinFilterNotEndsWith(GremlinBaseFilter):
    name = "Not ends with"
    arg_name = "new"

    def apply(self, statement, col, value):
        return self._apply(
            statement,
            col,
            (col, gremlin_python.process.traversal.TextP.notEndingWith(value)),
        )


class GremlinFilterContains(GremlinBaseFilter):
    name = "Contains"
    arg_name = "ct"

    def apply(self, statement, col, value):
        value_func = (
            janusgraph_python.process.traversal.Text.text_contains
            if janusgraph_python
            else gremlin_python.process.traversal.TextP.containing
        )

        statement = self._apply(statement, col, (col, value_func(value)))
        if janusgraph_python:
            statement = statement.fold().unfold()
        return statement


class GremlinFilterNotContains(GremlinBaseFilter):
    name = "Not contains"
    arg_name = "nct"

    def apply(self, statement, col, value):
        value_func = (
            janusgraph_python.process.traversal.Text.text_not_contains
            if janusgraph_python
            else gremlin_python.process.traversal.TextP.notContaining
        )

        return self._apply(statement, col, (col, value_func(value)))


class GremlinFilterGreater(GremlinBaseFilter):
    name = "Greater than"
    arg_name = "gt"

    def apply(self, statement, col, value):
        if isinstance(value, datetime.datetime):
            value = value.timestamp()
        elif isinstance(value, datetime.date):
            value = datetime.datetime.combine(value, datetime.datetime.min.time())

        return self._apply(
            statement, col, (col, gremlin_python.process.traversal.P.gt(value))
        )


class GremlinFilterSmaller(GremlinBaseFilter):
    name = "Smaller than"
    arg_name = "sm"

    def apply(self, statement, col, value):
        if isinstance(value, datetime.datetime):
            value = value.timestamp()
        elif isinstance(value, datetime.date):
            value = datetime.datetime.combine(value, datetime.datetime.min.time())

        return self._apply(
            statement, col, (col, gremlin_python.process.traversal.P.lt(value))
        )


class GremlinFilterGreaterEqual(GremlinBaseFilter):
    name = "Greater equal"
    arg_name = "gte"

    def apply(self, statement, col, value):
        if isinstance(value, datetime.datetime):
            value = value.timestamp()
        elif isinstance(value, datetime.date):
            value = datetime.datetime.combine(value, datetime.datetime.min.time())

        return self._apply(
            statement, col, (col, gremlin_python.process.traversal.P.gte(value))
        )


class GremlinFilterSmallerEqual(GremlinBaseFilter):
    name = "Smaller equal"
    arg_name = "lte"

    def apply(self, statement, col, value):
        if isinstance(value, datetime.datetime):
            value = value.timestamp()
        elif isinstance(value, datetime.date):
            value = datetime.datetime.combine(value, datetime.datetime.min.time())

        return self._apply(
            statement, col, (col, gremlin_python.process.traversal.P.lte(value))
        )


class GremlinFilterIn(GremlinBaseFilter):
    name = "One of"
    arg_name = "in"

    def apply(self, statement, col, value):
        return self._apply(
            statement, col, (col, gremlin_python.process.traversal.P.within(value))
        )


class GremlinFilterBetween(GremlinBaseFilter):
    name = "Between"
    arg_name = "bw"

    def apply(self, statement, col, value):
        if not isinstance(value, (list, tuple)) or len(value) != 2:
            raise ValueError("Value must be a list or tuple with two elements.")

        if isinstance(value[0], datetime.datetime):
            value = [v.timestamp() for v in value]
        elif isinstance(value[0], datetime.date):
            value = [
                datetime.datetime.combine(v, datetime.datetime.min.time())
                for v in value
            ]

        return self._apply(
            statement,
            col,
            (col, gremlin_python.process.traversal.P.between(*value)),
        )


class GremlinFilterRelationOneToOneOrManyToOneEqual(
    GremlinBaseFilterRelationOneToOneOrManyToOne, GremlinFilterEqual
):
    arg_name = "rel_o_m"

    def apply(self, statement, col, value):
        return statement.where(self._rel_apply(col, value))


class GremlinFilterRelationOneToManyOrManyToManyIn(
    GremlinBaseFilterRelationOneToManyOrManyToMany, GremlinFilterEqual
):
    name = "In"
    arg_name = "rel_m_m"

    def apply(self, statement, col, value):
        for filter in self._rel_apply(col, value):
            statement = statement.where(filter)
        return statement


class GremlinFilterConverter:
    """
    Helper class to get available filters for a gremlin column type.
    """

    conversion_table = (
        (
            "is_relation_one_to_one",
            [
                GremlinFilterRelationOneToOneOrManyToOneEqual,
                # GremlinFilterRelationOneToOneOrManyToOneNotEqual, # TODO: Not implemented yet
                # FilterTextContains,
            ],
        ),
        (
            "is_relation_many_to_one",
            [
                GremlinFilterRelationOneToOneOrManyToOneEqual,
                # GremlinFilterRelationOneToOneOrManyToOneNotEqual, # TODO: Not implemented yet
                # FilterTextContains,
            ],
        ),
        (
            "is_relation_one_to_many",
            [
                GremlinFilterRelationOneToManyOrManyToManyIn,
                # GremlinFilterRelationOneToManyOrManyToManyNotIn, # TODO: Not implemented yet
                # FilterTextContains,
            ],
        ),
        (
            "is_relation_many_to_many",
            [
                GremlinFilterRelationOneToManyOrManyToManyIn,
                # GremlinFilterRelationOneToManyOrManyToManyNotIn, # TODO: Not implemented yet
                # FilterTextContains,
            ],
        ),
        (
            "is_enum",
            [
                GremlinFilterTextContains,
                GremlinFilterEqual,
                GremlinFilterNotEqual,
                GremlinFilterIn,
            ],
        ),
        (
            "is_boolean",
            [GremlinFilterEqual, GremlinFilterNotEqual],
        ),
        (
            "is_text",
            [
                GremlinFilterTextContains,
                GremlinFilterStartsWith,
                GremlinFilterNotStartsWith,
                GremlinFilterEndsWith,
                GremlinFilterNotEndsWith,
                GremlinFilterContains,
                GremlinFilterNotContains,
                GremlinFilterEqual,
                GremlinFilterNotEqual,
                GremlinFilterIn,
            ],
        ),
        (
            "is_string",
            [
                GremlinFilterTextContains,
                GremlinFilterStartsWith,
                GremlinFilterNotStartsWith,
                GremlinFilterEndsWith,
                GremlinFilterNotEndsWith,
                GremlinFilterContains,
                GremlinFilterNotContains,
                GremlinFilterEqual,
                GremlinFilterNotEqual,
                GremlinFilterIn,
            ],
        ),
        (
            "is_json",
            [
                GremlinFilterTextContains,
                GremlinFilterStartsWith,
                GremlinFilterNotStartsWith,
                GremlinFilterEndsWith,
                GremlinFilterNotEndsWith,
                GremlinFilterContains,
                GremlinFilterNotContains,
                GremlinFilterEqual,
                GremlinFilterNotEqual,
                GremlinFilterIn,
            ],
        ),
        (
            "is_integer",
            [
                GremlinFilterBetween,
                GremlinFilterEqual,
                GremlinFilterNotEqual,
                GremlinFilterGreater,
                GremlinFilterSmaller,
                GremlinFilterGreaterEqual,
                GremlinFilterSmallerEqual,
                GremlinFilterIn,
            ],
        ),
        (
            "is_date",
            [
                GremlinFilterBetween,
                GremlinFilterEqual,
                GremlinFilterNotEqual,
                GremlinFilterGreater,
                GremlinFilterSmaller,
                GremlinFilterGreaterEqual,
                GremlinFilterSmallerEqual,
                GremlinFilterIn,
            ],
        ),
        (
            "is_datetime",
            [
                GremlinFilterBetween,
                GremlinFilterEqual,
                GremlinFilterNotEqual,
                GremlinFilterGreater,
                GremlinFilterSmaller,
                GremlinFilterGreaterEqual,
                GremlinFilterSmallerEqual,
                GremlinFilterIn,
            ],
        ),
    )
