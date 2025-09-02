import json
import typing
from datetime import datetime
from typing import Annotated, Any, Dict, Literal

from fastapi import HTTPException
from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    EmailStr,
    Field,
    ValidationError,
    ValidationInfo,
    field_validator,
)

from .const import logger
from .utils import ensure_tz_info, merge_schema, validate_utc

if typing.TYPE_CHECKING:
    from .security.sqla.models import Role, User

__all__ = [
    "PRIMARY_KEY",
    "DatetimeUTC",
    "RelInfo",
    "ColumnInfo",
    "ColumnEnumInfo",
    "ColumnRelationInfo",
    "SearchFilter",
    "InfoResponse",
    "BaseResponse",
    "BaseResponseSingle",
    "BaseResponseMany",
    "GeneralResponse",
    "FilterSchema",
    "QuerySchema",
    "QueryBody",
]

PRIMARY_KEY = int | str | list[str]

DatetimeUTC = Annotated[
    datetime, BeforeValidator(ensure_tz_info), AfterValidator(validate_utc)
]


def _convert_roles_to_list_of_string(roles: list["Role | str"]):
    from .security.sqla.models import Role

    return [x.name if isinstance(x, Role) else x for x in roles]


cached_schema: Dict[str, typing.Type[BaseModel]] = {}


def generate_user_get_schema(model: typing.Type["User"]):
    if "GetUserSchema" in cached_schema:
        return cached_schema["GetUserSchema"]

    from .backends.sqla.interface import SQLAInterface

    get_user_ignored_columns = ["oauth_accounts"]

    user_datamodel = SQLAInterface(model)
    pk_attrs = user_datamodel.get_pk_attrs()
    columns = [
        x
        for x in user_datamodel.get_user_column_list()
        + user_datamodel.get_property_column_list()
        if x not in get_user_ignored_columns
    ]
    schema = merge_schema(
        user_datamodel.generate_schema(
            columns,
            with_id=False,
            with_name=False,
        ),
        {
            **{pk: (PRIMARY_KEY, Field(...)) for pk in pk_attrs},
            "roles": (
                Annotated[list[str], BeforeValidator(_convert_roles_to_list_of_string)],
                Field([]),
            ),
            "permissions": (list[str], Field([])),
        },
        name=f"{model.__name__}-GetUserSchema",
    )
    cached_schema["GetUserSchema"] = schema
    return schema


def generate_user_create_schema(model: typing.Type["User"], exclude_relations=False):
    key = "CreateUserSchema" + ("-exclude_relations" if exclude_relations else "")
    if key in cached_schema:
        return cached_schema[key]

    from .backends.sqla.interface import SQLAInterface

    create_user_ignored_columns = [
        "id",
        "oauth_accounts",
        "roles",
        "last_login",
        "login_count",
        "fail_login_count",
        "created_on",
        "changed_on",
    ]

    user_datamodel = SQLAInterface(model)
    columns = [
        x
        for x in user_datamodel.get_user_column_list()
        if x not in create_user_ignored_columns
    ]
    if exclude_relations:
        columns = [x for x in columns if not user_datamodel.is_relation(x)]
    schema = merge_schema(
        user_datamodel.generate_schema(
            columns,
            with_id=False,
            with_name=False,
            optional=True,
            hide_sensitive_columns=False,
        ),
        {
            "email": (EmailStr, Field(...)),
        },
        name=f"{model.__name__}-{key}",
    )
    cached_schema[key] = schema
    return schema


def generate_user_update_schema(model: typing.Type["User"], exclude_relations=False):
    key = "UpdateUserSchema" + ("-exclude_relations" if exclude_relations else "")
    if key in cached_schema:
        return cached_schema[key]

    from .backends.sqla.interface import SQLAInterface

    update_user_ignored_columns = [
        "oauth_accounts",
        "roles",
        "last_login",
        "login_count",
        "fail_login_count",
        "created_on",
        "changed_on",
    ]

    user_datamodel = SQLAInterface(model)
    columns = [
        x
        for x in user_datamodel.get_user_column_list()
        if x not in update_user_ignored_columns
    ]
    if exclude_relations:
        columns = [x for x in columns if not user_datamodel.is_relation(x)]
    schema = merge_schema(
        user_datamodel.generate_schema(
            columns,
            with_id=False,
            with_name=False,
            optional=True,
            hide_sensitive_columns=False,
        ),
        {
            "email": (EmailStr | None, Field(None)),
        },
        name=f"{model.__name__}-{key}",
    )
    cached_schema[key] = schema
    return schema


class RelInfo(BaseModel):
    """
    Represents information about a relationship.

    Attributes:
        id (PRIMARY_KEY): The ID of the relationship.
        value (str): The value of the relationship.
    """

    id: PRIMARY_KEY = 0
    value: str = ""


class ColumnInfo(BaseModel):
    """
    Represents information about a column.

    Attributes:
        description (str): The description of the column.
        label (str): The label of the column.
        name (str): The name of the column.
        required (bool): Indicates if the column is required.
        type (str): The type of the column.
        unique (bool): Indicates if the column values must be unique.
    """

    description: str = ""
    label: str = ""
    name: str = ""
    required: bool = False
    type: str = "string"
    unique: bool = False


class ColumnEnumInfo(ColumnInfo):
    """
    Represents information about a column with enum values.

    Attributes:
        values (List[str]): The list of enum values.
    """

    values: list[str | int] = []


class ColumnRelationInfo(ColumnInfo):
    """
    Represents information about a column relation.

    Attributes:
        count (int): The count of column relations.
        values (List[RelInfo]): The list of column relations.
    """

    count: int = 0
    values: list[RelInfo] = []


class SearchFilter(BaseModel):
    """
    Represents a search filter.

    Attributes:
        name (str): The name of the filter.
        operator (str): The operator to be used for filtering.
    """

    name: str = ""
    operator: str = ""


class InfoResponse(BaseModel):
    """
    Represents the info response object.

    Attributes:
        add_columns (list[ColumnInfo | ColumnEnumInfo | ColumnRelationInfo]): The allowed columns for adding.
        add_title (str): The title for adding.
        add_schema (dict[str, Any]): The schema for adding.
        add_uischema (dict[str, Any] | None): The UI schema for adding.
        add_type (typing.Literal["json"] | typing.Literal["form"]): The type for adding. Defaults to "json".
        edit_columns (list[ColumnInfo | ColumnEnumInfo | ColumnRelationInfo]): The allowed columns for editing.
        edit_title (str): The title for editing.
        edit_schema (dict[str, Any]): The schema for editing.
        edit_uischema (dict[str, Any] | None): The UI schema for editing.
        edit_type (typing.Literal["json"] | typing.Literal["form"]): The type for editing. Defaults to "json".
        filters (dict[str, Any]): The filters for the response.
        filter_options (dict[str, Any]): The filter options for the response.
        permissions (list[str]): The permissions for the response.
        relations (list[str]): The relations for the response.
    """

    add_columns: list[ColumnInfo | ColumnEnumInfo | ColumnRelationInfo] = []
    add_title: str = ""
    add_schema: dict[str, Any] = {}
    add_uischema: dict[str, Any] | None = None
    add_type: typing.Literal["json"] | typing.Literal["form"] = "json"
    edit_columns: list[ColumnInfo | ColumnEnumInfo | ColumnRelationInfo] = []
    edit_title: str = ""
    edit_schema: dict[str, Any] = {}
    edit_uischema: dict[str, Any] | None = None
    edit_type: typing.Literal["json"] | typing.Literal["form"] = "json"
    filters: dict[str, Any] = {}
    filter_options: dict[str, Any] = {}
    permissions: list[str] = []
    relations: list[str] = []


class BaseResponse(BaseModel):
    """
    Represents a base response object.

    Attributes:
        description_columns (dict[str, str]): The description columns for the response.
        label_columns (dict[str, str]): The label columns for the response.
    """

    description_columns: dict[str, str] = {}
    label_columns: dict[str, str] = {}


class BaseResponseSingle(BaseResponse):
    """
    Represents a response containing a single item.

    Attributes:
        id (PRIMARY_KEY): The ID of the item.
        show_columns (list[str]): The columns to show in the response.
        show_title (str): The title for the response.
        result (BaseModel | None): The result of the response.
    """

    id: PRIMARY_KEY
    show_columns: list[str] = []
    show_title: str = ""
    result: BaseModel | None = None


class BaseResponseMany(BaseResponse):
    """
    Represents a response containing multiple items.

    Attributes:
        count (int): The count of items.
        ids (List[PRIMARY_KEY]): The IDs of the items.
        list_columns (List[str]): The columns to show in the list.
        list_title (str): The title for the list.
        order_columns (List[str]): The columns to order the items by.
        result (List[BaseModel] | None): The result of the response.
    """

    count: int
    ids: list[PRIMARY_KEY]
    list_columns: list[str] = []
    list_title: str = ""
    order_columns: list[str] = []
    result: list[BaseModel] | None = None


class GeneralResponse(BaseModel):
    """
    Represents a general response object.

    Attributes:
        detail (str): The detail of the response.
    """

    detail: str


class FilterSchema(BaseModel):
    """
    Represents a filter for querying data.

    Attributes:
        col (str): The column name to filter on.
        opr (str): The operator to use for the filter.
        value (Union[PRIMARY_KEY, bool, Dict[str, Any], List[Union[PRIMARY_KEY, bool, Dict[str, Any]]]]): The value to filter on.

    """

    col: str
    opr: str
    value: (
        PRIMARY_KEY | bool | dict[str, Any] | list[PRIMARY_KEY | bool | dict[str, Any]]
    )


class QuerySchema(BaseModel):
    """
    Represents the query parameters for selection, pagination, ordering, and filtering.

    Attributes:
        columns (str, optional): The columns to select in the query. Defaults to '[]'.
        page (int): The page number for pagination. Defaults to 0.
        page_size (int, optional): The number of items per page. Defaults to 25.
        order_column (str, optional): The column to order the results by.
        order_direction (Literal['asc', 'desc'], optional): The direction of the ordering (asc or desc).
        filters (str, optional): The filters to apply to the query. Defaults to '[]'.
        global_filter (str, optional): The filter to apply globally across all columns.
    """

    columns: str = "[]"
    page: int = 0
    page_size: int | None = 25
    order_column: str | None = None
    order_direction: Literal["asc", "desc"] | None = None
    filters: str = "[]"
    global_filter: str | None = None

    @field_validator("columns")
    @classmethod
    def validate_columns(cls, v: str | list[str]):
        try:
            logger.debug(f"Validating columns: {v}")
            columns = json.loads(v) if isinstance(v, str) else v
            logger.debug(f"Columns: {columns}")
            if not isinstance(columns, list):
                raise ValueError("Columns must be a list")
            return [str(col) for col in columns]
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400, detail="Invalid columns: Not a valid JSON string"
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @field_validator("order_direction")
    @classmethod
    def validate_order_fields(cls, v: str | None, info: ValidationInfo):
        data = info.data
        try:
            if bool(v) != bool(data.get("order_column")):
                raise ValueError(
                    "Both order_column and order_direction must be filled or empty"
                )
            return str(v) if v else v
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Both order_column and order_direction must be filled or empty",
            )

    @field_validator("filters")
    @classmethod
    def validate_filters(cls, v: str | list[FilterSchema]):
        try:
            logger.debug(f"Validating filters: {v}")
            filters = json.loads(v) if isinstance(v, str) else v
            logger.debug(f"Filters: {filters}")
            if not isinstance(filters, list):
                raise ValueError("Filters must be a list")
            new_filters = []
            for filter in filters:
                if isinstance(filter, FilterSchema):
                    new_filters.append(filter)
                elif isinstance(filter, dict):
                    new_filters.append(FilterSchema(**filter))
                else:
                    raise ValueError("Filter must be a dictionary")
            return new_filters
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400, detail="Invalid filters: Not a valid JSON string"
            )
        except ValidationError as e:
            raise HTTPException(
                status_code=400,
                detail={
                    "type": "ValidationError",
                    "loc": ["query", "filters"],
                    "msg": e.errors(),
                },
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))


class QueryBody(QuerySchema):
    """
    Schema for query, but in the request body.
    """

    filters: list[FilterSchema] = []
