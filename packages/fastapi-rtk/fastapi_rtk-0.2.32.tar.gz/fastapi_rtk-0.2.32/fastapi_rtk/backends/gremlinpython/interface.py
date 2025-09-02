import json
import typing

import fastapi
import gremlin_python.process.graph_traversal
import gremlin_python.process.traversal

from ...bases.db import DBQueryParams
from ...bases.filter import AbstractBaseFilter
from ...bases.interface import AbstractInterface
from ...const import logger
from ...exceptions import raise_exception
from ...utils import T, lazy_self, safe_call_sync, smart_run, use_default_when_none
from ..generic.interface import GenericInterface
from .column import GremlinColumn, GremlinRelationship, OnBeforeCreateParams
from .db import GremlinQueryBuilder
from .filters import GremlinFilterConverter
from .model import UNSPECIFIED_LABEL, GremlinModel
from .session import get_graph_traversal_factory

__all__ = ["GremlinInterface"]


class lazy(lazy_self["GremlinInterfaceMixin", T]): ...


class GremlinInterfaceMixin(
    AbstractInterface[
        GremlinModel,
        gremlin_python.process.graph_traversal.GraphTraversalSource,
        GremlinColumn | GremlinRelationship,
    ],
):
    """
    Mixins for GremlinInterface
    """

    filter_converter = GremlinFilterConverter()
    global_filter_class = lazy(
        lambda: raise_exception(
            "global_filter_class for GremlinInterface is not yet available",
            AbstractBaseFilter,
        )
    )

    # Query builders
    query = lazy(lambda self: GremlinQueryBuilder(self))
    query_count = lazy(lambda self: GremlinQueryBuilder(self))

    def __init__(self, obj, with_fk=True):
        AbstractInterface.__init__(self, obj, with_fk)

    """
    --------------------------------------------------------------------------------------------------------
        DEPENDENCIES METHODS
    --------------------------------------------------------------------------------------------------------
    """

    def get_session_factory(self):
        def get_graph_traversal_interface(
            traversal=fastapi.Depends(get_graph_traversal_factory()),
        ):
            self.obj.__session__ = traversal
            return traversal

        return get_graph_traversal_interface

    def get_download_session_factory(self):
        def get_graph_traversal_interface(
            traversal=fastapi.Depends(get_graph_traversal_factory(True)),
        ):
            self.obj.__session__ = traversal
            return traversal

        return get_graph_traversal_interface

    """
    --------------------------------------------------------------------------------------------------------
        COUNT AND CRUD METHODS
    --------------------------------------------------------------------------------------------------------
    """

    async def count(self, session, params=None) -> int:
        relevant_params = params.copy() if params else DBQueryParams()
        relevant_params.pop("list_columns", None)
        relevant_params.pop("page", None)
        relevant_params.pop("page_size", None)
        relevant_params.pop("order_column", None)
        relevant_params.pop("order_direction", None)
        self.query_count.statement = self._init_traversal(session)
        statement = await self.query_count.build_query(relevant_params)
        return await smart_run(statement.count().next)

    async def get_many(self, session, params=None) -> list[GremlinModel]:
        self.query.statement = self._init_traversal(session)
        statement = await self.query.build_query(params)
        if "list_columns" not in params:
            statement = self.query.apply_list_columns(statement, [])
        result = await smart_run(statement.toList)
        items = []
        for res in result:
            item = self._handle_data_from_gremlinpython(res, self._get_rel_parser())
            items.append(item)
        items = [
            self.obj.from_gremlinpython(
                item,
                preserve_as_list=[
                    x
                    for x in self.get_relation_columns()
                    if self.list_properties[x].uselist
                ],
            )
            for item in items
        ]
        return items

    async def get_one(self, session, params=None):
        self.query.statement = self._init_traversal(session)
        statement = await self.query.build_query(params)
        if "list_columns" not in params:
            statement = self.query.apply_list_columns(statement, [])
        has_next = await smart_run(statement.hasNext)
        result = await smart_run(statement.next) if has_next else None
        if result is not None:
            return self.obj.from_gremlinpython(
                self._handle_data_from_gremlinpython(result, self._get_rel_parser()),
                preserve_as_list=[
                    x
                    for x in self.get_relation_columns()
                    if self.list_properties[x].uselist
                ],
            )

    async def yield_per(self, session, params=None):
        relevant_params = params.copy() if params else DBQueryParams()
        relevant_params.pop("page", None)
        page_size = relevant_params.pop("page_size", 100)
        items = await self.get_many(session, relevant_params)
        while True:
            chunk = items[:page_size]
            items = items[page_size:]
            if not chunk:
                break
            yield chunk
        await smart_run(self.close, session)

    def add(self, session, item, *, flush=True, commit=True, refresh=True):
        original_session = session
        callbacks: list[typing.Callable] = []
        statement = self._init_traversal(session, type="add")
        data = item.to_gremlinpython()
        for key, value in data.items():
            if value is None:
                continue
            elif key is gremlin_python.process.traversal.T.label and item.__label__:
                continue
            elif self.is_relation(key):
                value = json.loads(value) if value else []
                if not isinstance(value, list):
                    value = [value]
                model_cls = self.list_properties[key].obj
                for index, val in enumerate(value):
                    source = data[gremlin_python.process.traversal.T.id]
                    target = val[model_cls.__mapper__.pk]
                    properties = self.list_properties[key].properties
                    if self.list_properties[key].direction != "out":
                        source, target = target, source
                    if self.list_properties[key].on_before_create:
                        source_model = item
                        target_model = getattr(item, key)[index]
                        if self.list_properties[key].direction != "out":
                            source_model, target_model = target_model, source_model
                        params = OnBeforeCreateParams(
                            session=session,
                            source=source,
                            target=target,
                            edge_name=self.list_properties[key].name,
                            properties=self.list_properties[key].properties,
                        )
                        additional_properties = safe_call_sync(
                            self.list_properties[key].on_before_create(
                                source_model, target_model, params
                            )
                        )
                        if additional_properties:
                            properties = {**(properties or {}), **additional_properties}
                    callbacks.append(
                        lambda s,
                        source=source,
                        target=target,
                        edge_name=self.list_properties[key].name,
                        properties=properties: self.create_edge(
                            s, source, target, edge_name, properties
                        )
                    )
                continue
            statement = statement.property(key, value)
        item = item.from_gremlinpython(statement.valueMap(True).next())
        for callback in callbacks:
            callback(original_session)
        return item

    def edit(self, session, item, *, flush=True, commit=True, refresh=False):
        original_session = session
        callbacks: list[typing.Callable] = []
        data = item.to_gremlinpython()
        statement = self._init_traversal(session, item=item)
        for key, value in data.items():
            if key in self.get_pk_attrs():
                raise ValueError(
                    "Primary key cannot be updated in Gremlin. Use a new instance instead."
                )
            elif value is None and not self.is_relation(key):
                statement = statement.properties(key).drop()
                continue
            elif (
                key is gremlin_python.process.traversal.T.id
                or key is gremlin_python.process.traversal.T.label
            ):
                continue
            elif self.is_relation(key):
                value = json.loads(value) if value else []
                if not isinstance(value, list):
                    value = [value]
                model_cls = self.list_properties[key].obj
                direction = self.list_properties[key].direction
                targets = [val[model_cls.__mapper__.pk] for val in value]
                properties_mapping = {}
                if self.list_properties[key].on_before_create:
                    for target_model in getattr(item, key, []):
                        source_model = item
                        if direction != "out":
                            source_model, target_model = target_model, source_model
                        params = OnBeforeCreateParams(
                            session=session,
                            source=source_model.get_pk(),
                            target=target_model.get_pk(),
                            edge_name=self.list_properties[key].name,
                            properties=self.list_properties[key].properties,
                        )
                        additional_properties = safe_call_sync(
                            self.list_properties[key].on_before_create(
                                source_model, target_model, params
                            )
                        )
                        if additional_properties:
                            properties_mapping[target_model.get_pk()] = (
                                additional_properties
                            )
                callbacks.append(
                    lambda s,
                    source=item.get_pk(),
                    targets=targets,
                    edge_name=self.list_properties[key].name,
                    properties=self.list_properties[key].properties,
                    direction=direction,
                    properties_mapping=properties_mapping: self.sync_edges(
                        s,
                        source,
                        targets,
                        edge_name,
                        properties,
                        direction,
                        properties_mapping=properties_mapping,
                    )
                )
                continue
            statement = statement.property(key, value)
        item = item.from_gremlinpython(statement.valueMap(True).next())
        for callback in callbacks:
            callback(original_session)
        return item

    def delete(self, session, item, *, flush=True, commit=True):
        statement = self._init_traversal(session, item=item)
        statement.drop().iterate()

    """
    --------------------------------------------------------------------------------------------------------
        SESSION METHODS - to be implemented
    --------------------------------------------------------------------------------------------------------
    """

    async def commit(self, session):
        pass

    def close(self, session):
        session.remote_connection.close()
        logger.info(f"Connection {session.remote_connection} closed.")

    """
    --------------------------------------------------------------------------------------------------------
        GET METHODS
    --------------------------------------------------------------------------------------------------------
    """

    def get_add_column_list(self):
        return [
            x
            for x in self.get_user_column_list()
            if x != self.obj.__mapper__.lk and self.is_valid_column(x)
        ]

    def get_edit_column_list(self):
        return [
            x
            for x in self.get_user_column_list()
            if x != self.obj.__mapper__.lk and self.is_valid_column(x)
        ]

    def get_order_column_list(self, list_columns):
        return [x for x in list_columns if x in self.list_columns]

    def get_search_column_list(self, list_columns):
        return [x for x in list_columns if x in self.list_properties]

    def get_type_name(self, col):
        if self.is_relation_one_to_one(col) or self.is_relation_many_to_one(col):
            return "Related"
        elif self.is_relation_one_to_many(col) or self.is_relation_many_to_many(col):
            return "RelatedList"
        return super().get_type_name(col)

    async def get_column_info(
        self,
        col,
        session,
        session_count,
        *,
        params=None,
        description_columns=None,
        label_columns=None,
    ):
        if self.is_relation(col) and self.list_properties[col].obj_properties:
            params = params or DBQueryParams()
            params["where"] = params.get("where", [])
            if not isinstance(params["where"], list):
                params["where"] = [params["where"]]
            for key, value in self.list_properties[col].obj_properties.items():
                params["where"].append((key, value))

        return await super().get_column_info(
            col,
            session,
            session_count,
            params=params,
            description_columns=description_columns,
            label_columns=label_columns,
        )

    """
    --------------------------------------------------------------------------------------------------------
        LIFESPAN METHODS
    --------------------------------------------------------------------------------------------------------
    """

    async def on_shutdown(self):
        pass

    """
    --------------------------------------------------------------------------------------------------------
        RELATED MODEL METHODS
    --------------------------------------------------------------------------------------------------------
    """

    def get_related_model(self, col_name):
        if self.is_relation(col_name):
            return self.list_properties[col_name].obj

        raise ValueError(f"{col_name} is not a relation")

    """
    --------------------------------------------------------------------------------------------------------
        IS METHODS
    --------------------------------------------------------------------------------------------------------
    """

    def is_relation(self, col_name):
        try:
            return (
                col_name in self.get_relation_columns()
                and self.list_properties[col_name].obj is not None
                and self.list_properties[col_name].direction != "both"
            )
        except Exception:
            return False

    def is_relation_one_to_one(self, col_name):
        if not self.is_relation(col_name):
            return False
        try:
            return not self.list_properties[col_name].uselist
        except Exception:
            return False

    def is_relation_one_to_many(self, col_name):
        if not self.is_relation(col_name):
            return False
        try:
            return self.list_properties[col_name].uselist
        except Exception:
            return False

    def is_relation_many_to_one(self, col_name):
        return self.is_relation_one_to_one(col_name)

    def is_relation_many_to_many(self, col_name):
        return self.is_relation_one_to_many(col_name)

    """
    --------------------------------------------------------------------------------------------------------
        IS METHODS - ONLY IN GremlinInterface
    --------------------------------------------------------------------------------------------------------
    """

    def is_valid_column(self, col_name: str):
        """
        Checks if the given column name is a valid column for the Gremlin model.

        - If the column is an instance of GremlinColumn and not a GremlinRelationship, it is valid.
        - If the column is a GremlinRelationship and it is a relation, it is valid.

        Args:
            col_name (str): The name of the column to check.

        Returns:
            bool: True if the column is valid, False otherwise.
        """
        col = self.list_properties[col_name]
        if isinstance(col, GremlinColumn) and not isinstance(col, GremlinRelationship):
            return True
        elif isinstance(col, GremlinRelationship) and self.is_relation(col_name):
            return True
        return False

    """
    --------------------------------------------------------------------------------------------------------
        GET METHODS - ONLY IN GremlinInterface
    --------------------------------------------------------------------------------------------------------
    """

    def get_relation_columns(self):
        return [
            k
            for k, v in self.list_properties.items()
            if isinstance(v, GremlinRelationship)
        ]

    """
    --------------------------------------------------------------------------------------------------------
        HELPER METHODS
    --------------------------------------------------------------------------------------------------------
    """

    @staticmethod
    def get_edges(
        session: gremlin_python.process.graph_traversal.GraphTraversalSource,
        source: str,
        edge_name: str,
        properties: dict[str, typing.Any] | None = None,
        direction: typing.Literal["out", "in", "both"] = "out",
    ) -> list[dict[str, typing.Any]]:
        """
        Retrieves edges from a vertex in the Gremlin graph.

        Args:
            session (GraphTraversalSource): The Gremlin session to use for the operation.
            source (str): The ID of the source vertex.
            edge_name (str): The name of the edge to retrieve.
            properties (dict[str, typing.Any], optional): Properties to filter the edges.
            direction (str, optional): The direction of the edges. Can be 'out', 'in', or 'both'. Defaults to 'out'.

        Returns:
            list[dict[str, typing.Any]]: A list of edges with their properties.
        """
        traversal = session.V(source)
        if direction == "out":
            traversal = traversal.outE(edge_name)
        elif direction == "in":
            traversal = traversal.inE(edge_name)
        elif direction == "both":
            traversal = traversal.bothE(edge_name)
        else:
            raise ValueError("Direction must be 'out', 'in', or 'both'.")
        if properties:
            for key, value in properties.items():
                traversal = traversal.has(key, value)
        edges = traversal.valueMap(True).toList()
        return [
            GremlinModel.parse_from_gremlinpython({"edge": x})["edge"] for x in edges
        ]

    @staticmethod
    def create_edge(
        session: gremlin_python.process.graph_traversal.GraphTraversalSource,
        source: str,
        target: str,
        edge_name: str,
        properties: dict[str, typing.Any] | None = None,
    ):
        """
        Creates an edge between two vertices in the Gremlin graph.

        Args:
            session (GraphTraversalSource): The Gremlin session to use for the operation.
            source (str): The ID of the source vertex.
            target (str): The ID of the target vertex.
            edge_name (str): The name of the edge to create.
            properties (dict[str, typing.Any], optional): Properties to set on the edge.

        Returns:
            None
        """
        traversal = (
            session.V(source)
            .addE(edge_name)
            .to(gremlin_python.process.graph_traversal.__.V(target))
        )
        if properties:
            for key, value in properties.items():
                traversal = traversal.property(key, value)
        traversal.iterate()

    @staticmethod
    def delete_edge(
        session: gremlin_python.process.graph_traversal.GraphTraversalSource,
        source: str,
        target: str,
        edge_name: str,
        properties: dict[str, typing.Any] | None = None,
    ):
        """
        Deletes an edge between two vertices in the Gremlin graph.

        Args:
            session (GraphTraversalSource): The Gremlin session to use for the operation.
            source (str): The ID of the source vertex.
            target (str): The ID of the target vertex.
            edge_name (str): The name of the edge to delete.
            properties (dict[str, typing.Any], optional): Properties to filter the edge to delete.

        Returns:
            None
        """
        traversal = (
            session.V(source)
            .outE(edge_name)
            .where(gremlin_python.process.graph_traversal.__.inV().hasId(target))
        )
        if properties:
            for key, value in properties.items():
                traversal = traversal.has(key, value)
        traversal.drop().iterate()

    @staticmethod
    def delete_edge_by_id(
        session: gremlin_python.process.graph_traversal.GraphTraversalSource,
        edge_id: str,
    ):
        """
        Deletes an edge by its ID in the Gremlin graph.

        Args:
            session (GraphTraversalSource): The Gremlin session to use for the operation.
            edge_id (str): The ID of the edge to delete.

        Returns:
            None
        """
        session.E(edge_id).drop().iterate()

    @staticmethod
    def sync_edges(
        session: gremlin_python.process.graph_traversal.GraphTraversalSource,
        source: str,
        targets: list[str],
        edge_name: str,
        properties: dict[str, typing.Any] | None = None,
        direction: typing.Literal["out", "in"] = "out",
        *,
        properties_mapping: dict[str, dict[str, typing.Any]] | None = None,
    ):
        """
        Synchronizes edges between a source vertex and multiple target vertices in the Gremlin graph.

        This method will delete edges that exist in the source but not in the targets,
        and create edges for targets that do not have an edge from the source.

        Args:
            session (GraphTraversalSource): The Gremlin session to use for the operation.
            source (str): The ID of the source vertex.
            targets (list[str]): A list of IDs of target vertices.
            edge_name (str): The name of the edge to synchronize.
            properties (dict[str, typing.Any], optional): Properties to set on the edges.
            direction (str, optional): The direction of the edges. Can be 'out' or 'in'. Defaults to 'out'.

        Returns:
            None
        """
        if direction not in ["out", "in"]:
            raise ValueError("Direction must be 'out' or 'in'.")
        existing_edges = GremlinInterface.get_edges(
            session, source, edge_name, properties, direction
        )
        key = "target" if direction == "out" else "source"
        to_be_deleted = [
            edge["id"] for edge in existing_edges if edge[key] not in targets
        ]
        to_be_created = [
            target
            for target in targets
            if target not in [edge[key] for edge in existing_edges]
        ]
        for edge_id in to_be_deleted:
            GremlinInterface.delete_edge_by_id(session, edge_id)
        for target in to_be_created:
            GremlinInterface.create_edge(
                session,
                source if key == "target" else target,
                target if key == "target" else source,
                edge_name,
                {
                    **(properties or {}),
                    **(
                        properties_mapping.get(target, {}) if properties_mapping else {}
                    ),
                },
            )

    def _get_rel_parser(self):
        """
        Returns a dictionary of relation parsers for the current object.
        The keys are the relation column names, and the values are the corresponding GremlinModel parsers.
        """
        return {
            k: self.list_properties[k].obj
            for k in [x for x in self.list_properties if self.is_relation(x)]
        }

    def _handle_data_from_gremlinpython(
        self, data: dict[str, typing.Any], rel_parser: dict[str, GremlinModel]
    ):
        """
        Handles the data returned from Gremlin Python and converts it to a dictionary suitable for the model.

        Args:
            data (dict[str, typing.Any]): The data returned from Gremlin Python.
            rel_parser (dict[str, GremlinModel]): A dictionary of relation parsers.

        Returns:
            dict[str, typing.Any]: A dictionary with the data formatted for the model.
        """
        item: dict[str, typing.Any] = data[self.obj.__label__ or UNSPECIFIED_LABEL]
        for key, value in data.items():
            if key == (self.obj.__label__ or UNSPECIFIED_LABEL):
                continue
            if self.list_properties[key].uselist:
                if not isinstance(value, list):
                    value = [value]
            else:
                if isinstance(value, list):
                    value = value[0] if value else None

            if value is None:
                continue
            parser = rel_parser.get(key, None)

            def func(data):
                func = self.obj.parse_from_gremlinpython
                if parser:
                    func = parser.from_gremlinpython
                    if self.list_properties[key].with_edge:
                        data = {**data[key], "edge": data["edge"]}
                result = func(
                    data,
                    preserve_as_list=[key]
                    if self.list_properties[key].uselist
                    else None,
                )
                if parser:
                    result = result.to_json()
                return result

            item[key] = (
                [func(data) for data in value]
                if self.list_properties[key].uselist
                else func(value)
            )
        return item

    def _init_traversal(
        self,
        session: gremlin_python.process.graph_traversal.GraphTraversalSource,
        *,
        type: typing.Literal["get", "add"] = "get",
        item: GremlinModel | None = None,
    ):
        """
        Initializes a Gremlin traversal for the given session and item.

        Args:
            session (gremlin_python.process.graph_traversal.GraphTraversalSource): The Gremlin session to use for the traversal.
            type (typing.Literal["get", "add"], optional): The type of traversal to initialize. Can be either "get" or "add". Defaults to "get".
            item (GremlinModel | None, optional): The item to use for the traversal. If None, the default object of the interface will be used. Defaults to None.

        Returns:
            gremlin_python.process.graph_traversal.GraphTraversal: The initialized traversal.
        """
        item = use_default_when_none(item, self.obj)
        traversal = session
        if type == "get":
            if item is self.obj:
                traversal = traversal.V()
            else:
                traversal = traversal.V(item.get_pk())
            if item.__label__:
                traversal = traversal.hasLabel(item.__label__)
            if item.__properties__:
                for key, value in item.__properties__.items():
                    traversal = traversal.has(key, value)
        elif type == "add":
            traversal = (
                traversal.addV(item.__label__) if item.__label__ else traversal.addV()
            )
            if item.__properties__:
                for key, value in item.__properties__.items():
                    traversal = traversal.property(key, value)
        return traversal


class GremlinInterface(GremlinInterfaceMixin, GenericInterface):
    """
    Represents an interface for a Gremlin model.
    """
