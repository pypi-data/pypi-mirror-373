__all__ = ["ExtenderMixin"]


class ExtenderMixin:
    """
    A utility class that can be used to extend the attributes of the parent classes.

    When a class inherits from this class, it will take all the non-private attributes of the child class and add them to the parent classes.

    Can also be combined with a class that is a subclass of `Model` from `fastapi_rtk.model` to add new columns when modifying the actual class is not possible.

    ### Example:

    ```python
    class Parent:
        parent_attr = "parent"

    class Child(ExtendingModel, Parent):
        child_attr = "child"

    print(Parent.parent_attr)  # Output: "parent"
    print(Parent.child_attr)  # Output: "child"
    ```
    """

    def __init_subclass__(cls) -> None:
        if ExtenderMixin in cls.__bases__:
            copy_vars = {
                k: v
                for k, v in vars(cls).items()
                if not k == "__module__" and not k == "__doc__"
            }
            cls._extend_parents(**copy_vars)
        return super().__init_subclass__()

    @classmethod
    def _extend_parents(cls, **kwargs):
        for base in cls.__bases__:
            if base is ExtenderMixin:
                continue
            for k, v in kwargs.items():
                setattr(base, k, v)
            if hasattr(base, "_extend_parents"):
                base._extend_parents(**kwargs)
