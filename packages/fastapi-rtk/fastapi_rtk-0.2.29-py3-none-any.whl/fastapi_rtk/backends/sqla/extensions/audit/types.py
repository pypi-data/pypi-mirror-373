import enum
import typing

from .....schemas import PRIMARY_KEY
from ...model import Model

__all__ = ["SQLAModel", "AuditOperation", "AuditEntry"]

SQLAModel = typing.TypeVar("SQLAModel", bound=Model)


class AuditOperation(str, enum.Enum):
    """
    Enum representing the type of audit operation performed on a SQLAlchemy model.
    """

    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"


class AuditEntry(typing.TypedDict):
    """
    Represents an audit entry for a SQLAlchemy model.
    """

    model: SQLAModel
    operation: AuditOperation
    pk: PRIMARY_KEY
    data: dict[str, typing.Any] | None
    updates: dict[str, typing.Any] | None
