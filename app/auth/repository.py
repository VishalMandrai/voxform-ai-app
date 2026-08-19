"""
Persistence layer for the auth/org domain.

Three small repositories, one per entity, each behind its own abstract
interface — kept separate rather than one giant "AuthRepository" so a
caller that only needs user lookups (e.g. a future audit-log feature)
can depend on just `UserRepository` without pulling in invite or org
persistence it doesn't use (interface segregation).
"""

from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from app.auth.models import InviteToken, Organization, User
from app.auth.schemas import InviteStats


class OrganizationRepository(ABC):
    @abstractmethod
    def create(self, organization: Organization) -> Organization: ...

    @abstractmethod
    def get_by_id(self, org_id: str) -> Organization | None: ...


class UserRepository(ABC):
    @abstractmethod
    def create(self, user: User) -> User: ...

    @abstractmethod
    def get_by_id(self, user_id: str) -> User | None: ...

    @abstractmethod
    def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    def list_for_org(self, org_id: str) -> list[User]: ...


class InviteTokenRepository(ABC):
    @abstractmethod
    def create(self, invite: InviteToken) -> InviteToken: ...

    @abstractmethod
    def get_by_token(self, token: str) -> InviteToken | None: ...

    @abstractmethod
    def mark_accepted(self, invite: InviteToken) -> InviteToken: ...


class MySQLOrganizationRepository(OrganizationRepository):
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, organization: Organization) -> Organization:
        self._db.add(organization)
        self._db.commit()
        self._db.refresh(organization)
        return organization

    def get_by_id(self, org_id: str) -> Organization | None:
        return self._db.query(Organization).filter(Organization.id == org_id).first()


class MySQLUserRepository(UserRepository):
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, user: User) -> User:
        self._db.add(user)
        self._db.commit()
        self._db.refresh(user)
        return user

    def get_by_id(self, user_id: str) -> User | None:
        return self._db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> User | None:
        return self._db.query(User).filter(User.email == email).first()

    def list_for_org(self, org_id: str) -> list[User]:
        return self._db.query(User).filter(User.org_id == org_id).all()


class MySQLInviteTokenRepository(InviteTokenRepository):
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, invite: InviteToken) -> InviteToken:
        self._db.add(invite)
        self._db.commit()
        self._db.refresh(invite)
        return invite

    def get_by_token(self, token: str) -> InviteToken | None:
        return self._db.query(InviteToken).filter(InviteToken.token == token).first()
    
    def all_invites(self, org_id: str) -> InviteStats:
        total_invites = len(self._db.query(InviteToken).filter(InviteToken.org_id == org_id).all())
        return InviteStats(total_invites=total_invites, org_id=org_id)

    def mark_accepted(self, invite: InviteToken) -> InviteToken:
        from datetime import UTC, datetime

        invite.accepted_at = datetime.now(UTC)
        self._db.commit()
        self._db.refresh(invite)
        return invite
