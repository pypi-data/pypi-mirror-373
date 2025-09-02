import contextlib

import fastapi
import gremlin_python.driver.driver_remote_connection
import gremlin_python.process.anonymous_traversal
import gremlin_python.process.graph_traversal
import gremlin_python.process.traversal

from ...bases.db import AbstractQueryBuilder
from ...const import logger
from ...setting import Setting
from ...utils import lazy
from .model import UNSPECIFIED_LABEL

try:
    import janusgraph_python.driver.serializer

    serializer = janusgraph_python.driver.serializer
except ImportError:
    logger.warning(
        "janusgraph_python is not installed. Some Gremlin features may not work as expected."
    )
    serializer = None

__all__ = ["GremlinQueryBuilder", "graph_db"]


class GremlinQueryBuilder(
    AbstractQueryBuilder[gremlin_python.process.graph_traversal.GraphTraversal]
):
    """
    A class that builds Gremlin queries for a graph database.
    """

    build_steps = list(reversed(AbstractQueryBuilder.DEFAULT_BUILD_STEPS))

    def __init__(self, datamodel, statement=None):
        try:
            super().__init__(datamodel, statement)
        except RuntimeError:
            pass

    def apply_list_columns(self, statement, list_columns):
        list_columns = list(
            dict.fromkeys(
                x.split(".")[0]
                for x in list_columns
                if x != self.datamodel.obj.__mapper__.pk
                and x != self.datamodel.obj.__mapper__.lk
                and x not in self.datamodel.get_property_column_list()
            )
        )
        relation_columns = [
            x for x in self.datamodel.get_relation_columns() if x in list_columns
        ]
        list_columns = [x for x in list_columns if x not in relation_columns]

        statement = statement.project(
            self.datamodel.obj.__label__ or UNSPECIFIED_LABEL, *relation_columns
        ).by(gremlin_python.process.graph_traversal.__.valueMap(True, *list_columns))

        for rel_col in relation_columns:
            direction = self.datamodel.list_properties[rel_col].direction
            sub_statement = gremlin_python.process.graph_traversal.__
            match direction:
                case "in":
                    sub_statement = sub_statement.inE
                case "out":
                    sub_statement = sub_statement.outE
                case "both":
                    sub_statement = sub_statement.bothE
            if self.datamodel.list_properties[rel_col].name:
                sub_statement = sub_statement(
                    self.datamodel.list_properties[rel_col].name
                )
            else:
                sub_statement = sub_statement()
            if self.datamodel.list_properties[rel_col].properties:
                for key, value in self.datamodel.list_properties[
                    rel_col
                ].properties.items():
                    sub_statement = sub_statement.has(key, value)
            sub_other_v_statement = (
                sub_statement.otherV()
                if not self.datamodel.list_properties[rel_col].with_edge
                else gremlin_python.process.graph_traversal.__.otherV()
            )
            if self.datamodel.list_properties[rel_col].obj_properties:
                for key, value in self.datamodel.list_properties[
                    rel_col
                ].obj_properties.items():
                    sub_other_v_statement = sub_other_v_statement.has(key, value)
            sub_other_v_statement = sub_other_v_statement.valueMap(True)
            if self.datamodel.list_properties[rel_col].with_edge:
                sub_statement = (
                    sub_statement.project("edge", rel_col)
                    .by(gremlin_python.process.graph_traversal.__.valueMap(True))
                    .by(sub_other_v_statement)
                )
            else:
                sub_statement = sub_other_v_statement
            sub_statement = sub_statement.fold()
            statement = statement.by(sub_statement)

        return statement

    def apply_pagination(self, statement, page, page_size):
        lower_range = page_size * (page or 0)
        return statement.range_(lower_range, lower_range + page_size)

    def apply_order_by(self, statement, order_column, order_direction):
        return statement.order().by(
            order_column,
            gremlin_python.process.traversal.Order.asc
            if order_direction == "asc"
            else gremlin_python.process.traversal.Order.desc,
        )

    def apply_where(self, statement, column, value):
        args = [column, value]
        func = statement.has
        if column.lower() == self.datamodel.obj.__mapper__.pk:
            func = statement.hasId
            args = args[1:]
        elif column.lower() == self.datamodel.obj.__mapper__.lk:
            func = statement.hasLabel
            args = args[1:]
        return func(*args)

    def apply_where_in(self, statement, column, values):
        args = [column, gremlin_python.process.traversal.within(values)]
        func = statement.has
        if column.lower() == self.datamodel.obj.__mapper__.pk:
            func = statement.hasId
            args = args[1:]
        elif column.lower() == self.datamodel.obj.__mapper__.lk:
            func = statement.hasLabel
            args = args[1:]
        return func(*args)

    def apply_filter(self, statement, filter):
        filter_classes = self.datamodel.filters.get(filter.col)
        filter_class = None
        for f in filter_classes:
            if f.arg_name == filter.opr:
                filter_class = f
                break
        if not filter_class:
            raise fastapi.HTTPException(
                status_code=400, detail=f"Invalid filter opr: {filter.opr}"
            )

        col = filter.col
        value = filter.value

        return self.apply_filter_class(statement, col, filter_class, value)

    def apply_filter_class(self, statement, col, filter_class, value):
        return filter_class.apply(statement, col, value)

    def apply_global_filter(self, statement, columns, global_filter):
        return super().apply_global_filter(statement, columns, global_filter)


class GremlinDatabaseSessionManager:
    gremlin_connection = lazy(lambda: Setting.GREMLIN_CONNECTION)

    @contextlib.contextmanager
    def connect(self, bind: str | None = None, keep_open=False):
        """
        Establishes a connection to the graph database.

        Args:
            bind (str | None, optional): The bind key to retrieve the connection for. If None, the default connection is returned. Defaults to None. UNUSED FOR NOW.
            keep_open (bool, optional): Whether to keep the connection open after use. Defaults to False.

        Yields:
            gremlin_python.driver.driver_remote_connection.DriverRemoteConnection: The graph database connection.
        """
        url, graph_object = self.gremlin_connection
        connection = (
            gremlin_python.driver.driver_remote_connection.DriverRemoteConnection(
                url,
                graph_object,
                # session=True, #! When true, can not add Edge
                message_serializer=serializer.JanusGraphSONSerializersV3d0()
                if serializer
                else None,
                **Setting.GREMLIN_CONNECTION_OPTIONS,
            )
        )
        try:
            if keep_open:
                logger.warning(
                    f"Connection {connection} is kept open. Make sure to close it manually when done."
                )
            yield connection
        except Exception:
            connection.rollback()
            raise
        finally:
            if keep_open:
                return
            connection.close()

    @contextlib.contextmanager
    def session(self, bind: str | None = None, keep_open=False):
        """
        Provides a graph database session for performing database operations.

        Args:
            bind (str | None, optional): The bind key to retrieve the session for. If None, the default session is returned. Defaults to None. UNUSED FOR NOW.
            keep_open (bool, optional): Whether to keep the connection open after use. Defaults to False.

        Yields:
            gremlin_python.process.graph_traversal.GraphTraversal: A graph traversal object for executing queries.
        """
        with self.connect(bind, keep_open) as connection:
            traversal = (
                gremlin_python.process.anonymous_traversal.traversal().withRemote(
                    connection
                )
            )
            traversal.remote_connection = connection
            yield traversal


graph_db = GremlinDatabaseSessionManager()
