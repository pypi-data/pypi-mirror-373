import asyncio
import collections
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Collection, Dict, Sequence, Set, Tuple

from sqlalchemy import Connection, Engine, MetaData
from sqlalchemy import Table as SA_Table
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql.schema import SchemaConst, SchemaItem
from sqlalchemy.util.typing import Literal

from ...bases.model import BasicModel

__all__ = ["Model", "metadata", "metadatas", "Base"]

camelcase_re = re.compile(r"([A-Z]+)(?=[a-z0-9])")


def camel_to_snake_case(name):
    def _join(match):
        word = match.group()

        if len(word) > 1:
            return ("_%s_%s" % (word[:-1], word[-1])).lower()

        return "_" + word.lower()

    return camelcase_re.sub(_join, name).lstrip("_")


metadatas: dict[str, MetaData] = {
    "default": MetaData(),
}

cache_id_property: dict[str, list[str]] = {}


class Model(BasicModel, DeclarativeBase):
    """
    Use this class has the base for your models,
    it will define your table names automatically
    MyModel will be called my_model on the database.

    ::

        from sqlalchemy import Integer, String
        from fastapi-rtk import Model

        class MyModel(Model):
            id = Column(Integer, primary_key=True)
            name = Column(String(50), unique = True, nullable=False)

    """

    _relationship_filters: collections.defaultdict[str, list[str]] | None = None

    __bind_key__: str | None = None
    """
    The bind key to use for this model. This allow you to use multiple databases. None means the default database. Default is None.
    """

    metadata = metadatas["default"]

    def __init_subclass__(cls, **kw: Any) -> None:
        # Set the bind key from the metadata __table__ if it exists
        if hasattr(cls, "__table__"):
            for key, metadata in metadatas.items():
                if metadata is cls.__table__.metadata and key != "default":
                    cls.__bind_key__ = key

        # Overwrite the metadata if the bind key is set
        if cls.__bind_key__:
            if cls.__bind_key__ not in metadatas:
                metadatas[cls.__bind_key__] = MetaData()
            cls.metadata = metadatas[cls.__bind_key__]
        return super().__init_subclass__(**kw)

    @declared_attr
    def __tablename__(cls) -> str:
        """
        Returns the table name for the given class.

        The table name is derived from the class name by converting
        any uppercase letters to lowercase and inserting an underscore
        before each uppercase letter.

        Returns:
            str: The table name.
        """
        return camel_to_snake_case(cls.__name__)

    __table_args__ = {"extend_existing": True}

    @classmethod
    def load_options(cls, col: str):
        """
        Load options for a given column with optional relationship filters. To be used when using loader options from `sqlalchemy.orm` such as `joinedLoad` or `selectinload`. The relationship filter can be defined using the `relationship_filter` decorator.

        Args:
            col (str): The name of the column to load options for.

        Returns:
            The attribute of the class with applied relationship filters if any.

        Raises:
            AttributeError: If the specified column does not exist in the class.
        """
        attr = getattr(cls, col)
        if cls._relationship_filters and col in cls._relationship_filters:
            criteria = []
            for func_name in cls._relationship_filters[col]:
                criteria.append(getattr(cls, func_name)())
            attr = attr.and_(*criteria)
        return attr

    @classmethod
    def get_pk_attrs(cls):
        return [col.name for col in cls.__mapper__.primary_key]


class Table(SA_Table):
    """
    This class is a wrapper around the SQLAlchemy `Table` class that allows you to autoload the table from the database asynchronously.

    Initialize it like you would a normal `Table` object.
    """

    def __init__(
        self,
        name: str,
        metadata: MetaData,
        *args: SchemaItem,
        schema: str | None | Literal[SchemaConst.BLANK_SCHEMA] = None,
        quote: bool | None = None,
        quote_schema: bool | None = None,
        autoload_with: Engine | Connection | None = None,
        autoload_replace: bool = True,
        keep_existing: bool = False,
        extend_existing: bool = False,
        resolve_fks: bool = True,
        include_columns: Collection[str] | None = None,
        implicit_returning: bool = True,
        comment: str | None = None,
        info: Dict[Any, Any] | None = None,
        listeners: Sequence[Tuple[str, Callable[..., Any]]] | None = None,
        prefixes: Sequence[str] | None = None,
        _extend_on: Set[SA_Table] | None = None,
        _no_init: bool = True,
        **kw: Any,
    ) -> None:
        from ...db import DatabaseSessionManager

        db = DatabaseSessionManager()

        if autoload_with:
            if isinstance(autoload_with, Engine):
                db.init_db(autoload_with.url)
            else:
                db.init_db(autoload_with.engine.url)

        with ThreadPoolExecutor() as executor:
            future = executor.submit(
                asyncio.run,
                db.autoload_table(
                    lambda conn: SA_Table.__init__(
                        self,
                        name,
                        metadata,
                        *args,
                        schema=schema,
                        quote=quote,
                        quote_schema=quote_schema,
                        autoload_with=conn,
                        autoload_replace=autoload_replace,
                        keep_existing=keep_existing,
                        extend_existing=extend_existing,
                        resolve_fks=resolve_fks,
                        include_columns=include_columns,
                        implicit_returning=implicit_returning,
                        comment=comment,
                        info=info,
                        listeners=listeners,
                        prefixes=prefixes,
                        _extend_on=_extend_on,
                        _no_init=_no_init,
                        **kw,
                    )
                ),
            )
            future.result()


metadata = metadatas["default"]


"""
    This is for retro compatibility
"""
Base = Model
