import typing

__all__ = ["prettify_dict"]


def prettify_dict(d: typing.Dict[str, typing.Any], indent: int = 0) -> str:
    """
    Prettify a dictionary to a string.

    Args:
        d (Dict[str, Any]): The dictionary to be prettified.
        indent (int, optional): The number of spaces to indent each level. Defaults to 0.

    Returns:
        str: The prettified dictionary as a string.
    """
    result = ""
    for key, value in d.items():
        result += " " * indent + f"{key}: "
        if isinstance(value, dict):
            result += "\n" + prettify_dict(value, indent + 2)
        else:
            result += f"{value}\n"
    return result
