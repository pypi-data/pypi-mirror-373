import typing

from pwdlib.hashers import HasherProtocol
from pwdlib.hashers.base import ensure_str

from .utils import check_password_hash, generate_password_hash

__all__ = ["PBKDF2Hasher"]


class PBKDF2Hasher(HasherProtocol):
    @classmethod
    def identify(cls, hash: typing.Union[str, bytes]) -> bool:
        return ensure_str(hash).startswith("pbkdf2")

    def hash(
        self,
        password: typing.Union[str, bytes],
        *,
        salt: typing.Union[bytes, None] = None,
    ) -> str:
        return generate_password_hash(password, method="pbkdf2")

    def verify(
        self,
        password: typing.Union[str, bytes],
        hash: typing.Union[str, bytes],
    ) -> bool:
        try:
            return check_password_hash(hash, password)
        except Exception:
            return False

    def check_needs_rehash(self, hash: typing.Union[str, bytes]) -> bool:
        return False
