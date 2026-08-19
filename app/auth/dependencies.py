"""
Auth dependencies shared by every module's router.

`get_current_user` reads the session cookie, verifies the JWT, and
returns the User — this is the ONE place a router asks "who is making
this request?" `require_role` builds on it for role-gated routes.

Every other module's router depends on these functions, never on
AuthService internals — the auth module's only public surface for the
rest of the app is this file plus the schemas it returns.
"""

from fastapi import Cookie, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.jwt_handler import JWTTokenIssuer, TokenIssuer
from app.auth.models import Role, User
from app.auth.schemas import UserRead
from app.auth.password_hasher import BcryptPasswordHasher, PasswordHasher
from app.auth.repository import (
    InviteTokenRepository,
    MySQLInviteTokenRepository,
    MySQLOrganizationRepository,
    MySQLUserRepository,
    OrganizationRepository,
    UserRepository,
)
from app.auth.service import AuthService
from app.core.config import get_settings
from app.core.db import get_db
from app.core.exceptions import ValidationError, NotAuthenticatedUser, SessionExpired

SESSION_COOKIE_NAME = "voiceform_session"


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return MySQLUserRepository(db)


def get_invite_repository(db: Session = Depends(get_db)) -> InviteTokenRepository:
    return MySQLInviteTokenRepository(db)


def get_org_repository(db: Session = Depends(get_db)) -> OrganizationRepository:
    return MySQLOrganizationRepository(db)


def get_password_hasher() -> PasswordHasher:
    return BcryptPasswordHasher()


def get_token_issuer() -> TokenIssuer:
    settings = get_settings()
    return JWTTokenIssuer(secret_key=settings.jwt_secret_key, expires_minutes=settings.jwt_expires_minutes)


def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
    invite_repository: InviteTokenRepository = Depends(get_invite_repository),
    org_repository: OrganizationRepository = Depends(get_org_repository),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    token_issuer: TokenIssuer = Depends(get_token_issuer),
) -> AuthService:
    return AuthService(user_repository, invite_repository, org_repository, password_hasher, token_issuer)


def get_current_user(
    session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
    auth_service: AuthService = Depends(get_auth_service),
):
    if session_token is None:
        # print("No Token for authentication.")
        # raise HTTPException(status_code=401, detail="Not authenticated")
        raise NotAuthenticatedUser("Not authenticated")
        
    return auth_service.get_current_user(session_token)


def get_optional_current_user(
    session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
    auth_service: AuthService = Depends(get_auth_service),
) -> User | None:
    """For pages that render differently when logged in but don't require it."""
    if session_token is None:
        return None
    try:
        return auth_service.get_current_user(session_token)
    except ValidationError:
        return None


def require_role(*allowed_roles: Role) -> UserRead:
    """
    Dependency factory for role-gated routes.

    Usage: `Depends(require_role(Role.ORG_ADMIN))`. Kept as a factory
    rather than a fixed list of per-role dependencies so new roles don't
    require new functions — only new call sites.
    """

    def _check(current_user: UserRead = Depends(get_current_user)) -> UserRead:
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="You do not have permission to do this")
        
        return current_user

    return _check
