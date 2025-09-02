import collections
import inspect
import typing
from enum import Enum
from typing import Any, Callable, Dict, List, Sequence

from fastapi import Depends, Response
from fastapi.datastructures import Default
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute, BaseRoute
from fastapi.types import IncEx
from fastapi.utils import generate_unique_id
from sqlalchemy import Table as SA_Table
from sqlalchemy.orm.relationships import _RelationshipDeclared

from .backends.sqla.model import Model
from .dependencies import check_g_user, has_access_dependency
from .utils import T

__all__ = [
    "expose",
    "login_required",
    "permission_name",
    "protect",
    "response_model_str",
    "relationship_filter",
    "docs",
]


def permission_name(name):
    """
    Decorator that sets the permission name for a function.

    Args:
        name (str): The name of the permission.

    Returns:
        function: The decorated function.

    Example:
        @permission_name("info")
        def my_function():
            pass
    """

    def wrap(f):
        f = _select_function(f)
        f._permission_name = name
        return f

    return wrap


def expose(
    path: str = "/",
    methods: List[str] = ["GET"],
    *,
    response_model: Any = Default(None),
    status_code: int | None = None,
    tags: List[str | Enum] | None = None,
    dependencies: Sequence[Depends] | None = None,
    summary: str | None = None,
    description: str | None = None,
    response_description: str = "Successful Response",
    responses: Dict[int | str, Dict[str, Any]] | None = None,
    deprecated: bool | None = None,
    operation_id: str | None = None,
    response_model_include: IncEx | None = None,
    response_model_exclude: IncEx | None = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    include_in_schema: bool = True,
    response_class: type[Response] = Default(JSONResponse),
    name: str | None = None,
    callbacks: List[BaseRoute] | None = None,
    openapi_extra: Dict[str, Any] | None = None,
    generate_unique_id_function: Callable[[APIRoute], str] = Default(
        generate_unique_id
    ),
):
    """
    Decorator to expose a function as an API endpoint.

    Args:
        path (str, optional): The URL path for the endpoint. Defaults to "/".
        methods (List[str], optional): The HTTP methods allowed for the endpoint. Defaults to ["GET"].
        response_model (Any, optional): The response model for the endpoint. Defaults to Default(None).
        status_code (int | None, optional): The status code for the response. Defaults to None.
        tags (List[str | Enum] | None, optional): The tags for the endpoint. Defaults to None.
        dependencies (Sequence[Depends] | None, optional): The dependencies for the endpoint. Defaults to None.
        summary (str | None, optional): The summary for the endpoint. Defaults to None.
        description (str | None, optional): The description for the endpoint. Defaults to None.
        response_description (str, optional): The description for the response. Defaults to "Successful Response".
        responses (Dict[int | str, Dict[str, Any]] | None, optional): The responses for the endpoint. Defaults to None.
        deprecated (bool | None, optional): Whether the endpoint is deprecated. Defaults to None.
        operation_id (str | None, optional): The operation ID for the endpoint. Defaults to None.
        response_model_include (IncEx | None, optional): The fields to include in the response model. Defaults to None.
        response_model_exclude (IncEx | None, optional): The fields to exclude from the response model. Defaults to None.
        response_model_by_alias (bool, optional): Whether to use the alias for the response model. Defaults to True.
        response_model_exclude_unset (bool, optional): Whether to exclude unset fields from the response model. Defaults to False.
        response_model_exclude_defaults (bool, optional): Whether to exclude default fields from the response model. Defaults to False.
        response_model_exclude_none (bool, optional): Whether to exclude None fields from the response model. Defaults to False.
        include_in_schema (bool, optional): Whether to include the endpoint in the schema. Defaults to True.
        response_class (type[Response], optional): The response class for the endpoint. Defaults to Default(JSONResponse).
        name (str | None, optional): The name of the endpoint. Defaults to None.
        callbacks (List[BaseRoute] | None, optional): The callbacks for the endpoint. Defaults to None.
        openapi_extra (Dict[str, Any] | None, optional): Extra OpenAPI information for the endpoint. Defaults to None.
        generate_unique_id_function ([type], optional): The function to generate a unique ID. Defaults to Default(generate_unique_id).

    Returns:
        Callable: The wrapped function.

    Example:
    ```python
        @expose("/hello", methods=["GET"], response_model=str)
        def hello():
            return "Hello, World!"
    ```
    """

    def wrap(f):
        f = _select_function(f)
        f._url = {
            "path": path,
            "methods": list(set(methods)),
            "response_model": response_model,
            "status_code": status_code,
            "tags": tags,
            "dependencies": dependencies,
            "summary": summary,
            "description": description,
            "response_description": response_description,
            "responses": responses,
            "deprecated": deprecated,
            "operation_id": operation_id,
            "response_model_include": response_model_include,
            "response_model_exclude": response_model_exclude,
            "response_model_by_alias": response_model_by_alias,
            "response_model_exclude_unset": response_model_exclude_unset,
            "response_model_exclude_defaults": response_model_exclude_defaults,
            "response_model_exclude_none": response_model_exclude_none,
            "include_in_schema": include_in_schema,
            "response_class": response_class,
            "name": name,
            "callbacks": callbacks,
            "openapi_extra": openapi_extra,
            "generate_unique_id_function": generate_unique_id_function,
        }

        return f

    return wrap


def login_required(f):
    """
    A decorator that adds login requirement to a function.

    This decorator should be used in conjunction with the `expose` decorators.

    Args:
        f (function): The function to be wrapped.

    Returns:
        The wrapped function with the login requirement added.

    Example:
    ```python
        @expose("/users", methods=["GET"], response_model=List[User])
        @login_required()
        def get_users(session: AsyncSession | Session = Depends(get_session())):
            ...
    """
    f = _select_function(f)
    if not hasattr(f, "_dependencies"):
        f._dependencies = []

    f._dependencies.append((check_g_user(), None))

    return f


def protect(_=False):
    """
    A decorator that adds a permission-based access control to a function.

    This decorator should be used in conjunction with the `expose` and `permission_name` decorators.

    Args:
        _ (bool, optional): Placeholder argument. Defaults to False.

    Returns:
        function: The wrapped function.

    Example:
    ```python
        @expose("/users", methods=["GET"], response_model=List[User])
        @protect()
        @permission_name("info")
        def get_users(session: AsyncSession | Session = Depends(get_session())):
            ...
    ```
    """

    def wrap(f):
        f = _select_function(f)

        if not hasattr(f, "_dependencies"):
            f._dependencies = []

        f._dependencies.append(
            (
                has_access_dependency,
                {"api": ":self", "permission": ":f._permission_name"},
            )
        )

        return f

    return wrap


def response_model_str(property: str):
    """
    Decorator that sets the response model based on the given string, that will be converted to an attribute of the API class.

    This decorator should be used in conjunction with the `expose` decorator.

    `response_model` attribute in the `expose` decorator will be overwritten by this decorator.

    Args:
        property (str): The response model string.

    Returns:
        Callable: The decorated function.

    Example:
    ```python
        @expose("/users", methods=["GET"])
        @response_model_str("list_return_schema")
        def get_users(session: AsyncSession | Session = Depends(get_session())):
            ...
    ```
    """

    def wrap(f):
        f = _select_function(f)
        f._response_model_str = property
        return f

    return wrap


def priority(value: int):
    """
    Decorator that sets the priority of the endpoint. High value means higher priority. Higher priority endpoints will be exposed first.

    This is useful if you want to control the order of the endpoints in the API schema, because earlier endpoints will take precedence over later endpoints.

    This decorator should be used in conjunction with the `expose` decorator.

    #### Endpoint that are created without the priority decorator will always take precedence over the endpoints that are created with the priority decorator.
    #### Priority 1-9 are reserved for the automatically generated endpoints. if you really want to use them, you can set the priority to 10 or higher.

    Args:
        value (int): The priority value.

    Returns:
        Callable: The decorated function.

    Example:
    ```python
        @expose("/users", methods=["GET"])
        @priority(1)
        def get_users(session: AsyncSession | Session = Depends(get_session())):
            ...
    ```
    """

    def wrap(f):
        f = _select_function(f)
        f._priority = value
        return f

    return wrap


def _select_function(f):
    """
    Selects the underlying function from a method or a function.

    Args:
        f: The method or function to select from.

    Returns:
        The underlying function.

    """
    if hasattr(f, "__func__"):
        return f.__func__
    return f


def relationship_filter(attr: typing.Union[str, _RelationshipDeclared]):
    """
    Decorator that adds a filter to a relationship of a model when querying the database.
    The function should return a valid criteria.

    Args:
        attr (typing.Union[str, _RelationshipDeclared]): The attribute name or the column of the relationship.

    Raises:
        Exception: If the attribute for the relationship could not be found.

    Returns:
        classmethod: The wrapped classmethod that will be used as a filter.

    Example:

    ```python
        from sqlalchemy import Column, Integer, String, select
        from sqlalchemy.orm import Mapped, relationship, selectinload
        from fastapi_rtk import Model, User, relationship_filter

        class MyModel(Model):
            id = Column(Integer, primary_key=True)
            name = Column(String(50), unique = True, nullable=False)

            users: Mapped[list[User]] = relationship(User, back_populates="my_models")

            @relationship_filter(users)
            def active_users(cls):
                return User.is_active == True # Only lists active users

        # Select all MyModel instances with their active users
        stmt = select(MyModel).options(selectinload(MyModel.load_options("users")))
    ```
    """
    if isinstance(attr, _RelationshipDeclared):
        caller_locals = inspect.currentframe().f_back.f_locals
        caller_locals = {k: v for k, v in caller_locals.items() if v is attr}
        if not caller_locals:
            raise Exception(
                "relationship_filter decorator could not find the attribute for the relationship."
            )
        attr = list(caller_locals.keys())[0]

    def wrap(f):
        if f is not classmethod:
            f = classmethod(f)
        f = _relationship_filter(f, attr)
        return f

    return wrap


def _relationship_filter(f: T, attr: typing.Union[str, _RelationshipDeclared]) -> T:
    return _RelationshipFilter(f, attr)


class _RelationshipFilter:
    _f: classmethod
    _attr: str

    def __init__(self, f: classmethod, attr: str):
        self._f = f
        self._attr = attr

    def __set_name__(self, owner: type[Model], name: str):
        owner._relationship_filters = (
            owner._relationship_filters or collections.defaultdict(list)
        )
        owner._relationship_filters[self._attr].append(self._f.__name__)

        # Replace this class with the underlying function
        setattr(owner, name, self._f)


def docs(description="", data: dict[str, str] | None = None):
    """
    Decorator to add documentation to a table from a SQLAlchemy model.
    This decorator should be used on classes that inherit from `Model` or a `Table`.

    Args:
        description (str, optional): Description of the table. Defaults to "".
        data (dict[str, str] | None, optional): Dictionary of column names and their descriptions. Defaults to None.

    Raises:
        TypeError: If the class does not inherit from `Model` or `Table`.

    Returns:
        type[T]: The wrapped class.

    Example:
    ```python
        from fastapi_rtk import Model, docs

        @docs(description="This is a test table", data={"column1": "This is column 1"})
        class TestTable(Model):
            __tablename__ = "test_table"
            column1 = Column(Integer, primary_key=True)
            column2 = Column(String(50))
    ```
    """
    from .cli.export import table_documentation

    data = data or {}

    def wrap(cls: type[T]) -> type[T]:
        if isinstance(cls, SA_Table):
            tablename = cls.name
        else:
            if not issubclass(cls, Model):
                raise TypeError(
                    "The @docs decorator can only be used on classes that inherit from Model."
                )
            tablename = cls.__tablename__

        table_documentation[tablename]["description"] = (
            description or table_documentation[tablename]["description"]
        )
        table_documentation[tablename]["columns"].update(data)

        return cls

    return wrap
