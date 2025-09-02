import collections
import json
import typing

import fastapi
import gremlin_python.process.graph_traversal
import gremlin_python.process.traversal
import janusgraph_python.process.traversal

from ...const import logger
from ...setting import Setting
from ...utils import lazy
from ..generic.exceptions import MultipleColumnsException
from ..generic.model import GenericModel, Mapper
from .column import GremlinColumn, GremlinRelationship
from .exceptions import GremlinMissingLabelException, LKMultipleException

__all__ = ["GremlinModel"]

UNSPECIFIED_LABEL = "__unspecified_label_"

try:
    import janusgraph_python

    janusgraph_python_exists = True
except ImportError:
    janusgraph_python_exists = False


class GremlinMapper(Mapper[GremlinColumn | GremlinRelationship]):
    lk: str | None = None
    """
    The label key of the model. Used to set the label from the database to the model. Defaults to `label`.
    """


class GremlinModel(GenericModel):
    """
    A base class for Gremlin models, which are used to represent vertices in a Gremlin graph.

    ## Example:

    ```python
    from fastapi_rtk import GremlinModel, GremlinColumn, GremlinRelationship, GremlinInterface, ModelRestApi
    from app import toolkit  # Assuming you have a `toolkit` instance set up for your FastAPI application.

    class User(GremlinModel):
        __label__ = "Person"

        id = GremlinColumn(str, primary_key=True) # Primary key of the model, typically the vertex ID in the graph.
        label = GremlinColumn(str, label_key=True, default="Person") # Label of the vertex. Label from the graph will be stored here.
        firstname = GremlinColumn(str, default="") # A property in the model, which will be stored as a property in the vertex.
        type = GremlinColumn(str, default="user") # A type of the model, which can be used to filter vertices in the graph.

        tasks = GremlinRelationship(
            list,
            name="related",  # The name of the edge in the graph.
            properties={"type": "task"},  # Additional properties to filter the edge.
            uselist=True,  # Whether the relationship is a list of related vertices.
            obj="Task",  # The model class that this relationship points to. If given, the related object can be added or edited.
            obj_properties={"type": "task"},  # Additional properties to filter the related vertex.
        )

        friends = GremlinRelationship(
            list,
            name="related",
            properties={"type": "friend"},
            uselist=True,
            with_edge=True,  # If True, the column will return a dictionary with two keys: "edge" and the property name. The "edge" key will contain the edge properties. If `obj` is set, the related object needs to have an `edge` property to hold the edge properties.
            direction="both",  # The direction of the relationship. Use "in" for incoming relationships, "out" for outgoing relationships, or "both" for both directions.
            obj_properties={"type": "user"},  # Additional properties to filter the related vertex.
        ) # Without `obj`, frontend will see the column as a simple dictionary.

    class Task(GremlinModel):
        __label__ = "Task"

        ... # Similar to User, but represents a task in the graph.

    class UserApi(ModelRestApi):
        resource_name = "users"  # The name of the API resource.
        datamodel = GremlinInterface(User)  # The data model for the API, which is the User model.

        ... # Additional API methods and configurations.

    toolkit.add_api(UserApi)  # Register the API with the toolkit.
    ```
    """

    __ignore_init__ = True
    __model_callbacks__: dict[
        str, list[typing.Callable[[typing.Type["GremlinModel"]], None]]
    ] = collections.defaultdict(list)

    __mapper__: GremlinMapper = lazy(lambda: GremlinMapper(), only_instance=False)
    """
    A mapper that contains the primary key, properties, and columns of the model.
    """

    def __init_subclass__(cls):
        if cls.__label__ is None:
            if not cls.__ignore_label__:
                raise GremlinMissingLabelException(
                    f"Gremlin model '{cls.__name__}' must have a label defined. If you want to ignore this, set '__ignore_label__ = True' in the class definition."
                )
            else:
                logger.info(
                    f"Gremlin model '{cls.__name__}' does not have a label defined. This will result in query of vertices without any filtering on label."
                )

        if cls.__name__ in GremlinModel.__model_callbacks__:
            for callback in GremlinModel.__model_callbacks__[cls.__name__]:
                callback(cls)
            del GremlinModel.__model_callbacks__[cls.__name__]

        # Do not ignore the init for subclasses of GremlinModel
        cls.__ignore_init__ = False
        super().__init_subclass__()
        cls.__mapper__.columns = [
            x
            for x in cls.__mapper__.columns
            if not isinstance(cls.__mapper__.properties[x], GremlinRelationship)
        ]
        for key, value in cls.__mapper__.properties.items():
            if value.label_key:
                if cls.__mapper__.lk and cls.__mapper__.lk != key:
                    raise LKMultipleException(
                        cls.__name__, "Only one label key is allowed"
                    )
                cls.__mapper__.lk = key

    __label__: str | None = None
    """
    The label of the model, used to filter vertices in Gremlin queries. If not set, the model will not be filtered by label, which may lead to unexpected results.
    """
    __properties__: dict[str, typing.Any] | None = None
    """
    Properties of the model, used to filter vertices in Gremlin queries.
    """
    __ignore_label__ = False
    """
    If set to True, the model will not require a label. This is useful for models that do not represent a specific vertex type, or when the label is not relevant for the model's functionality.
    """
    __session__: gremlin_python.process.graph_traversal.GraphTraversalSource = None
    """
    The session used for executing Gremlin queries. This is typically set by the interface.
    """
    __data__: dict[str, typing.Any] = None
    """
    The data of the model instance, typically set during initialization. You can get the whole data from the database by accessing this attribute.
    """
    __reserved_letters__ = lazy(lambda: Setting.JANUSGRAPH_RESERVED_LETTERS)
    """
    A list of reserved letters that cannot be used in the primary key of the model. This is to avoid conflicts with JanusGraph's internal representation of vertices and edges. Only used if `janusgraph_python` is available.
    """
    __janusgraph_python_exists__ = lazy(
        lambda: janusgraph_python_exists, only_instance=False
    )
    """
    A boolean indicating whether the `janusgraph_python` package is available.
    """

    def __init__(self, __table__=None, **kwargs):
        self.__table__ = __table__
        super().__init__(**kwargs)
        self.__data__ = kwargs

    @classmethod
    def from_gremlinpython(
        cls,
        data: dict[str, typing.Any],
        /,
        preserve_as_list: list[str] | None = None,
    ):
        """
        Create an instance of the model from a dictionary typically returned by a Gremlin query.

        Args:
            data (dict[str, typing.Any]): The dictionary to parse, typically from a Gremlin query with valueMap.
            preserve_as_list (list[str] | None, optional): A list of keys that should be preserved as lists even if they contain a single item. If None, all keys are treated normally. Defaults to None.

        Returns:
            GremlinModel: An instance of the model with properties set from the parsed data.
        """
        params = {"id_key": cls.__mapper__.pk, "preserve_as_list": preserve_as_list}
        if cls.__mapper__.lk:
            params["label_key"] = cls.__mapper__.lk
        parsed_data = cls.parse_from_gremlinpython(data, **params)
        for key in parsed_data.keys():
            column = cls.__mapper__.properties.get(key)
            if (
                not column
                or not isinstance(column, GremlinRelationship)
                or not column.obj
            ):
                continue
            value = parsed_data[key]
            if not value:
                continue
            if column.uselist:
                value = [column.obj.from_gremlinpython(v) for v in value]
            else:
                value = column.obj.from_gremlinpython(value)
            parsed_data[key] = value
        return cls(__table__=True, **parsed_data)

    def to_gremlinpython(self):
        """
        Convert the model instance to a Gremlin Python compatible dictionary.

        Returns:
            dict: A dictionary representation of the model instance suitable for Gremlin Python, with keys for the primary key and label, and other properties as they are.
        """
        return self.parse_to_gremlinpython(
            self.to_json(with_id=False, with_name=False),
            id_key=self.__mapper__.pk,
            label_key=self.__mapper__.lk,
        )

    def to_json(self, *, with_id=True, with_name=True):
        """
        Convert the model instance to a JSON-compatible dictionary.

        - Properties that are not set will be excluded from the output.
        - Properties that are instances of `GremlinModel` will be converted to their JSON representation.
        - Properties that are lists or tuples will have their items converted to JSON representations if they are instances of `GremlinModel`.

        Args:
            with_id (bool, optional): Whether to include the `id_` field in the output. Defaults to True.
            with_name (bool, optional): Whether to include the `name_` field in the output. Defaults to True.

        Returns:
            dict: A dictionary representation of the model instance, with keys for each property and the `id_` and `name_` fields if specified.
        """
        data = dict[str, typing.Any]()
        cls = self.__class__
        for key in self.__mapper__.properties.keys():
            if not getattr(cls, key).is_column_set(self):
                continue
            value = getattr(self, key)
            if isinstance(value, GremlinModel):
                value = value.to_json(with_id=with_id, with_name=with_name)
            elif isinstance(value, (list, tuple)):
                value = [
                    v.to_json(with_id=with_id, with_name=with_name)
                    if isinstance(v, GremlinModel)
                    else v
                    for v in value
                ]
            data[key] = value
        if with_id:
            data["id_"] = self.id_
        if with_name:
            data["name_"] = self.name_
        return data

    @staticmethod
    def parse_from_gremlinpython(
        data: dict[str, typing.Any],
        /,
        id_key="id",
        label_key="label",
        preserve_as_list: list[str] | None = None,
    ):
        """
        Parse a dictionary from Gremlin Python into a dictionary with specific keys.

        Args:
            data (dict[str, typing.Any]): The dictionary to parse, typically from a Gremlin query with valueMap.
            id_key (str, optional): The key for the primary key in the parsed dictionary. Defaults to "id".
            label_key (str, optional): The key for the label in the parsed dictionary. Defaults to "label".
            preserve_as_list (list[str] | None, optional): A list of keys that should be preserved as lists even if they contain a single item. If None, all keys are treated normally. Defaults to None.

        Returns:
            dict: A dictionary with keys for the primary key and label, and other properties as they are.
        """
        parsed = dict[str, typing.Any]()
        for key, value in data.items():
            if (
                (isinstance(value, list) or isinstance(value, tuple))
                and len(value) == 1
                and (preserve_as_list is None or key not in preserve_as_list)
            ):
                value = value[0]

            # A dictionary means it is coming from the database directly, and not a stringified JSON.
            if isinstance(value, dict):
                value = GremlinModel.parse_from_gremlinpython(value)
            elif isinstance(
                value, janusgraph_python.process.traversal.RelationIdentifier
            ):
                parsed["source"] = value.out_vertex_id
                parsed["target"] = value.in_vertex_id
                value = str(value)

            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                pass
            except TypeError:
                pass
            if key == gremlin_python.process.traversal.T.id:
                parsed[id_key] = value
            elif key == gremlin_python.process.traversal.T.label:
                parsed[label_key] = value
            else:
                parsed[key] = value
        return parsed

    @staticmethod
    def parse_to_gremlinpython(
        data: dict[str, typing.Any], /, id_key="id", label_key="label"
    ):
        """
        Convert a dictionary to a Gremlin Python compatible format.

        Args:
            data (dict[str, typing.Any]): The dictionary to convert.
            id_key (str): The key for the primary key in Gremlin Python.
            label_key (str): The key for the label in Gremlin Python.

        Returns:
            dict: A dictionary representation suitable for Gremlin Python.
        """
        result = dict[str, typing.Any]()
        for key, value in data.items():
            if isinstance(value, (list, tuple, dict)):
                value = json.dumps(value)
            if key == id_key:
                key = gremlin_python.process.traversal.T.id
            elif key == label_key:
                key = gremlin_python.process.traversal.T.label
            result[key] = value
        return result

    @staticmethod
    def _register_model_callback(
        model_name: str, callback: typing.Callable[[typing.Type["GremlinModel"]], None]
    ):
        """
        Register a callback for a model that will be called when the model is loaded.

        Args:
            model_name (str): The name of the model to register the callback for.
            callback (typing.Callable[[typing.Type["GremlinModel"]], None]): The callback function to register. It should accept a single argument, which is the model class itself.
        """
        GremlinModel.__model_callbacks__[model_name].append(callback)

    def is_model_valid(self):
        try:
            super().is_model_valid()
        except MultipleColumnsException:
            if not self.__table__:
                raise
        if not self.__janusgraph_python_exists__:
            return
        pk = self.get_pk()
        if isinstance(pk, str):
            for letter in self.__reserved_letters__:
                if letter in pk:
                    raise fastapi.HTTPException(
                        fastapi.status.HTTP_400_BAD_REQUEST,
                        f"Primary key '{pk}' contains reserved letter '{letter}'. "
                        "Please use a different primary key.",
                    )
