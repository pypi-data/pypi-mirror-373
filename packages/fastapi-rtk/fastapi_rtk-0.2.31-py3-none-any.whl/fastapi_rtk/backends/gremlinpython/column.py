import typing

import gremlin_python.process.graph_traversal
import pydantic

from ...utils import T, use_default_when_none
from ..generic.column import UNSET, GenericColumn, _Unset

if typing.TYPE_CHECKING:
    from .model import GremlinModel

__all__ = ["GremlinColumn", "GremlinRelationship"]


class OnBeforeCreateParams(typing.TypedDict):
    session: gremlin_python.process.graph_traversal.GraphTraversalSource
    source: str
    target: str
    edge_name: str
    properties: dict[str, typing.Any] | None


class GremlinColumn(GenericColumn[T]):
    label_key = False

    def __init__(
        self,
        col_type: typing.Type[T],
        *,
        primary_key: bool = False,
        auto_increment: bool = False,
        unique: bool = False,
        nullable: bool = True,
        label_key: bool = False,
        default: T
        | typing.Callable[[], T]
        | typing.Callable[["GremlinModel"], T]
        | _Unset = UNSET,
    ):
        """
        Initializes a GenericColumn instance.

        Args:
            col_type (typing.Type[T]): The type of the column.
            primary_key (bool, optional): Whether the column is a primary key. Defaults to False.
            auto_increment (bool, optional): Whether the column is auto incremented. Only works if the column is a primary key. Defaults to False.
            unique (bool, optional): Whether the column is unique. Defaults to False.
            nullable (bool, optional): Whether the column is nullable. Defaults to True.
            label_key (bool, optional): Whether the column is a label key. If True, the column will be used as the label key in the Gremlin graph. Defaults to False.
            default (T | typing.Callable[[], T] | typing.Callable[["GenericModel"], T] | _NoDefaultValue, optional): The default value of the column. Will be used if the column is not set by the user. Defaults to UNSET (no default value).

        Raises:
            GenericColumnException: If auto increment is set on a non-primary key column or if the column type is not int when auto increment is set.
            GenericColumnException: If auto increment is set on a non-integer column type.
        """
        self.label_key = label_key
        super().__init__(
            col_type,
            primary_key=primary_key,
            auto_increment=auto_increment,
            unique=unique,
            nullable=nullable,
            default=default,
        )


class GremlinRelationship(GremlinColumn[T]):
    """
    A column that represents a relation in Gremlin.
    """

    name: str | None = None
    properties: dict[str, typing.Any] | None = None
    direction: typing.Literal["in", "out", "both"] = "out"
    uselist = False
    with_edge = False
    obj: typing.Type["GremlinModel"] | str | None = None
    obj_properties: dict[str, typing.Any] | None = None
    on_before_create: (
        typing.Callable[
            ["GremlinModel", "GremlinModel", OnBeforeCreateParams],
            None | dict[str, typing.Any],
        ]
        | None
    ) = None

    def __init__(
        self,
        col_type: typing.Type[T],
        *,
        name: str | None = None,
        properties: dict[str, typing.Any] | None = None,
        direction: typing.Literal["in", "out", "both"] = "out",
        uselist=False,
        with_edge=False,
        obj: typing.Type["GremlinModel"] | str | None = None,
        obj_properties: dict[str, typing.Any] | None = None,
        nullable: bool = True,
        default: T
        | typing.Callable[[], T]
        | typing.Callable[["GremlinModel"], T]
        | _Unset = UNSET,
        on_before_create: typing.Callable[
            ["GremlinModel", "GremlinModel", OnBeforeCreateParams],
            None
            | dict[str, typing.Any]
            | typing.Coroutine[None, None, dict[str, typing.Any] | None],
        ]
        | None = None,
    ):
        """
        Initializes a GenericColumn instance.

        Args:
            col_type (typing.Type[T]): The type of the column.
            name (str | None, optional): The edge name of the relation. Defaults to None.
            properties (dict[str, typing.Any] | None, optional): Additional properties to filter the edge of the relation. Defaults to None.
            direction (typing.Literal["in", "out", "both"], optional): The direction of the relation. Use "in" for incoming relations and "out" for outgoing relations or "both" for both directions. Defaults to "out".
            uselist (bool, optional): Whether the relation is a list. Defaults to False.
            with_edge (bool, optional): Whether to return the edge properties along with the related vertex. If True, the column will return a dictionary with two keys: "edge" and the property name. When `obj` is set, the related object needs to have an `edge` property to hold the edge properties. Defaults to False.
            obj (typing.Type["GremlinModel"] | str | None, optional): The model class that this relation points to. To handle relation to itself, use `typing.Self`. To use a simple dictionary, gives nothing. Defaults to None.
            obj_properties (dict[str, typing.Any] | None, optional): Additional properties to filter the related vertex of the relation. Defaults to None.
            nullable (bool, optional): Whether the column is nullable. Defaults to True.
            default (T | typing.Callable[[], T] | typing.Callable[["GenericModel"], T] | _NoDefaultValue, optional): The default value of the column. Will be used if the column is not set by the user. Defaults to UNSET (no default value).
            on_before_create (typing.Callable[["GremlinModel", "GremlinModel", OnBeforeCreateParams], None | dict[str, typing.Any]] | typing.Coroutine[None, None, dict[str, typing.Any] | None], optional): A callback function to be called before creating the relation. It receives the source model, target model, and a dictionary with parameters for creating the edge. The function can return a dictionary with additional properties to set on the edge or None. Defaults to None.

        Raises:
            GenericColumnException: If auto increment is set on a non-primary key column or if the column type is not int when auto increment is set.
            GenericColumnException: If auto increment is set on a non-integer column type.
        """
        self.name = name
        self.properties = properties
        self.direction = direction
        self.uselist = uselist
        self.with_edge = with_edge
        self.obj = obj
        self.obj_properties = obj_properties
        self.on_before_create = on_before_create
        if uselist:
            if col_type is not list:
                raise TypeError(
                    "The col_type of a GremlinRelationship with uselist=True must be `list`."
                )
        else:
            if col_type is not typing.Any:
                raise TypeError(
                    "The col_type of a GremlinRelationship with uselist=False must be `typing.Any`."
                )
        super().__init__(
            col_type,
            primary_key=False,
            auto_increment=False,
            unique=False,
            nullable=nullable,
            label_key=False,
            default=default,
        )

    def __set_name__(self, owner, name):
        from .model import GremlinModel

        if self.obj is typing.Self:
            self.obj = owner
            if self.uselist:
                if issubclass(self.obj, GremlinModel):
                    self.col_type = (
                        self.col_type
                        | typing.Annotated[
                            list[self.obj],
                            pydantic.AfterValidator(
                                lambda values: [v.to_json() for v in values]
                                if values
                                else values
                            ),
                        ]
                    )
                else:
                    self.col_type = self.col_type | list[self.obj]
            else:
                if issubclass(self.obj, GremlinModel):
                    self.col_type = (
                        self.col_type
                        | typing.Annotated[
                            self.obj,
                            pydantic.AfterValidator(lambda v: v.to_json()),
                        ]
                    )
                else:
                    self.col_type = self.col_type | self.obj
        elif isinstance(self.obj, type) and issubclass(self.obj, GremlinModel):
            self.obj_properties = use_default_when_none(
                self.obj_properties, self.obj.__properties__
            )
        elif isinstance(self.obj, str):
            GremlinModel._register_model_callback(
                self.obj,
                lambda model: setattr(self, "obj", model),
            )
            GremlinModel._register_model_callback(
                self.obj,
                lambda model: setattr(
                    self,
                    "obj_properties",
                    use_default_when_none(self.obj_properties, model.__properties__),
                ),
            )

        return super().__set_name__(owner, name)
