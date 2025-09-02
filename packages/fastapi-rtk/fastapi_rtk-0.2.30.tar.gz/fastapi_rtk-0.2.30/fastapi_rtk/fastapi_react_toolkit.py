import inspect
import io
import logging
import os
from contextlib import asynccontextmanager
from typing import Awaitable, Callable

import Secweb
import Secweb.ContentSecurityPolicy
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, TemplateNotFound, select_autoescape
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from starlette.routing import _DefaultLifespan

from .api.model_rest_api import ModelRestApi
from .auth import Auth
from .cli.commands import upgrade
from .const import BASE_APIS, DEFAULT_SECWEB_PARAMS, logger
from .db import db
from .dependencies import set_global_background_tasks, set_global_user
from .globals import GlobalsMiddleware, g
from .middlewares import (
    ProfilerMiddleware,
    SecWebPatchDocsMiddleware,
    SecWebPatchReDocMiddleware,
)
from .security.sqla.apis import (
    AuthApi,
    InfoApi,
    PermissionsApi,
    PermissionViewApi,
    RolesApi,
    UsersApi,
    ViewsMenusApi,
)
from .security.sqla.models import Api, Permission, PermissionApi, Role
from .security.sqla.security_manager import SecurityManager
from .setting import Setting
from .utils import deep_merge, safe_call, smart_run
from .version import __version__

__all__ = ["FastAPIReactToolkit"]


class FastAPIReactToolkit:
    """
    The main class for the `FastAPIReactToolkit` library.

    This class provides a set of methods to initialize a FastAPI application, add APIs, manage permissions and roles,
    and initialize the database with permissions, APIs, roles, and their relationships.

    Args:
        app (FastAPI | None, optional): The FastAPI application instance. If set, the `initialize` method will be called with this instance. Defaults to None.
        create_tables (bool, optional): Whether to create tables in the database. Not needed if you use a migration system like Alembic. Defaults to False.
        upgrade_db (bool, optional): Whether to upgrade the database automatically with the `upgrade` command. Same as running `fastapi-rtk db upgrade`. Defaults to False.
        cleanup (bool, optional): Whether to clean up old permissions and roles in the database using `SecurityManager.cleanup()`. Defaults to False.
        auth (Auth | None, optional): The authentication configuration. Set this if you want to customize the authentication system. See the `Auth` class for more details. Defaults to None.
        exclude_apis (list[BASE_APIS] | None, optional): List of security APIs to be excluded when initializing the FastAPI application. Defaults to None.
        global_user_dependency (bool, optional): Whether to add the `set_global_user` dependency to the FastAPI application. This allows you to access the current user with the `g.user` object. Defaults to True.
        global_background_tasks (bool, optional): Whether to add the `set_global_background_tasks` dependency to the FastAPI application. This allows you to access the background tasks with the `g.background_tasks` object. Defaults to True.
        instrumentator (Instrumentator | None, optional): The instrumentator to use for monitoring the FastAPI application. Defaults to `Instrumentator(**Setting.INSTRUMENTATOR_CONFIG)`.
        on_startup (Callable[[FastAPI], None]  |  Awaitable[Callable[[FastAPI], None]]  |  None, optional): Function to call when the app is starting up. Can either be a regular function or an async function. If the function takes a `FastAPI` instance as an argument, it will be passed to the function. Defaults to None.
        on_shutdown (Callable[[FastAPI], None]  |  Awaitable[Callable[[FastAPI], None]]  |  None, optional): Function to call when the app is shutting down. Can either be a regular function or an async function. If the function takes a `FastAPI` instance as an argument, it will be passed to the function. Defaults to None.
        debug (bool, optional): Whether to log debug messages. Defaults to False.

    ## Example:

    ```python
    import logging

    from fastapi import FastAPI, Request, Response
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi_rtk import FastAPIReactToolkit, User
    from fastapi_rtk.manager import UserManager

    from .base_data import add_base_data

    logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
    logging.getLogger().setLevel(logging.INFO)


    class CustomUserManager(UserManager):
        async def on_after_login(
            self,
            user: User,
            request: Request | None = None,
            response: Response | None = None,
        ) -> None:
            await super().on_after_login(user, request, response)
            print("User logged in: ", user)


    async def on_startup(app: FastAPI):
        await add_base_data()
        print("base data added")
        pass


    app = FastAPI(docs_url="/openapi/v1")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:6006"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    toolkit = FastAPIReactToolkit(
        auth={
            "user_manager": CustomUserManager,
            # "password_helper": FABPasswordHelper(),  #! Add this line to use old password hash
        },
        create_tables=True,
        on_startup=on_startup,
    )
    toolkit.config.from_pyfile("./app/config.py")
    toolkit.initialize(app)

    from .apis import *
    ```
    """

    app: FastAPI = None

    # Database configuration
    create_tables: bool = False
    upgrade_db = False
    cleanup = False

    # Application configuration
    exclude_apis: list[BASE_APIS] = None
    global_user_dependency = True
    global_background_tasks = True
    instrumentator: Instrumentator = None
    on_startup: (
        Callable[[FastAPI], None] | Awaitable[Callable[[FastAPI], None]] | None
    ) = None
    on_shutdown: (
        Callable[[FastAPI], None] | Awaitable[Callable[[FastAPI], None]] | None
    ) = None

    # Public attributes
    apis: list[ModelRestApi] = None
    initialized = False
    security: SecurityManager = None

    # Private attributes
    _mounted = False

    def __init__(
        self,
        app: FastAPI | None = None,
        *,
        # Database configuration
        create_tables: bool = False,
        upgrade_db: bool = False,
        cleanup: bool = False,
        # Application configuration
        auth: Auth | None = None,
        exclude_apis: list[BASE_APIS] | None = None,
        global_user_dependency: bool = True,
        global_background_tasks: bool = True,
        instrumentator: Instrumentator | None = None,
        on_startup: (
            Callable[[FastAPI], None] | Awaitable[Callable[[FastAPI], None]] | None
        ) = None,
        on_shutdown: (
            Callable[[FastAPI], None] | Awaitable[Callable[[FastAPI], None]] | None
        ) = None,
        debug: bool = False,
    ):
        """
        Initializes the FastAPIReactToolkit with the given parameters.

        Args:
            app (FastAPI | None, optional): The FastAPI application instance. If set, the `initialize` method will be called with this instance. Defaults to None.
            create_tables (bool, optional): Whether to create tables in the database. Not needed if you use a migration system like Alembic. Defaults to False.
            upgrade_db (bool, optional): Whether to upgrade the database automatically with the `upgrade` command. Same as running `fastapi-rtk db upgrade`. Defaults to False.
            cleanup (bool, optional): Whether to clean up old permissions and roles in the database using `SecurityManager.cleanup()`. Defaults to False.
            auth (Auth | None, optional): The authentication configuration. Set this if you want to customize the authentication system. See the `Auth` class for more details. Defaults to None.
            exclude_apis (list[BASE_APIS] | None, optional): List of security APIs to be excluded when initializing the FastAPI application. Defaults to None.
            global_user_dependency (bool, optional): Whether to add the `set_global_user` dependency to the FastAPI application. This allows you to access the current user with the `g.user` object. Defaults to True.
            global_background_tasks (bool, optional): Whether to add the `set_global_background_tasks` dependency to the FastAPI application. This allows you to access the background tasks with the `g.background_tasks` object. Defaults to True.
            instrumentator (Instrumentator | None, optional): The instrumentator to use for monitoring the FastAPI application. Defaults to `Instrumentator(**Setting.INSTRUMENTATOR_CONFIG)`.
            on_startup (Callable[[FastAPI], None]  |  Awaitable[Callable[[FastAPI], None]]  |  None, optional): Function to call when the app is starting up. Can either be a regular function or an async function. If the function takes a `FastAPI` instance as an argument, it will be passed to the function. Defaults to None.
            on_shutdown (Callable[[FastAPI], None]  |  Awaitable[Callable[[FastAPI], None]]  |  None, optional): Function to call when the app is shutting down. Can either be a regular function or an async function. If the function takes a `FastAPI` instance as an argument, it will be passed to the function. Defaults to None.
            debug (bool, optional): Whether to log debug messages. Defaults to False.
        """
        g.current_app = self
        self.apis = []
        self.security = SecurityManager(self)

        # Database configuration
        self.create_tables = create_tables
        self.upgrade_db = upgrade_db
        self.cleanup = cleanup

        self.exclude_apis = exclude_apis or []
        self.global_user_dependency = global_user_dependency
        self.global_background_tasks = global_background_tasks
        self.instrumentator = instrumentator
        self.on_startup = on_startup
        self.on_shutdown = on_shutdown

        if auth:
            for key, value in auth.items():
                setattr(g.auth, key, value)

        if app:
            self.initialize(app)

        if debug:
            logger.setLevel(logging.DEBUG)

    def initialize(self, app: FastAPI) -> None:
        """
        Initializes the FastAPI application.

        Args:
            app (FastAPI): The FastAPI application instance.

        Returns:
            None
        """
        if self.initialized:
            return

        self.initialized = True
        self.app = app

        # Read config once
        self._init_config()

        # Add SecWeb
        if Setting.SECWEB_ENABLED:
            Secweb.SecWeb(
                app, **deep_merge(DEFAULT_SECWEB_PARAMS, Setting.SECWEB_PARAMS)
            )

            if Setting.SECWEB_PATCH_DOCS:
                self.app.add_middleware(SecWebPatchDocsMiddleware, fastapi=app)

            if Setting.SECWEB_PATCH_REDOC:
                self.app.add_middleware(SecWebPatchReDocMiddleware)

        # Initialize the database connection
        self.connect_to_database()

        # Initialize the lifespan
        self._init_lifespan()

        # Add the ProfilerMiddleware
        if Setting.PROFILER_ENABLED:
            try:
                import pyinstrument  # type: ignore
            except ImportError:
                raise RuntimeError(
                    "Profiler is enabled but pyinstrument is not installed, please install pyinstrument to use the profiler"
                )
            g.pyinstrument = pyinstrument
            self.app.add_middleware(ProfilerMiddleware)
            logger.info("PROFILER ENABLED")

        # Add the GlobalsMiddleware
        self.app.add_middleware(GlobalsMiddleware)
        if self.global_user_dependency:
            self.app.router.dependencies.append(Depends(set_global_user()))
        if self.global_background_tasks:
            self.app.router.dependencies.append(Depends(set_global_background_tasks))

        # Initialize the instrumentator
        if not self.instrumentator:
            self.instrumentator = Instrumentator(**Setting.INSTRUMENTATOR_CONFIG)
        self.instrumentator.instrument(
            app=self.app, **Setting.INSTRUMENTATOR_INSTRUMENT_CONFIG
        )

        # Add the APIs
        self._init_basic_apis()

    def add_api(self, api: ModelRestApi | type[ModelRestApi]):
        """
        Adds the specified API to the FastAPI application.

        Parameters:
        - api (ModelRestApi | type[ModelRestApi]): The API to add to the FastAPI application.

        Returns:
        - None

        Raises:
        - ValueError: If the API is added after the `mount()` method is called.
        """
        if self._mounted:
            raise ValueError(
                "API Mounted after mount() was called, please add APIs before calling mount()"
            )

        api = api if isinstance(api, ModelRestApi) else api()
        previous_api = next(
            (a for a in self.apis if a.resource_name == api.resource_name), None
        )
        if previous_api:
            logger.warning(
                f"API {api.resource_name} already exists, replacing with new API"
            )
            self.apis.remove(previous_api)
        self.apis.append(api)
        api.toolkit = self

    def total_permissions(self) -> list[str]:
        """
        Returns the total list of permissions required by all APIs.

        Returns:
        - list[str]: The total list of permissions.
        """
        permissions = []
        for api in self.apis:
            permissions.extend(getattr(api, "permissions", []))
        return list(set(permissions))

    def connect_to_database(self):
        """
        Connects to the database using the configured SQLAlchemy database URI.

        This method initializes the database session maker with the SQLAlchemy
        database URI specified in the configuration.

        Raises:
            ValueError: If the `SQLALCHEMY_DATABASE_URI` is not set in the configuration.
        """
        uri = Setting.SQLALCHEMY_DATABASE_URI
        if not uri:
            logger.warning(
                "SQLALCHEMY_DATABASE_URI is not set in the configuration, skipping database connection, any database related operation will fail"
            )
            return

        binds = Setting.SQLALCHEMY_BINDS
        db.init_db(uri, binds)
        logger.info("Connected to database")
        logger.info(f"URI: {db._engine.url}")
        if db._engine_binds:
            logger.info("BINDS =========================")
            for bind, engine in db._engine_binds.items():
                logger.info(f"{bind}: {engine.url}")
            logger.info("BINDS =========================")

    async def init_database(self):
        """
        Initializes the database by inserting permissions, APIs, roles, and their relationships.

        The initialization process is as follows:
        1. Inserts permissions into the database.
        2. Inserts APIs into the database.
        3. Inserts roles into the database.
        4. Inserts the relationship between permissions and APIs into the database.
        5. Inserts the relationship between permissions, APIs, and roles into the database.

        Returns:
            None
        """
        if not db._engine:
            logger.warning(
                "Database not connected, skipping database initialization, any database related operation will fail"
            )
            return

        async with db.session() as session:
            logger.info("INITIALIZING DATABASE")
            await self._insert_permissions(session)
            await self._insert_apis(session)
            await self._insert_roles(session)
            await self._associate_permission_with_api(session)
            await self._associate_permission_api_with_role(session)
            if self.cleanup:
                await self.security.cleanup()
            logger.info("DATABASE INITIALIZED")

    async def _insert_permissions(self, session: AsyncSession | Session):
        new_permissions = self.total_permissions()
        stmt = select(Permission).where(Permission.name.in_(new_permissions))
        result = await safe_call(session.scalars(stmt))
        existing_permissions = [permission.name for permission in result.all()]
        if len(new_permissions) == len(existing_permissions):
            return

        permission_objs = [
            Permission(name=permission)
            for permission in new_permissions
            if permission not in existing_permissions
        ]
        for permission in permission_objs:
            logger.info(f"ADDING PERMISSION {permission}")
            session.add(permission)
        await safe_call(session.commit())

    async def _insert_apis(self, session: AsyncSession | Session):
        new_apis = [api.__class__.__name__ for api in self.apis]
        stmt = select(Api).where(Api.name.in_(new_apis))
        result = await safe_call(session.scalars(stmt))
        existing_apis = [api.name for api in result.all()]
        if len(new_apis) == len(existing_apis):
            return

        api_objs = [Api(name=api) for api in new_apis if api not in existing_apis]
        for api in api_objs:
            logger.info(f"ADDING API {api}")
            session.add(api)
        await safe_call(session.commit())

    async def _insert_roles(self, session: AsyncSession | Session):
        new_roles = [g.admin_role, g.public_role]
        stmt = select(Role).where(Role.name.in_(new_roles))
        result = await safe_call(session.scalars(stmt))
        existing_roles = [role.name for role in result.all()]
        if len(new_roles) == len(existing_roles):
            return

        role_objs = [
            Role(name=role) for role in new_roles if role not in existing_roles
        ]
        for role in role_objs:
            logger.info(f"ADDING ROLE {role}")
            session.add(role)
        await safe_call(session.commit())

    async def _associate_permission_with_api(self, session: AsyncSession | Session):
        for api in self.apis:
            new_permissions = getattr(api, "permissions", [])
            if not new_permissions:
                continue

            # Get the api object
            api_stmt = select(Api).where(Api.name == api.__class__.__name__)
            api_obj = await safe_call(session.scalar(api_stmt))

            if not api_obj:
                raise ValueError(f"API {api.__class__.__name__} not found")

            permission_stmt = select(Permission).where(
                and_(
                    Permission.name.in_(new_permissions),
                    ~Permission.id.in_([p.permission_id for p in api_obj.permissions]),
                )
            )
            permission_result = await safe_call(session.scalars(permission_stmt))
            new_permissions = permission_result.all()

            if not new_permissions:
                continue

            for permission in new_permissions:
                session.add(
                    PermissionApi(permission_id=permission.id, api_id=api_obj.id)
                )
                logger.info(f"ASSOCIATING PERMISSION {permission} WITH API {api_obj}")
            await safe_call(session.commit())

    async def _associate_permission_api_with_role(
        self, session: AsyncSession | Session
    ):
        # Read config based roles
        roles_dict = Setting.ROLES

        for role_name, role_permissions in roles_dict.items():
            role_stmt = select(Role).where(Role.name == role_name)
            role_result = await safe_call(session.scalars(role_stmt))
            role = role_result.first()
            if not role:
                role = Role(name=role_name)
                logger.info(f"ADDING ROLE {role}")
                session.add(role)

            for api_name, permission_name in role_permissions:
                permission_api_stmt = (
                    select(PermissionApi)
                    .where(
                        and_(Api.name == api_name, Permission.name == permission_name)
                    )
                    .join(Permission)
                    .join(Api)
                )
                permission_api = await safe_call(session.scalar(permission_api_stmt))
                if not permission_api:
                    permission_stmt = select(Permission).where(
                        Permission.name == permission_name
                    )
                    permission = await safe_call(session.scalar(permission_stmt))
                    if not permission:
                        permission = Permission(name=permission_name)
                        logger.info(f"ADDING PERMISSION {permission}")
                        session.add(permission)

                    stmt = select(Api).where(Api.name == api_name)
                    api = await safe_call(session.scalar(stmt))
                    if not api:
                        api = Api(name=api_name)
                        logger.info(f"ADDING API {api}")
                        session.add(api)

                    permission_api = PermissionApi(permission=permission, api=api)
                    logger.info(f"ADDING PERMISSION-API {permission_api}")
                    session.add(permission_api)

                # Associate role with permission-api
                if role not in permission_api.roles:
                    permission_api.roles.append(role)
                    logger.info(
                        f"ASSOCIATING {role} WITH PERMISSION-API {permission_api}"
                    )

                await safe_call(session.commit())

        # Get admin role
        admin_role_stmt = select(Role).where(Role.name == g.admin_role)
        admin_role = await safe_call(session.scalar(admin_role_stmt))

        if admin_role:
            # Get list of permission-api.assoc_permission_api_id of the admin role
            stmt = (
                select(PermissionApi)
                .where(~PermissionApi.roles.contains(admin_role))
                .join(Api)
            )
            result = await safe_call(session.scalars(stmt))
            existing_assoc_permission_api_roles = result.all()

            # Add admin role to all permission-api objects
            for permission_api in existing_assoc_permission_api_roles:
                permission_api.roles.append(admin_role)
                logger.info(
                    f"ASSOCIATING {admin_role} WITH PERMISSION-API {permission_api}"
                )
            await safe_call(session.commit())

    def _mount_static_folder(self):
        """
        Mounts the static folder specified in the configuration.

        Returns:
            None
        """
        # If the folder does not exist, create it
        os.makedirs(Setting.STATIC_FOLDER, exist_ok=True)

        static_folder = Setting.STATIC_FOLDER
        self.app.mount("/static", StaticFiles(directory=static_folder), name="static")

    def _mount_template_folder(self):
        """
        Mounts the template folder specified in the configuration.

        Returns:
            None
        """
        # If the folder does not exist, create it
        os.makedirs(Setting.TEMPLATE_FOLDER, exist_ok=True)

        templates = Jinja2Templates(directory=Setting.TEMPLATE_FOLDER)

        @self.app.get("/{full_path:path}", response_class=HTMLResponse)
        def index(request: Request):
            try:
                nonce = Secweb.ContentSecurityPolicy.Nonce_Processor()
                return templates.TemplateResponse(
                    request=request,
                    name="index.html",
                    context={
                        "base_path": (
                            Setting.BASE_PATH or request.scope["root_path"]
                        ).rstrip("/")
                        + "/",
                        "nonce": nonce,
                        "csp_nonce": lambda: nonce,
                        "app_name": Setting.APP_NAME,
                        **Setting.TEMPLATE_CONTEXT,
                    },
                )
            except TemplateNotFound:
                raise HTTPException(status_code=404, detail="Not Found")

    """
    -----------------------------------------
         INIT FUNCTIONS
    -----------------------------------------
    """

    def _init_config(self):
        """
        Initializes the configuration for the FastAPI application.

        This method reads the configuration values from the `g.config` dictionary and sets the corresponding attributes
        of the FastAPI application.
        """
        if self.app:
            self.app.title = Setting.APP_NAME
            self.app.summary = Setting.APP_SUMMARY or self.app.summary
            self.app.description = Setting.APP_DESCRIPTION or self.app.description
            self.app.version = Setting.APP_VERSION or __version__
            self.app.openapi_url = Setting.APP_OPENAPI_URL or self.app.openapi_url
            self.app.root_path = Setting.BASE_PATH or self.app.root_path

        if Setting.DEBUG:
            logger.setLevel(logging.DEBUG)

    def _init_lifespan(self):
        if g.is_migrate:
            return

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Integrate the router for each API
            for api in self.apis:
                api.integrate_router(app)

            # Add the endpoint for the metrics
            self.instrumentator.expose(app, **Setting.INSTRUMENTATOR_EXPOSE_CONFIG)

            # Add the JS manifest route
            self._init_js_manifest()

            # Mount the static and template folders
            self._mounted = True
            self._mount_static_folder()
            self._mount_template_folder()

            await db.init_fastapi_rtk_tables()

            if self.upgrade_db:
                await smart_run(upgrade)

            if self.create_tables and db._engine:
                await db.create_all()

            # Creating permission, apis, roles, and connecting them
            await self.init_database()

            # On startup
            if self.on_startup:
                parameter_length = len(
                    inspect.signature(self.on_startup).parameters.values()
                )
                if parameter_length > 0:
                    await safe_call(self.on_startup(app))
                else:
                    await safe_call(self.on_startup())

            for api in self.apis:
                await safe_call(api.on_startup())
                if hasattr(api, "datamodel"):
                    await safe_call(api.datamodel.on_startup())

            yield

            # On shutdown
            for api in self.apis:
                await safe_call(api.on_shutdown())
                if hasattr(api, "datamodel"):
                    await safe_call(api.datamodel.on_shutdown())

            if self.on_shutdown:
                parameter_length = len(
                    inspect.signature(self.on_shutdown).parameters.values()
                )
                if parameter_length > 0:
                    await safe_call(self.on_shutdown(app))
                else:
                    await safe_call(self.on_shutdown())

            # Run when the app is shutting down
            await db.close()

        # Check whether lifespan is already set
        if not isinstance(self.app.router.lifespan_context, _DefaultLifespan):
            raise ValueError(
                "Lifespan already set, please do not set lifespan directly in the FastAPI app"
            )

        self.app.router.lifespan_context = lifespan

    def _init_basic_apis(self):
        apis = [
            AuthApi,
            InfoApi,
            PermissionsApi,
            PermissionViewApi,
            RolesApi,
            UsersApi,
            ViewsMenusApi,
        ]
        for api in apis:
            if api.__name__ in self.exclude_apis:
                continue
            self.add_api(api)

    def _init_js_manifest(self):
        @self.app.get("/server-config.js", response_class=StreamingResponse)
        def js_manifest():
            env = Environment(autoescape=select_autoescape(["html", "xml"]))
            template_string = "window.fab_react_config = {{ react_vars |tojson }}"
            template = env.from_string(template_string)
            rendered_string = template.render(react_vars=Setting.FAB_REACT_CONFIG)
            content = rendered_string.encode("utf-8")
            scriptfile = io.BytesIO(content)
            return StreamingResponse(
                scriptfile,
                media_type="application/javascript",
            )

    """
    -----------------------------------------
         PROPERTY FUNCTIONS
    -----------------------------------------
    """

    @property
    def config(self):
        return g.config
