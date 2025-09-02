import typing

import sqlalchemy
from sqlalchemy import types as sa_types

__all__ = ["is_sqla_type"]


def is_sqla_type(
    col: sqlalchemy.Column, sa_type: typing.Type[sa_types.TypeEngine]
) -> bool:
    """
    Check if the column is an instance of the given SQLAlchemy type.

    Args:
        col (Column): The SQLAlchemy Column to check.
        sa_type (Type[sa_types.TypeEngine]): The SQLAlchemy type to check against.

    Returns:
        bool: True if the column is an instance of the given SQLAlchemy type, False otherwise.
    """
    return (
        isinstance(col, sa_type)
        or isinstance(col, sa_types.TypeDecorator)
        and isinstance(col.impl, sa_type)
    )
