"""
JWT issuing/verification.

`TokenIssuer` is the abstraction. `JWTTokenIssuer` is the concrete
implementation using PyJWT. Kept separate from AuthService so the
choice of token format (JWT vs opaque session id vs PASETO) can change
without touching login/invite-acceptance business logic.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from app.auth.models import Role
from app.core.exceptions import ValidationError, SessionExpired


@dataclass(frozen=True)
class TokenPayload:
    user_id: str
    org_id: str
    role: Role


class TokenIssuer(ABC):
    @abstractmethod
    def issue(self, payload: TokenPayload) -> str: ...

    @abstractmethod
    def verify(self, token: str) -> TokenPayload: ...


class JWTTokenIssuer(TokenIssuer):
    def __init__(self, secret_key: str, algorithm: str = "HS256", expires_minutes: int = 60 * 24 * 7) -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._expires_minutes = expires_minutes

    def issue(self, payload: TokenPayload) -> str:
        import jwt                                      # imported lazily

        now = datetime.now(UTC)
        claims = {
            "sub": payload.user_id,
            "org_id": payload.org_id,
            "role": payload.role.value,
            "iat": now,
            "exp": now + timedelta(minutes=self._expires_minutes),
        }
        return jwt.encode(claims, self._secret_key, algorithm=self._algorithm)

    def verify(self, token: str) -> TokenPayload:
        import jwt  # imported lazily

        try:
            claims = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
        except jwt.PyJWTError as exc:
            raise SessionExpired("Invalid or expired session token") from exc

        try:
            return TokenPayload(
                user_id=claims["sub"],
                org_id=claims["org_id"],
                role=Role(claims["role"]),
            )
        except (KeyError, ValueError) as exc:
            raise ValidationError("Malformed session token") from exc
