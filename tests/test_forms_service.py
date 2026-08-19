import pytest

from app.core.exceptions import NotFoundError
from app.forms.models import FieldType
from app.forms.schemas import FieldCreate, FormCreate
from app.forms.service import FormService
from tests.fakes import FakeFormRepository

ORG_A = "org-a"
ORG_B = "org-b"


def make_service() -> FormService:
    return FormService(FakeFormRepository())


def test_create_form_with_fields():
    service = make_service()
    payload = FormCreate(
        title="Household survey",
        description="Annual census",
        fields=[
            FieldCreate(label="Full name", field_type=FieldType.TEXT),
            FieldCreate(label="Household size", field_type=FieldType.NUMBER),
            FieldCreate(
                label="Housing type",
                field_type=FieldType.CHOICE,
                options=["Owned", "Rented"],
            ),
        ],
    )

    form = service.create_form(ORG_A, payload)

    assert form.title == "Household survey"
    assert form.org_id == ORG_A
    assert len(form.fields) == 3
    assert form.fields[2].options == ["Owned", "Rented"]
    assert [f.position for f in form.fields] == [0, 1, 2]


def test_get_form_not_found_raises():
    service = make_service()
    with pytest.raises(NotFoundError):
        service.get_form("does-not-exist", ORG_A)


def test_get_form_from_different_org_raises_not_found():
    """Org isolation: org B should not be able to fetch org A's form by id."""
    service = make_service()
    form = service.create_form(ORG_A, FormCreate(title="A", fields=[FieldCreate(label="x", field_type=FieldType.TEXT)]))

    with pytest.raises(NotFoundError):
        service.get_form(form.id, ORG_B)


def test_list_forms_only_returns_own_org_forms():
    service = make_service()
    service.create_form(ORG_A, FormCreate(title="A1", fields=[FieldCreate(label="x", field_type=FieldType.TEXT)]))
    service.create_form(ORG_A, FormCreate(title="A2", fields=[FieldCreate(label="y", field_type=FieldType.TEXT)]))
    service.create_form(ORG_B, FormCreate(title="B1", fields=[FieldCreate(label="z", field_type=FieldType.TEXT)]))

    org_a_forms = service.list_forms(ORG_A)
    org_b_forms = service.list_forms(ORG_B)

    assert {f.title for f in org_a_forms} == {"A1", "A2"}
    assert {f.title for f in org_b_forms} == {"B1"}


def test_delete_form_removes_it():
    service = make_service()
    form = service.create_form(
        ORG_A, FormCreate(title="Temp", fields=[FieldCreate(label="x", field_type=FieldType.TEXT)])
    )

    service.delete_form(form.id, ORG_A)

    with pytest.raises(NotFoundError):
        service.get_form(form.id, ORG_A)


def test_delete_nonexistent_form_raises():
    service = make_service()
    with pytest.raises(NotFoundError):
        service.delete_form("ghost-id", ORG_A)


def test_delete_form_from_different_org_raises_not_found():
    """Org isolation: org B should not be able to delete org A's form."""
    service = make_service()
    form = service.create_form(
        ORG_A, FormCreate(title="A", fields=[FieldCreate(label="x", field_type=FieldType.TEXT)])
    )

    with pytest.raises(NotFoundError):
        service.delete_form(form.id, ORG_B)

    # Confirm it's still there for the rightful owner.
    assert service.get_form(form.id, ORG_A) is not None


def test_choice_field_requires_at_least_two_options():
    with pytest.raises(ValueError):
        FieldCreate(label="Housing type", field_type=FieldType.CHOICE, options=["Owned"])
