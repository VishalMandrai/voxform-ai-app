"""
ORM models for the auth/org domain.

Three entities:
  - Organization: the tenant. Forms/responses are scoped to one of these.
  - User: belongs to exactly one Organization, has a Role.
  - InviteToken: a one-time token an org admin generates to bring a new
    user (admin or respondent) into their org. There is no public
    signup endpoint — every account starts from an accepted invite,
    except the very first org+admin pair, which only a seed script can
    create (see scripts/seed_org.py).
"""

import enum
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Role(str, enum.Enum):
    ORG_ADMIN = "org_admin"
    RESPONDENT = "respondent"


def _role_column():
    """
    A Role column that stores the lowercase `.value` ("org_admin") rather
    than SQLAlchemy's default of the member NAME ("ORG_ADMIN").

    Without `values_callable`, SQLAlchemy's Enum type persists
    `Role.ORG_ADMIN.name`, which would silently diverge from the
    lowercase value used everywhere else (JWT claims, JSON responses,
    Pydantic schemas) — harmless as long as only this app ever reads the
    column back through SQLAlchemy, but a real foot-gun for any direct
    SQL (analytics queries in Phase 3, manual debugging, another
    service reading the same table).
    """
    return mapped_column(Enum(Role, values_callable=lambda enum_cls: [member.value for member in enum_cls]), nullable=False)


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    users: Mapped[list["User"]] = relationship(back_populates="organization")

    def __init__(self, **kwargs) -> None:
        """Assign id eagerly so the object is valid before any DB insert/flush (see forms.models.Form)."""
        kwargs.setdefault("id", str(uuid.uuid4()))
        kwargs.setdefault("created_at", _utcnow())
        super().__init__(**kwargs)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = _role_column()
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    organization: Mapped["Organization"] = relationship(back_populates="users")

    def __init__(self, **kwargs) -> None:
        kwargs.setdefault("id", str(uuid.uuid4()))
        kwargs.setdefault("created_at", _utcnow())
        kwargs.setdefault("is_active", True)
        super().__init__(**kwargs)


class InviteToken(Base):
    """
    A single-use, expiring token an org admin issues for a specific
    email + role within their org. Accepting it (with a chosen password)
    creates the User and consumes the token.
    """

    __tablename__ = "invite_tokens"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    token: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = _role_column()
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    def __init__(self, **kwargs) -> None:
        kwargs.setdefault("id", str(uuid.uuid4()))
        kwargs.setdefault("token", uuid.uuid4().hex)
        kwargs.setdefault("created_at", _utcnow())
        kwargs.setdefault("expires_at", _utcnow() + timedelta(days=7))
        super().__init__(**kwargs)

    @property
    def is_expired(self) -> bool:
        expires = self.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=UTC)
        return _utcnow() > expires

    @property
    def is_accepted(self) -> bool:
        return self.accepted_at is not None
