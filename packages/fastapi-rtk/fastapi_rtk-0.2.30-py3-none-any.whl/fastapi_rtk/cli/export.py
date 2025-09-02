import collections
import json
import typing

import jsonschema2md
import typer

from ..api.model_rest_api import ModelRestApi
from ..backends.sqla.model import metadatas
from ..const import (
    ACCESSTOKEN_TABLE,
    API_TABLE,
    ASSOC_PERMISSION_API_ROLE_TABLE,
    ASSOC_USER_ROLE_TABLE,
    OAUTH_TABLE,
    PERMISSION_API_TABLE,
    PERMISSION_TABLE,
    ROLE_TABLE,
    USER_TABLE,
)
from ..db import db
from ..globals import g
from .commands import version_callback
from .const import logger
from .decorators import ensure_fastapi_rtk_tables_exist
from .types import (
    APIDataDocs,
    APIDocs,
    APIMetadataDocs,
    APIPathDocs,
    DBDataDocs,
    DBDocs,
    DBTableColumnDocs,
    DBTableDocs,
    TableDocumentation,
)
from .utils import json_to_markdown, run_in_current_event_loop

export_app = typer.Typer(rich_markup_mode="rich")

table_documentation: collections.defaultdict[str, TableDocumentation] = (
    collections.defaultdict(lambda: TableDocumentation(description="", columns={}))
)


@export_app.callback()
@ensure_fastapi_rtk_tables_exist
def callback(
    version: typing.Annotated[
        typing.Union[bool, None],
        typer.Option(
            "--version", help="Show the version and exit.", callback=version_callback
        ),
    ] = None,
) -> None:
    """
    FastAPI RTK Export CLI - The [bold]fastapi-rtk export[/bold] command line app. 😎

    Export your [bold]FastAPI React Toolkit[/bold] data easily with this CLI.
    """


@export_app.command()
def api_schema(
    apis: typing.Annotated[
        str | None,
        typer.Option(
            ...,
            help="The APIs to export. Can be a list of APIs separated by '|' or based on the separator set in the parameter. It can also be a single API name. If not provided, all APIs will be exported. E.g: 'UsersApi|ProductsApi' or 'UsersApi'.",
        ),
    ] = None,
    filename: typing.Annotated[
        str,
        typer.Option(
            ...,
            help="The filename to export the schema to.",
        ),
    ] = "api_schema.json",
    separator: typing.Annotated[
        str,
        typer.Option(
            ...,
            help="The separator to use for the exported schema.",
        ),
    ] = "|",
):
    """
    Export the JSONForms schema from the APIs to a file.
    """
    api_classes = g.current_app.apis
    if apis:
        # Split the APIs based on the separator
        api_names = apis.split(separator)
        # Filter the APIs based on the provided names
        api_classes = [
            api for api in api_classes if api.__class__.__name__ in api_names
        ]
        # Throws error if APIs contains `BaseApi`
        if any(not isinstance(api, ModelRestApi) for api in api_classes):
            raise ValueError("You cannot export APIs that are not ModelRestApi.")
    else:
        api_classes = [api for api in api_classes if isinstance(api, ModelRestApi)]

    result = run_in_current_event_loop(_export_api_schema(api_classes), 100)
    # Save the result to a file
    with open(filename, "w") as f:
        f.write(json.dumps(result, indent=2))
    logger.info(f"Exported API schema to {filename}.")


@export_app.command()
def api_docs(
    apis: typing.Annotated[
        str | None,
        typer.Option(
            ...,
            help="The APIs to export. Can be a list of APIs separated by '|' or based on the separator set in the parameter. It can also be a single API name. If not provided, all APIs will be exported. E.g: 'UsersApi|ProductsApi' or 'UsersApi'.",
        ),
    ] = None,
    filename: typing.Annotated[
        str,
        typer.Option(
            ...,
            help="The filename to export the schema to.",
        ),
    ] = "api_docs.md",
    separator: typing.Annotated[
        str,
        typer.Option(
            ...,
            help="The separator to use for the exported schema.",
        ),
    ] = "|",
):
    """
    Export the API documentation to a markdown file.
    """
    api_data_docs = APIDocs(APIs={}, Schemas={})
    api_classes = g.current_app.apis
    if apis:
        # Split the APIs based on the separator
        api_names = apis.split(separator)
        # Filter the APIs based on the provided names
        api_classes = [
            api for api in api_classes if api.__class__.__name__ in api_names
        ]

    for api in api_classes:
        api.integrate_router(g.current_app.app)
        api_data_docs["APIs"][api.__class__.__name__] = APIDataDocs(
            Description=api.description, Paths=[], Metadata={}
        )

    openapi_docs = g.current_app.app.openapi()
    parser = jsonschema2md.Parser(
        examples_as_yaml=False, show_examples="all", header_level=1
    )

    # Load all schema into the docs
    for key, schema in openapi_docs["components"]["schemas"].items():
        parsed_schema = parser.parse_schema(schema)
        parsed_schema[0] = parsed_schema[0].replace(key, f"Schemas-{key}")
        api_data_docs["Schemas"][key] = "".join(parsed_schema)
    api_data_docs["Schemas"] = list(api_data_docs["Schemas"].values())

    for path, data in openapi_docs["paths"].items():
        for method, method_data in data.items():
            for tag in method_data["tags"]:
                if tag not in api_data_docs["APIs"]:
                    continue

                api_path_docs = APIPathDocs(
                    path=path,
                    method=method.upper(),
                    description=method_data.get("summary", ""),
                )

                # Add responses to the API data docs
                responses = []
                for status_code, response_data in method_data.get(
                    "responses", {}
                ).items():
                    content = (
                        response_data.get("content", {})
                        .get("application/json", {})
                        .get("schema", {})
                        .get("$ref", "")
                    )
                    content = (f"[{content.split('/')[-1]}]" if content else "") + (
                        f"({content})" if content else ""
                    )
                    content = content.replace("#/components/", "#").replace("/", "-")
                    response = {
                        "status code": status_code,
                        "description": response_data.get("description", ""),
                        "content": content,
                    }
                    responses.append(response)

                # Add body to the API data docs
                body = method_data.get("requestBody", {}).get("content", {})
                if body:
                    content = list(body.values())[0].get("schema", {}).get("$ref", "")
                    content = (f"[{content.split('/')[-1]}]" if content else "") + (
                        f"({content})" if content else ""
                    )
                    content = content.replace("#/components/", "#").replace("/", "-")
                    body = content

                api_metadata_docs = APIMetadataDocs(
                    Parameters=method_data.get("parameters", []),
                    Body=body,
                    Responses=responses,
                )

                # Add metadata to the API data docs
                api_data_docs["APIs"][tag]["Metadata"][path] = api_metadata_docs

                api_data_docs["APIs"][tag]["Paths"].append(api_path_docs)

                # Add schema
                schemas_to_add = []
                for resp in responses:
                    if resp["content"]:
                        schemas_to_add.append(resp["content"])

                if body:
                    schemas_to_add.append(body)

                for schema in schemas_to_add:
                    key = schema.split("]")[0].replace("[", "")
                    schema = openapi_docs["components"]["schemas"].get(key)
                    if schema:
                        parsed_schema = parser.parse_schema(schema)
                        parsed_schema[0] = parsed_schema[0].replace(
                            key, f"Schemas-{key}"
                        )

    with open(filename, "w") as f:
        f.write(
            json_to_markdown(
                api_data_docs,
                configuration={
                    "Paths": {"list_as_table": True},
                    "Parameters": {"list_as_table": True},
                    "Responses": {"list_as_table": True},
                    "Schemas": {"list_as_is": True},
                },
            )
        )
    logger.info(f"Exported API docs to {filename}.")


@export_app.command()
def db_docs(
    tables: typing.Annotated[
        str | None,
        typer.Option(
            ...,
            help="The tables to export. Can be a list of tables separated by '|' or based on the separator set in the parameter. It can also be a single table name. If not provided, all tables will be exported. E.g: 'Users|Products' or 'Users'.",
        ),
    ] = None,
    filename: typing.Annotated[
        str,
        typer.Option(
            ...,
            help="The filename to export the schema to.",
        ),
    ] = "db_docs.md",
    separator: typing.Annotated[
        str,
        typer.Option(
            ...,
            help="The separator to use for the exported schema.",
        ),
    ] = "|",
):
    """
    Export the database schema to a markdown file.
    """
    # Generate the table documentation
    _generate_fastapi_rtk_tables_docs()

    data = DBDocs(Database={})
    for bind, metadata in metadatas.items():
        data["Database"][bind] = DBDataDocs(Summary=[], Tables={})
        for table in metadata.sorted_tables:
            table_docs = DBTableDocs(
                Description=table_documentation[table.name].get("description"),
                Columns=[],
            )
            for column in table.columns:
                table_column_docs = DBTableColumnDocs(
                    name=column.name,
                    type=str(column.type),
                    nullable=column.nullable,
                    description=table_documentation[table.name]
                    .get("columns", {})
                    .get(column.name, ""),
                    default=str(column.default or ""),
                )
                table_docs["Columns"].append(table_column_docs)
            table_docs["PrimaryKeys"] = [
                column.name for column in table.primary_key.columns
            ]
            data["Database"][bind]["Summary"].append(
                {
                    "name": table.name,
                    "description": table_documentation[table.name].get("description"),
                }
            )
            data["Database"][bind]["Tables"][table.name] = table_docs

    # Filter the tables based on the provided names
    if tables:
        # Split the tables based on the separator
        table_names = tables.split(separator)
        # Filter the tables based on the provided names
        for bind, db_data in data["Database"].items():
            db_data["Tables"] = {
                table_name: table_docs
                for table_name, table_docs in db_data["Tables"].items()
                if table_name in table_names
            }

    # Convert the data to markdown
    markdown = json_to_markdown(
        data,
        configuration={
            "Summary": {"list_as_table": True},
            "Columns": {"list_as_table": True},
        },
    )

    # Save the result to a file
    with open(filename, "w") as f:
        f.write(markdown)
    logger.info(f"Exported DB docs to {filename}.")


async def _export_api_schema(apis: list[ModelRestApi]):
    result = {}
    for api in apis:
        async with db.session(
            getattr(api.datamodel.obj, "__bind_key__", None)
        ) as session:
            info = await api._generate_info_schema([], session, session)
            result[api.__class__.__name__] = {}
            result[api.__class__.__name__]["add"] = {
                "schema": info.add_schema,
                "ui_schema": info.add_uischema,
            }
            result[api.__class__.__name__]["edit"] = {
                "schema": info.edit_schema,
                "ui_schema": info.edit_uischema,
            }
    return result


def _generate_fastapi_rtk_tables_docs():
    # User docs
    table_documentation[USER_TABLE]["description"] = (
        table_documentation[USER_TABLE]["description"]
        or "Stores the user information within the application."
    )
    table_documentation[USER_TABLE]["columns"] = table_documentation[USER_TABLE][
        "columns"
    ] or {
        "id": "Primary key.",
        "email": "User's email address.",
        "username": "User's login username.",
        "password": "User's hashed password.",
        "first_name": "First name of the user.",
        "last_name": "Last name of the user.",
        "active": "Whether the user account is active.",
        "last_login": "Timestamp of the last login.",
        "login_count": "Number of successful logins.",
        "fail_login_count": "Number of failed login attempts.",
        "created_on": "When the user was created.",
        "changed_on": "When the user was last updated.",
        "created_by_fk": f"FK to `{USER_TABLE}.id` (who created this user).",
        "changed_by_fk": f"FK to `{USER_TABLE}.id` (who last updated this user).",
    }

    # Role docs
    table_documentation[ROLE_TABLE]["description"] = (
        table_documentation[ROLE_TABLE]["description"]
        or "Stores the roles within the application."
    )
    table_documentation[ROLE_TABLE]["columns"] = table_documentation[ROLE_TABLE][
        "columns"
    ] or {
        "id": "Primary key.",
        "name": "Role name.",
    }

    # Permission docs
    table_documentation[PERMISSION_TABLE]["description"] = (
        table_documentation[PERMISSION_TABLE]["description"]
        or "Stores the permissions within the application."
    )
    table_documentation[PERMISSION_TABLE]["columns"] = table_documentation[
        PERMISSION_TABLE
    ]["columns"] or {
        "id": "Primary key.",
        "name": "Permission name.",
    }

    # Api docs
    table_documentation[API_TABLE]["description"] = (
        table_documentation[API_TABLE]["description"]
        or "Stores the API classes within the application."
    )
    table_documentation[API_TABLE]["columns"] = table_documentation[API_TABLE][
        "columns"
    ] or {
        "id": "Primary key.",
        "name": "API class name.",
    }

    # Permission API docs
    table_documentation[PERMISSION_API_TABLE]["description"] = (
        table_documentation[PERMISSION_API_TABLE]["description"]
        or "Stores which permissions are associated with which API."
    )
    table_documentation[PERMISSION_API_TABLE]["columns"] = table_documentation[
        PERMISSION_API_TABLE
    ]["columns"] or {
        "id": "Primary key.",
        "view_menu_id": f"FK to `{PERMISSION_TABLE}.id`.",
        "api_id": f"FK to `{API_TABLE}.id`.",
    }

    # Assoc Permission API Role docs
    table_documentation[ASSOC_PERMISSION_API_ROLE_TABLE]["description"] = (
        table_documentation[ASSOC_PERMISSION_API_ROLE_TABLE]["description"]
        or "Stores which roles are associated with which API permissions."
    )
    table_documentation[ASSOC_PERMISSION_API_ROLE_TABLE]["columns"] = (
        table_documentation[ASSOC_PERMISSION_API_ROLE_TABLE]["columns"]
        or {
            "id": "Primary key.",
            "role_id": f"FK to `{ROLE_TABLE}.id`.",
            "permission_view_id": f"FK to `{PERMISSION_API_TABLE}.id`.",
        }
    )

    # Assoc User Role docs
    table_documentation[ASSOC_USER_ROLE_TABLE]["description"] = (
        table_documentation[ASSOC_USER_ROLE_TABLE]["description"]
        or "Stores which roles are associated with which users."
    )
    table_documentation[ASSOC_USER_ROLE_TABLE]["columns"] = table_documentation[
        ASSOC_USER_ROLE_TABLE
    ]["columns"] or {
        "id": "Primary key.",
        "user_id": f"FK to `{USER_TABLE}.id`.",
        "role_id": f"FK to `{ROLE_TABLE}.id`.",
    }

    # Oauth docs
    table_documentation[OAUTH_TABLE]["description"] = (
        table_documentation[OAUTH_TABLE]["description"]
        or "Stores the OAuth accounts associated with users."
    )
    table_documentation[OAUTH_TABLE]["columns"] = table_documentation[OAUTH_TABLE][
        "columns"
    ] or {
        "id": "Primary key.",
        "user_id": f"FK to `{USER_TABLE}.id`. Identifies the user.",
        "oauth_name": "OAuth provider name (e.g., Google, GitHub).",
        "access_token": "Access token from the OAuth provider.",
        "expires_at": "Token expiration timestamp (epoch).",
        "refresh_token": "Refresh token for the OAuth provider.",
        "account_id": "Unique account ID from the OAuth provider.",
        "account_email": "Email address associated with the OAuth account.",
    }

    # AccessToken docs
    table_documentation[ACCESSTOKEN_TABLE]["description"] = (
        table_documentation[ACCESSTOKEN_TABLE]["description"]
        or "Stores the access tokens for users."
    )
    table_documentation[ACCESSTOKEN_TABLE]["columns"] = table_documentation[
        ACCESSTOKEN_TABLE
    ]["columns"] or {
        "token": "Access token string.",
        "created_at": "Timestamp when the token was created.",
        "user_id": f"FK to `{USER_TABLE}.id`. Identifies the user.",
    }
