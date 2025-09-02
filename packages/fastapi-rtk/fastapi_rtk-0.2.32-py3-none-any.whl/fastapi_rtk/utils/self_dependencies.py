import fastapi

__al__ = ["SelfDepends", "SelfType"]


class BaseSelf:
    attr: str | None = None
    ignored_keys: list[str] = None

    def __init__(self):
        self.ignored_keys = ["attr", "__class__"]

    def __getattribute__(self, name: str):
        # Special handling for when name is "ignored_keys" or in self.ignored_keys
        if name == "ignored_keys" or name in self.ignored_keys:
            return super().__getattribute__(name)

        # If attr is not set, set attr to the attribute name
        curr_attr = self.attr
        if curr_attr is None:
            curr_attr = ""
        curr_attr += f".{name}" if curr_attr else name
        self.attr = curr_attr

        return self

    def __call__(self, cls):
        split = self.attr.split(".")
        result = None
        for attr in split:
            result = getattr(result or cls, attr)
        return result


class SelfDepends(BaseSelf):
    """
    A class that can be used to create a dependency that depends on the class instance.

    Sometimes you need to create a dependency that requires the class instance to be passed as a parameter when using Depends() from FastAPI. This class can be used to create such dependencies.

    ### Example:

    ```python
        class MyApi:
            @expose("/my_endpoint")
            def my_endpoint(self, permissions: List[str] = SelfDepends().get_current_permissions):
                # Do something
                pass

            def get_current_permissions(self):
                # Do something that requires the class instance, and should returns a function that can be used as a dependency
                pass
    ```

    is equivalent to:

    ```python
        # self. is actually not possible here, that's why we use the string representation of the attribute
        class MyApi:
            @expose("/my_endpoint")
            def my_endpoint(self, permissions: List[str] = Depends(self.get_current_permissions)):
                # Do something
                pass

            def get_current_permissions(self):
                # Do something that requires the class instance, and should returns a function that can be used as a dependency
                pass
    ```
    """

    args = None
    kwargs = None

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.ignored_keys.append("args")
        self.ignored_keys.append("kwargs")
        self.args = args or ()
        self.kwargs = kwargs or {}

    def __call__(self, cls):
        result = super().__call__(cls)
        return fastapi.Depends(result(*self.args, **self.kwargs))


class SelfType(BaseSelf):
    """
    A class that can be used to create a dependency that depends on the class instance.

    Sometimes you need to create a type that depends on the class instance. This class can be used to create such types.

    ### Example:

    ```python
        class MyApi:
            @expose("/my_endpoint")
            def my_endpoint(self, schema: BaseModel = SelfType().datamodel.obj.schema):
                # Do something
                pass

            @expose("/my_other_endpoint")
            def my_other_endpoint(self, schema: BaseModel = SelfType.with_depends().datamodel.obj.schema):
                # Do something
                pass
    ```

    is equivalent to:

    ```python
        # self. is actually not possible here, that's why we use the string representation of the attribute
        class MyApi:
            @expose("/my_endpoint")
            def my_endpoint(self, schema: self.datamodel.obj.schema):
                # Do something
                pass

            @expose("/my_other_endpoint")
            def my_other_endpoint(self, schema: self.datamodel.obj.schema = Depends()):
                # Do something
                pass
    ```
    """

    depends = False

    def __init__(self, depends: bool = False):
        super().__init__()
        self.ignored_keys.append("depends")
        self.depends = depends
        self.attr = None

    @classmethod
    def with_depends(cls):
        return cls(depends=True)
