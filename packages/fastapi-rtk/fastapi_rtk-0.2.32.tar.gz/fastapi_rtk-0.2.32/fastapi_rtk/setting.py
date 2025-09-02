import typing

from .const import (
    DEFAULT_API_MAX_PAGE_SIZE,
    DEFAULT_PROFILER_FOLDER,
    DEFAULT_STATIC_FOLDER,
    DEFAULT_TEMPLATE_FOLDER,
    logger,
)
from .globals import g

if typing.TYPE_CHECKING:
    from .bases.file_manager import AbstractFileManager, AbstractImageManager


__all__ = ["Setting"]

logger = logger.getChild("setting")


class _Setting:
    """
    A static class to have an overview of the settings of the FastAPI application. It is designed to be used as a static class and as a single source of truth for the settings.

    This `Setting` is useful for documentation purposes, as it provides a clear overview of the settings available in the application. It is not intended to be used as a configuration manager or to modify the settings at runtime.
    """

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str | None:
        """
        SQLAlchemy database URI.
        """
        return g.config.get("SQLALCHEMY_DATABASE_URI")

    @property
    def SQLALCHEMY_BINDS(self) -> dict[str, str] | None:
        """
        SQLAlchemy binds.
        """
        return g.config.get("SQLALCHEMY_BINDS")

    @property
    def SQLALCHEMY_ENGINE_OPTIONS(self) -> dict[str, typing.Any]:
        """
        SQLAlchemy engine options.
        """
        return g.config.get("SQLALCHEMY_ENGINE_OPTIONS", {})

    @property
    def SQLALCHEMY_ENGINE_OPTIONS_BINDS(self) -> dict[str, typing.Any]:
        """
        SQLAlchemy engine options for binds.
        """
        return g.config.get("SQLALCHEMY_ENGINE_OPTIONS_BINDS", {})

    @property
    def ROLES(self) -> dict[str, list[list[str] | tuple[str, str]]]:
        return g.config.get("ROLES") or g.config.get("FAB_ROLES", {})

    @property
    def STATIC_FOLDER(self) -> str:
        return g.config.get("STATIC_FOLDER", DEFAULT_STATIC_FOLDER)

    @property
    def TEMPLATE_FOLDER(self) -> str:
        return g.config.get("TEMPLATE_FOLDER", DEFAULT_TEMPLATE_FOLDER)

    @property
    def FILE_MANAGER(self) -> "AbstractFileManager | None":
        """
        The file manager to use for file uploads.
        """
        return g.config.get("FILE_MANAGER")

    @property
    def IMAGE_MANAGER(self) -> "AbstractImageManager | None":
        """
        The image manager to use for image uploads.
        """
        return g.config.get("IMAGE_MANAGER")

    @property
    def UPLOAD_FOLDER(self) -> str | None:
        return g.config.get("UPLOAD_FOLDER")

    @property
    def IMG_UPLOAD_FOLDER(self) -> str | None:
        return g.config.get("IMG_UPLOAD_FOLDER")

    @property
    def FILE_ALLOWED_EXTENSIONS(self) -> list[str] | None:
        return g.config.get("FILE_ALLOWED_EXTENSIONS")

    @property
    def IMG_ALLOWED_EXTENSIONS(self) -> list[str]:
        return g.config.get(
            "IMG_ALLOWED_EXTENSIONS", ["gif", "jpg", "jpeg", "png", "tiff"]
        )

    @property
    def BASE_PATH(self) -> str | None:
        return g.config.get("BASE_PATH")

    @property
    def FAB_REACT_CONFIG(self) -> dict[str, typing.Any]:
        return g.config.get("FAB_REACT_CONFIG", {})

    @property
    def PROFILER_ENABLED(self) -> bool:
        """
        Whether the profiler is enabled.
        """
        return g.config.get("PROFILER_ENABLED", False)

    @property
    def PROFILER_FOLDER(self) -> str:
        """
        The folder to store profiler files.
        """
        return g.config.get("PROFILER_FOLDER", DEFAULT_PROFILER_FOLDER)

    @property
    def PROFILER_TYPE(self) -> str:
        """
        The profiler type.
        """
        return g.config.get("PROFILER_TYPE", "html")

    @property
    def PROFILER_RENDERER(self) -> str:
        """
        The profiler renderer.
        """
        return g.config.get("PROFILER_RENDERER", "HTMLRenderer")

    @property
    def INSTRUMENTATOR_CONFIG(self) -> dict[str, typing.Any]:
        """
        Instrumentator configuration.
        """
        return g.config.get("INSTRUMENTATOR_CONFIG", {})

    @property
    def INSTRUMENTATOR_INSTRUMENT_CONFIG(self) -> dict[str, typing.Any]:
        """
        Instrumentator instrument configuration.
        """
        return g.config.get("INSTRUMENTATOR_INSTRUMENT_CONFIG", {})

    @property
    def INSTRUMENTATOR_EXPOSE_CONFIG(self) -> dict[str, typing.Any]:
        """
        Instrumentator expose configuration.
        """
        return g.config.get("INSTRUMENTATOR_EXPOSE_CONFIG", {})

    @property
    def AUTH_LOGIN_COOKIE(self) -> bool:
        return g.config.get("AUTH_LOGIN_COOKIE", True)

    @property
    def AUTH_LOGIN_JWT(self) -> bool | None:
        return g.config.get("AUTH_LOGIN_JWT")

    @property
    def AUTH_USER_REGISTRATION(self) -> bool | None:
        return g.config.get("AUTH_USER_REGISTRATION")

    @property
    def AUTH_USER_REGISTRATION_ROLE(self) -> list[str] | str | None:
        return g.config.get("AUTH_USER_REGISTRATION_ROLE")

    @property
    def AUTH_USER_RESET_PASSWORD(self) -> bool | None:
        return g.config.get("AUTH_USER_RESET_PASSWORD")

    @property
    def AUTH_USER_VERIFY(self) -> bool | None:
        return g.config.get("AUTH_USER_VERIFY")

    @property
    def AUTH_ROLES_MAPPING(self) -> dict[str, list[str]]:
        return g.config.get("AUTH_ROLES_MAPPING", {})

    @property
    def AUTH_ROLES_SYNC_AT_LOGIN(self) -> bool:
        logger.warning(
            "`AUTH_ROLES_SYNC_AT_LOGIN` is no longer used, please use `on_before_login` callback and set the `role_keys` to `user_dict` parameter."
        )
        return g.config.get("AUTH_ROLES_SYNC_AT_LOGIN", False)

    @property
    def OAUTH_CLIENTS(self) -> list[dict[str, typing.Any]]:
        return g.config.get("OAUTH_CLIENTS", g.config.get("OAUTH_PROVIDERS", []))

    @property
    def OAUTH_REDIRECT_URI(self) -> str | None:
        return g.config.get("OAUTH_REDIRECT_URI")

    @property
    def API_MAX_PAGE_SIZE(self) -> int:
        return g.config.get(
            "API_MAX_PAGE_SIZE",
            g.config.get("FAB_API_MAX_PAGE_SIZE", DEFAULT_API_MAX_PAGE_SIZE),
        )

    @property
    def APP_NAME(self) -> str:
        return g.config.get("APP_NAME", "FastAPI React Toolkit")

    @property
    def APP_SUMMARY(self) -> str | None:
        return g.config.get("APP_SUMMARY")

    @property
    def APP_DESCRIPTION(self) -> str | None:
        return g.config.get("APP_DESCRIPTION")

    @property
    def APP_VERSION(self) -> str | None:
        return g.config.get("APP_VERSION")

    @property
    def APP_OPENAPI_URL(self) -> str | None:
        return g.config.get("APP_OPENAPI_URL")

    @property
    def TEXT_FILTER_SEPARATOR(self) -> str:
        return g.config.get("TEXT_FILTER_SEPARATOR", ";")

    @property
    def DEBUG(self) -> bool:
        return g.config.get("DEBUG", False)

    @property
    def SECWEB_ENABLED(self) -> bool:
        return g.config.get("SECWEB_ENABLED", False)

    @property
    def SECWEB_PARAMS(self) -> dict[str, typing.Any]:
        return g.config.get("SECWEB_PARAMS", {})

    @property
    def SECWEB_PATCH_DOCS(self) -> bool:
        return g.config.get("SECWEB_PATCH_DOCS", True)

    @property
    def SECWEB_PATCH_REDOC(self) -> bool:
        return g.config.get("SECWEB_PATCH_REDOC", True)

    @property
    def TEMPLATE_CONTEXT(self) -> dict[str, typing.Any]:
        return g.config.get("TEMPLATE_CONTEXT", {})

    @property
    def GREMLIN_CONNECTION(self) -> tuple[str, str] | None:
        """
        The Gremlin URL and graph object.
        """
        return g.config.get("GREMLIN_CONNECTION", g.config.get("GREMLIN_URL"))

    @property
    def GREMLIN_CONNECTION_OPTIONS(self) -> dict[str, typing.Any]:
        """
        The Gremlin connection options.

        See `gremlin_python.driver.driver_remote_connection.DriverRemoteConnection` for more details.
        """
        return g.config.get("GREMLIN_CONNECTION_OPTIONS", {})

    @property
    def JANUSGRAPH_RESERVED_LETTERS(self) -> list[str]:
        return g.config.get("JANUSGRAPH_RESERVED_LETTERS", ["-"])


Setting = _Setting()
"""
Single source of truth for the configuration of the FastAPI React Toolkit.
"""
