import typing

import sqlalchemy.dialects.postgresql as postgresql
from sqlalchemy import types as sa_types

__all__ = ["FileColumn", "ImageColumn", "ListColumn", "JSONBListColumn"]


class FileColumn(sa_types.TypeDecorator):
    """
    Extends SQLAlchemy to support and mostly identify a File Column
    """

    impl = sa_types.Text
    cache_ok = True


class ImageColumn(sa_types.TypeDecorator):
    """
    Extends SQLAlchemy to support and mostly identify an Image Column

    """

    impl = sa_types.Text
    cache_ok = True

    def __init__(self, thumbnail_size=(20, 20, True), size=(100, 100, True), **kw):
        sa_types.TypeDecorator.__init__(self, **kw)
        self.thumbnail_size = thumbnail_size
        self.size = size


class ListColumn(sa_types.TypeDecorator):
    """
    Extends SQLAlchemy to support and mostly identify a List Column
    """

    impl = sa_types.JSON
    cache_ok = True

    def __init__(self, col_type: type | None = None, *args, **kwargs):
        """
        Initializes the ListColumn with a specific column type.

        Args:
            col_type (type | None, optional): The type of the items in the list. When given, the column will attempt to coerce the items in the list to this type. Defaults to None.
        """
        super().__init__(*args, **kwargs)
        self.col_type = col_type

    def process_bind_param(self, value, dialect):
        if not value:
            return value
        if not isinstance(value, list):
            raise ValueError("Value must be a list")
        if self.col_type:
            value = [self.col_type(v) for v in value]
        return value


class JSONBListColumn(ListColumn):
    """
    Extends ListColumn to use PostgreSQL's JSONB type.
    """

    impl = postgresql.JSONB


ExportMode = typing.Literal["simplified", "detailed"]
