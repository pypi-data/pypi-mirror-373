import asyncio
import contextlib
import contextvars
from typing import (
    Any,
    Callable,
    Dict,
    Literal,
    Optional,
)

from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.models import ID, OAP, UP
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseOAuthAccountTable
from sqlalchemy import (
    Connection,
    Engine,
    MetaData,
    Select,
    create_engine,
    func,
    select,
)
from sqlalchemy import Table as SA_Table
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import (
    Session,
    scoped_session,
    sessionmaker,
)

from .backends.sqla.model import Table, metadata, metadatas
from .const import FASTAPI_RTK_TABLES
from .security.sqla.models import OAuthAccount, User
from .utils import T, lazy_self, safe_call, smart_run, smartdefaultdict

__all__ = [
    "UserDatabase",
    "db",
    "get_session_factory",
    "get_user_db",
]


class UserDatabase(SQLAlchemyUserDatabase[UP, ID]):
    """
    Modified version of the SQLAlchemyUserDatabase class from fastapi_users_db_sqlalchemy.
    - Allow the use of both async and sync database connections.
    - Allow the use of get_by_username method to get a user by username.

    Database adapter for SQLAlchemy.

    :param session: SQLAlchemy session instance.
    :param user_table: SQLAlchemy user model.
    :param oauth_account_table: Optional SQLAlchemy OAuth accounts model.
    """

    session: AsyncSession | Session

    def __init__(
        self,
        session: AsyncSession | Session,
        user_table: type,
        oauth_account_table: type[SQLAlchemyBaseOAuthAccountTable] | None = None,
    ):
        super().__init__(session, user_table, oauth_account_table)

    async def get(self, id: ID) -> Optional[UP]:
        statement = select(self.user_table).where(self.user_table.id == id)
        return await self._get_user(statement)

    async def get_by_email(self, email: str) -> Optional[UP]:
        statement = select(self.user_table).where(
            func.lower(self.user_table.email) == func.lower(email)
        )
        return await self._get_user(statement)

    async def get_by_oauth_account(self, oauth: str, account_id: str) -> Optional[UP]:
        if self.oauth_account_table is None:
            raise NotImplementedError()

        statement = (
            select(self.user_table)
            .join(self.oauth_account_table)
            .where(self.oauth_account_table.oauth_name == oauth)
            .where(self.oauth_account_table.account_id == account_id)
        )
        return await self._get_user(statement)

    async def create(self, create_dict: Dict[str, Any]) -> UP:
        user = self.user_table(**create_dict)
        self.session.add(user)
        await safe_call(self.session.commit())
        await safe_call(self.session.refresh(user))
        return user

    async def update(self, user: UP, update_dict: Dict[str, Any]) -> UP:
        for key, value in update_dict.items():
            setattr(user, key, value)
        self.session.add(user)
        await safe_call(self.session.commit())
        await safe_call(self.session.refresh(user))
        return user

    async def delete(self, user: UP) -> None:
        await self.session.delete(user)
        await safe_call(self.session.commit())

    async def add_oauth_account(self, user: UP, create_dict: Dict[str, Any]) -> UP:
        if self.oauth_account_table is None:
            raise NotImplementedError()

        await safe_call(self.session.refresh(user))
        oauth_account = self.oauth_account_table(**create_dict)
        self.session.add(oauth_account)
        user.oauth_accounts.append(oauth_account)
        self.session.add(user)

        await safe_call(self.session.commit())

        return user

    async def update_oauth_account(
        self, user: UP, oauth_account: OAP, update_dict: Dict[str, Any]
    ) -> UP:
        if self.oauth_account_table is None:
            raise NotImplementedError()

        for key, value in update_dict.items():
            setattr(oauth_account, key, value)
        self.session.add(oauth_account)
        await safe_call(self.session.commit())

        return user

    async def get_by_username(self, username: str) -> Optional[UP]:
        statement = select(self.user_table).where(
            func.lower(self.user_table.username) == func.lower(username)
        )
        return await self._get_user(statement)

    async def _get_user(self, statement: Select) -> Optional[UP]:
        results = await smart_run(self.session.execute, statement)
        return results.unique().scalar_one_or_none()


class lazy(lazy_self["DatabaseSessionManager", T]): ...


class DatabaseSessionManager:
    Table = Table

    current_session = lazy(lambda self: self._session_context.get(None), cache=False)
    """
    The current session in this context.

    This will return the session that is currently set in the context regardless of the bind key.
    """
    current_session_bind = lazy(
        lambda self: smartdefaultdict[str, AsyncSession | Session | None](
            lambda key: self._sessions_context[key].get(None)
        ),
        cache=False,
    )
    """
    The current session in this context, but binded to a specific key.

    This will return the session that is currently set in the context for the given bind key.

    Usage:
    ```python
    from fastapi_rtk import db

    # Somewhere in your code, you can get the current session for a specific bind key
        session = db.current_session_bind["my_bind_key"] # Use `None` to get session without bind key
    ```
    """

    _engine: AsyncEngine | Engine | None = None
    _sessionmaker: async_sessionmaker[AsyncSession] | sessionmaker[Session] | None = (
        None
    )
    _engine_binds: dict[str, AsyncEngine | Engine] = None
    _sessionmaker_binds: dict[
        str, async_sessionmaker[AsyncSession] | sessionmaker[Session]
    ] = None
    _scoped_session_maker: (
        async_scoped_session[AsyncSession] | scoped_session[Session] | None
    ) = None
    _scoped_session_maker_binds: dict[
        str, async_scoped_session[AsyncSession] | scoped_session[Session]
    ] = None
    _scoped_session: AsyncSession | Session | None = None
    _scoped_session_binds: dict[str, AsyncSession | Session] = None

    _session_context = contextvars.ContextVar[AsyncSession | Session](
        "DatabaseSessionManager:current_session"
    )
    _sessions_context = smartdefaultdict[
        str, contextvars.ContextVar[AsyncSession | Session]
    ](
        lambda key: contextvars.ContextVar[AsyncSession | Session](
            f"DatabaseSessionManager:current_session:{key}"
        )
    )

    def __init__(self) -> None:
        self._engine_binds = {}
        self._sessionmaker_binds = {}
        self._scoped_session_maker_binds = {}
        self._scoped_session_binds = {}

    def init_db(self, url: str, binds: dict[str, str] | None = None):
        """
        Initializes the database engine and session maker.

        Args:
            url (str): The URL of the database.
            binds (dict[str, str] | None, optional): Additional database URLs to bind to. Defaults to None.
        """
        from .setting import Setting

        self._engine = self._init_engine(url, Setting.SQLALCHEMY_ENGINE_OPTIONS)
        self._sessionmaker = self._init_sessionmaker(self._engine)
        self._scoped_session_maker = self._init_scoped_session(self._sessionmaker)

        for key, value in (binds or {}).items():
            self._engine_binds[key] = self._init_engine(
                value,
                Setting.SQLALCHEMY_ENGINE_OPTIONS_BINDS.get(key, {}),
            )
            self._sessionmaker_binds[key] = self._init_sessionmaker(
                self._engine_binds[key]
            )
            self._scoped_session_maker_binds[key] = self._init_scoped_session(
                self._sessionmaker_binds[key]
            )

    def get_engine(self, bind: str | None = None):
        """
        Returns the database engine.

        Args:
            bind (str | None, optional): The bind key to retrieve the engine for. If None, the default engine is returned. Defaults to None.

        Returns:
            AsyncEngine | Engine | None: The database engine or None if it does not exist.
        """
        return self._engine_binds.get(bind) if bind else self._engine

    def get_metadata(self, bind: str | None = None):
        """
        Retrieves the metadata associated with the specified bind.

        If bind is specified, but the metadata does not exist, a new metadata is created and associated with the bind.

        Parameters:
            bind (str | None, optional): The bind key to retrieve the metadata for. If None, the default metadata is returned. Defaults to None.

        Returns:
            The metadata associated with the specified bind. If bind is None, returns the default metadata.
        """
        if bind:
            bind_metadata = metadatas.get(bind)
            if not bind_metadata:
                bind_metadata = MetaData()
                metadatas[bind] = bind_metadata
            return bind_metadata
        return metadata

    async def init_fastapi_rtk_tables(self):
        """
        Initializes the tables required for FastAPI RTK to function.
        """
        tables = [
            table for key, table in metadata.tables.items() if key in FASTAPI_RTK_TABLES
        ]
        fastapi_rtk_metadata = MetaData()
        for table in tables:
            table.to_metadata(fastapi_rtk_metadata)
        async with self.connect() as connection:
            await self._create_all(connection, fastapi_rtk_metadata)

    async def close(self):
        """
        If engine exists, disposes the engine and sets it to None.

        If engine binds exist, disposes all engine binds and sets them to None.
        """
        if self._scoped_session_maker:
            await safe_call(self._scoped_session_maker.remove())
            self._scoped_session_maker = None

        if self._scoped_session_maker_binds:
            for scoped_session_maker in self._scoped_session_maker_binds.values():
                await safe_call(scoped_session_maker.remove())
            self._scoped_session_maker_binds.clear()

        if self._engine:
            await safe_call(self._engine.dispose())
            self._engine = None
            self._sessionmaker = None

        if self._engine_binds:
            for engine in self._engine_binds.values():
                await safe_call(engine.dispose())
            self._engine_binds.clear()
            self._sessionmaker_binds.clear()

    @contextlib.asynccontextmanager
    async def connect(self, bind: str | None = None):
        """
        Establishes a connection to the database.

        ***EVEN IF THE CONNECTION IS SYNC, ASYNC WITH ... AS ... IS STILL NEEDED.***

        Args:
            bind (str | None, optional): The bind key to retrieve the connection for. If None, the default connection is returned. Defaults to None.

        Raises:
            Exception: If the DatabaseSessionManager is not initialized.

        Yields:
            AsyncConnection | Connection: The database connection.
        """
        engine = self._engine_binds.get(bind) if bind else self._engine
        if not engine:
            raise Exception("DatabaseSessionManager is not initialized")

        if isinstance(engine, AsyncEngine):
            async with engine.begin() as connection:
                try:
                    yield connection
                except Exception:
                    await connection.rollback()
                    raise
        else:
            with engine.begin() as connection:
                try:
                    yield connection
                except Exception:
                    connection.rollback()
                    raise

    @contextlib.asynccontextmanager
    async def session(self, bind: str | None = None):
        """
        Provides a database session for performing database operations.

        ***EVEN IF THE SESSION IS SYNC, ASYNC WITH ... AS ... IS STILL NEEDED.***

        Args:
            bind (str | None, optional): The bind key to retrieve the session for. If None, the default session is returned. Defaults to None.

        Raises:
            Exception: If the DatabaseSessionManager is not initialized.

        Yields:
            AsyncSession | Session: The database session.
        """
        session_maker = (
            self._sessionmaker_binds.get(bind) if bind else self._sessionmaker
        )
        if not session_maker:
            raise Exception("DatabaseSessionManager is not initialized")

        session = session_maker()
        token = self._session_context.set(session)
        bind_token = self._sessions_context[bind].set(session)
        try:
            yield session
        except Exception:
            await safe_call(session.rollback())
            raise
        finally:
            await safe_call(session.close())
            self._session_context.reset(token)
            self._sessions_context[bind].reset(bind_token)

    @contextlib.asynccontextmanager
    async def scoped_session(self, bind: str | None = None):
        """
        Provides a scoped database session class for performing database operations.

        ***EVEN IF THE SESSION IS SYNC, ASYNC WITH ... AS ... IS STILL NEEDED.***

        Args:
            bind (str | None, optional): The bind key to retrieve the scoped session for. If None, the default scoped session is returned. Defaults to None.

        Raises:
            Exception: If the DatabaseSessionManager is not initialized.

        Yields:
            scoped_session[Session] | async_scoped_session[AsyncSession]: The scoped database session.

        Returns:
            None
        """
        scoped_session_maker = (
            self._scoped_session_maker_binds.get(bind)
            if bind
            else self._scoped_session_maker
        )
        if not scoped_session_maker:
            raise Exception("DatabaseSessionManager is not initialized")
        scoped_session = scoped_session_maker()

        try:
            yield scoped_session
        except Exception:
            await safe_call(scoped_session_maker.rollback())
            raise
        finally:
            await safe_call(scoped_session_maker.remove())

    # Used for testing
    async def create_all(self, binds: list[str] | Literal["all"] | None = "all"):
        """
        Creates all tables in the database.

        Args:
            binds (list[str] | Literal["all"] | None, optional): The database URLs to create tables in. Defaults to "all".
        """
        async with self.connect() as connection:
            await self._create_all(connection, metadata)

        if not self._engine_binds or not binds:
            return

        bind_keys = self._engine_binds.keys() if binds == "all" else binds
        for key in bind_keys:
            async with self.connect(key) as connection:
                await self._create_all(connection, metadatas[key])

    async def drop_all(self, binds: list[str] | Literal["all"] | None = "all"):
        """
        Drops all tables in the database.

        Args:
            binds (list[str] | Literal["all"] | None, optional): The database URLs to drop tables in. Defaults to "all".
        """
        async with self.connect() as connection:
            await self._create_all(connection, metadata, drop=True)

        if not self._engine_binds or not binds:
            return

        bind_keys = self._engine_binds.keys() if binds == "all" else binds
        for key in bind_keys:
            async with self.connect(key) as connection:
                await self._create_all(connection, metadatas[key], drop=True)

    async def autoload_table(self, func: Callable[[Connection], SA_Table]):
        """
        Autoloads a table from the database using the provided function.

        As `autoload_with` is not supported in async SQLAlchemy, this method is used to autoload tables asynchronously.

        *If the `db` is not initialized, the function is run without a connection. So it has the same behavior as creating the table without autoloading.*

        *After the table is autoloaded, the database connection is closed. This means `autoload_table` should not be used with primary `db`. Consider using a separate `db` instance instead.*

        Args:
            func (Callable[[Connection], SA_Table]): The function to autoload the table.

        Returns:
            SA_Table: The autoloaded table.
        """
        if not self._engine:
            return func(None)

        try:
            async with self.connect() as conn:
                if isinstance(conn, AsyncConnection):
                    return await conn.run_sync(func)
                else:
                    return func(conn)
        finally:
            await self.close()

    def _init_engine(self, url: str, engine_options: dict[str, Any]):
        """
        Initializes the database engine.

        Args:
            url (str): The URL of the database.
            engine_options (dict[str, Any]): The options to pass to the database engine.

        Returns:
            AsyncEngine | Engine: The database engine. If the URL is an async URL, an async engine is returned.
        """
        try:
            return create_async_engine(url, **engine_options)
        except InvalidRequestError:
            return create_engine(url, **engine_options)

    def _init_sessionmaker(self, engine: AsyncEngine | Engine):
        """
        Initializes the database session maker.

        Args:
            engine (AsyncEngine | Engine): The database engine.

        Returns:
            async_sessionmaker[AsyncSession] | sessionmaker[Session]: The database session maker.
        """
        if isinstance(engine, AsyncEngine):
            return async_sessionmaker(
                bind=engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
        return sessionmaker(
            bind=engine,
            class_=Session,
            expire_on_commit=False,
        )

    def _init_scoped_session(
        self, sessionmaker: async_sessionmaker[AsyncSession] | sessionmaker[Session]
    ):
        """
        Initializes the scoped session.

        Args:
            sessionmaker (async_sessionmaker[AsyncSession] | sessionmaker[Session]): The session maker to use.

        Returns:
            scoped_session | async_scoped_session: The scoped session.
        """
        if isinstance(sessionmaker, async_sessionmaker):
            return async_scoped_session(sessionmaker, scopefunc=asyncio.current_task)
        return scoped_session(sessionmaker)

    async def _create_all(
        self, connection: Connection | AsyncConnection, metadata: MetaData, drop=False
    ):
        """
        Creates all tables in the database based on the metadata.

        Args:
            connection (Connection | AsyncConnection): The database connection.
            metadata (MetaData): The metadata object containing the tables to create.
            drop (bool, optional): Whether to drop the tables instead of creating them. Defaults to False.

        Returns:
            None
        """
        func = metadata.drop_all if drop else metadata.create_all
        if isinstance(connection, AsyncConnection):
            return await connection.run_sync(func)
        return func(connection)


db = DatabaseSessionManager()


def get_session_factory(bind: str | None = None):
    """
    Factory function that returns an async generator function that yields a database session.

    Can be used as a dependency in FastAPI routes.

    Args:
        bind (str | None, optional): The bind key to retrieve the session for. If None, the default session is returned. Defaults to None.

    Returns:
        typing.Callable[[], AsyncGenerator[AsyncSession | Session, None]]: A generator function that yields a database session.

    Usage:
    ```python
        @app.get("/items/")
        async def read_items(session: AsyncSession | Session = Depends(get_session_factory())):
            # Use the session to interact with the database
    ```
    """

    async def get_session_dependency():
        async with db.session(bind) as session:
            yield session

    return get_session_dependency


def get_scoped_session(bind: str | None = None):
    """
    A coroutine function that returns a function that yields a scoped database session class.

    Can be used as a dependency in FastAPI routes.

    Args:
        bind (str | None, optional): The bind key to retrieve the scoped session for. If None, the default scoped session is returned. Defaults to None.

    Returns:
        AsyncGenerator[scoped_session[Session], async_scoped_session[AsyncSession]]: A generator that yields a scoped database session.

    Usage:
    ```python
        @app.get("/items/")
        async def read_items(session: scoped_session[Session] = Depends(get_scoped_session())):
            # Use the session to interact with the database
    ```
    """

    async def get_scoped_session_dependency():
        async with db.scoped_session(bind) as session:
            yield session

    return get_scoped_session_dependency


async def get_user_db(
    session: AsyncSession | Session = Depends(get_session_factory(User.__bind_key__)),
):
    """
    A dependency for FAST API to get the UserDatabase instance.

    Parameters:
    - session: The async session object for the database connection.

    Yields:
    - UserDatabase: An instance of the UserDatabase class.

    """
    yield UserDatabase(session, User, OAuthAccount)
