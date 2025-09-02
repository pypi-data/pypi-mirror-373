"""
This allows to use global variables inside the FastAPI application using async mode.
# Usage
Just import `g` and then access (set/get) attributes of it:
```python
from your_project.globals import g
g.foo = "foo"
# In some other code
assert g.foo == "foo"
```
Best way to utilize the global `g` in your code is to set the desired
value in a FastAPI dependency, like so:
```python
async def set_global_foo() -> None:
    g.foo = "foo"
@app.get("/test/", dependencies=[Depends(set_global_foo)])
async def test():
    assert g.foo == "foo"
```
# Setup
Add the `GlobalsMiddleware` to your app:
```python
app = fastapi.FastAPI(
    title="Your app API",
)
app.add_middleware(GlobalsMiddleware)  # <-- This line is necessary
```
Then just use it. ;-)
# Default values
You may use `g.set_default("name", some_value)` to set a default value
for a global variable. This default value will then be used instead of `None`
when the variable is accessed before it was set.
Note that default values should only be set at startup time, never
inside dependencies or similar. Otherwise you may run into the issue that
the value was already used any thus have a value of `None` set already, which
would result in the default value not being used.
"""

from collections.abc import Awaitable, Callable
from contextvars import ContextVar, copy_context
from typing import TYPE_CHECKING, Any

import fastapi
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .config import Config
from .const import (
    AUTH_ROLE_CONFIG,
    BEARER_CONFIG,
    BEARER_STRATEGY_CONFIG,
    COOKIE_CONFIG,
    COOKIE_STRATEGY_CONFIG,
    DEFAULT_ADMIN_ROLE,
    DEFAULT_PUBLIC_ROLE,
)
from .utils import lazy, lazy_import

if TYPE_CHECKING:
    from .auth import AuthConfigurator
    from .bases.file_manager import AbstractFileManager, AbstractImageManager
    from .fastapi_react_toolkit import FastAPIReactToolkit
    from .security.sqla.models import User

__all__ = ["g"]


class Globals:
    __slots__ = ("_vars", "_defaults")

    _vars: dict[str, ContextVar]
    _defaults: dict[str, Any]

    # Type annotations for the attributes
    user: "User"
    """
    The current user object. It will be `None` when not used in a request context.
    """
    auth: "AuthConfigurator"
    """
    The configuration settings for the authentication.
    """
    config: Config
    """
    The configuration settings for the FastAPI React Toolkit.
    """
    admin_role: str
    """
    The role key for the admin role. Default is `"Admin"`.
    """
    public_role: str
    """
    The role key for the public role. Default is `"Public"`.
    """
    is_migrate: bool
    """
    A boolean value to indicate if the application is in migration mode. `True` when you are running a command from `fastapi-rtk` CLI.
    """
    sensitive_data: dict[str, list[str]]
    """
    A dictionary used to store list of sensitive columns for each model that should not be returned in the list and get endpoints. Default is `{"User": ["password", "hashed_password"]}`.
    """
    background_tasks: fastapi.BackgroundTasks
    """
    The background tasks object to add tasks to be executed after the response is sent. It will be `None` when not used in a request context.
    """
    file_manager: "AbstractFileManager"
    """
    The file manager object to manage files in the application. Defaults to `FileManager` from `fastapi_rtk.file_managers.file_manager`.
    """
    image_manager: "AbstractImageManager"
    """
    The image manager object to manage images in the application. Defaults to `ImageManager` from `fastapi_rtk.file_managers.image_manager`.
    """
    current_app: "FastAPIReactToolkit"

    def __init__(self) -> None:
        object.__setattr__(self, "_vars", {})
        object.__setattr__(self, "_defaults", {})

    def set_default(self, name: str, default: Any) -> None:
        """Set a default value for a variable."""

        # Ignore if default is already set and is the same value
        if name in self._defaults and default is self._defaults[name]:
            return

        # Ensure we don't have a value set already - the default will have
        # no effect then
        if name in self._vars:
            raise RuntimeError(
                f"Cannot set default as variable {name} was already set",
            )

        # Set the default already!
        self._defaults[name] = default

    def _get_default_value(self, name: str) -> Any:
        """Get the default value for a variable."""

        default = self._defaults.get(name, None)

        return default() if callable(default) else default

    def _ensure_var(self, name: str) -> None:
        """Ensure a ContextVar exists for a variable."""

        if name not in self._vars:
            default = self._get_default_value(name)
            self._vars[name] = ContextVar(f"globals:{name}", default=default)

    def __getattr__(self, name: str) -> Any:
        """Get the value of a variable."""

        self._ensure_var(name)
        return self._vars[name].get()

    def __setattr__(self, name: str, value: Any) -> None:
        """Set the value of a variable."""

        self._ensure_var(name)
        self._vars[name].set(value)


async def globals_middleware_dispatch(
    request: Request,
    call_next: Callable,
) -> Response:
    """Dispatch the request in a new context to allow globals to be used."""

    ctx = copy_context()

    def _call_next() -> Awaitable[Response]:
        return call_next(request)

    return await ctx.run(_call_next)


class GlobalsMiddleware(BaseHTTPMiddleware):  # noqa
    """Middleware to setup the globals context using globals_middleware_dispatch()."""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app, globals_middleware_dispatch)


def basic_callback():
    """
    Initializes the configuration settings for the FastAPI React Toolkit.

    This method reads the configuration values from the `g.config` dictionary and sets the corresponding attributes
    in the `g.auth`. It also sets the default values for any missing configuration settings.

    The configuration settings that are read and set include:
    - Authentication keys from `g.auth`
    - Cookie configuration settings
    - Cookie strategy configuration settings
    - Bearer strategy configuration settings
    - Role keys

    Note: The `g.config` dictionary should contain the necessary configuration values for the FastAPI React Toolkit.
    """
    from .auth import BearerConfig, CookieConfig, StrategyConfig

    AUTH_CONFIG = g.auth.auth_config()
    cookie_config: CookieConfig = {}
    bearer_config: BearerConfig = {}
    cookie_strategy_config: StrategyConfig = {}
    bearer_strategy_config: StrategyConfig = {}
    for key, value in g.config.items():
        if key in AUTH_CONFIG:
            setattr(g.auth, AUTH_CONFIG[key], value)
        elif key in COOKIE_CONFIG:
            cookie_config[COOKIE_CONFIG[key]] = value
        elif key in COOKIE_STRATEGY_CONFIG:
            cookie_strategy_config[COOKIE_STRATEGY_CONFIG[key]] = value
        elif key in BEARER_CONFIG:
            bearer_config[BEARER_CONFIG[key]] = value
        elif key in BEARER_STRATEGY_CONFIG:
            bearer_strategy_config[BEARER_STRATEGY_CONFIG[key]] = value
        elif key in AUTH_ROLE_CONFIG:
            setattr(g, AUTH_ROLE_CONFIG[key], value)

    if cookie_config:
        g.auth.cookie_config = cookie_config
    if bearer_config:
        g.auth.bearer_config = bearer_config
    if cookie_strategy_config:
        g.auth.cookie_strategy_config = cookie_strategy_config
    if bearer_strategy_config:
        g.auth.bearer_strategy_config = bearer_strategy_config


g = Globals()
g.set_default(
    "auth", lazy_import("fastapi_rtk.auth", lambda mod: mod.AuthConfigurator())
)
g.set_default("config", Config())
g.set_default("admin_role", DEFAULT_ADMIN_ROLE)
g.set_default("public_role", DEFAULT_PUBLIC_ROLE)
g.set_default("is_migrate", False)
g.set_default("sensitive_data", {"User": ["password", "hashed_password"]})
g.set_default(
    "file_manager",
    lazy(
        lambda: lazy_import(
            "fastapi_rtk.setting", lambda mod: mod.Setting.FILE_MANAGER
        )()
        or lazy_import("fastapi_rtk.file_managers", lambda mod: mod.FileManager())()
    ),
)
g.set_default(
    "image_manager",
    lazy(
        lambda: lazy_import(
            "fastapi_rtk.setting", lambda mod: mod.Setting.IMAGE_MANAGER
        )()
        or lazy_import("fastapi_rtk.file_managers", lambda mod: mod.ImageManager())()
    ),
)
g.config.add_callback(basic_callback)
