import collections
import datetime
import typing

import pydantic
import sqlalchemy.dialects.postgresql
import sqlalchemy.event
import sqlalchemy.orm
from sqlalchemy import MetaData, Sequence

from .....const import logger
from .....db import db
from .....globals import g
from .....security.sqla.models import User
from .....utils import (
    class_factory_from_dict,
    lazy,
    prettify_dict,
    run_coroutine_in_threadpool,
    safe_call_sync,
    smart_run,
    smartdefaultdict,
)
from ...column import mapped_column
from ...interface import SQLAInterface
from ...model import Model
from ...session import SQLAConnection, SQLASession
from .types import AuditEntry, AuditOperation, SQLAModel

__all__ = ["audit_model_factory", "Audit"]


logger = logger.getChild("audit")

BASE_AUDIT_TABLE_NAME = "audit_log"
BASE_AUDIT_SEQUENCE = BASE_AUDIT_TABLE_NAME + "_id_seq"


def audit_model_factory(
    class_name: str = "AuditTable",
    bases: tuple[type, ...] = (Model,),
    dialects: typing.Literal["postgresql"] | None = None,
    **kwargs: typing.Any,
) -> typing.Type[SQLAModel]:
    """
    Factory function to create an SQLAlchemy model for auditing.

    Args:
        class_name (str, optional): The name of the audit table class. Defaults to "AuditTable".
        bases (tuple[type, ...], optional): The base classes for the audit table class. Defaults to (Model,).
        dialects (typing.Literal["postgresql"] | None, optional): The database dialect to use. Defaults to None.
        **kwargs (typing.Any): Additional attributes to add or override in the model.

    Returns:
        typing.Type[SQLAModel]: The SQLAlchemy model class for the audit table.
    """
    attrs = {
        "__tablename__": BASE_AUDIT_TABLE_NAME,
        "id": mapped_column(
            sqlalchemy.Integer, Sequence(BASE_AUDIT_SEQUENCE), primary_key=True
        ),
        "created": mapped_column(
            sqlalchemy.DateTime(timezone=True),
            nullable=False,
            default=lambda: datetime.datetime.now(datetime.timezone.utc),
        ),
        "table": mapped_column(sqlalchemy.String(256), nullable=False),
        "table_id": mapped_column(sqlalchemy.String(1024), nullable=False),
        "operation": mapped_column(sqlalchemy.String(256), nullable=False),
        "data": mapped_column(
            sqlalchemy.dialects.postgresql.JSONB
            if dialects == "postgresql"
            else sqlalchemy.JSON,
        ),
        "updates": mapped_column(
            sqlalchemy.dialects.postgresql.JSONB
            if dialects == "postgresql"
            else sqlalchemy.JSON,
        ),
        "created_by_fk": mapped_column(
            sqlalchemy.Integer,
            sqlalchemy.ForeignKey(User.id, ondelete="SET NULL"),
            default=User.get_user_id,
        ),
        "created_by": sqlalchemy.orm.relationship(User),
        "__table_args__": (
            sqlalchemy.Index("ix_audit_table_id", "table", "table_id", unique=False),
        ),
        "__repr__": lambda self: prettify_dict(
            {
                "id": self.id,
                "created": self.created,
                "table": self.table,
                "table_id": self.table_id,
                "operation": self.operation,
                "data": self.data,
                "updates": self.updates,
            }
        ),
        **kwargs,
    }
    return class_factory_from_dict(class_name, bases, **attrs)


class Audit:
    """
    A class to handle auditing of SQLAlchemy models using session events.

    ***If the model of the audit needs to be changed, ensure that the `create_entry` method is updated accordingly***.

    ## Example:
    ```python
    import sqlalchemy
    from fastapi_rtk import Audit, Model

    @Audit.audit_model # Will audit the model and its subclasses
    @Audit.exclude_properties(["password", "secret_key"]) # Add this to ignore specific properties
    class MyModel(Model):
        __tablename__ = "my_model"
        id = mapped_column(sqlalchemy.Integer, primary_key=True)
        name = mapped_column(sqlalchemy.String(256))
        password = mapped_column(sqlalchemy.String(256))
        secret_key = mapped_column(sqlalchemy.String(256))

    @Audit.exclude_model # To exclude a model from being audited
    class MySubclassModel(MyModel):
        __tablename__ = "my_subclass_model"
        id = mapped_column(sqlalchemy.Integer, primary_key=True)
        additional_field = mapped_column(sqlalchemy.String(256))

    @Audit.audit_model
    @Audit.include_properties(["name"]) # To include only specific properties
    class AnotherModel(Model):
        __tablename__ = "another_model"
        id = mapped_column(sqlalchemy.Integer, primary_key=True)
        name = mapped_column(sqlalchemy.String(256))
        description = mapped_column(sqlalchemy.String(512))
    ```
    """

    model = lazy(lambda: audit_model_factory(), only_instance=False)
    """
    The SQLAlchemy model representing the audit table.
    """
    interfaces = smartdefaultdict[typing.Type[SQLAModel], SQLAInterface](
        lambda model: SQLAInterface(model)
    )
    """
    Dictionary mapping SQLAlchemy models to their interfaces.
    """
    schemas = dict[str, typing.Type[pydantic.BaseModel]]()
    """
    Dictionary mapping model name combined with columns with attributes to their corresponding schema.
    """

    models = list[typing.Type[SQLAModel]]()
    """
    List of models to be audited.
    """
    excluded_models = list[typing.Type[SQLAModel]]()
    """
    List of models to be excluded from auditing.
    """
    included_properties = collections.defaultdict[typing.Type[SQLAModel], list[str]](
        list[str]
    )
    """
    Dictionary mapping models to properties that should be included in auditing. When not given, all properties will be included.
    """
    excluded_properties = collections.defaultdict[typing.Type[SQLAModel], list[str]](
        list[str]
    )
    """
    Dictionary mapping models to properties that should be excluded from auditing.
    """
    callbacks = list[
        typing.Callable[
            [AuditEntry], None | typing.Coroutine[typing.Any, typing.Any, None]
        ]
    ]()
    """
    List of callbacks to be called after adding the audit to the database.
    """

    _session_callbacks_after_flush_postexec = collections.defaultdict[
        sqlalchemy.orm.Session,
        list[
            typing.Callable[[], None | typing.Coroutine[typing.Any, typing.Any, None]]
        ](),
    ](list)
    """
    Dictionary mapping SQLAlchemy sessions to their post-execution callbacks.
    """
    _session_callbacks_after_commit = collections.defaultdict[
        sqlalchemy.orm.Session,
        list[
            typing.Callable[[], None | typing.Coroutine[typing.Any, typing.Any, None]]
        ](),
    ](list)
    """
    Dictionary mapping SQLAlchemy sessions to their commit callbacks.
    """
    _configured = False
    """
    Flag to indicate if the audit class has been configured.
    """

    @classmethod
    def setup(cls):
        """
        Set up the audit class.

        - Attach `after_flush` event to `sqlalchemy.orm.Session` to collect audit entries and add callbacks to the session.
        - Attach `after_flush_postexec` event to `sqlalchemy.orm.Session` to run callbacks after the session flush post-execution.
        - Attach `after_commit` event to `sqlalchemy.orm.Session` to run callbacks after the session commit.
        - Attach `after_rollback` event to `sqlalchemy.orm.Session` to clear callbacks when a rollback occurs.
        """
        if cls._configured:
            return
        sqlalchemy.event.listen(sqlalchemy.orm.Session, "after_flush", cls._after_flush)
        sqlalchemy.event.listen(
            sqlalchemy.orm.Session, "after_flush_postexec", cls._after_flush_postexec
        )
        sqlalchemy.event.listen(
            sqlalchemy.orm.Session, "after_commit", cls._after_commit
        )
        sqlalchemy.event.listen(
            sqlalchemy.orm.Session, "after_rollback", cls._after_rollback
        )
        cls._configured = True
        logger.info("Audit class configured.")

    @classmethod
    def audit_model(
        cls,
        model_cls: typing.Type[SQLAModel] | None = None,
        *,
        include: list[str] | str | None = None,
        exclude: list[str] | str | None = None,
    ):
        """
        Decorator to register a model and its subclasses for auditing.

        Args:
            model_cls (typing.Type[SQLAModel]): The SQLAlchemy model class to audit.
            include (list[str] | str | None, optional): List of property names to include in the audit. Defaults to None.
            exclude (list[str] | str | None, optional): List of property names to exclude from the audit. Defaults to None.

        Returns:
            typing.Type[SQLAModel]: The audited model class.

        Raises:
            ValueError: If the model class is not provided and no include or exclude properties are specified.

        Example:
            ```python
            @Audit.audit_model # Standard usage, audits everything
            # Or, @Audit.audit_model(include="name, description") # To include specific properties
            # Or, @Audit.audit_model(exclude="password, secret_key") # To exclude specific properties
            class MyModel(Model):
                __tablename__ = "my_model"
                id = mapped_column(sqlalchemy.Integer, primary_key=True)
                name = mapped_column(sqlalchemy.String(256))
                description = mapped_column(sqlalchemy.String(512))
                created = mapped_column(sqlalchemy.DateTime, default=sqlalchemy.func.now())
                updated = mapped_column(sqlalchemy.DateTime, default=sqlalchemy.func.now(), onupdate=sqlalchemy.func.now())
            ```
        """
        if include or exclude:

            def decorator(model_cls: typing.Type[SQLAModel]) -> typing.Type[SQLAModel]:
                model_cls = cls.audit_model(model_cls)
                params = [
                    (include, cls.include_properties),
                    (exclude, cls.exclude_properties),
                ]
                for args, func in params:
                    if not args:
                        continue
                    if not isinstance(args, tuple):
                        args = (args,)
                    model_cls = func(*args)(model_cls)
                return model_cls

            return decorator

        if not model_cls:
            raise ValueError("Model class must be provided to `audit_model` decorator.")

        cls.setup()
        cls.models.append(model_cls)
        logger.info(
            f"Model {model_cls.__name__} and its subclasses registered for audit."
        )
        return model_cls

    @classmethod
    def exclude_model(cls, model_cls: typing.Type[SQLAModel]):
        """
        Decorator to exclude a model from being audited.

        Args:
            model_cls (typing.Type[SQLAModel]): The SQLAlchemy model class to exclude.

        Returns:
            typing.Type[SQLAModel]: The excluded model class.
        """
        cls.excluded_models.append(model_cls)
        logger.info(f"Model {model_cls.__name__} excluded from audit.")
        return model_cls

    @classmethod
    def include_properties(cls, properties: list[str] | str, *args, separator=","):
        """
        Decorator to include specific properties in the audit for a model.

        Args:
            properties (list[str] | str): List of property names to include or a single property name.
            *args: Additional property names to include.
            separator (str, optional): Separator to split the properties string. Defaults to ','.

        Returns:
            typing.Callable[[typing.Type[SQLAModel]], typing.Type[SQLAModel]]: A decorator that applies the inclusion.

        Example:
            ```python
            @Audit.include_properties(["name", "description"]) # To include specific properties
            # Or, @Audit.include_properties("name, description")
            # Or, @Audit.include_properties("name", "description")
            class MyModel(Model):
                __tablename__ = "my_model"
                id = mapped_column(sqlalchemy.Integer, primary_key=True)
                name = mapped_column(sqlalchemy.String(256))
                description = mapped_column(sqlalchemy.String(512))
            ```
        """
        if isinstance(properties, str):
            properties = properties.split(separator)
        properties.extend(args)

        def decorator(model_cls: typing.Type[SQLAModel]):
            cls.included_properties[model_cls].extend(properties)
            logger.info(
                f"Only properties {properties} included in audit for model {model_cls.__name__}."
            )
            return model_cls

        return decorator

    @classmethod
    def exclude_properties(cls, properties: list[str] | str, *args, separator=","):
        """
        Decorator to exclude specific properties from being audited for a model.

        Args:
            properties (list[str]): List of property names to exclude.
            *args: Additional property names to exclude.
            separator (str, optional): Separator to split the properties string. Defaults to ','.

        Returns:
            typing.Callable[[typing.Type[SQLAModel]], typing.Type[SQLAModel]]: A decorator that applies the exclusion.

        Example:
            ```python
            @Audit.exclude_properties(["password", "secret_key"]) # To exclude specific properties
            # Or, @Audit.exclude_properties("password, secret_key")
            # Or, @Audit.exclude_properties("password", "secret_key")
            class MyModel(Model):
                __tablename__ = "my_model"
                id = mapped_column(sqlalchemy.Integer, primary_key=True)
                name = mapped_column(sqlalchemy.String(256))
                password = mapped_column(sqlalchemy.String(256))
                secret_key = mapped_column(sqlalchemy.String(256))
            ```
        """
        if isinstance(properties, str):
            properties = properties.split(separator)
        properties.extend(args)

        def decorator(model_cls: typing.Type[SQLAModel]):
            cls.excluded_properties[model_cls].extend(properties)
            logger.info(
                f"Properties {properties} excluded from audit for model {model_cls.__name__}."
            )
            return model_cls

        return decorator

    @classmethod
    def callback(
        cls,
        func: typing.Callable[
            [AuditEntry], None | typing.Coroutine[typing.Any, typing.Any, None]
        ],
    ):
        """
        Decorator to register a callback function that will be called after an audit entry is added to the database.

        Args:
            func (typing.Callable[[AuditEntry], None | typing.Coroutine[typing.Any, typing.Any, None]]): The callback function to register.

        Returns:
            typing.Callable[[AuditEntry], None | typing.Coroutine[typing.Any, typing.Any, None]]: The registered callback function.
        """
        cls.callbacks.append(func)
        logger.info(f"Callback {func.__name__} registered.")
        return func

    """
    --------------------------------------------------------------------------------------------------------
        MODEL METHODS - implemented
    --------------------------------------------------------------------------------------------------------
    """

    @classmethod
    def set_model(cls, model_cls: typing.Type[SQLAModel]):
        """
        Set the model class for the audit.

        Args:
            model_cls (typing.Type[SQLAModel]): The SQLAlchemy model class to set.
        """
        cls.model = model_cls
        logger.info(f"Audit model set to {model_cls.__name__}.")

    @classmethod
    def create_entry(cls, audit: AuditEntry):
        """
        Create an audit entry from the given audit data.

        Args:
            audit (AuditEntry): The audit entry to create.

        Returns:
            AuditTable: An instance of the audit table model with the provided audit data.
        """
        return cls.model(
            table=audit["model"].__tablename__,
            table_id=str(audit["pk"]),
            operation=audit["operation"],
            data=audit.get("data"),
            updates=audit.get("updates"),
            created_by_fk=g.user.id if g.user else None,
        )

    @classmethod
    async def create_table(cls, conn: SQLAConnection = None):
        """
        Create the audit table in the database.

        Args:
            conn (SQLAConnection, optional): The database connection to use. Defaults to None.
        """
        if not conn:
            async with db.connect(cls.model.__bind_key__) as conn:
                return await cls.create_table(conn)

        audit_metadata = MetaData()
        cls.model.__table__.to_metadata(audit_metadata)
        return await db._create_all(conn, audit_metadata)

    @classmethod
    def create_table_sync(cls, *args, **kwargs):
        """
        Synchronous version of `create_table`.

        Args:
            *args: Positional arguments to pass to `create_table`.
            **kwargs: Keyword arguments to pass to `create_table`.

        Returns:
            T: The result of the synchronous table creation.
        """
        return run_coroutine_in_threadpool(cls.create_table(*args, **kwargs))

    @classmethod
    async def insert_entries(
        cls,
        entries: list[SQLAModel],
        session: SQLASession | None = None,
        commit=True,
        raise_exception=False,
    ):
        """
        Insert multiple audit entries into the database.

        Args:
            entries (list[SQLAModel]): The audit entries to insert.
            session (SQLASession | None, optional): The database session to use. Defaults to None.
            commit (bool, optional): Whether to commit the session after inserting. Defaults to True.
            raise_exception (bool, optional): Whether to raise an exception if the insert fails. Defaults to False.

        Raises:
            e: The exception raised during the insert.
        """
        try:
            if not session:
                async with db.session(cls.model.__bind_key__) as session:
                    await cls.insert_entries(entries, session, raise_exception)
            session.add_all(entries)
            for entry in entries:
                logger.info(f"[{entry.operation}] {entry.table} {entry.table_id}")
                logger.debug(f"Entry data: \n{prettify_dict(entry.data)}")
            if commit:
                await smart_run(session.commit)
        except Exception as e:
            logger.error(f"Error inserting audit entries: {e}")
            if not raise_exception:
                return
            raise e

    @classmethod
    def insert_entries_sync(cls, *args, **kwargs):
        """
        Synchronous version of `insert_entries`.

        Args:
            *args: Positional arguments to pass to `insert_entries`.
            **kwargs: Keyword arguments to pass to `insert_entries`.

        Returns:
            T: The result of the synchronous insert operation.
        """
        return run_coroutine_in_threadpool(cls.insert_entries(*args, **kwargs))

    """
    --------------------------------------------------------------------------------------------------------
        EVENT LISTENER METHODS - implemented
    --------------------------------------------------------------------------------------------------------
    """

    @classmethod
    def _after_flush(cls, session: sqlalchemy.orm.Session, *_):
        """
        Event handler for `after_flush` event.

        Args:
            session (sqlalchemy.orm.Session): The SQLAlchemy session that was flushed.
        """
        audit_entries = cls._get_audit_entries_sync(session)
        if not audit_entries:
            logger.debug("No models to be audited in `after_flush`.")
            return

        audit_models = [cls.create_entry(entry) for entry in audit_entries]
        existing_session = None
        if any(
            entry["model"].__bind_key__ == cls.model.__bind_key__
            for entry in audit_entries
        ):
            existing_session = session
        cls._session_callbacks_after_flush_postexec[session].append(
            lambda audit_models=audit_models,
            existing_session=existing_session: cls.insert_entries_sync(
                audit_models, session=existing_session, commit=not existing_session
            )
        )
        for entry in audit_entries:
            for callback in cls.callbacks:
                cls._session_callbacks_after_commit[session].append(
                    lambda entry=entry, callback=callback: safe_call_sync(
                        callback(entry)
                    )
                )

    @classmethod
    def _after_flush_postexec(cls, session: sqlalchemy.orm.Session, *_):
        """
        Event handler for `after_flush_postexec` event.

        Args:
            session (sqlalchemy.orm.Session): The SQLAlchemy session that was flushed post-execution.
        """
        callbacks = cls._session_callbacks_after_flush_postexec.pop(session, [])
        if not callbacks:
            logger.debug("No callbacks to run in `after_flush_postexec`.")
            return
        for callback in callbacks:
            callback()

    @classmethod
    def _after_commit(cls, session: sqlalchemy.orm.Session):
        """
        Event handler for `after_commit` event.

        Args:
            session (sqlalchemy.orm.Session): The SQLAlchemy session that was committed.
        """
        callbacks = cls._session_callbacks_after_commit.pop(session, [])
        if not callbacks:
            logger.debug("No callbacks to run in `after_commit`.")
            return
        for callback in callbacks:
            callback()

    @classmethod
    def _after_rollback(cls, session: sqlalchemy.orm.Session):
        """
        Event handler for `after_rollback` event.

        Args:
            session (sqlalchemy.orm.Session): The SQLAlchemy session that was rolled back.
        """
        cls._session_callbacks_after_flush_postexec.pop(session, None)
        cls._session_callbacks_after_commit.pop(session, None)
        logger.debug("Rolled back changes in session, clearing callbacks.")

    """
    --------------------------------------------------------------------------------------------------------
        HELPER METHODS - implemented
    --------------------------------------------------------------------------------------------------------
    """

    @classmethod
    async def _get_audit_entries(
        cls,
        session: sqlalchemy.orm.Session,
    ):
        """
        Get audit entries from the session.

        Args:
            session (sqlalchemy.orm.Session): The SQLAlchemy session to get audit entries from.

        Returns:
            list[AuditEntry]: A list of audit entries.
        """
        audit_entry_deque = collections.deque[tuple[SQLAInterface, AuditOperation]]()
        for model in session.new:
            if not cls._should_audit(model):
                logger.debug(
                    f"[{AuditOperation.INSERT}] Model is not registered or excluded from audit: {model.__class__.__name__}"
                )
                continue
            if not hasattr(model, "__tablename__"):
                continue
            audit_entry_deque.append((model, AuditOperation.INSERT))
        for model in session.dirty:
            if not cls._should_audit(model):
                logger.debug(
                    f"[{AuditOperation.UPDATE}] Model is not registered or excluded from audit: {model.__class__.__name__}"
                )
                continue
            if not hasattr(model, "__tablename__"):
                continue
            if not session.is_modified(model):
                continue
            audit_entry_deque.append((model, AuditOperation.UPDATE))
        for model in session.deleted:
            if not cls._should_audit(model):
                logger.debug(
                    f"[{AuditOperation.DELETE}] Model is not registered or excluded from audit: {model.__class__.__name__}"
                )
                continue
            if not hasattr(model, "__tablename__"):
                continue
            audit_entry_deque.append((model, AuditOperation.DELETE))
        return await cls._process_audit_entries(audit_entry_deque)

    @classmethod
    def _get_audit_entries_sync(cls, *args, **kwargs):
        """
        Synchronous version of `_get_audit_entries`.

        Args:
            *args: Positional arguments to pass to `_get_audit_entries`.
            **kwargs: Keyword arguments to pass to `_get_audit_entries`.

        Returns:
            list[AuditEntry]: A list of audit entries.
        """
        return run_coroutine_in_threadpool(cls._get_audit_entries(*args, **kwargs))

    @classmethod
    async def _process_audit_entries(
        cls,
        audit_entry_deque: collections.deque[tuple[SQLAModel, AuditOperation]],
        result: list[AuditEntry] | None = None,
        sessions: dict[str, SQLASession] | None = None,
    ):
        """
        Process audit entries from the given queue.

        Args:
            audit_entry_deque (collections.deque[tuple[SQLAModel, AuditOperation]]): The audit entries to process.
            result (list[AuditEntry] | None, optional): The list to store the processed audit entries. Defaults to None. Used for recursion.
            sessions (dict[str, SQLASession] | None, optional): The sessions to use for processing. Defaults to None. Used for recursion.

        Raises:
            ValueError: If the data is invalid.

        Returns:
            list[AuditEntry]: A list of processed audit entries.
        """
        result = result if result is not None else []
        sessions = sessions if sessions is not None else {}
        while audit_entry_deque:
            dat = audit_entry_deque.popleft()
            model, operation = dat
            if model.__bind_key__ not in sessions:
                async with db.session(model.__bind_key__) as session:
                    sessions[model.__bind_key__] = session
                    audit_entry_deque.appendleft(dat)  # Re-add to process later
                    await cls._process_audit_entries(
                        audit_entry_deque, result, sessions
                    )
                    del sessions[model.__bind_key__]
            else:
                session = sessions[model.__bind_key__]
                if operation == AuditOperation.DELETE:
                    result.append(
                        AuditEntry(
                            model=model,
                            operation=AuditOperation.DELETE,
                            pk=str(model.id_),
                        )
                    )
                else:
                    excluded_properties = set[str]()
                    for excluded_model in cls.excluded_properties:
                        if model.__class__ == excluded_model or issubclass(
                            model.__class__, excluded_model
                        ):
                            excluded_properties.update(
                                cls.excluded_properties[excluded_model]
                            )
                    state = sqlalchemy.inspect(model)
                    model_keys = cls.included_properties[model.__class__] or [
                        x for x in state.attrs.keys() if x not in excluded_properties
                    ]
                    datamodel = cls.interfaces[model.__class__]
                    schema_key = f"{model.__class__.__name__}-{'-'.join(model_keys)}"
                    schema = cls.schemas.get(schema_key)
                    if not schema:
                        cls.schemas[schema_key] = schema = datamodel.generate_schema(
                            model_keys,
                            with_id=False,
                            with_name=False,
                            optional=True,
                            related_kwargs={"with_property": False},
                        )
                    data = schema.model_validate(model).model_dump(mode="json")
                    if operation == AuditOperation.INSERT:
                        updates = {k: (None, v) for k, v in data.items()}
                        result.append(
                            AuditEntry(
                                model=model,
                                operation=AuditOperation.INSERT,
                                pk=str(model.id_),
                                data=data,
                                updates=updates,
                            )
                        )
                    elif operation == AuditOperation.UPDATE:
                        updated_columns = [
                            x
                            for x in model_keys
                            if state.attrs[x].history.has_changes()
                        ]
                        old_model = await datamodel.get_one(
                            session,
                            {
                                "list_columns": updated_columns,
                                "where_id": model.id_,
                            },
                        )
                        if not old_model:
                            logger.warning(
                                f"[{AuditOperation.UPDATE}] Skipping audit entry due to missing old model data from the database: {model.__class__.__name__} {model.id_}"
                            )
                            continue
                        change_schema_key = f"{old_model.__class__.__name__}-{'-'.join(updated_columns)}"
                        change_schema = cls.schemas.get(change_schema_key)
                        if not change_schema:
                            cls.schemas[change_schema_key] = change_schema = (
                                datamodel.generate_schema(
                                    updated_columns,
                                    with_id=False,
                                    with_name=False,
                                    optional=True,
                                    related_kwargs={"with_property": False},
                                )
                            )
                        old_data = change_schema.model_validate(old_model).model_dump(
                            mode="json"
                        )
                        updates = {
                            k: (old_data[k], data[k]) for k in old_data if k in data
                        }
                        if not updates:
                            logger.debug(
                                f"[{AuditOperation.UPDATE}] No changes detected for model: {model.__class__.__name__} {model.id_}"
                            )
                            continue
                        result.append(
                            AuditEntry(
                                model=model,
                                operation=AuditOperation.UPDATE,
                                pk=str(model.id_),
                                data=data,
                                updates=updates,
                            )
                        )
        return result

    @classmethod
    def _should_audit(cls, model: SQLAModel):
        """
        Check if a model should be audited.

        Args:
            model (SQLAModel): The SQLAlchemy model instance to check.

        Returns:
            bool: True if the model should be audited, False otherwise.
        """
        return model.__class__ not in cls.excluded_models and (
            model.__class__ in cls.models
            or any(issubclass(model.__class__, m) for m in cls.models)
        )
