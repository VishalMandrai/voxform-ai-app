"""
Password hashing.

`PasswordHasher` is the abstraction; `BcryptPasswordHasher` is today's
implementation. AuthService depends on the interface, so switching to
argon2 later (or using a different hasher in tests) is a new class, not
a rewrite of AuthService.
"""

from abc import ABC, abstractmethod


class PasswordHasher(ABC):
    @abstractmethod
    def hash(self, plain_password: str) -> str: ...

    @abstractmethod
    def verify(self, plain_password: str, hashed_password: str) -> bool: ...


class BcryptPasswordHasher(PasswordHasher):
    def __init__(self) -> None:
        import bcrypt  # imported lazily: keeps this module importable without the dependency installed

        self._bcrypt = bcrypt

    def hash(self, plain_password: str) -> str:
        salt = self._bcrypt.gensalt()
        return self._bcrypt.hashpw(plain_password.encode("utf-8"), salt).decode("utf-8")

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        try:
            return self._bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
        except ValueError:
            # Malformed hash (e.g. corrupted data) — treat as a failed verification, not a crash.
            return False
