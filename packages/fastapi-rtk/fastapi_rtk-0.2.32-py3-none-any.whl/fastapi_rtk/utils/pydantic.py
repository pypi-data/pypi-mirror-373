import typing

import pydantic

__all__ = ["generate_schema_from_typed_dict"]


def generate_schema_from_typed_dict(typed_dict: type):
    """
    Generate a Pydantic model schema from a TypedDict.
    Args:
        typed_dict (type): A type that is a subclass of dict, typically a TypedDict.
    Returns:
        BaseModel: A Pydantic model generated from the TypedDict.
    Raises:
        TypeError: If the provided typed_dict is not a type or not a subclass of dict.
    """
    if not isinstance(typed_dict, type) or not issubclass(typed_dict, dict):
        raise TypeError("typed_dict must be a type that is a subclass of dict")

    fields = {}
    for key, val in typed_dict.__annotations__.items():
        if getattr(val, "__origin__", None) is typing.NotRequired:
            fields[key] = (val.__args__[0], pydantic.Field(None))
        else:
            fields[key] = (val, pydantic.Field(...))
    return pydantic.create_model(typed_dict.__name__, **fields)
