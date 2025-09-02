import typing

__all__ = ["class_factory_from_dict"]


def class_factory_from_dict(
    class_name: str, base_classes: tuple = (object,), **kwargs: typing.Any
):
    """
    Create a class dynamically from a dictionary of attributes.

    Args:
        class_name (str): The name of the class to be created.
        base_classes (tuple): A tuple of base classes for the new class.
        **kwargs: Keyword arguments representing attributes of the class.

    Returns:
        type: A new class type with the specified name and attributes.
    """
    return type(class_name, base_classes, kwargs)
