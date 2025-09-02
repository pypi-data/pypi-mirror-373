from typing import Optional

from fastapi_users.password import PasswordHelper
from pwdlib import PasswordHash

from ..hashers import PBKDF2Hasher, ScryptHasher

__all__ = ["FABPasswordHelper"]


class FABPasswordHelper(PasswordHelper):
    """
    Helper class for old version of password-related operations in the FAB React Toolkit.

    Args:
        password_hash (Optional[PasswordHash]): An optional `PasswordHash` object to use for password hashing.

    Attributes:
        password_hash (PasswordHash): The `PasswordHash` object used for password hashing.

    """

    def __init__(self, password_hash: Optional[PasswordHash] = None) -> None:
        if password_hash is None:
            self.password_hash = PasswordHash(
                (
                    ScryptHasher(),
                    PBKDF2Hasher(),
                )
            )
        else:
            self.password_hash = password_hash  # pragma: no cover
