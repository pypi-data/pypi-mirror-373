import asyncio
import csv
import enum
import re
import types
import typing
from enum import Enum
from typing import Any, Callable, Dict, List, Literal, Tuple, Type

import fastapi
import pydantic
from fastapi import Body, Depends, HTTPException, Response
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, ConfigDict, Field, create_model
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session
from sqlalchemy.orm import Session, scoped_session

from ..backends.sqla.filters import BaseFilter
from ..backends.sqla.interface import SQLAInterface
from ..backends.sqla.model import Model
from ..bases.db import DBQueryParams
from ..bases.session import AbstractSession
from ..const import AVAILABLE_ROUTES, PERMISSION_PREFIX
from ..decorators import expose, permission_name, priority
from ..dependencies import current_permissions, has_access_dependency
from ..exceptions import raise_exception
from ..globals import g
from ..schemas import (
    PRIMARY_KEY,
    BaseResponseMany,
    BaseResponseSingle,
    ColumnEnumInfo,
    ColumnInfo,
    ColumnRelationInfo,
    GeneralResponse,
    InfoResponse,
    QueryBody,
    QuerySchema,
    RelInfo,
)
from ..setting import Setting
from ..types import ExportMode
from ..utils import (
    AsyncTaskRunner,
    CSVJSONConverter,
    Line,
    SelfDepends,
    SelfType,
    T,
    deep_merge,
    lazy_self,
    merge_schema,
    smart_run,
)
from .base_api import BaseApi

__all__ = ["ModelRestApi"]


class Params(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: PRIMARY_KEY | None = None
    ids: List[PRIMARY_KEY] | None = None
    q: QuerySchema | None = None
    session: AsyncSession | Session | AbstractSession | typing.Any | None = None
    body: BaseModel | None = None
    item: Model | Any | None = None
    items: List[Model | Any] | None = None
    extra: Any | None = None


class P_ID(Params):
    id: PRIMARY_KEY


class P_IDS(Params):
    ids: List[PRIMARY_KEY]


class P_Q(Params):
    q: QuerySchema


class P_SESSION(Params):
    session: AsyncSession | Session | AbstractSession | typing.Any


class P_BODY(Params):
    body: BaseModel


class P_ITEM(Params):
    item: Model | Any


class P_ITEMS(Params):
    items: List[Model | Any]


class PARAM_Q(P_Q):
    pass


class PARAM_IDS_Q_SESSION_ITEMS(P_IDS, P_Q, P_SESSION, P_ITEMS):
    pass


class PARAM_ID_SESSION(P_ID, P_SESSION):
    pass


class PARAM_ID_SESSION_ITEM(P_ID, P_SESSION, P_ITEM):
    pass


class PARAM_BODY_SESSION(P_BODY, P_SESSION):
    pass


class lazy(lazy_self["ModelRestApi", T]): ...


class ModelRestApi(BaseApi):
    """
    Base API class for FastAPI with built-in RESTful endpoints for common data operations.

    This class automatically delivers standard routes for CRUD (Create, Read, Update, Delete),
    file and image management, data download, bulk operations, filtering, and pagination.
    Each route is extensible with corresponding pre- and post-processing methods, allowing for custom logic
    before and after the main operation.

    Usage:

    ```python
    from fastapi_rtk import ModelRestApi, SQLAInterface
    from app.models import User
    from app import toolkit

    class UsersApi(ModelRestApi):
        resource_name = "users"
        datamodel = SQLAInterface(User)

    toolkit.add_api(UsersApi) # Assuming `toolkit` is an instance of FastAPIReactToolkit
    ```
    """

    """
    -------------
     GENERAL
    -------------
    """

    datamodel = lazy(
        lambda self: raise_exception(
            f"datamodel must be set in {self.__class__.__name__}", SQLAInterface
        )
    )
    """
    The SQLAlchemy interface object.

    Usage:
    ```python
    datamodel = SQLAInterface(User)
    ```
    """
    resource_name = lazy(lambda self: self.datamodel.obj.__name__.lower())
    """
    The name of the resource. If not given, will use the class name of the datamodel object in lowercase.
    """
    max_page_size = lazy(lambda: Setting.API_MAX_PAGE_SIZE)
    """
    The maximum page size for the related fields in add_columns, edit_columns, and search_columns properties.
    """
    file_manager = lazy(
        lambda self: g.file_manager.get_instance_with_subfolder(self.resource_name)
    )
    """
    The file manager instance for the API. Defaults to `g.file_manager` with the subfolder set to the resource name.
    """
    image_manager = lazy(
        lambda self: g.image_manager.get_instance_with_subfolder(self.resource_name)
    )
    """
    The image manager instance for the API. Defaults to `g.image_manager` with the subfolder set to the resource name.
    """

    routes: list[AVAILABLE_ROUTES] = lazy(
        lambda self: [
            x
            for x in [
                "image",
                "file",
                "info",
                "download",
                "bulk",
                "get_list",
                "get",
                "post",
                "put",
                "delete",
            ]
            if x not in self.exclude_routes
        ]
    )
    """
    The list of routes to expose. available routes: `info`, `download`, `bulk`, `get_list`, `get`, `post`, `put`, `delete`.
    """
    exclude_routes: List[AVAILABLE_ROUTES] = lazy(lambda: [])
    """
    The list of routes to exclude. available routes: `info`, `download`, `bulk`, `get_list`, `get`, `post`, `put`, `delete`.
    """
    protected_routes: List[AVAILABLE_ROUTES] = lazy(
        lambda self: [x for x in self.routes if x not in self.exclude_protected_routes]
    )
    """
    The list of routes to protect. Defaults to all routes within `routes` property except those in `exclude_protected_routes`.
    """
    exclude_protected_routes: List[AVAILABLE_ROUTES] = lazy(lambda: [])
    """
    The list of routes to exclude from protection. Defaults to `[]`.
    """
    base_order: Tuple[str, Literal["asc", "desc"]] | None = None
    """
    The default order for the list endpoint. Set this to set the default order for the list endpoint.

    Example:
    ```python
    base_order = ("name", "asc")
    ```
    """
    base_filters: List[Tuple[str, Type[BaseFilter], Any]] | None = None
    """
    The default filters to apply for the following endpoints: `download`, `list`, `show`, `add`, and `edit`. Defaults to None.

    Example:
    ```python
    base_filters = [
        ["status", FilterEqual, "active"],
    ]
    ```
    """
    label_columns = lazy(lambda: dict[str, str]())
    """
    The label for each column in the list columns and show columns properties.

    Example:
    ```python
    label_columns = {
        "name": "Name",
        "description": "Description",
    }
    ```
    """
    order_column_enum = lazy(
        lambda self: Enum(
            f"{self.__class__.__name__}-OrderColumnEnum",
            {col: col for col in self.order_columns},
            type=str,
        )
    )
    """
    The enum for the order columns in the list endpoint.
    """
    query_schema: Type[QuerySchema] = lazy(
        lambda self: merge_schema(
            QuerySchema,
            {
                "order_column": (
                    self.order_column_enum | None,
                    Field(default=None),
                ),
            },
            True,
            f"{self.__class__.__name__}-QuerySchema",
        )
    )
    """
    The query schema for the list endpoint.
    
    DO NOT MODIFY UNLESS YOU KNOW WHAT YOU ARE DOING.
    """
    download_body_schema: Type[QueryBody] = lazy(
        lambda self: merge_schema(
            QueryBody,
            {
                "order_column": (self.order_column_enum | None, Field(default=None)),
            },
            True,
            f"{self.__class__.__name__}-DownloadBodySchema",
        )
    )
    """
    The body schema for the download endpoint.
    
    DO NOT MODIFY UNLESS YOU KNOW WHAT YOU ARE DOING.
    """

    """
    -------------
     INFO
    -------------
    """

    filter_options = lazy(lambda: dict[str, typing.Any]())
    """
    Additional filter options from the user for the info endpoint.

    Example:
    ```python
    filter_options = {
        "odd_numbers": [1, 3, 5, 7, 9],
    }
    ```
    """
    description_columns = lazy(lambda: dict[str, str]())
    """
    The description for each column in the add columns, edit columns, and search columns properties.

    Example:
    ```python
    description_columns = {
        "name": "Name of the item",
        "description": "Description of the item",
    }
    ```
    """
    add_query_rel_fields = lazy(
        lambda: dict[str, list[tuple[str, typing.Type[BaseFilter], typing.Any]]]()
    )
    """
    The query fields for the related fields in the add_columns property.

    Example:
    ```python
    add_query_rel_fields = {
        "user": [
            ["username", FilterEqual, "admin"],
        ],
    }
    ```
    """
    edit_query_rel_fields = lazy(
        lambda: dict[str, list[tuple[str, typing.Type[BaseFilter], typing.Any]]]()
    )
    """
    The query fields for the related fields in the edit_columns property.

    Example:
    ```python
    edit_query_rel_fields = {
        "user": [
            ["username", FilterEqual, "admin"],
        ],
    }
    ```
    """
    search_query_rel_fields = lazy(
        lambda: dict[str, list[tuple[str, typing.Type[BaseFilter], typing.Any]]]()
    )
    """
    The query fields for the related fields in the filters.

    Example:
    ```python
    search_query_rel_fields = {
        "user": [
            ["username", FilterEqual, "admin"],
        ],
    }
    ```
    """
    order_rel_fields = lazy(
        lambda: dict[str, tuple[str, typing.Literal["asc", "desc"]]]()
    )
    """
    Order the related fields in the add columns, edit columns, and search columns properties.

    Example:
    ```python
    order_rel_fields = {
        "user": ("username", "asc"),
    }
    ```
    """
    search_filters = lazy(lambda: dict[str, list[typing.Type[BaseFilter]]]())
    """
    Add additional filters to the search columns.

    Example:
    ```python
    search_filters = {
        "name": [FilterNameStartsWithA],
    }
    ```
    """
    search_exclude_filters = lazy(
        lambda: dict[str, list[typing.Type[BaseFilter] | str]]()
    )
    """
    Exclude filters from the search columns.

    Can be a list of filter classes or a list of strings with the filter names.

    Example:
    ```python
    search_exclude_filters = {
        "name": ['eq', 'in', FilterNotEqual, FilterStartsWith],
    }
    ```
    """
    info_return_schema: Type[InfoResponse] = lazy(
        lambda self: merge_schema(
            InfoResponse,
            {
                "add_title": (str, Field(default=self.add_title)),
                "edit_title": (str, Field(default=self.edit_title)),
                "filter_options": (dict, Field(default={})),
                "add_type": (
                    typing.Literal["json"] | typing.Literal["form"],
                    Field(
                        default="form"
                        if any(
                            x
                            in self.datamodel.get_file_column_list()
                            + self.datamodel.get_image_column_list()
                            for x in self.add_columns
                        )
                        else "json"
                    ),
                ),
                "edit_type": (
                    typing.Literal["json"] | typing.Literal["form"],
                    Field(
                        default="form"
                        if any(
                            x
                            in self.datamodel.get_file_column_list()
                            + self.datamodel.get_image_column_list()
                            for x in self.edit_columns
                        )
                        else "json"
                    ),
                ),
            },
            name=f"{self.__class__.__name__}-InfoResponse",
        )
    )
    """
    The response schema for the info endpoint. 

    DO NOT MODIFY UNLESS YOU KNOW WHAT YOU ARE DOING.
    """

    """
    -------------
     TITLES
    -------------
    """

    list_title = lazy(
        lambda self: "List " + self._prettify_name(self.datamodel.obj.__name__)
    )
    """
    The title for the list endpoint. If not provided, Defaults to "List {ModelName}".
    """
    show_title = lazy(
        lambda self: "Show " + self._prettify_name(self.datamodel.obj.__name__)
    )
    """
    The title for the show endpoint. If not provided, Defaults to "Show {ModelName}".
    """
    add_title = lazy(
        lambda self: "Add " + self._prettify_name(self.datamodel.obj.__name__)
    )
    """
    The title for the add endpoint. If not provided, Defaults to "Add {ModelName}".
    """
    edit_title = lazy(
        lambda self: "Edit " + self._prettify_name(self.datamodel.obj.__name__)
    )
    """
    The title for the edit endpoint. If not provided, Defaults to "Edit {ModelName}".
    """

    """
    -------------
     COLUMNS
    -------------
    """

    list_columns = lazy(
        lambda self: [
            x
            for x in self.datamodel.get_user_column_list()
            + self.datamodel.get_property_column_list()
            if x not in self.list_exclude_columns
        ]
    )
    """
    The list of columns to display in the list endpoint. If not provided, all columns will be displayed.
    """
    show_columns = lazy(
        lambda self: [
            x
            for x in self.datamodel.get_user_column_list()
            + self.datamodel.get_property_column_list()
            if x not in self.show_exclude_columns
        ]
    )
    """
    The list of columns to display in the show endpoint and for the result of the add and edit endpoint. If not provided, all columns will be displayed.
    """
    add_columns = lazy(
        lambda self: [
            x
            for x in self.datamodel.get_add_column_list()
            if x not in self.add_exclude_columns
        ]
    )
    """
    The list of columns to display in the add endpoint. If not provided, all columns will be displayed.
    """
    edit_columns = lazy(
        lambda self: [
            x
            for x in self.datamodel.get_edit_column_list()
            if x not in self.edit_exclude_columns
        ]
    )
    """
    The list of columns to display in the edit endpoint. If not provided, all columns will be displayed.
    """
    search_columns = lazy(
        lambda self: self.datamodel.get_search_column_list(
            list_columns=self.list_columns
        )
    )
    """
    The list of columns that are allowed to be filtered in the list endpoint. If not provided, all columns will be allowed.
    """
    order_columns = lazy(
        lambda self: self.datamodel.get_order_column_list(
            list_columns=self.list_columns
        )
    )
    """
    The list of columns that can be ordered in the list endpoint. If not provided, all columns will be allowed.
    """

    """
    -------------
     EXCLUDE COLUMNS
    -------------
    """

    list_exclude_columns = lazy(lambda: list[str]())
    """
    The list of columns to exclude from the list endpoint.
    """
    show_exclude_columns = lazy(lambda: list[str]())
    """
    The list of columns to exclude from the show endpoint.
    """
    add_exclude_columns = lazy(lambda: list[str]())
    """
    The list of columns to exclude from the add endpoint.
    """
    edit_exclude_columns = lazy(lambda: list[str]())
    """
    The list of columns to exclude from the edit endpoint.
    """
    search_exclude_columns = lazy(lambda: list[str]())
    """
    The list of columns to exclude from the search columns.
    """

    """
    -------------
     SELECT COLUMNS
    -------------
    """

    extra_list_fetch_columns = lazy(lambda: list[str]())
    """
    The list of columns to be fetch from the database alongside the `list_columns`. Useful if you don't want some columns to be shown but still want to fetch them.
    """
    list_select_columns = lazy(
        lambda self: self.list_columns + self.extra_list_fetch_columns
    )
    """
    The list of columns to be selected from the database and as a result of the list endpoint. If not provided, `list_columns` + `extra_list_fetch_columns` will be used.

    Useful if you need to modify which columns to be returned while keeping everything else the same.
    """
    extra_show_fetch_columns = lazy(lambda: list[str]())
    """
    The list of columns to be fetch from the database alongside the `show_columns`. Useful if you don't want some columns to be shown but still want to fetch them.
    """
    show_select_columns = lazy(
        lambda self: self.show_columns + self.extra_show_fetch_columns
    )
    """
    The list of columns to be selected from the database and as a result of the show endpoint. If not provided, `show_columns` + `extra_show_fetch_columns` will be used.

    Useful if you need to modify which columns to be returned while keeping everything else the same.
    """

    """
    -------------
     JSONFORMS SCHEMAS
    -------------
    """

    add_jsonforms_schema: Dict[str, Any] | None = None
    """
    The `JSONForms` schema for the add endpoint. If not provided, Defaults to the schema generated from the `add_columns` property.
    """
    add_jsonforms_uischema: Dict[str, Any] | None = None
    """
    The `JSONForms` uischema for the add endpoint. If not provided, it will let `JSONForms` generate the uischema.
    """
    edit_jsonforms_schema: Dict[str, Any] | None = None
    """
    The `JSONForms` schema for the edit endpoint. If not provided, Defaults to the schema generated from the `edit_columns` property.
    """
    edit_jsonforms_uischema: Dict[str, Any] | None = None
    """
    The `JSONForms` uischema for the edit endpoint. If not provided, it will let `JSONForms` generate the uischema.
    """

    """
    -------------
     OBJECT SCHEMAS
    -------------
    """

    list_obj_schema = lazy(
        lambda self: self.datamodel.generate_schema(
            self.list_select_columns,
            with_id=False,
            with_name=False,
            name=f"{self.__class__.__name__}-ListObjSchema",
        )
    )
    """
    The schema for the object in the list endpoint.

    DO NOT MODIFY UNLESS YOU KNOW WHAT YOU ARE DOING.
    """
    show_obj_schema = lazy(
        lambda self: self.datamodel.generate_schema(
            self.show_select_columns,
            with_id=False,
            with_name=False,
            name=f"{self.__class__.__name__}-ShowObjSchema",
        )
    )
    """
    The schema for the object in the show endpoint.

    DO NOT MODIFY UNLESS YOU KNOW WHAT YOU ARE DOING.
    """
    add_obj_schema = lazy(
        lambda self: self.datamodel.generate_schema(
            self.add_columns,
            with_id=False,
            with_name=False,
            name=f"{self.__class__.__name__}-AddObjSchema",
            hide_sensitive_columns=False,
        )
    )
    """
    The schema for the object in the add endpoint.

    DO NOT MODIFY UNLESS YOU KNOW WHAT YOU ARE DOING.
    """
    edit_obj_schema = lazy(
        lambda self: self.datamodel.generate_schema(
            self.edit_columns,
            with_id=False,
            with_name=False,
            optional=True,
            name=f"{self.__class__.__name__}-EditObjSchema",
            hide_sensitive_columns=False,
        )
    )
    """
    The schema for the object in the edit endpoint.

    DO NOT MODIFY UNLESS YOU KNOW WHAT YOU ARE DOING.
    """

    """
    -------------
     BODY SCHEMAS
    -------------
    """

    add_schema: typing.Type[BaseModel] = lazy(
        lambda self: typing.Annotated[
            self._create_request_schema(
                merge_schema(
                    self.add_obj_schema,
                    self._handle_schema_extra_fields(self.add_schema_extra_fields),
                    name=f"{self.__class__.__name__}-AddObjSchema-Merged",
                ),
                name=f"{self.__class__.__name__}-AddSchema",
            ),
            fastapi.Form(media_type="multipart/form-data")
            if any(
                x
                in self.datamodel.get_file_column_list()
                + self.datamodel.get_image_column_list()
                for x in self.add_columns
            )
            else None,
        ]
    )
    """
    The schema for the add endpoint.

    DO NOT MODIFY UNLESS YOU KNOW WHAT YOU ARE DOING.
    """
    edit_schema: typing.Type[BaseModel] = lazy(
        lambda self: typing.Annotated[
            self._create_request_schema(
                merge_schema(
                    self.edit_obj_schema,
                    self._handle_schema_extra_fields(self.edit_schema_extra_fields),
                    name=f"{self.__class__.__name__}-EditObjSchema-Merged",
                ),
                optional=True,
                name=f"{self.__class__.__name__}-EditSchema",
            ),
            fastapi.Form(media_type="multipart/form-data")
            if any(
                x
                in self.datamodel.get_file_column_list()
                + self.datamodel.get_image_column_list()
                for x in self.edit_columns
            )
            else None,
        ]
    )
    """
    The schema for the edit endpoint.

    DO NOT MODIFY UNLESS YOU KNOW WHAT YOU ARE DOING.
    """
    add_schema_extra_fields = lazy(
        lambda: dict[str, type | tuple[type, pydantic.fields.FieldInfo]]()
    )
    """
    Extra fields to add to the add schema. Useful when you want to add extra fields in the body of the add endpoint for your custom logic.

    Example:
    ```python
    add_schema_extra_fields = {
        "extra_field": str,
        "extra_field_with_field_info": (str, Field(default="default_value")),
    }
    ```
    """
    edit_schema_extra_fields = lazy(
        lambda: dict[str, type | tuple[type, pydantic.fields.FieldInfo]]()
    )
    """
    Extra fields to add to the edit schema. Useful when you want to add extra fields in the body of the edit endpoint for your custom logic.

    Example:
    ```python
    edit_schema_extra_fields = {
        "extra_field": str,
        "extra_field_with_field_info": (str, Field(default="default_value")),
    }
    ```
    """

    """
    -------------
     RETURN SCHEMAS
    -------------
    """

    list_return_schema: Type[BaseResponseMany] = lazy(
        lambda self: merge_schema(
            BaseResponseMany,
            {
                **vars(self),
                "result": (List[self.list_obj_schema], ...),
            },
            True,
            f"{self.__class__.__name__}-ListResponse",
        )
    )
    """
    The response schema for the list endpoint.
    
    DO NOT MODIFY UNLESS YOU KNOW WHAT YOU ARE DOING.
    """
    show_return_schema: Type[BaseResponseSingle] = lazy(
        lambda self: merge_schema(
            BaseResponseSingle,
            {
                **vars(self),
                "result": (self.show_obj_schema, ...),
            },
            True,
            f"{self.__class__.__name__}-ShowResponse",
        )
    )
    """
    The response schema for the show endpoint.

    DO NOT MODIFY UNLESS YOU KNOW WHAT YOU ARE DOING.
    """
    add_return_schema: Type[BaseResponseSingle] = lazy(
        lambda self: merge_schema(
            self.show_return_schema,
            {},
            name=f"{self.__class__.__name__}-AddResponse",
        )
    )
    """
    The response schema for the add endpoint.

    DO NOT MODIFY UNLESS YOU KNOW WHAT YOU ARE DOING.
    """
    edit_return_schema: Type[BaseResponseSingle] = lazy(
        lambda self: merge_schema(
            self.show_return_schema,
            {},
            name=f"{self.__class__.__name__}-EditResponse",
        )
    )
    """
    The response schema for the edit endpoint.

    DO NOT MODIFY UNLESS YOU KNOW WHAT YOU ARE DOING.
    """

    """
    -------------
     PRIVATE
    -------------
    """

    _default_info_schema = lazy(
        lambda self: self.__class__.info_return_schema
        is ModelRestApi.info_return_schema
    )
    """
    A flag to indicate if the default info schema is used.

    DO NOT MODIFY.
    """

    def __init__(self):
        if not self.datamodel:
            raise Exception(f"Missing datamodel in {self.__class__.__name__} API.")
        self._init_properties()
        self.post_properties()
        self.post_schema()
        self._init_routes()
        super().__init__()

    def post_properties(self):
        """
        Post properties to be called after the init_properties method.
        """
        pass

    def post_schema(self):
        """
        Post schema to be called after the init_schema method.
        """
        pass

    """
    -------------
     INIT FUNCTIONS
    -------------
    """

    def _init_properties(self) -> None:
        """
        Handle the initialization of the properties of the API.
        """

        for key, value in self.search_filters.items():
            datamodel, _ = self._get_datamodel_and_column(key)
            self.datamodel.filters[key].extend([v(datamodel) for v in value])

        for key, value in self.search_exclude_filters.items():
            value = [v.arg_name if isinstance(v, BaseFilter) else v for v in value]
            self.datamodel.exclude_filters[key].extend(value)
            self.datamodel.filters[key] = [
                x for x in self.datamodel.filters[key] if x.arg_name not in value
            ]

        self.exclude_routes = [x.lower() for x in self.exclude_routes]

        # Check for 2nd level relations in search columns
        not_supported_search_columns = [
            x for x in self.search_columns if x.count(".") > 1
        ]
        if not_supported_search_columns:
            raise Exception(
                f"Search columns with 2nd level relations are not supported: {not_supported_search_columns}"
            )

        self._gen_labels_columns(self.list_columns)
        self._gen_labels_columns(self.show_columns)
        self._gen_labels_columns(self.search_columns)

        # Instantiate all the filters
        if self.base_filters:
            self.base_filters = self._init_filters(self.datamodel, self.base_filters)

        field_keys = [
            "add_query_rel_fields",
            "edit_query_rel_fields",
            "search_query_rel_fields",
        ]
        for key in field_keys:
            filter_dict = getattr(self, key)
            for field, filters in filter_dict.items():
                filter_dict[field] = self._init_filters(
                    self.datamodel.get_related_interface(field), filters
                )

    def _init_routes(self):
        """
        Init routes for the API.
        """
        is_image_column_exist = len(self.datamodel.get_image_column_list()) > 0
        if not is_image_column_exist:
            if "image" in self.routes:
                self.routes.remove("image")

        is_file_column_exist = len(self.datamodel.get_file_column_list()) > 0
        if not is_file_column_exist:
            if "file" in self.routes:
                self.routes.remove("file")

        for route in self.routes:
            getattr(self, route)()

    """
    -------------
     DEPENDENCIES
    -------------
    """

    def get_current_permissions(self):
        """
        Returns the current permissions dependency.

        Returns:
            Callable[..., Coroutine[Any, Any, Any | list]]: The current permissions that the user has for the API dependency.
        """
        return current_permissions(self)

    """
    -------------
     ROUTES
    -------------
     """

    def image(self):
        """
        Image endpoint for the API. Used to retrieve the image from the application.

        This endpoint is only available if the model has image columns.
        """
        if not self.datamodel.get_image_column_list():
            return

        priority(11)(self.image_headless)
        permission_name("image")(self.image_headless)
        expose(
            "/_image/{filename}",
            methods=["GET"],
            name="Get Image",
            description="Get an image from the application.",
            response_class=FileResponse,
            dependencies=[Depends(has_access_dependency(self, "image"))]
            if "image" in self.protected_routes
            else None,
        )(self.image_headless)

    def file(self):
        """
        File endpoint for the API. Used to retrieve the file from the application.

        This endpoint is only available if the model has file columns.
        """
        if not self.datamodel.get_file_column_list():
            return

        priority(10)(self.file_headless)
        permission_name("file")(self.file_headless)
        expose(
            "/_file/{filename}",
            methods=["GET"],
            name="Get File",
            description="Get a file from the application.",
            response_class=FileResponse,
            dependencies=[Depends(has_access_dependency(self, "file"))]
            if "file" in self.protected_routes
            else None,
        )(self.file_headless)

    def info(self):
        """
        Info endpoint for the API.
        """
        priority(9)(self.info_headless)
        permission_name("info")(self.info_headless)
        expose(
            "/_info",
            methods=["GET"],
            name="Get Info",
            description="Get the info for this API's Model.",
            response_model=self.info_return_schema | typing.Any,
            dependencies=[Depends(has_access_dependency(self, "info"))]
            if "info" in self.protected_routes
            else None,
        )(self.info_headless)

    def download(self):
        """
        Download endpoint for the API.
        """
        priority(8)(self.download_headless)
        permission_name("download")(self.download_headless)
        expose(
            "/download",
            methods=["GET"],
            name="Download",
            description="Download list of items in CSV format.",
            dependencies=[Depends(has_access_dependency(self, "download"))]
            if "download" in self.protected_routes
            else None,
        )(self.download_headless)

    #! Disabled until further notice
    # def upload(self):
    #     """
    #     Upload endpoint for the API.
    #     """
    #     priority(7)(self.upload_headless)
    #     permission_name("upload")(self.upload_headless)
    #     expose(
    #         "/upload",
    #         methods=["POST"],
    #         name="Upload",
    #         description="Upload a CSV file to be added to the database.",
    #         dependencies=[Depends(has_access_dependency(self, "upload"))],
    #     )(self.upload_headless)

    def bulk(self):
        """
        Bulk endpoint for the API.
        """
        priority(6)(self.bulk_headless)
        permission_name("bulk")(self.bulk_headless)
        expose(
            "/bulk/{handler}",
            methods=["POST"],
            name="Bulk",
            description="Handle bulk operations.",
            dependencies=[Depends(has_access_dependency(self, "bulk"))]
            if "bulk" in self.protected_routes
            else None,
        )(self.bulk_headless)

    def get_list(self):
        """
        List endpoint for the API.
        """
        priority(5)(self.get_list_headless)
        permission_name("get")(self.get_list_headless)
        expose(
            "/",
            methods=["GET"],
            name="Get items",
            description="Get a list of items.",
            response_model=self.list_return_schema | typing.Any,
            dependencies=[Depends(has_access_dependency(self, "get"))]
            if "get_list" in self.protected_routes
            else None,
        )(self.get_list_headless)

    def get(self):
        """
        Get endpoint for the API.
        """
        priority(4)(self.get_headless)
        permission_name("get")(self.get_headless)
        expose(
            "/{id}",
            methods=["GET"],
            name="Get item",
            description="Get a single item.",
            response_model=self.show_return_schema | typing.Any,
            dependencies=[Depends(has_access_dependency(self, "get"))]
            if "get" in self.protected_routes
            else None,
        )(self.get_headless)

    def post(self):
        """
        Post endpoint for the API.
        """
        priority(3)(self.post_headless)
        permission_name("post")(self.post_headless)
        expose(
            "/",
            methods=["POST"],
            name="Add item",
            description="Add a new item.",
            response_model=self.add_return_schema | typing.Any,
            dependencies=[Depends(has_access_dependency(self, "post"))]
            if "post" in self.protected_routes
            else None,
        )(self.post_headless)

    def put(self):
        """
        Put endpoint for the API.
        """
        priority(2)(self.put_headless)
        permission_name("put")(self.put_headless)
        expose(
            "/{id}",
            methods=["PUT"],
            name="Update item",
            description="Update an item.",
            response_model=self.edit_return_schema | typing.Any,
            dependencies=[Depends(has_access_dependency(self, "put"))]
            if "put" in self.protected_routes
            else None,
        )(self.put_headless)

    def delete(self):
        """
        Delete endpoint for the API.
        """
        priority(1)(self.delete_headless)
        permission_name("delete")(self.delete_headless)
        expose(
            "/{id}",
            methods=["DELETE"],
            response_model=GeneralResponse | typing.Any,
            name="Delete item",
            description="Delete an item.",
            dependencies=[Depends(has_access_dependency(self, "delete"))]
            if "delete" in self.protected_routes
            else None,
        )(self.delete_headless)

    """
    -------------
     ROUTE HEADLESS METHODS
    -------------
    """

    async def image_headless(self, filename: str):
        """
        Retrieves an image based on the filename.
        """
        async with AsyncTaskRunner():
            pre_image = await smart_run(self.pre_image, filename)
            if pre_image is not None:
                if isinstance(pre_image, str):
                    filename = pre_image
                else:
                    return pre_image
            is_image_exist = self.image_manager.file_exists(filename)
            if not is_image_exist:
                raise HTTPException(
                    status_code=404, detail=f"Image '{filename}' not found."
                )
            return StreamingResponse(self.image_manager.stream_file(filename))

    async def file_headless(self, filename: str):
        """
        Retrieves a file based on the filename.
        """
        async with AsyncTaskRunner():
            pre_file = await smart_run(self.pre_file, filename)
            if pre_file is not None:
                if isinstance(pre_file, str):
                    filename = pre_file
                else:
                    return pre_file
            is_file_exist = self.file_manager.file_exists(filename)
            if not is_file_exist:
                raise HTTPException(
                    status_code=404, detail=f"File '{filename}' not found."
                )
            return StreamingResponse(self.file_manager.stream_file(filename))

    async def info_headless(
        self,
        permissions: List[str] = SelfDepends().get_current_permissions,
        session: AsyncSession | Session = SelfDepends().datamodel.get_session_factory,
        session_count: AsyncSession
        | Session = SelfDepends().datamodel.get_session_factory,
    ):
        """
        Retrieves information in a headless mode.

        Args:
            permissions (List[str]): A list of permissions.
            session (async_scoped_session AsyncSession
        | Session): A database scoped session.

        Returns:
            info_return_schema: The information return schema.

        ### Note:
            If you are overriding this method, make sure to copy all the decorators too.
        """
        async with AsyncTaskRunner():
            info = (
                (
                    await smart_run(
                        self._generate_info_schema, permissions, session, session_count
                    )
                )
                if self._default_info_schema
                else self.info_return_schema()
            )
            await smart_run(self.pre_info, info, permissions, session)
            return info

    async def download_headless(
        self,
        q: QuerySchema = SelfType.with_depends().query_schema,
        session: AsyncSession
        | Session = SelfDepends().datamodel.get_download_session_factory,
        export_mode: ExportMode = "simplified",
        delimiter: str = ",",
        quotechar: str = '"',
        label: str = "",
        check_validity: bool = False,
    ):
        """
        Downloads a file in a headless mode.

        Args:
            body (QueryBody): The query body.
            session (AsyncSession | Session): A database scoped session.
            export_mode (str): The export mode. Can be "simplified" or "detailed". Defaults to "simplified".
            delimiter (str): The delimiter for the CSV file. Defaults to ",".
            quotechar (str): Quote character for the CSV file. Defaults to '"'.
            label (str): The label for the CSV file. Defaults to the resource name.
            check_validity (bool): If True, only checks the validity of the request and returns a 200 OK response.

        Returns:
            StreamingResponse: The streaming response.
        """
        async with AsyncTaskRunner():
            q.columns = []
            self._validate_query_parameters(q)
            list_columns: list[str] = self.list_columns.copy()
            label_columns = self.label_columns.copy()

            if export_mode == "detailed":
                list_columns = []
                for column in self.list_columns:
                    if self.datamodel.is_relation_one_to_one(
                        column
                    ) or self.datamodel.is_relation_many_to_one(column):
                        rel_interface = self.datamodel.get_related_interface(column)
                        cols = [
                            x
                            for x in self.datamodel.get_columns_from_related_col(column)
                            if not rel_interface.is_relation(x.split(".")[-1])
                        ]
                        for col in cols:
                            list_columns.append(col)
                            label_columns[col] = label_columns.get(col, col)
                        continue

                    if column not in list_columns:
                        list_columns.append(column)

            if check_validity:
                await smart_run(self.datamodel.close, session)
                return GeneralResponse(detail="OK")

            params = self._handle_query_params(q)
            params["page_size"] = 100  # Set a default page size for export
            return StreamingResponse(
                self._export_data(
                    self.datamodel.yield_per(session, params),
                    list_columns,
                    label_columns,
                    self.list_obj_schema,
                    export_mode=export_mode,
                    delimiter=delimiter,
                    quotechar=quotechar,
                ),
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename={label or self.resource_name}.csv",
                },
            )

    #! Disabled until further notice
    # async def upload_headless(
    #     self,
    #     file: UploadFile,
    #     query: QueryManager = SelfDepends().datamodel.get_query_manager_factory,
    #     session: AsyncSession | Session = SelfDepends().datamodel.get_session_factory,
    #     delimiter: str = ",",
    #     quotechar: str | None = None,
    # ):
    #     """
    #     Uploads a file in a headless mode.

    #     Args:
    #         file (UploadFile): The uploaded file.
    #         query (QueryManager): The query manager object.
    #         session (AsyncSession | Session): A database scoped session.
    #         delimiter (str, optional): The delimiter for the CSV file. Defaults to ",".
    #         quotechar (str | None): Quote character for the CSV file. If not given, it will not be used. Defaults to None.

    #     Raises:
    #         HTTPException: If the file type is not CSV.

    #     Returns:
    #         list[dict[str, typing.Any]]: The list of items added to the database.
    #     """
    #     if not file.content_type.endswith("csv"):
    #         raise HTTPException(
    #             status_code=400,
    #             detail="Invalid file type. Only CSV files are allowed.",
    #         )

    #     return await self._import_data(
    #         await file.read(), query, session, delimiter, quotechar=quotechar
    #     )

    async def bulk_headless(
        self,
        handler: str,
        body: dict | list = Body(...),
        session: AsyncSession | Session = SelfDepends().datamodel.get_session_factory,
    ):
        """
        Bulk handler in headless mode.

        Args:
            handler (str): The handler name.
            body (dict | list): The request body.
            session (AsyncSession | Session): A database scoped session.

        Returns:
            Response: The response object.

        ### Note:
            If you are overriding this method, make sure to copy all the decorators too.
        """
        async with AsyncTaskRunner():
            bulk_handler: Callable | None = getattr(self, f"bulk_{handler}", None)
            if not bulk_handler:
                raise HTTPException(status_code=404, detail="Handler not found")
            try:
                return await smart_run(bulk_handler, body, self.datamodel, session)
            except NotImplementedError as e:
                raise HTTPException(status_code=404, detail=str(e))

    async def bulk_handler(
        self,
        body: dict | list,
        query: SQLAInterface,
        session: AsyncSession | Session,
    ) -> Response:
        """
        Bulk handler for the API.
        To be implemented by the subclass.

        Example:
        ```python
        async def bulk_read(self, body: dict | list, query: QueryManager, session: AsyncSession | Session) -> Response:
            items = await smart_run(query.get_many, session, params={"where_in": (self.datamodel.get_pk_attr(), [item["id"] for item in body])})
            pks, data = self.datamodel.convert_to_result(items)
            return data
        ```

        Args:
            body (dict | list): The request body.
            query (SQLAInterface): The `datamodel` interface.
            session (AsyncSession | Session): A database scoped session.

        Returns:
            Response: The response object.

        Raises:
            NotImplementedError: If the method is not implemented. To be implemented by the subclass.
        """
        raise NotImplementedError("Bulk handler not implemented")

    async def get_list_headless(
        self,
        q: QuerySchema = SelfType.with_depends().query_schema,
        session: AsyncSession | Session = SelfDepends().datamodel.get_session_factory,
        session_count: AsyncSession
        | Session = SelfDepends().datamodel.get_session_factory,
    ):
        """
        Retrieves all items in a headless mode.

        Args:
            q (QuerySchema): The query schema.
            query (QueryManager): The query manager object.
            session (AsyncSession | Session): A database scoped session.
            session_count (AsyncSession | Session): A database scoped session for counting.

        Returns:
            list_return_schema: The list return schema.

        ### Note:
            If you are overriding this method, make sure to copy all the decorators too.
        """
        async with AsyncTaskRunner():
            self._validate_query_parameters(q)
            params = self._handle_query_params(q)
            try:
                async with asyncio.TaskGroup() as tg:
                    task_items = tg.create_task(
                        smart_run(self.datamodel.get_many, session, params)
                    )
                    task_count = tg.create_task(
                        smart_run(self.datamodel.count, session_count, params)
                    )
                items, count = await task_items, await task_count
                pks, data = self.datamodel.convert_to_result(items)
                schema = self.list_return_schema
                if q.columns:
                    list_obj_schema = self.datamodel.generate_schema(
                        q.columns,
                        with_id=False,
                        with_name=False,
                    )
                    schema = merge_schema(
                        schema, {"result": (List[list_obj_schema], ...)}, True
                    )

                body = await smart_run(
                    schema,
                    result=data,
                    count=count,
                    ids=pks,
                    description_columns=self.description_columns,
                    label_columns=self.label_columns,
                    list_columns=self.list_columns,
                    list_title=self.list_title,
                    order_columns=self.order_columns,
                )
                await smart_run(
                    self.pre_get_list,
                    body,
                    PARAM_IDS_Q_SESSION_ITEMS(
                        ids=pks, q=q, session=session, items=items
                    ),
                )
                return body
            except* Exception as e:
                for ex in e.exceptions:
                    raise ex

    async def get_headless(
        self,
        id=SelfType().datamodel.id_schema,
        session: AsyncSession | Session = SelfDepends().datamodel.get_session_factory,
    ):
        """
        Retrieves a single item in a headless mode.

        Args:
            id (str): The id of the item.
            session (AsyncSession | Session): A database scoped session.

        Returns:
            show_return_schema: The show return schema.

        ### Note:
            If you are overriding this method, make sure to copy all the decorators too.
        """
        async with AsyncTaskRunner():
            item = await smart_run(
                self.datamodel.get_one,
                session,
                params={
                    "list_columns": self.show_select_columns,
                    "where_id": id,
                    "filter_classes": self.base_filters,
                },
            )
            if not item:
                raise HTTPException(status_code=404, detail="Item not found")
            pk, data = self.datamodel.convert_to_result(item)
            body = await smart_run(
                self.show_return_schema,
                id=pk,
                result=data,
                description_columns=self.description_columns,
                label_columns=self.label_columns,
                show_columns=self.show_columns,
                show_title=self.show_title,
            )
            await smart_run(
                self.pre_get,
                body,
                PARAM_ID_SESSION_ITEM(id=id, session=session, item=item),
            )
            return body

    async def post_headless(
        self,
        body: BaseModel = SelfType().add_schema,
        session: AsyncSession | Session = SelfDepends().datamodel.get_session_factory,
    ):
        """
        Creates a new item in a headless mode.

        Args:
            body (BaseModel): The request body.
            session (AsyncSession | Session): A database scoped session.

        Returns:
            add_return_schema: The add return schema.

        ### Note:
            If you are overriding this method, make sure to copy all the decorators too.
        """
        async with AsyncTaskRunner():
            async with AsyncTaskRunner():
                body_json = await smart_run(
                    self._process_body,
                    session,
                    body,
                    self.add_query_rel_fields,
                    self.add_schema_extra_fields.keys()
                    if self.add_schema_extra_fields
                    else None,
                )
                item = self.datamodel.obj(**body_json)
                pre_add = await smart_run(
                    self.pre_add,
                    item,
                    PARAM_BODY_SESSION(body=body, session=session),
                )
                if pre_add is not None:
                    if isinstance(pre_add, Model):
                        item = pre_add
                    else:
                        AsyncTaskRunner.remove_tasks_by_tag("file")
                        return pre_add
                item = await smart_run(self.datamodel.add, session, item)
            post_add = await smart_run(
                self.post_add,
                item,
                PARAM_BODY_SESSION(body=body, session=session),
            )
            if post_add is not None:
                if isinstance(post_add, Model):
                    item = post_add
                else:
                    return post_add
            pk, data = self.datamodel.convert_to_result(item)
            body = await smart_run(self.add_return_schema, id=pk, result=data)
            return body

    async def put_headless(
        self,
        id=SelfType().datamodel.id_schema,
        body: BaseModel = SelfType().edit_schema,
        session: AsyncSession | Session = SelfDepends().datamodel.get_session_factory,
    ):
        """
        Updates an item in a headless mode.

        Args:
            id (str): The id of the item.
            body (BaseModel): The request body.
            session (AsyncSession | Session): A database scoped session.

        Returns:
            add_return_schema: The add return schema.

        ### Note:
            If you are overriding this method, make sure to copy all the decorators too.
        """
        async with AsyncTaskRunner():
            async with AsyncTaskRunner():
                item = await smart_run(
                    self.datamodel.get_one,
                    session,
                    params={
                        "list_columns": self.show_select_columns,
                        "where_id": id,
                        "filter_classes": self.base_filters,
                    },
                )
                if not item:
                    raise HTTPException(status_code=404, detail="Item not found")
                body_json = await smart_run(
                    self._process_body,
                    session,
                    body,
                    self.edit_query_rel_fields,
                    self.edit_schema_extra_fields.keys()
                    if self.edit_schema_extra_fields
                    else None,
                    item=item,
                )
                await smart_run(
                    self.pre_update_merge,
                    item,
                    body_json,
                    PARAM_BODY_SESSION(body=body, session=session),
                )
                item.update(body_json)
                pre_update = await smart_run(
                    self.pre_update,
                    item,
                    PARAM_BODY_SESSION(body=body, session=session),
                )
                if pre_update is not None:
                    if isinstance(pre_update, Model):
                        item = pre_update
                    else:
                        AsyncTaskRunner.remove_tasks_by_tag("file")
                        return pre_update
                item = await smart_run(self.datamodel.edit, session, item)
            post_update = await smart_run(
                self.post_update,
                item,
                PARAM_BODY_SESSION(body=body, session=session),
            )
            if post_update is not None:
                if isinstance(post_update, Model):
                    item = post_update
                else:
                    return post_update
            pk, data = self.datamodel.convert_to_result(item)
            body = await smart_run(self.edit_return_schema, id=pk, result=data)
            return body

    async def delete_headless(
        self,
        id=SelfType().datamodel.id_schema,
        session: AsyncSession | Session = SelfDepends().datamodel.get_session_factory,
    ):
        """
        Deletes an item in a headless mode.

        Args:
            id (str): The id of the item.
            query (QueryManager): The query manager object.
            session (AsyncSession | Session): A database scoped session.

        Returns:
            GeneralResponse: The general response.

        ### Note:
            If you are overriding this method, make sure to copy all the decorators too.
        """
        async with AsyncTaskRunner():
            async with AsyncTaskRunner():
                item = await smart_run(
                    self.datamodel.get_one,
                    session,
                    params={
                        "list_columns": self.show_select_columns,
                        "where_id": id,
                        "filter_classes": self.base_filters,
                    },
                )
                if not item:
                    raise HTTPException(status_code=404, detail="Item not found")
                pre_delete = await smart_run(
                    self.pre_delete,
                    item,
                    PARAM_ID_SESSION(id=id, session=session),
                )
                if pre_delete is not None:
                    if isinstance(pre_delete, Model):
                        item = pre_delete
                    else:
                        return pre_delete
                # Delete all related files and images
                file_and_image_columns = [
                    x
                    for x in self.datamodel.get_file_column_list()
                    + self.datamodel.get_image_column_list()
                    if getattr(item, x, None)
                ]
                for column in file_and_image_columns:
                    fm = (
                        self.file_manager
                        if self.datamodel.is_file(column)
                        else self.image_manager
                    )
                    AsyncTaskRunner.add_task(
                        lambda fm=fm, filename=getattr(item, column): smart_run(
                            fm.delete_file, filename
                        )
                    )
                await smart_run(self.datamodel.delete, session, item)
            post_delete = await smart_run(
                self.post_delete,
                item,
                PARAM_ID_SESSION(id=id, session=session),
            )
            if post_delete is not None:
                if isinstance(post_delete, Model):
                    item = post_delete
                else:
                    return post_delete
            body = GeneralResponse(detail="Item deleted")
            return body

    """
    -------------
     PRE AND POST METHODS
    -------------
    """

    async def pre_image(self, filename: str) -> None | str | typing.Any:
        """
        Pre-process the image request before returning it.
        The response still needs to adhere to the FileResponse schema.

        - When a `str` is returned, it will be used as the filename for the image.
        - When any other value is returned, it is assumed to be a response to be returned directly.

        Args:
            filename (str): The filename of the image.
        """
        pass

    async def pre_file(self, filename: str) -> None | str | typing.Any:
        """
        Pre-process the file request before returning it.
        The response still needs to adhere to the FileResponse schema.

        - When a `str` is returned, it will be used as the filename for the file.
        - When any other value is returned, it is assumed to be a response to be returned directly.

        Args:
            filename (str): The filename of the file.
        """
        pass

    async def pre_info(
        self,
        info: InfoResponse,
        permissions: List[str],
        session: async_scoped_session[AsyncSession] | scoped_session[Session],
    ):
        """
        Pre-process the info response before returning it.
        The response still needs to adhere to the InfoResponse schema.

        Args:
            info (InfoResponse): The info response.
            permissions (List[str]): A list of permissions.
            session (async_scoped_session AsyncSession
        | Session): A database scoped session.
        """
        pass

    async def pre_get_list(
        self, body: BaseResponseMany, params: PARAM_IDS_Q_SESSION_ITEMS
    ):
        """
        Pre-process the list response before returning it.
        The response still needs to adhere to the BaseResponseMany schema.

        Args:
            body (BaseResponseMany): The response body.
            params (Params): Additional data passed to the handler.
        """
        pass

    async def pre_get(self, body: BaseResponseSingle, params: PARAM_ID_SESSION_ITEM):
        """
        Pre-process the get response before returning it.
        The response still needs to adhere to the BaseResponseSingle schema.

        Args:
            body (BaseResponseSingle): The response body.
            params (Params): Additional data passed to the handler.
        """
        pass

    async def pre_add(
        self, item: Model, params: PARAM_BODY_SESSION
    ) -> None | Model | typing.Any:
        """
        Pre-process the item before adding it to the database.

        - When a `Model` is returned, it will replace the current `item` and be added to the database.
        - When any other value is returned, it is assumed to be a response to be returned directly.

        Args:
            item (Model): The item to be added to the database.
            params (Params): Additional data passed to the handler.
        """
        pass

    async def post_add(
        self, item: Model, params: PARAM_BODY_SESSION
    ) -> None | Model | typing.Any:
        """
        Post-process the item after adding it to the database.
        But before sending the response.

        - When a `Model` is returned, it will replace the current `item`.
        - When any other value is returned, it is assumed to be a response to be returned directly.

        Args:
            item (Model): The item that was added to the database.
            params (Params): Additional data passed to the handler.
        """
        pass

    async def pre_update_merge(
        self,
        item: Model,
        data: dict[str, typing.Any],
        params: PARAM_BODY_SESSION,
    ):
        """
        Pre-process the item before merging it with the data.

        Args:
            item (Model): The item that will be updated in the database.
            data (dict[str, typing.Any]): The data to merge with the item.
            params (PARAM_BODY_QUERY_SESSION): Additional data passed to the handler.
        """
        pass

    async def pre_update(
        self, item: Model, params: PARAM_BODY_SESSION
    ) -> None | Model | typing.Any:
        """
        Pre-process the item before updating it in the database.

        - When a `Model` is returned, it will replace the current `item` and be updated in the database.
        - When any other value is returned, it is assumed to be a response to be returned directly.

        Args:
            item (Model): The item that will be updated in the database.
            params (Params): Additional data passed to the handler.
        """
        pass

    async def post_update(
        self, item: Model, params: PARAM_BODY_SESSION
    ) -> None | Model | typing.Any:
        """
        Post-process the item after updating it in the database.
        But before sending the response.

        - When a `Model` is returned, it will replace the current `item`.
        - When any other value is returned, it is assumed to be a response to be returned directly.

        Args:
            item (Model): The item that was updated in the database.
            params (Params): Additional data passed to the handler.
        """
        pass

    async def pre_delete(
        self, item: Model, params: PARAM_ID_SESSION
    ) -> None | Model | typing.Any:
        """
        Pre-process the item before deleting it from the database.

        - When a `Model` is returned, it will replace the current `item` and be deleted from the database.
        - When any other value is returned, it is assumed to be a response to be returned directly.

        Args:
            item (Model): The item that will be deleted from the database.
            params (Params): Additional data passed to the handler.
        """
        pass

    async def post_delete(
        self, item: Model, params: PARAM_ID_SESSION
    ) -> None | Model | typing.Any:
        """
        Post-process the item after deleting it from the database.
        But before sending the response.

        - When a `Model` is returned, it will replace the current `item`.
        - When any other value is returned, it is assumed to be a response to be returned directly.

        Args:
            item (Model): The item that was deleted from the database.
            params (Params): Additional data passed to the handler.
        """
        pass

    def _create_request_schema(
        self, schema: Type[BaseModel], optional=False, name: str | None = None
    ):
        """
        Create a request schema based on the provided `schema` parameter. Useful for creating request schemas for add and edit endpoints, as it will transform the relation columns into the appropriate schema.

        Args:
            schema (Type[BaseModel]): The base schema to create the request schema from.
            optional (bool, optional): Flag indicating whether the request schema is optional. Defaults to False.
            name (str | None, optional): The name of the request schema. Defaults to None.

        Returns:
            pydantic.BaseModel: The created request schema.
        """
        columns = [
            x
            for x in schema.model_fields.keys()
            if not self.datamodel.is_pk(x) and self.datamodel.is_relation(x)
        ]
        rel_schema = dict()
        for col in columns:
            params = {}
            if optional or self.datamodel.is_nullable(col):
                params["default"] = None
            # For relation, where the relation is one-to-one or many-to-one
            if self.datamodel.is_relation_one_to_one(
                col
            ) or self.datamodel.is_relation_many_to_one(col):
                related_interface = self.datamodel.get_related_interface(col)
                type = related_interface.id_schema | RelInfo
                if optional or self.datamodel.is_nullable(col):
                    type = (
                        type
                        | None
                        | typing.Annotated[
                            typing.Literal["null"],
                            pydantic.AfterValidator(lambda _: None),
                        ]
                    )
                rel_schema[col] = (
                    type,
                    Field(**params),
                )
            else:
                if not optional:
                    params["default"] = []
                type = (
                    List[self.datamodel.get_related_interface(col).id_schema]
                    | List[RelInfo]
                )
                if optional or self.datamodel.is_nullable(col):
                    type = (
                        type
                        | None
                        | typing.Annotated[
                            list[str],
                            pydantic.AfterValidator(
                                lambda value: []
                                if len(value) == 1 and value[0] == "null"
                                else value
                            ),
                        ]
                    )
                related_interface = self.datamodel.get_related_interface(col)
                rel_schema[col] = (
                    type,
                    Field(**params),
                )

        new_schema_name = f"{self.__class__.__name__}-{schema.__name__}"
        new_schema = create_model(
            name or new_schema_name,
            **rel_schema,
            __base__=schema,
        )
        new_schema.model_config["extra"] = "forbid"
        return new_schema

    async def _generate_info_schema(
        self,
        permissions: List[str],
        session: AsyncSession | Session,
        session_count: AsyncSession | Session,
    ):
        """
        Generates the information schema for the API based on the given permissions and database session.

        Args:
            permissions (List[str]): The list of permissions for the API.
            session (AsyncSession | Session): The database session.
            session_count (AsyncSession | Session): The database session for counting.

        Returns:
            InfoSchema: The calculated information schema for the API.
        """
        schema = self.info_return_schema()
        schema.permissions = permissions
        schema.add_columns = []
        schema.edit_columns = []
        schema.filters = {}

        for key, val in self.filter_options.items():
            val = await smart_run(val) if callable(val) else val
            schema.filter_options[key] = val

        rel_cache = {}

        if f"{PERMISSION_PREFIX}post" in permissions:
            for col in self.add_columns:
                filters = self.add_query_rel_fields.get(col)
                order_column, order_direction = self.order_rel_fields.get(
                    col, (None, None)
                )
                cache_key = f"{col}_{filters}_{order_column}_{order_direction}"
                col_info = rel_cache.get(
                    cache_key, self.cache.get(f"column_info_{col}")
                )
                if not col_info:
                    col_info = await smart_run(
                        self.datamodel.get_column_info,
                        col,
                        session,
                        session_count,
                        params={
                            "page": 0,
                            "page_size": self.max_page_size,
                            "order_column": order_column,
                            "order_direction": order_direction,
                            "filter_classes": filters,
                        },
                        description_columns=self.description_columns,
                        label_columns=self.label_columns,
                    )
                    rel_cache[cache_key] = col_info
                    if not isinstance(col_info, ColumnRelationInfo):
                        self.cache[f"column_info_{col}"] = col_info
                schema.add_columns.append(col_info)

            schema.add_schema = (
                self.add_jsonforms_schema
                or self._generate_jsonforms_schema(
                    self.add_obj_schema, schema.add_columns
                )
            )
            schema.add_uischema = self.add_jsonforms_uischema

        if f"{PERMISSION_PREFIX}put" in permissions:
            for col in self.edit_columns:
                filters = self.edit_query_rel_fields.get(col)
                order_column, order_direction = self.order_rel_fields.get(
                    col, (None, None)
                )
                cache_key = f"{col}_{filters}_{order_column}_{order_direction}"
                col_info = rel_cache.get(
                    cache_key, self.cache.get(f"column_info_{col}")
                )
                if not col_info:
                    col_info = await smart_run(
                        self.datamodel.get_column_info,
                        col,
                        session,
                        session_count,
                        params={
                            "page": 0,
                            "page_size": self.max_page_size,
                            "order_column": order_column,
                            "order_direction": order_direction,
                            "filter_classes": filters,
                        },
                        description_columns=self.description_columns,
                        label_columns=self.label_columns,
                    )
                    rel_cache[cache_key] = col_info
                    if not isinstance(col_info, ColumnRelationInfo):
                        self.cache[f"column_info_{col}"] = col_info
                schema.edit_columns.append(col_info)

            schema.edit_schema = (
                self.edit_jsonforms_schema
                or self._generate_jsonforms_schema(
                    self.edit_obj_schema, schema.edit_columns
                )
            )
            schema.edit_uischema = self.edit_jsonforms_uischema

        for col in self.search_columns:
            info = dict()
            datamodel, col_to_get = self._get_datamodel_and_column(col)

            filters = self.cache.get(f"info_filters_{col}", None)
            if not filters:
                filters = datamodel.filters[col_to_get]
                # Add search filters and search exclude filters to the filters
                if "." in col:
                    filters.extend(self.datamodel.filters[col])
                    filters = [
                        f
                        for f in filters
                        if f.arg_name not in self.datamodel.exclude_filters[col]
                    ]

                filters = [{"name": f.name, "operator": f.arg_name} for f in filters]
                self.cache[f"info_filters_{col}"] = filters
            info["filters"] = filters
            info["label"] = self.label_columns.get(col)
            query_filters = self.search_query_rel_fields.get(col)
            order_column, order_direction = self.order_rel_fields.get(col, (None, None))
            cache_key = f"{col}_{query_filters}_{order_column}_{order_direction}"
            info["schema"] = rel_cache.get(
                cache_key, self.cache.get(f"column_info_{col}")
            )
            if not info["schema"]:
                info["schema"] = await smart_run(
                    datamodel.get_column_info,
                    col_to_get,
                    session,
                    session_count,
                    params={
                        "page": 0,
                        "page_size": self.max_page_size,
                        "order_column": order_column,
                        "order_direction": order_direction,
                        "filter_classes": query_filters,
                    },
                    description_columns=self.description_columns,
                    label_columns=self.label_columns,
                )
                if not isinstance(info["schema"], ColumnRelationInfo):
                    self.cache[f"column_info_{col}"] = info["schema"]
                info["schema"].name = col
            schema.filters[col] = info

        return schema

    def _get_datamodel_and_column(self, col: str):
        """
        Gets the corresponding datamodel and column name for a given column. Useful for handling relations.

        Args:
            col (str): The column name.

        Returns:
            Tuple[SQLAInterface, str]: The datamodel and the related column name.
        """
        datamodel = self.datamodel
        col_to_get = col
        while "." in col_to_get:
            rel_col, col_to_get = col_to_get.split(".", 1)
            datamodel = datamodel.get_related_interface(rel_col)
        return datamodel, col_to_get

    async def _process_body(
        self,
        session: AsyncSession | Session,
        body: BaseModel | Dict[str, Any],
        filter_dict: dict[str, list[tuple[str, BaseFilter, Any]]],
        exclude: list[str] | None = None,
        *,
        item: Model | None = None,
    ) -> Dict[str, Any]:
        """
        Process the body of the request by handling relations and returning a new body dictionary.

        Args:
            session (AsyncSession | Session): The session object for the database connection.
            body (BaseModel | Dict[str, Any]): The request body.
            filter_dict (dict[str, list[tuple[str, BaseFilter, Any]]): The filter dictionary.
            exclude (list[str] | None, optional): The list of fields to exclude from the body. Defaults to None.
            item (Model | None, optional): The item to be updated. Defaults to None.

        Returns:
            Dict[str, Any]: The transformed body dictionary.

        Raises:
            HTTPException: If any related items are not found or if an item is not found for a one-to-one or many-to-one relation.
        """
        body_json = (
            body.model_dump(exclude_unset=True, exclude=exclude)
            if isinstance(body, BaseModel)
            else body
        )
        new_body = {}
        for key, value in body_json.items():
            # Return the value as is if it is not a relation
            if not self.datamodel.is_relation(key):
                # If the value is a file or an image, convert it to a file path
                if self.datamodel.is_file(key) or self.datamodel.is_image(key):
                    # Only process if the value is not a string
                    if isinstance(value, str):
                        new_body[key] = value
                        continue

                    fm = (
                        self.file_manager
                        if self.datamodel.is_file(key)
                        else self.image_manager
                    )

                    # Delete existing file or image if it is being updated
                    if item and hasattr(item, key) and getattr(item, key):
                        old_filename = getattr(item, key)
                        AsyncTaskRunner.add_task(
                            lambda fm=fm, old_filename=old_filename: smart_run(
                                fm.delete_file, old_filename
                            ),
                            tags=["file"],
                        )

                    # Only process if the value exists and is not None
                    if value:
                        new_name = fm.generate_name(value.filename)
                        content = await value.read()
                        AsyncTaskRunner.add_task(
                            lambda fm=fm, content=content, new_name=new_name: smart_run(
                                fm.save_content_to_file, content, new_name
                            ),
                            tags=["file"],
                        )
                        value = new_name

                new_body[key] = value
                continue

            if not value:
                if self.datamodel.is_relation_one_to_many(
                    key
                ) or self.datamodel.is_relation_many_to_many(key):
                    new_body[key] = []
                else:
                    new_body[key] = None
                continue

            related_interface = self.datamodel.get_related_interface(key)
            related_items = None

            if isinstance(value, list):
                value = [
                    val.get("id") if isinstance(val, dict) else val for val in value
                ]
                related_items = await smart_run(
                    related_interface.get_many,
                    session,
                    params={
                        "where_id_in": value,
                        "filter_classes": filter_dict.get(key),
                    },
                )
                # If the length is not equal, then some items were not found
                if len(related_items) != len(value):
                    raise HTTPException(
                        status_code=400, detail=f"Some items in {key} not found"
                    )

                new_body[key] = related_items
                continue

            value = value.get("id") if isinstance(value, dict) else value
            related_item = await smart_run(
                related_interface.get_one,
                session,
                params={"where_id": value, "filter_classes": filter_dict.get(key)},
            )
            if not related_item:
                raise HTTPException(400, detail=f"{key} not found")
            new_body[key] = related_item

        return new_body

    """
    -----------------------------------------
         HELPER FUNCTIONS
    -----------------------------------------
    """

    def _gen_labels_columns(self, list_columns: List[str]) -> None:
        """
        Auto generates pretty label_columns from list of columns
        """
        for col in list_columns:
            if not self.label_columns.get(col):
                self.label_columns[col] = self._prettify_column(col)

    @staticmethod
    def _prettify_name(name: str) -> str:
        """
        Prettify pythonic variable name.

        For example, 'HelloWorld' will be converted to 'Hello World'

        :param name:
            Name to prettify.
        """
        return re.sub(r"(?<=.)([A-Z])", r" \1", name)

    @staticmethod
    def _prettify_column(name: str) -> str:
        """
        Prettify pythonic variable name.

        For example, 'hello_world' will be converted to 'Hello World'

        :param name:
            Name to prettify.
        """
        return re.sub("[._]", " ", name).title()

    def _init_filters(
        self, datamodel: SQLAInterface, filters: List[Tuple[str, Type[BaseFilter], Any]]
    ):
        """
        Initialize the filter for the API.

        Args:
            datamodel (SQLAInterface): The datamodel object.
            filters (List[Tuple[str, Type[BaseFilter], Any]]): The list of filters to initialize.

        Returns:
            List[Tuple[str, Type[BaseFilter], Any]]: The initialized filters.
        """
        return [
            (
                x[0],
                x[1](
                    datamodel
                    if "." not in x[0]
                    else datamodel.get_related_interface(x[0].split(".")[0])
                ),
                x[2],
            )
            for x in filters
        ]

    def _handle_schema_extra_fields(
        self,
        schema_extra_fields: dict[str, type | tuple[type, pydantic.fields.FieldInfo]],
    ):
        """
        Handle the schema extra fields for the API.
        This will transform the fields into a dictionary with the field name as the key and the field type as the value if the field is not a tuple.

        Args:
            schema_extra_fields (dict[str, type | tuple[type, pydantic.fields.FieldInfo]]): The schema extra fields to handle.

        Returns:
            dict[str, tuple[type, pydantic.fields.FieldInfo]]: The transformed schema extra fields.
        """
        result: dict[str, tuple[type, pydantic.fields.FieldInfo]] = dict()

        for key in schema_extra_fields:
            value = schema_extra_fields[key]
            if not isinstance(value, tuple):
                is_nullable = False
                try:
                    args = typing.get_args(value)
                    for arg in args:
                        if arg is types.NoneType:
                            is_nullable = True
                            break
                except Exception:
                    pass

                result[key] = (
                    value,
                    Field(**{"default": None} if is_nullable else {}),
                )
            else:
                result[key] = value

        return result

    def _generate_jsonforms_schema(
        self,
        schema: type[BaseModel],
        info_columns: list[ColumnInfo | ColumnEnumInfo | ColumnRelationInfo],
    ):
        """
        Generate the JSONForms schema for the API.

        Args:
            schema (type[BaseModel]): The schema to generate the JSONForms schema from.
            info_columns (list[ColumnInfo | ColumnEnumInfo | ColumnRelationInfo]): The list of columns to include in the JSONForms schema.

        Returns:
            dict: The generated JSONForms schema.
        """
        jsonforms_schema = schema.model_json_schema()

        # Remove unused vars
        jsonforms_schema.pop("$defs", None)

        for key, value in jsonforms_schema["properties"].items():
            label = self.label_columns.get(key)
            if label:
                value["title"] = label

            description = self.description_columns.get(key)
            if description:
                value["description"] = description

            if self.datamodel.is_file(key) or self.datamodel.is_image(key):
                value["type"] = "string"
                value["contentMediaType"] = (
                    ", ".join(
                        [
                            f"application/{ext}"
                            for ext in self.file_manager.allowed_extensions
                        ]
                    )
                    if self.file_manager.allowed_extensions
                    else ""
                    if self.datamodel.is_file(key)
                    else ", ".join(
                        [
                            f"image/{ext}"
                            for ext in self.image_manager.allowed_extensions
                        ]
                    )
                    if self.image_manager.allowed_extensions
                    else "image/*"
                )
            elif self.datamodel.is_boolean(key):
                value["type"] = "boolean"
            elif self.datamodel.is_integer(key):
                value["type"] = "integer"
            elif self.datamodel.is_enum(key):
                value["type"] = "string"
                enum_val = self.datamodel.get_enum_value(key)
                if isinstance(enum_val, enum.EnumType):
                    enum_val = [str(item.value) for item in enum_val]
                value["enum"] = enum_val
            elif self.datamodel.is_json(key) or self.datamodel.is_jsonb(key):
                value["type"] = "object"
            elif self.datamodel.is_relation(key):
                info = [x for x in info_columns if x.name == key]
                if not info:
                    raise Exception(f"Could not find info for {key} in {info_columns}")
                info = info[0]

                value["type"] = "string"
                value["oneOf"] = [
                    {
                        "const": str(item.id),
                        "title": item.value,
                    }
                    for item in info.values
                ]
                if not value["oneOf"]:
                    value["oneOf"].append(
                        {
                            "const": "null",
                            "title": "null",
                        }
                    )
                    value["readOnly"] = True

                if self.datamodel.is_relation_one_to_many(
                    key
                ) or self.datamodel.is_relation_many_to_many(key):
                    value["type"] = "array"
                    value["uniqueItems"] = True
                    value["items"] = {"oneOf": value["oneOf"]}
                    del value["oneOf"]
            else:
                # Check for anyOf (multiple possible types) and convert it to only one type
                anyOf = value.get("anyOf")
                if anyOf:
                    anyOf = filter(lambda x: x.get("type") != "null", anyOf)
                    for item in anyOf:
                        value = deep_merge(value, item)

            # Check whether it is nullable
            if self.datamodel.is_nullable(key):
                value["type"] = [value["type"], "null"]

            # Remove unused vars
            value.pop("anyOf", None)
            value.pop("default", None)
            value.pop("$ref", None)

            # Check whether the value should be a `secret`
            if key in g.sensitive_data.get(self.datamodel.obj.__name__, []):
                value["format"] = "password"

            jsonforms_schema["properties"][key] = value

        return jsonforms_schema

    async def _export_data(
        self,
        data: list[Model],
        list_columns: list[str],
        label_columns: dict[str, str],
        schema: type[BaseModel],
        *,
        export_mode: ExportMode = "simplified",
        delimiter: str = ",",
        quotechar: str = '"',
    ):
        """
        Export data to CSV format.

        Args:
            data (list[Model]): List of data to export.
            list_columns (list[str]): List of columns to include in the export.
            label_columns (dict[str, str]): Mapping of column names to labels.
            schema (type[BaseModel]): Schema for the data.
            export_mode (ExportMode, optional): Export mode (simplified or detailed). Defaults to "simplified".
            delimiter (str, optional): Delimiter for the CSV file. Defaults to ",".
            quotechar (str): Quote character for the CSV file. Defaults to '"'.

        Yields:
            str: CSV formatted data.
        """
        line = Line()
        writer = csv.writer(line, delimiter=delimiter, quotechar=quotechar)

        # header
        labels = []
        for key in list_columns:
            if export_mode == "detailed":
                labels.append(key)
            else:
                labels.append(label_columns[key])

        # rows
        writer.writerow(labels)
        yield line.read()

        async for chunk in data:
            for item in chunk:
                async with AsyncTaskRunner():
                    item_model = schema.model_validate(item, from_attributes=True)
                item_dict = item_model.model_dump(mode="json")
                row = CSVJSONConverter._json_to_csv(
                    item_dict,
                    list_columns=list_columns,
                    delimiter=delimiter,
                    export_mode=export_mode,
                )
                writer.writerow(row)
                yield line.read()

    async def _import_data(
        self,
        data: str | bytes,
        session: AsyncSession | Session,
        *,
        delimiter: str = ",",
        quotechar: str = '"',
    ):
        """
        Import data from CSV format. This will parse the CSV data and resolve any relationships.

        Args:
            data (str | bytes): The CSV data to import.
            query (QueryManager): The query manager object.
            session (AsyncSession | Session): The session object for the database connection.
            delimiter (str, optional): Delimiter for the CSV file. Defaults to ",".
            quotechar (str): Quote character for the CSV file. Defaults to '"'.

        Raises:
            HTTPException: If the length of the items does not match the number of items found for one-to-many or many-to-many relationships.

        Returns:
            list[dict[str, typing.Any]]: List of dictionaries containing the imported data with relationships resolved.
        """
        list_data = await smart_run(
            CSVJSONConverter.csv_to_json,
            data,
            delimiter=delimiter,
            quotechar=quotechar,
        )

        # Parse relationships
        for dat in list_data:
            relation_data = {}

            for col in self.add_columns:
                if col not in dat:
                    continue

                if self.datamodel.is_relation(col):
                    rel_interface = self.datamodel.get_related_interface(col)

                    item = dat.get(col)
                    if isinstance(item, list):
                        items = await smart_run(
                            rel_interface.get_many,
                            session,
                            params={
                                "where_id_in": item,
                            },
                        )
                        if len(items) != len(item):
                            raise HTTPException(
                                status_code=400,
                                detail=f"Length of {col} does not match the number of items found.",
                            )
                        item = items
                        continue
                    else:
                        item = await smart_run(
                            rel_interface.get_one,
                            session,
                            params={
                                "where": [(k, v) for k, v in dat.get(col, {}).items()]
                            },
                        )
                        if not item:
                            item = rel_interface.obj(**dat.get(col, {}))
                            await smart_run(
                                rel_interface.add, session, item, commit=False
                            )

                    relation_data[col] = item
                    dat[col] = item

            dat.update(
                **{
                    **self.add_obj_schema(**dat).model_dump(exclude_unset=True),
                    **relation_data,
                },
            )
            await smart_run(
                self.datamodel.add, session, self.datamodel.obj(**dat), commit=False
            )
        await smart_run(self.datamodel.commit, session)

        return list_data

    """
    --------------------------------------------------------------------------------------------------------
        ROUTE HELPER METHODS
    --------------------------------------------------------------------------------------------------------
    """

    def _validate_query_parameters(self, q: QuerySchema):
        """
        Validate the query parameters.

        - Check if the `filters` are specified in the search columns.
        - Check if the `columns` are specified in the list select columns.

        Args:
            q (QuerySchema): The query schema containing the parameters.

        Raises:
            HTTPException: If any of the filters or columns are invalid.
        """
        for filter in q.filters:
            if filter.col not in self.search_columns:
                raise HTTPException(
                    status_code=400, detail=f"Invalid filter: {filter.col}"
                )
        for col in q.columns:
            if col not in self.list_select_columns:
                raise HTTPException(status_code=400, detail=f"Invalid column: {col}")

    def _handle_query_params(self, q: QuerySchema):
        """
        Handle the query parameters for the API.

        Args:
            q (QuerySchema): The query schema containing the parameters.

        Returns:
            DBQueryParams: The query parameters for the database query.
        """
        base_order = None
        base_order_direction = None
        if self.base_order:
            base_order, base_order_direction = self.base_order
        return DBQueryParams(
            list_columns=q.columns or self.list_select_columns,
            page=q.page,
            page_size=q.page_size,
            order_column=q.order_column or base_order,
            order_direction=q.order_direction or base_order_direction,
            filters=q.filters,
            filter_classes=self.base_filters,
            global_filter=(self.list_columns, q.global_filter)
            if q.global_filter
            else None,
        )
