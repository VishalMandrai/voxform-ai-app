import pytest

from app.core.exceptions import NotFoundError, ValidationError
from app.forms.models import FieldType
from app.forms.schemas import FieldCreate, FormCreate
from app.forms.service import FormService
from app.responses.schemas import AnswerIn, ResponseCreate
from app.responses.service import ResponseService
from tests.fakes import FakeFormRepository, FakeResponseRepository

ORG_A = "org-a"
ORG_B = "org-b"
RESPONDENT_ID = "respondent-1"


def make_services():
    form_repo = FakeFormRepository()
    form_service = FormService(form_repo)
    response_service = ResponseService(FakeResponseRepository(), form_repo)
    return form_service, response_service


def make_sample_form(form_service: FormService, org_id: str = ORG_A):
    return form_service.create_form(
        org_id,
        FormCreate(
            title="Survey",
            fields=[
                FieldCreate(label="Name", field_type=FieldType.TEXT),
                FieldCreate(label="Age", field_type=FieldType.NUMBER),
                FieldCreate(
                    label="Housing type",
                    field_type=FieldType.CHOICE,
                    options=["Owned", "Rented"],
                ),
            ],
        ),
    )


def test_submit_valid_response():
    form_service, response_service = make_services()
    form = make_sample_form(form_service)
    name_field, age_field, housing_field = form.fields

    payload = ResponseCreate(
        answers=[
            AnswerIn(field_id=name_field.id, value="Asha"),
            AnswerIn(field_id=age_field.id, value="34"),
            AnswerIn(field_id=housing_field.id, value="Owned"),
        ]
    )

    response = response_service.submit_response(form.id, ORG_A, RESPONDENT_ID, payload)

    assert response.form_id == form.id
    assert response.org_id == ORG_A
    assert response.respondent_id == RESPONDENT_ID
    assert len(response.answers) == 3


def test_submit_response_missing_required_field_raises():
    form_service, response_service = make_services()
    form = make_sample_form(form_service)
    name_field, _age_field, _housing_field = form.fields

    payload = ResponseCreate(answers=[AnswerIn(field_id=name_field.id, value="Asha")])

    with pytest.raises(ValidationError, match="Missing required field"):
        response_service.submit_response(form.id, ORG_A, RESPONDENT_ID, payload)


def test_submit_response_invalid_choice_value_raises():
    form_service, response_service = make_services()
    form = make_sample_form(form_service)
    name_field, age_field, housing_field = form.fields

    payload = ResponseCreate(
        answers=[
            AnswerIn(field_id=name_field.id, value="Asha"),
            AnswerIn(field_id=age_field.id, value="34"),
            AnswerIn(field_id=housing_field.id, value="Castle"),  # not a valid option
        ]
    )

    with pytest.raises(ValidationError, match="not a valid option"):
        response_service.submit_response(form.id, ORG_A, RESPONDENT_ID, payload)


def test_submit_response_non_numeric_number_field_raises():
    form_service, response_service = make_services()
    form = make_sample_form(form_service)
    name_field, age_field, housing_field = form.fields

    payload = ResponseCreate(
        answers=[
            AnswerIn(field_id=name_field.id, value="Asha"),
            AnswerIn(field_id=age_field.id, value="not-a-number"),
            AnswerIn(field_id=housing_field.id, value="Owned"),
        ]
    )

    with pytest.raises(ValidationError, match="expects a number"):
        response_service.submit_response(form.id, ORG_A, RESPONDENT_ID, payload)


def test_submit_response_unknown_form_raises_not_found():
    _form_service, response_service = make_services()

    with pytest.raises(NotFoundError):
        response_service.submit_response("ghost-form-id", ORG_A, RESPONDENT_ID, ResponseCreate(answers=[]))


def test_submit_response_to_another_orgs_form_raises_not_found():
    """Org isolation: org B can't submit a response against org A's form."""
    form_service, response_service = make_services()
    form = make_sample_form(form_service, org_id=ORG_A)
    name_field, age_field, housing_field = form.fields

    payload = ResponseCreate(
        answers=[
            AnswerIn(field_id=name_field.id, value="Asha"),
            AnswerIn(field_id=age_field.id, value="34"),
            AnswerIn(field_id=housing_field.id, value="Owned"),
        ]
    )

    with pytest.raises(NotFoundError):
        response_service.submit_response(form.id, ORG_B, RESPONDENT_ID, payload)


def test_list_responses_for_form():
    form_service, response_service = make_services()
    form = make_sample_form(form_service)
    name_field, age_field, housing_field = form.fields

    payload = ResponseCreate(
        answers=[
            AnswerIn(field_id=name_field.id, value="Asha"),
            AnswerIn(field_id=age_field.id, value="34"),
            AnswerIn(field_id=housing_field.id, value="Owned"),
        ]
    )
    response_service.submit_response(form.id, ORG_A, RESPONDENT_ID, payload)

    responses = response_service.list_responses(form.id, ORG_A)

    assert len(responses) == 1


def test_list_responses_does_not_leak_across_orgs():
    form_service, response_service = make_services()
    form = make_sample_form(form_service, org_id=ORG_A)
    name_field, age_field, housing_field = form.fields

    payload = ResponseCreate(
        answers=[
            AnswerIn(field_id=name_field.id, value="Asha"),
            AnswerIn(field_id=age_field.id, value="34"),
            AnswerIn(field_id=housing_field.id, value="Owned"),
        ]
    )
    response_service.submit_response(form.id, ORG_A, RESPONDENT_ID, payload)

    # A different org querying the same form_id should see nothing.
    assert response_service.list_responses(form.id, ORG_B) == []
