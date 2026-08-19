import pytest

from app.auth.models import InviteToken, Organization, Role, User
from app.auth.schemas import InviteCreate
from app.auth.service import AuthService
from app.core.exceptions import NotFoundError, ValidationError
from tests.fakes import (
    FakeInviteTokenRepository,
    FakeOrganizationRepository,
    FakePasswordHasher,
    FakeTokenIssuer,
    FakeUserRepository,
)


def make_service():
    users = FakeUserRepository()
    invites = FakeInviteTokenRepository()
    orgs = FakeOrganizationRepository()
    hasher = FakePasswordHasher()
    tokens = FakeTokenIssuer()
    service = AuthService(users, invites, orgs, hasher, tokens)
    return service, users, invites, orgs, hasher


def seed_org_and_admin(users, orgs, hasher, email="admin@acme.com", password="secret123"):
    """Mirrors what scripts/seed_org.py does — the only sanctioned way to create an org."""
    org = orgs.create(Organization(name="Acme"))
    admin = users.create(
        User(
            org_id=org.id,
            email=email,
            hashed_password=hasher.hash(password),
            full_name="Admin Person",
            role=Role.ORG_ADMIN,
        )
    )
    return org, admin


def test_login_with_valid_credentials_returns_token():
    service, users, _invites, orgs, hasher = make_service()
    seed_org_and_admin(users, orgs, hasher, email="admin@acme.com", password="secret123")

    token = service.login("admin@acme.com", "secret123")

    assert token is not None
    user = service.get_current_user(token)
    assert user.email == "admin@acme.com"
    assert user.role == Role.ORG_ADMIN


def test_login_with_wrong_password_raises():
    service, users, _invites, orgs, hasher = make_service()
    seed_org_and_admin(users, orgs, hasher, email="admin@acme.com", password="secret123")

    with pytest.raises(ValidationError, match="Invalid email or password"):
        service.login("admin@acme.com", "wrong-password")


def test_login_with_unknown_email_raises():
    service, *_ = make_service()
    with pytest.raises(ValidationError, match="Invalid email or password"):
        service.login("nobody@nowhere.com", "whatever")


def test_login_with_inactive_user_raises():
    service, users, _invites, orgs, hasher = make_service()
    _org, admin = seed_org_and_admin(users, orgs, hasher)
    admin.is_active = False

    with pytest.raises(ValidationError, match="Invalid email or password"):
        service.login("admin@acme.com", "secret123")


def test_org_admin_can_create_invite():
    service, users, invites, orgs, hasher = make_service()
    org, admin = seed_org_and_admin(users, orgs, hasher)

    invite = service.create_invite(
        org.id, admin, InviteCreate(email="new@acme.com", full_name="New Person", role=Role.RESPONDENT)
    )

    assert invite.email == "new@acme.com"
    assert invite.role == Role.RESPONDENT
    assert invites.get_by_token(invite.token) is not None


def test_respondent_cannot_create_invite():
    service, users, _invites, orgs, hasher = make_service()
    org, _admin = seed_org_and_admin(users, orgs, hasher)
    respondent = users.create(
        User(
            org_id=org.id,
            email="respondent@acme.com",
            hashed_password=hasher.hash("pw"),
            full_name="Respondent Person",
            role=Role.RESPONDENT,
        )
    )

    with pytest.raises(ValidationError, match="Only an org admin"):
        service.create_invite(
            org.id, respondent, InviteCreate(email="x@acme.com", full_name="X", role=Role.RESPONDENT)
        )


def test_cannot_invite_an_email_that_already_has_an_account():
    service, users, _invites, orgs, hasher = make_service()
    org, admin = seed_org_and_admin(users, orgs, hasher, email="admin@acme.com")

    with pytest.raises(ValidationError, match="already exists"):
        service.create_invite(
            org.id, admin, InviteCreate(email="admin@acme.com", full_name="Dup", role=Role.RESPONDENT)
        )


def test_accept_invite_creates_user_with_invited_role_and_name():
    service, users, invites, orgs, hasher = make_service()
    org, admin = seed_org_and_admin(users, orgs, hasher)
    invite = service.create_invite(
        org.id, admin, InviteCreate(email="new@acme.com", full_name="New Person", role=Role.RESPONDENT)
    )

    token = service.accept_invite(invite.token, "brandnewpassword")

    user = service.get_current_user(token)
    assert user.email == "new@acme.com"
    assert user.full_name == "New Person"
    assert user.role == Role.RESPONDENT
    assert user.org_id == org.id


def test_accept_invite_twice_raises():
    service, users, invites, orgs, hasher = make_service()
    org, admin = seed_org_and_admin(users, orgs, hasher)
    invite = service.create_invite(
        org.id, admin, InviteCreate(email="new@acme.com", full_name="New Person", role=Role.RESPONDENT)
    )
    service.accept_invite(invite.token, "brandnewpassword")

    with pytest.raises(ValidationError, match="already been used"):
        service.accept_invite(invite.token, "anotherpassword")


def test_accept_expired_invite_raises():
    service, users, invites, orgs, hasher = make_service()
    org, admin = seed_org_and_admin(users, orgs, hasher)

    from datetime import UTC, datetime, timedelta

    expired_invite = invites.create(
        InviteToken(
            org_id=org.id,
            email="late@acme.com",
            full_name="Late Person",
            role=Role.RESPONDENT,
            expires_at=datetime.now(UTC) - timedelta(days=1),
        )
    )

    with pytest.raises(ValidationError, match="expired"):
        service.accept_invite(expired_invite.token, "somepassword")


def test_accept_nonexistent_invite_raises_not_found():
    service, *_ = make_service()
    with pytest.raises(NotFoundError):
        service.accept_invite("does-not-exist", "somepassword")


def test_list_org_users_only_returns_that_org():
    service, users, _invites, orgs, hasher = make_service()
    org_a, _admin_a = seed_org_and_admin(users, orgs, hasher, email="admin-a@acme.com")
    org_b, _admin_b = seed_org_and_admin(users, orgs, hasher, email="admin-b@other.com")

    users_a = service.list_org_users(org_a.id)
    users_b = service.list_org_users(org_b.id)

    assert {u.email for u in users_a} == {"admin-a@acme.com"}
    assert {u.email for u in users_b} == {"admin-b@other.com"}
