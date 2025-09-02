import typing


class APIPathDocs(typing.TypedDict):
    """
    API Path Docs TypedDict.
    """

    path: str
    method: str
    description: str
    result: str


class APIMetadataDocs(typing.TypedDict):
    Parameters: list[dict[str, typing.Any]]
    Body: dict[str, typing.Any]
    Responses: list[dict[str, typing.Any]]


class APIDataDocs(typing.TypedDict):
    """
    API Data Docs TypedDict.
    """

    Description: str
    Paths: list[APIPathDocs]
    Metadata: dict[str, APIMetadataDocs]


class APIDocs(typing.TypedDict):
    """
    API Docs TypedDict.
    """

    APIs: dict[str, APIDataDocs]
    Schemas: dict[str, typing.Any] | list


class DBTableColumnDocs(typing.TypedDict):
    name: str
    type: str
    nullable: bool
    description: str
    default: str


class DBTableDocs(typing.TypedDict):
    """
    DB Table Docs TypedDict.
    """

    Description: str
    Columns: list[DBTableColumnDocs]
    PrimaryKeys: list[str]


class DBDataDocs(typing.TypedDict):
    """
    DB Data Docs TypedDict.
    """

    Summary: list[dict[str, str]]
    Tables: dict[str, DBTableDocs]


class DBDocs(typing.TypedDict):
    """
    DB Docs TypedDict.
    """

    Database: dict[str, DBDataDocs]


class TableDocumentation(typing.TypedDict):
    """
    Table Documentation TypedDict.
    """

    description: str
    columns: dict[str, str]
