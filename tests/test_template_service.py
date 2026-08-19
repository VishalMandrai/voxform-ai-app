import pytest

from app.core.exceptions import NotFoundError
from app.form_templates.service import TemplateService
from app.forms.models import Field, FieldType, Form
from tests.fakes import FakeFormRepository

ORG_A = "org-a"


def make_service_with_template() -> tuple[TemplateService, FakeFormRepository, Form]:
    repo = FakeFormRepository()
    service = TemplateService(repo)

    template = Form(org_id=None, title="Household Census", description="Standard census", is_template=True)
    template.fields.append(Field(label="Full name", field_type=FieldType.TEXT, position=0))
    template.fields.append(
        Field(
            label="Housing type",
            field_type=FieldType.CHOICE,
            options_csv="Owned,Rented",
            position=1,
        )
    )
    repo.create(template)

    return service, repo, template


def test_list_templates_returns_global_templates():
    service, _repo, template = make_service_with_template()

    templates = service.list_templates()

    assert len(templates) == 1
    assert templates[0].id == template.id


def test_get_template_returns_it():
    service, _repo, template = make_service_with_template()

    fetched = service.get_template(template.id)

    assert fetched.id == template.id


def test_get_nonexistent_template_raises():
    service, _repo, _template = make_service_with_template()
    with pytest.raises(NotFoundError):
        service.get_template("does-not-exist")


def test_clone_template_creates_new_org_owned_form_with_same_fields():
    service, repo, template = make_service_with_template()

    cloned = service.clone_template(template.id, ORG_A)

    assert cloned.id != template.id
    assert cloned.org_id == ORG_A
    assert cloned.is_template is False
    assert cloned.title == template.title
    assert len(cloned.fields) == 2
    assert {f.label for f in cloned.fields} == {"Full name", "Housing type"}
    # Original template must be untouched.
    assert repo.get_by_id(template.id, org_id=None).org_id is None


def test_clone_template_with_title_override():
    service, _repo, template = make_service_with_template()

    cloned = service.clone_template(template.id, ORG_A, title_override="Our Census 2026")

    assert cloned.title == "Our Census 2026"


def test_cloned_form_fields_are_independent_copies():
    """Editing a clone's fields must never mutate the shared template."""
    service, repo, template = make_service_with_template()

    cloned = service.clone_template(template.id, ORG_A)
    cloned.fields[0].label = "Changed in the clone"

    original = repo.get_by_id(template.id, org_id=None)
    assert original.fields[0].label == "Full name"
