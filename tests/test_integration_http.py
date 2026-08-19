"""
Integration test for the full HTTP stack, Phase 2.

Goes through the real FastAPI app, real repositories (SQLAlchemy code
running against SQLite in-memory instead of MySQL — same code path),
and the real auth flow: login via /api/auth/login sets a real signed
JWT in a cookie on the TestClient, exactly as a browser would.

This is what proves the auth wiring (Depends(get_current_user),
require_role, org scoping) is correct end-to-end — the fake-backed unit
tests (test_auth_service.py, test_forms_service.py, etc.) intentionally
bypass FastAPI's dependency injection and routing entirely.
"""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.models import Organization, Role, User
from app.auth.password_hasher import BcryptPasswordHasher
from app.core.db import Base, get_db
from app.main import app

# Import models so Base.metadata knows about every table.
from app.auth import models as _auth_models  # noqa: F401
from app.forms import models as _forms_models  # noqa: F401
from app.responses import models as _responses_models  # noqa: F401


@pytest.fixture()
def db_session_factory():
    """Builds the SQLite-backed session factory and overrides get_db with it."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db() -> Generator:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestingSessionLocal
    app.dependency_overrides.clear()


def _seed_org_admin(session_factory, org_name: str, email: str, password: str) -> tuple[str, str]:
    """Mirrors scripts/seed_org.py — returns (org_id, user_id)."""
    db = session_factory()
    try:
        hasher = BcryptPasswordHasher()
        org = Organization(name=org_name)
        db.add(org)
        db.commit()
        db.refresh(org)

        admin = User(
            org_id=org.id,
            email=email,
            hashed_password=hasher.hash(password),
            full_name="Admin Person",
            role=Role.ORG_ADMIN,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        return org.id, admin.id
    finally:
        db.close()


@pytest.fixture()
def client(db_session_factory) -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def admin_client(client: TestClient, db_session_factory) -> TestClient:
    """A TestClient already logged in as an org admin for 'Acme'."""
    _seed_org_admin(db_session_factory, "Acme", "admin@acme.com", "secret123")
    login_response = client.post(
        "/api/auth/login", json={"email": "admin@acme.com", "password": "secret123"}
    )
    assert login_response.status_code == 200
    return client


def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_unauthenticated_request_to_protected_route_returns_401(client: TestClient):
    response = client.get("/api/forms")
    assert response.status_code == 401


def test_login_with_wrong_password_returns_401(client: TestClient, db_session_factory):
    _seed_org_admin(db_session_factory, "Acme", "admin@acme.com", "secret123")
    response = client.post("/api/auth/login", json={"email": "admin@acme.com", "password": "wrong"})
    assert response.status_code == 401


def test_login_sets_cookie_and_me_endpoint_works(admin_client: TestClient):
    response = admin_client.get("/api/auth/me")
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "admin@acme.com"
    assert body["role"] == "org_admin"


def test_create_and_fetch_form(admin_client: TestClient):
    payload = {
        "title": "Household survey",
        "description": "Annual census",
        "fields": [
            {"label": "Full name", "field_type": "text", "is_required": True, "options": []},
            {
                "label": "Housing type",
                "field_type": "choice",
                "is_required": True,
                "options": ["Owned", "Rented"],
            },
        ],
    }

    create_response = admin_client.post("/api/forms", json=payload)
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["title"] == "Household survey"
    assert len(created["fields"]) == 2

    form_id = created["id"]
    fetch_response = admin_client.get(f"/api/forms/{form_id}")
    assert fetch_response.status_code == 200
    assert fetch_response.json()["id"] == form_id


def test_get_nonexistent_form_returns_404(admin_client: TestClient):
    response = admin_client.get("/api/forms/does-not-exist")
    assert response.status_code == 404


def test_list_forms_returns_created_forms(admin_client: TestClient):
    admin_client.post(
        "/api/forms",
        json={"title": "A", "fields": [{"label": "x", "field_type": "text", "is_required": True, "options": []}]},
    )
    admin_client.post(
        "/api/forms",
        json={"title": "B", "fields": [{"label": "y", "field_type": "text", "is_required": True, "options": []}]},
    )

    response = admin_client.get("/api/forms")
    assert response.status_code == 200
    titles = {f["title"] for f in response.json()}
    assert titles == {"A", "B"}


def test_submit_response_end_to_end(admin_client: TestClient):
    create_response = admin_client.post(
        "/api/forms",
        json={
            "title": "Survey",
            "fields": [
                {"label": "Name", "field_type": "text", "is_required": True, "options": []},
                {
                    "label": "Housing type",
                    "field_type": "choice",
                    "is_required": True,
                    "options": ["Owned", "Rented"],
                },
            ],
        },
    )
    form = create_response.json()
    name_field, housing_field = form["fields"]

    submit_response = admin_client.post(
        f"/api/forms/{form['id']}/responses",
        json={
            "answers": [
                {"field_id": name_field["id"], "value": "Asha"},
                {"field_id": housing_field["id"], "value": "Owned"},
            ],
            "raw_transcript": "my name is asha and i own my home",
        },
    )
    assert submit_response.status_code == 201

    list_response = admin_client.get(f"/api/forms/{form['id']}/responses")
    assert list_response.status_code == 200
    responses = list_response.json()
    assert len(responses) == 1
    assert len(responses[0]["answers"]) == 2


def test_submit_response_with_invalid_choice_returns_400(admin_client: TestClient):
    create_response = admin_client.post(
        "/api/forms",
        json={
            "title": "Survey",
            "fields": [
                {
                    "label": "Housing type",
                    "field_type": "choice",
                    "is_required": True,
                    "options": ["Owned", "Rented"],
                }
            ],
        },
    )
    form = create_response.json()
    housing_field = form["fields"][0]

    submit_response = admin_client.post(
        f"/api/forms/{form['id']}/responses",
        json={"answers": [{"field_id": housing_field["id"], "value": "Castle"}]},
    )
    assert submit_response.status_code == 400


def test_delete_form(admin_client: TestClient):
    create_response = admin_client.post(
        "/api/forms",
        json={"title": "Temp", "fields": [{"label": "x", "field_type": "text", "is_required": True, "options": []}]},
    )
    form_id = create_response.json()["id"]

    delete_response = admin_client.delete(f"/api/forms/{form_id}")
    assert delete_response.status_code == 204

    fetch_response = admin_client.get(f"/api/forms/{form_id}")
    assert fetch_response.status_code == 404


def test_home_page_renders(admin_client: TestClient):
    response = admin_client.get("/")
    assert response.status_code == 200
    assert "VoiceForm" in response.text


def test_form_builder_page_renders(admin_client: TestClient):
    response = admin_client.get("/forms/new")
    assert response.status_code == 200


def test_fill_form_page_renders(admin_client: TestClient):
    create_response = admin_client.post(
        "/api/forms",
        json={"title": "Survey", "fields": [{"label": "Name", "field_type": "text", "is_required": True, "options": []}]},
    )
    form_id = create_response.json()["id"]

    response = admin_client.get(f"/forms/{form_id}")
    assert response.status_code == 200
    assert "Survey" in response.text


# ---------------------------------------------------------------------------
# Org isolation — these are the tests that matter most for Phase 2
# ---------------------------------------------------------------------------


def test_org_b_cannot_see_org_as_forms(client: TestClient, db_session_factory):
    _seed_org_admin(db_session_factory, "Acme", "admin@acme.com", "secret123")
    _seed_org_admin(db_session_factory, "Globex", "admin@globex.com", "secret456")

    acme_login = client.post("/api/auth/login", json={"email": "admin@acme.com", "password": "secret123"})
    assert acme_login.status_code == 200
    create_response = client.post(
        "/api/forms",
        json={"title": "Acme Survey", "fields": [{"label": "x", "field_type": "text", "is_required": True, "options": []}]},
    )
    form_id = create_response.json()["id"]

    # Switch sessions: log in as Globex's admin.
    globex_login = client.post("/api/auth/login", json={"email": "admin@globex.com", "password": "secret456"})
    assert globex_login.status_code == 200

    fetch_response = client.get(f"/api/forms/{form_id}")
    assert fetch_response.status_code == 404

    list_response = client.get("/api/forms")
    assert list_response.json() == []


def test_org_b_cannot_delete_org_as_form(client: TestClient, db_session_factory):
    _seed_org_admin(db_session_factory, "Acme", "admin@acme.com", "secret123")
    _seed_org_admin(db_session_factory, "Globex", "admin@globex.com", "secret456")

    client.post("/api/auth/login", json={"email": "admin@acme.com", "password": "secret123"})
    create_response = client.post(
        "/api/forms",
        json={"title": "Acme Survey", "fields": [{"label": "x", "field_type": "text", "is_required": True, "options": []}]},
    )
    form_id = create_response.json()["id"]

    client.post("/api/auth/login", json={"email": "admin@globex.com", "password": "secret456"})
    delete_response = client.delete(f"/api/forms/{form_id}")
    assert delete_response.status_code == 404


# ---------------------------------------------------------------------------
# Role gating
# ---------------------------------------------------------------------------


def test_respondent_cannot_create_form(client: TestClient, db_session_factory):
    _seed_org_admin(db_session_factory, "Acme", "admin@acme.com", "secret123")
    admin_login = client.post("/api/auth/login", json={"email": "admin@acme.com", "password": "secret123"})
    assert admin_login.status_code == 200

    invite_response = client.post(
        "/api/auth/invites",
        json={"email": "respondent@acme.com", "full_name": "Resp Person", "role": "respondent"},
    )
    assert invite_response.status_code == 201
    invite_token = invite_response.json()["token"]

    accept_response = client.post(
        "/api/auth/invites/accept", json={"token": invite_token, "password": "respondentpw123"}
    )
    assert accept_response.status_code == 200  # logs the respondent in, replacing the admin session

    create_response = client.post(
        "/api/forms",
        json={"title": "Should fail", "fields": [{"label": "x", "field_type": "text", "is_required": True, "options": []}]},
    )
    assert create_response.status_code == 403


def test_respondent_can_view_and_fill_a_form(client: TestClient, db_session_factory):
    _seed_org_admin(db_session_factory, "Acme", "admin@acme.com", "secret123")
    client.post("/api/auth/login", json={"email": "admin@acme.com", "password": "secret123"})

    create_response = client.post(
        "/api/forms",
        json={"title": "Survey", "fields": [{"label": "Name", "field_type": "text", "is_required": True, "options": []}]},
    )
    form = create_response.json()
    field_id = form["fields"][0]["id"]

    invite_response = client.post(
        "/api/auth/invites",
        json={"email": "respondent@acme.com", "full_name": "Resp Person", "role": "respondent"},
    )
    invite_token = invite_response.json()["token"]
    client.post("/api/auth/invites/accept", json={"token": invite_token, "password": "respondentpw123"})

    # Respondent can view the form...
    view_response = client.get(f"/api/forms/{form['id']}")
    assert view_response.status_code == 200

    # ...and submit a response to it.
    submit_response = client.post(
        f"/api/forms/{form['id']}/responses",
        json={"answers": [{"field_id": field_id, "value": "Asha"}]},
    )
    assert submit_response.status_code == 201


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------


def test_admin_can_clone_template_into_own_org(admin_client: TestClient, db_session_factory):
    # Insert a template directly via the DB session, since there's no
    # public "create template" route (templates are seeded, not created
    # by org admins in Phase 2).
    from app.forms.models import Field, FieldType, Form

    db = db_session_factory()
    try:
        template = Form(org_id=None, title="Census Template", is_template=True)
        template.fields.append(Field(label="Full name", field_type=FieldType.TEXT, position=0))
        db.add(template)
        db.commit()
        db.refresh(template)
        template_id = template.id
    finally:
        db.close()

    list_response = admin_client.get("/api/templates")
    assert list_response.status_code == 200
    assert any(t["id"] == template_id for t in list_response.json())

    clone_response = admin_client.post(f"/api/templates/{template_id}/clone", json={})
    assert clone_response.status_code == 201
    cloned = clone_response.json()
    assert cloned["title"] == "Census Template"
    assert len(cloned["fields"]) == 1

    # The clone should now show up in the org's own forms list.
    forms_response = admin_client.get("/api/forms")
    assert any(f["id"] == cloned["id"] for f in forms_response.json())


# ---------------------------------------------------------------------------
# Analytics (Phase 3)
# ---------------------------------------------------------------------------


def test_org_overview_with_no_data(admin_client: TestClient):
    response = admin_client.get("/api/analytics/overview")
    assert response.status_code == 200
    body = response.json()
    assert body["total_forms"] == 0
    assert body["total_responses"] == 0
    assert body["forms"] == []


def test_org_overview_reflects_real_form_and_response(admin_client: TestClient):
    create_response = admin_client.post(
        "/api/forms",
        json={
            "title": "Survey",
            "fields": [
                {"label": "Name", "field_type": "text", "is_required": True, "options": []},
                {
                    "label": "Housing type",
                    "field_type": "choice",
                    "is_required": True,
                    "options": ["Owned", "Rented"],
                },
            ],
        },
    )
    form = create_response.json()
    name_field, housing_field = form["fields"]

    admin_client.post(
        f"/api/forms/{form['id']}/responses",
        json={
            "answers": [
                {"field_id": name_field["id"], "value": "Asha"},
                {"field_id": housing_field["id"], "value": "Owned"},
            ]
        },
    )

    overview_response = admin_client.get("/api/analytics/overview")
    assert overview_response.status_code == 200
    overview = overview_response.json()
    assert overview["total_forms"] == 1
    assert overview["total_responses"] == 1
    assert overview["forms"][0]["form_id"] == form["id"]
    assert overview["forms"][0]["response_count"] == 1


def test_form_dashboard_aggregates_real_sql_correctly(admin_client: TestClient):
    """
    This is the test that actually exercises real SQL GROUP BY / func.date()
    aggregation (via SQLite here, MySQL in production) — the unit tests in
    test_analytics_service.py exercise the same logic in pure Python against
    FakeAnalyticsRepository, but only this test proves the real query syntax
    in MySQLAnalyticsRepository is valid and correct.
    """
    create_response = admin_client.post(
        "/api/forms",
        json={
            "title": "Survey",
            "fields": [
                {"label": "Name", "field_type": "text", "is_required": True, "options": []},
                {"label": "Age", "field_type": "number", "is_required": False, "options": []},
                {
                    "label": "Housing type",
                    "field_type": "choice",
                    "is_required": True,
                    "options": ["Owned", "Rented"],
                },
            ],
        },
    )
    form = create_response.json()
    name_field, age_field, housing_field = form["fields"]

    admin_client.post(
        f"/api/forms/{form['id']}/responses",
        json={
            "answers": [
                {"field_id": name_field["id"], "value": "Asha"},
                {"field_id": age_field["id"], "value": "30"},
                {"field_id": housing_field["id"], "value": "Owned"},
            ]
        },
    )
    admin_client.post(
        f"/api/forms/{form['id']}/responses",
        json={
            "answers": [
                {"field_id": name_field["id"], "value": "Ravi"},
                {"field_id": age_field["id"], "value": "50"},
                {"field_id": housing_field["id"], "value": "Owned"},
            ]
        },
    )
    admin_client.post(
        f"/api/forms/{form['id']}/responses",
        json={
            "answers": [
                {"field_id": name_field["id"], "value": "Lee"},
                {"field_id": housing_field["id"], "value": "Rented"},
            ]
        },
    )

    dashboard_response = admin_client.get(f"/api/analytics/forms/{form['id']}")
    assert dashboard_response.status_code == 200
    dashboard = dashboard_response.json()

    assert dashboard["total_responses"] == 3
    # All 3 responses answered both required fields (Name, Housing type).
    assert dashboard["completion_rate"] == 1.0
    assert sum(d["count"] for d in dashboard["responses_by_day"]) == 3

    housing_stats = next(f for f in dashboard["field_stats"] if f["label"] == "Housing type")
    breakdown = {c["option"]: c["count"] for c in housing_stats["choice_breakdown"]}
    assert breakdown == {"Owned": 2, "Rented": 1}

    age_stats = next(f for f in dashboard["field_stats"] if f["label"] == "Age")
    assert age_stats["number_stats"]["count"] == 2
    assert age_stats["number_stats"]["minimum"] == 30.0
    assert age_stats["number_stats"]["maximum"] == 50.0
    assert age_stats["number_stats"]["average"] == 40.0


def test_form_dashboard_not_found_returns_404(admin_client: TestClient):
    response = admin_client.get("/api/analytics/forms/does-not-exist")
    assert response.status_code == 404


def test_dashboard_does_not_leak_across_orgs(client: TestClient, db_session_factory):
    _seed_org_admin(db_session_factory, "Acme", "admin@acme.com", "secret123")
    _seed_org_admin(db_session_factory, "Globex", "admin@globex.com", "secret456")

    client.post("/api/auth/login", json={"email": "admin@acme.com", "password": "secret123"})
    create_response = client.post(
        "/api/forms",
        json={"title": "Acme Survey", "fields": [{"label": "x", "field_type": "text", "is_required": True, "options": []}]},
    )
    form_id = create_response.json()["id"]

    client.post("/api/auth/login", json={"email": "admin@globex.com", "password": "secret456"})
    dashboard_response = client.get(f"/api/analytics/forms/{form_id}")
    assert dashboard_response.status_code == 404

    overview_response = client.get("/api/analytics/overview")
    assert overview_response.json()["total_forms"] == 0


def test_respondent_cannot_access_dashboard(client: TestClient, db_session_factory):
    _seed_org_admin(db_session_factory, "Acme", "admin@acme.com", "secret123")
    client.post("/api/auth/login", json={"email": "admin@acme.com", "password": "secret123"})

    invite_response = client.post(
        "/api/auth/invites",
        json={"email": "respondent@acme.com", "full_name": "Resp Person", "role": "respondent"},
    )
    invite_token = invite_response.json()["token"]
    client.post("/api/auth/invites/accept", json={"token": invite_token, "password": "respondentpw123"})

    overview_response = client.get("/api/analytics/overview")
    assert overview_response.status_code == 403

    dashboard_page_response = client.get("/dashboard")
    assert dashboard_page_response.status_code == 403


def test_csv_export_contains_expected_rows(admin_client: TestClient):
    create_response = admin_client.post(
        "/api/forms",
        json={
            "title": "Survey",
            "fields": [{"label": "Name", "field_type": "text", "is_required": True, "options": []}],
        },
    )
    form = create_response.json()
    name_field = form["fields"][0]

    admin_client.post(
        f"/api/forms/{form['id']}/responses",
        json={"answers": [{"field_id": name_field["id"], "value": "Asha"}]},
    )

    export_response = admin_client.get(f"/api/analytics/forms/{form['id']}/export.csv")
    assert export_response.status_code == 200
    assert export_response.headers["content-type"].startswith("text/csv")
    assert "attachment" in export_response.headers["content-disposition"]

    lines = export_response.text.splitlines()
    assert lines[0] == "response_id,submitted_at,Name"
    assert "Asha" in lines[1]


def test_csv_export_not_found_returns_404(admin_client: TestClient):
    response = admin_client.get("/api/analytics/forms/does-not-exist/export.csv")
    assert response.status_code == 404


def test_dashboard_pages_render(admin_client: TestClient):
    create_response = admin_client.post(
        "/api/forms",
        json={
            "title": "Survey",
            "fields": [
                {"label": "Name", "field_type": "text", "is_required": True, "options": []},
                {
                    "label": "Housing type",
                    "field_type": "choice",
                    "is_required": True,
                    "options": ["Owned", "Rented"],
                },
            ],
        },
    )
    form = create_response.json()
    name_field, housing_field = form["fields"]
    admin_client.post(
        f"/api/forms/{form['id']}/responses",
        json={
            "answers": [
                {"field_id": name_field["id"], "value": "Asha"},
                {"field_id": housing_field["id"], "value": "Owned"},
            ]
        },
    )

    overview_page = admin_client.get("/dashboard")
    assert overview_page.status_code == 200
    assert "Survey" in overview_page.text

    form_page = admin_client.get(f"/dashboard/forms/{form['id']}")
    assert form_page.status_code == 200
    assert "Housing type" in form_page.text
