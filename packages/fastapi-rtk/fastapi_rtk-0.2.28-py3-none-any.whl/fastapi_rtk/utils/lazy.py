import functools
import importlib
import inspect
import types
import typing

T = typing.TypeVar("T")
C = typing.TypeVar("C")

__all__ = ["lazy", "lazy_import", "lazy_self"]


class lazy(typing.Generic[T]):
    """
    A descriptor that lazily evaluates a function and caches the result.

    This is useful for lazy loading of attributes in classes, where the value is computed only when accessed for the first time.

    **Beware that setting the `only_instance` to `False` with `cache` set to `True` will cache the value on the class itself, resulting the value being shared across all instances of the class.**

    Example usage:
    ```python
    from fastapi_rtk import lazy

    class MyClass:
        @lazy
        def my_lazy_attribute(self):
            # This function will be called only once when the attribute is accessed
            return compute_heavy_value()

        my_second_lazy_attribute = lazy(lambda self: self.my_lazy_attribute + 1) # This will also be lazily evaluated, using the first lazy attribute
        my_third_lazy_attribute = lazy(lambda cls: cls.my_second_lazy_attribute + 2, cache=False) # This will not cache the result, so it will be recomputed every time it is accessed.
        my_fourth_lazy_attribute = lazy(lambda cls: cls.my_third_lazy_attribute + 3, only_instance=False) # This will also work on the class itself, not just on instances.

    my_instance = MyClass()
    print(my_instance.my_lazy_attribute)  # This will call the function and cache the result
    print(my_instance.my_second_lazy_attribute)  # This will also call the function and cache the result
    print(my_instance.my_third_lazy_attribute)  # This will call the function every time, since cache is False
    print(MyClass.my_fourth_lazy_attribute)  # This will also call the function and cache the result on the class itself
    print(my_instance.my_fourth_lazy_attribute)  # Since it has been cached on the class, it will return the cached value
    ```
    """

    _default_value = object()

    def __init__(
        self,
        func: typing.Callable[[], T] | typing.Callable[[C], T],
        *,
        cache=True,
        only_instance=True,
    ):
        """
        Initializes the lazy descriptor with a function to be lazily evaluated.

        Args:
            func (typing.Callable[[], T]): The function to be lazily evaluated. It can take no arguments or a single argument which is the instance of the class (or the class itself if `only_instance` is False).
            cache (bool, optional): Whether to cache the result of the lazy evaluation. If True, the result will be stored after the first evaluation and returned on subsequent accesses. Defaults to True.
            only_instance (bool, optional): Whether the lazy evaluation should only be applied to instance attributes. If True, the descriptor will only work on instance attributes and accessing it on the class itself will return the descriptor instead of evaluating the function. Defaults to True.
        """
        self.__func = func
        functools.wraps(self.__func, self)  # Preserve the original function's metadata
        self.__cache = cache
        self.__only_instance = only_instance
        self.__name__ = str(id(self.__func))  # will be set by __set_name__

    def __set_name__(self, owner: type, name: str):
        """
        Sets the name of the descriptor when it is assigned to a class.
        This is called by Python when the descriptor is assigned to a class attribute.
        """
        self.__name__ = name

    @typing.overload
    def __get__(self, instance: None, owner: type) -> typing.Self: ...
    @typing.overload
    def __get__(self, instance: object, owner: type) -> T: ...
    def __get__(self, instance: object | None, owner: type) -> T:
        """
        Retrieves the value of the lazy attribute from the instance or class.

        If the attribute is not yet computed, it will call the lazy function to compute it and store the result in the instance's `__dict__` if `cache` is True.
        """
        if instance is None:
            if self.__only_instance:
                return self
            target = owner
        else:
            target = instance

        name = self.__name__

        # If the name starts with "__" but does not end with "__", it is a private attribute
        # and we should prefix it with the owner's class name to avoid conflicts.
        if name.startswith("__") and not name.endswith("__"):
            name = f"_{owner.__name__}{name}"

        if not self.__cache:
            return self.call_function(target)

        # Check whether the obj has __dict__ attribute
        if not hasattr(target, "__dict__"):
            raise AttributeError(
                f"{target} does not have a __dict__ attribute, cannot cache lazy attribute {name}."
            )

        default_value = self._default_value if self.__only_instance else self
        value = target.__dict__.get(name, default_value)
        if value is default_value:
            value = self.call_function(target)
            if self.__only_instance:
                target.__dict__[name] = value
            else:
                setattr(owner, name, value)
        return value

    def __call__(self, *args, **kwds):
        """
        Allows the descriptor to be called as a function, returning the result of the lazy evaluation.
        """
        return self.__func(*args, **kwds)

    def call_function(self, target: object | type, *args, **kwargs):
        """
        Calls the lazy function with the target object or class as the first argument, followed by any additional arguments.

        Args:
            target (object | type): The target object or class to pass as the first argument to the lazy function.

        Returns:
            T: The result of the lazy function call.
        """
        params = inspect.signature(self.__func).parameters
        if len(params) == 0:
            return self(*args, **kwargs)
        else:
            return self(target, *args, **kwargs)

    @classmethod
    def is_lazy(cls, cls_or_instance: type | object, attr_name: str) -> bool:
        """
        Checks if the given attribute of the class or instance is a lazy descriptor.

        Args:
            cls_or_instance (type | object): The class or instance to check for the lazy attribute.
            attr_name (str): The name of the attribute to check.

        Returns:
            bool: True if the attribute is a lazy descriptor, False otherwise.
        """
        # Always check the class
        if not isinstance(cls_or_instance, type):
            cls_or_instance = type(cls_or_instance)
        try:
            lazy = inspect.getattr_static(cls_or_instance, attr_name)
            return isinstance(lazy, cls)
        except AttributeError:
            return False

    @classmethod
    def get_lazy(cls, cls_or_instance: type | object, attr_name: str) -> typing.Self:
        """
        Retrieves the lazy descriptor from the class or instance.

        Args:
            cls_or_instance (type | object): The class or instance to get the lazy attribute from.
            attr_name (str): The name of the attribute to retrieve.

        Raises:
            TypeError: If the attribute is not a lazy descriptor.
            AttributeError: If the attribute does not exist in the class or instance.

        Returns:
            typing.Self: The lazy descriptor if it exists and is of the correct type.
        """
        try:
            lazy = object.__getattribute__(cls_or_instance, attr_name)
            if not isinstance(lazy, cls):
                raise TypeError(
                    f"{attr_name} in {cls_or_instance} is not a '{cls.__name__}', but '{type(lazy).__name__}'."
                )
        except AttributeError:
            raise AttributeError(
                f"{cls_or_instance} does not have a lazy attribute named {attr_name}"
            )


class lazy_import(lazy[T]):
    """
    A descriptor that lazily imports a module or retrieves an attribute from a module.

    This is useful for deferring the import of a module until it is actually needed, which can help reduce startup time and memory usage and also avoid circular import issues.
    """

    def __init__(
        self,
        module_name: str,
        getter: str | typing.Callable[[types.ModuleType], T],
        *,
        cache=True,
        only_instance=True,
    ):
        """
        Initializes the lazy import descriptor with a module name and a getter function or attribute name.

        Args:
            module_name (str): The name of the module to be lazily imported.
            getter (str | typing.Callable[[types.ModuleType], T]): The name of the attribute to retrieve from the module, or a callable that takes the module as an argument and returns a value of type T.
            cache (bool, optional): Whether to cache the result of the lazy import. If True, the result will be stored after the first import and returned on subsequent accesses. Defaults to True.
            only_instance (bool, optional): Whether the lazy import should only be applied to instance attributes. If True, the descriptor will only work on instance attributes and accessing it on the class itself will return the descriptor instead of evaluating the import. Defaults to True.
        """

        def import_func() -> T:
            module = importlib.import_module(module_name)
            if isinstance(getter, str):
                return getattr(module, getter)
            else:
                return getter(module)

        super().__init__(import_func, cache=cache, only_instance=only_instance)


class lazy_self(lazy[T], typing.Generic[C, T]):
    """
    A wrapper around `lazy` that type hints the first argument as the class instance.

    **To get the correct type hinting, it is better to subclass this class like so:**
    ```python
    from fastapi_rtk import lazy_self
    class lazy(lazy_self["MyClass", T]): ...

    class MyClass:
        my_attr = lazy(lambda self: self.some_method()) # The self and my_attr will be correctly typed as MyClass and T respectively.
    """

    def __init__(
        self, func: typing.Callable[[C], T], *, cache=True, only_instance=True
    ):
        super().__init__(func, cache=cache, only_instance=only_instance)
