from typing import TYPE_CHECKING, Any, Dict

from fastapi import APIRouter, Depends

from ..const import PERMISSION_PREFIX, logger
from ..utils import T, lazy_self, update_signature
from ..utils import lazy as o_lazy

if TYPE_CHECKING:
    from ..fastapi_react_toolkit import FastAPIReactToolkit

__all__ = ["BaseApi"]


class lazy(lazy_self["BaseApi", T]): ...


class BaseApi:
    """
    Base API class for FastAPI.

    Provides a foundation for exposing API routes with integrated permission and authentication support.
    Handles route registration, permission management, and toolkit integration, allowing you to build
    secure and extensible APIs.

    See [FastAPI path]("https://fastapi.tiangolo.com/tutorial/path-params/") and [FastAPI query]("https://fastapi.tiangolo.com/tutorial/query-params/") for more details on how to use path and query parameters in your API endpoints.

    Usage:

    ```python
    from fastapi_rtk import BaseApi, expose, login_required, protect

    class MyApi(BaseApi):
        resource_name = "my_resource"

        @expose('/public', methods=['GET'])
        async def hello_world(self):
            return {"message": "Hello, World!"}

        @expose('/public_with_params', methods=['GET'])
        async def hello_with_params(self, name: str):
            return {"message": f"Hello, {name}!"}

        @expose('/private', methods=['GET'])
        @login_required
        async def private_hello(self):
            return {"message": "Hello, Private World!"}

        @expose('/users_with_get_permission', methods=['GET'])
        @protect()
        @permission_name('get')
        async def get_users(self):
            return {"users": ["Alice", "Bob", "Charlie"]}
    ```
    """

    version = "v1"
    """
    Version for the API. Defaults to "v1".
    """
    resource_name = lazy(lambda self: self.__class__.__name__.lower())
    """
    The name of the resource. If not given, will use the class name.
    """
    description = ""
    """
    Description for the API. Will be used for the API documentation via `fastapi-rtk export api-docs`.
    """
    base_permissions: list[str] | None = None
    """
    List of base permissions for the API. Defaults to None.

    Example:
        base_permissions = ["can_get", "can_post"]
    """
    permissions: list[str] = lazy(lambda self: [])
    """
    List of permissions for the API.

    DO NOT MODIFY UNLESS YOU KNOW WHAT YOU ARE DOING.
    """
    messages: list[str] = lazy(lambda self: [])
    """
    List of messages to log when the API is added to the toolkit.

    DO NOT MODIFY UNLESS YOU KNOW WHAT YOU ARE DOING.
    """
    toolkit: "FastAPIReactToolkit" = None
    """
    The FastAPIReactToolkit object. Automatically set when the API is added to the toolkit.
    """
    cache: Dict[str, Any] = lazy(lambda self: dict())
    """
    The cache for the API.
    
    DO NOT MODIFY.
    """
    router = lazy(
        lambda self: APIRouter(
            prefix=f"/api/{self.version}/{self.resource_name}",
            tags=[self.__class__.__name__],
        )
    )
    """
    The FastAPI router object.

    DO NOT MODIFY UNLESS YOU KNOW WHAT YOU ARE DOING.
    """

    def __init__(self):
        """
        If you override this method, make sure to call `super().__init__()` at the end.
        """
        self._initialize_router()

    async def on_startup(self):
        """
        Method to run on startup.

        This will be called by `FastAPIReactToolkit` when the application starts.
        """
        pass

    async def on_shutdown(self):
        """
        Method to run on shutdown.

        This will be called by `FastAPIReactToolkit` when the application shuts down.
        """
        pass

    def integrate_router(self, app: APIRouter):
        """
        Integrates the router into the FastAPI app.

        Args:
            app (APIRouter): The FastAPI app.
        """
        for message in self.messages:
            logger.info(message)
        app.include_router(self.router)

    def _initialize_router(self):
        """
        Initializes the router for the API. This method is called automatically when the API is initialized.
        """
        ROUTE_SUFFIX = "_headless"
        priority_routes = []
        routes = [f"{x}{ROUTE_SUFFIX}" for x in getattr(self, "routes", [])]
        for attr_name in [x for x in dir(self) if not o_lazy.is_lazy(self, x)]:
            if attr_name.endswith(ROUTE_SUFFIX) and attr_name not in routes:
                continue

            attr = getattr(self, attr_name)
            if hasattr(attr, "_permission_name"):
                permission_name = getattr(attr, "_permission_name")
                permission_name_with_prefix = f"{PERMISSION_PREFIX}{permission_name}"

                if not self._is_in_base_permissions(permission_name):
                    continue

                self.permissions.append(permission_name_with_prefix)

            if hasattr(attr, "_url"):
                data = attr._url
                if hasattr(attr, "_response_model_str"):
                    data["response_model"] = getattr(self, attr._response_model_str)

                extra_dependencies = []
                if hasattr(attr, "_dependencies"):
                    extra_dependencies = attr._dependencies
                if extra_dependencies and not data.get("dependencies"):
                    data["dependencies"] = []
                for dep in extra_dependencies:
                    func, kwargs = dep
                    if kwargs:
                        for key, val in kwargs.items():
                            if val == ":self":
                                kwargs[key] = self
                            elif val.startswith(":f"):
                                prop = val.split(".")[1]
                                kwargs[key] = getattr(attr, prop)
                        func = Depends(func(**kwargs))
                    else:
                        func = Depends(func)
                    data["dependencies"].append(func)

                path, methods, rest_data = (
                    data["path"],
                    data["methods"],
                    {k: v for k, v in data.items() if k != "methods"},
                )

                self.messages.append(
                    f"Registering route {self.router.prefix}{path} {methods}"
                )

                for method in methods:
                    method = method.lower()
                    router_func = getattr(self.router, method)

                    priority = getattr(attr, "_priority", None)

                    # If it is a bound method of a class, get the function
                    if hasattr(attr, "__func__"):
                        attr = attr.__func__

                    #! Update self parameter in the function signature, so that self is not treated as a parameter
                    attr = update_signature(self, attr)

                    if priority is not None:
                        priority_routes.append((priority, router_func, rest_data, attr))
                        continue

                    # Add the route to the router
                    router_func(**rest_data)(attr)

        # Sort the priority routes by priority
        priority_routes.sort(key=lambda x: x[0], reverse=True)

        # Add the priority routes to the router
        for _, router_func, rest_data, attr in priority_routes:
            router_func(**rest_data)(attr)

    def _is_in_base_permissions(self, permission: str):
        """
        Check if the permission is in the `base_permissions`.

        If the `base_permissions` are not set, it will return True.

        Args:
            permission (str): The permission to check.

        Returns:
            bool: True if the permission is in the `base_permissions` or if the `base_permissions` are not set, False otherwise.
        """
        return (
            f"{PERMISSION_PREFIX}{permission}" in self.base_permissions
            if self.base_permissions
            else True
        )
