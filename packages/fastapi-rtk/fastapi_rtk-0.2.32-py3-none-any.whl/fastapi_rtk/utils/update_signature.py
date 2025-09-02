import inspect
import types

import fastapi

from .self_dependencies import SelfDepends, SelfType

__all__ = ["update_signature"]


def update_signature(cls, f):
    """
    Copy a function and update its signature to include the class instance as the first parameter instead of string "self" for FastAPI Route Dependencies.

    It also replaces SelfDepends and SelfType with the actual value.

    Args:
        f (Callable): The function to be updated.
    Returns:
        Callable: The updated function.
    """
    # Get the function's parameters
    old_signature = inspect.signature(f)
    old_parameters = list(old_signature.parameters.values())
    if not old_parameters:
        return f
    old_first_parameter, *old_parameters = old_parameters

    # If the first parameter is self, replace it
    if old_first_parameter.name == "self":
        new_first_parameter = old_first_parameter.replace(
            default=fastapi.Depends(lambda: cls)
        )

        new_parameters = [new_first_parameter]
        for parameter in old_parameters:
            parameter = parameter.replace(kind=inspect.Parameter.KEYWORD_ONLY)
            if isinstance(parameter.default, SelfDepends):
                parameter = parameter.replace(default=parameter.default(cls))
            elif isinstance(parameter.default, SelfType):
                parameter = parameter.replace(
                    annotation=parameter.default(cls),
                    default=(
                        fastapi.Depends()
                        if parameter.default.depends
                        else inspect.Parameter.empty
                    ),
                )
            new_parameters.append(parameter)

        new_signature = old_signature.replace(parameters=new_parameters)

        # Copy the function to avoid modifying the original
        f = copy_function(f)

        setattr(
            f, "__signature__", new_signature
        )  # Set the new signature to the function

    return f


def copy_function(f):
    """Copy a function."""
    return types.FunctionType(
        f.__code__,
        f.__globals__,
        name=f.__name__,
        argdefs=f.__defaults__,
        closure=f.__closure__,
    )
