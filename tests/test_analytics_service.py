from datetime import UTC, datetime, timedelta

import pytest

from app.analytics.repository import AnalyticsRepository
from app.analytics.service import AnalyticsService
from app.core.exceptions import NotFoundError
from app.forms.models import Field, FieldType, Form
from app.responses.models import AnswerValue, Response
from tests.fakes import FakeAnalyticsRepository

ORG_A = "org-a"
ORG_B = "org-b"


def make_form(org_id: str | None = ORG_A, is_template: bool = False) -> Form:
    form = Form(org_id=org_id, title="Household Survey", is_template=is_template)
    form.fields.append(Field(label="Name", field_type=FieldType.TEXT, position=0, is_required=True))
    form.fields.append(Field(label="Age", field_type=FieldType.NUMBER, position=1, is_required=False))
    form.fields.append(
        Field(
            label="Housing type",
            field_type=FieldType.CHOICE,
            options_csv="Owned,Rented",
            position=2,
            is_required=True,
        )
    )
    return form


def make_response(form: Form, org_id: str, answers: dict[str, str], days_ago: int = 0) -> Response:
    response = Response(
        form_id=form.id,
        org_id=org_id,
        respondent_id="respondent-1",
        submitted_at=datetime.now(UTC) - timedelta(days=days_ago),
    )
    for field in form.fields:
        if field.label in answers:
            response.answers.append(AnswerValue(field_id=field.id, value=answers[field.label]))
    return response


def make_repository(forms: list[Form], responses: list[Response]) -> AnalyticsRepository:
    forms_dict = {f.id: f for f in forms}
    responses_dict = {r.id: r for r in responses}
    return FakeAnalyticsRepository(forms_dict, responses_dict)


# ---------------------------------------------------------------------------
# Org overview
# ---------------------------------------------------------------------------


def test_org_overview_counts_forms_and_responses():
    form = make_form()
    responses = [
        make_response(form, ORG_A, {"Name": "Asha", "Housing type": "Owned"}),
        make_response(form, ORG_A, {"Name": "Ravi", "Housing type": "Rented"}),
    ]
    service = AnalyticsService(make_repository([form], responses))

    overview = service.get_org_overview(ORG_A)

    assert overview.total_forms == 1
    assert overview.total_responses == 2
    assert overview.forms[0].response_count == 2
    assert overview.forms[0].title == "Household Survey"


def test_org_overview_excludes_templates():
    template = make_form(org_id=None, is_template=True)
    owned_form = make_form()
    service = AnalyticsService(make_repository([template, owned_form], []))

    overview = service.get_org_overview(ORG_A)

    assert overview.total_forms == 1
    assert overview.forms[0].form_id == owned_form.id


def test_org_overview_does_not_leak_across_orgs():
    form_a = make_form(org_id=ORG_A)
    form_b = make_form(org_id=ORG_B)
    response_a = make_response(form_a, ORG_A, {"Name": "Asha", "Housing type": "Owned"})
    response_b = make_response(form_b, ORG_B, {"Name": "Lee", "Housing type": "Rented"})
    service = AnalyticsService(make_repository([form_a, form_b], [response_a, response_b]))

    overview_a = service.get_org_overview(ORG_A)

    assert overview_a.total_forms == 1
    assert overview_a.total_responses == 1
    assert overview_a.forms[0].form_id == form_a.id


def test_org_overview_with_no_data_returns_zeros():
    service = AnalyticsService(make_repository([], []))

    overview = service.get_org_overview(ORG_A)

    assert overview.total_forms == 0
    assert overview.total_responses == 0
    assert overview.forms == []


# ---------------------------------------------------------------------------
# Per-form dashboard
# ---------------------------------------------------------------------------


def test_form_dashboard_not_found_raises():
    service = AnalyticsService(make_repository([], []))
    with pytest.raises(NotFoundError):
        service.get_form_dashboard("does-not-exist", ORG_A)


def test_form_dashboard_from_another_org_raises_not_found():
    form = make_form(org_id=ORG_A)
    service = AnalyticsService(make_repository([form], []))

    with pytest.raises(NotFoundError):
        service.get_form_dashboard(form.id, ORG_B)


def test_form_dashboard_completion_rate_all_required_fields_answered():
    form = make_form()
    # Both responses answer Name + Housing type (both required); Age (optional) varies.
    responses = [
        make_response(form, ORG_A, {"Name": "Asha", "Housing type": "Owned", "Age": "34"}),
        make_response(form, ORG_A, {"Name": "Ravi", "Housing type": "Rented"}),
    ]
    service = AnalyticsService(make_repository([form], responses))

    dashboard = service.get_form_dashboard(form.id, ORG_A)

    assert dashboard.total_responses == 2
    assert dashboard.completion_rate == 1.0


def test_form_dashboard_completion_rate_partial():
    form = make_form()
    responses = [
        make_response(form, ORG_A, {"Name": "Asha", "Housing type": "Owned"}),  # complete
        make_response(form, ORG_A, {"Name": "Ravi"}),  # missing required Housing type
    ]
    service = AnalyticsService(make_repository([form], responses))

    dashboard = service.get_form_dashboard(form.id, ORG_A)

    assert dashboard.completion_rate == 0.5


def test_form_dashboard_with_zero_responses_has_zero_completion_rate_not_divide_error():
    form = make_form()
    service = AnalyticsService(make_repository([form], []))

    dashboard = service.get_form_dashboard(form.id, ORG_A)

    assert dashboard.total_responses == 0
    assert dashboard.completion_rate == 0.0


def test_form_dashboard_choice_field_breakdown():
    form = make_form()
    responses = [
        make_response(form, ORG_A, {"Name": "Asha", "Housing type": "Owned"}),
        make_response(form, ORG_A, {"Name": "Ravi", "Housing type": "Owned"}),
        make_response(form, ORG_A, {"Name": "Lee", "Housing type": "Rented"}),
    ]
    service = AnalyticsService(make_repository([form], responses))

    dashboard = service.get_form_dashboard(form.id, ORG_A)
    housing_stats = next(f for f in dashboard.field_stats if f.label == "Housing type")

    assert housing_stats.choice_breakdown is not None
    breakdown_by_option = {c.option: c.count for c in housing_stats.choice_breakdown}
    assert breakdown_by_option == {"Owned": 2, "Rented": 1}


def test_form_dashboard_number_field_stats():
    form = make_form()
    responses = [
        make_response(form, ORG_A, {"Name": "Asha", "Housing type": "Owned", "Age": "20"}),
        make_response(form, ORG_A, {"Name": "Ravi", "Housing type": "Owned", "Age": "40"}),
    ]
    service = AnalyticsService(make_repository([form], responses))

    dashboard = service.get_form_dashboard(form.id, ORG_A)
    age_stats = next(f for f in dashboard.field_stats if f.label == "Age")

    assert age_stats.number_stats is not None
    assert age_stats.number_stats.minimum == 20.0
    assert age_stats.number_stats.maximum == 40.0
    assert age_stats.number_stats.average == 30.0


def test_form_dashboard_text_field_has_no_breakdown():
    form = make_form()
    responses = [make_response(form, ORG_A, {"Name": "Asha", "Housing type": "Owned"})]
    service = AnalyticsService(make_repository([form], responses))

    dashboard = service.get_form_dashboard(form.id, ORG_A)
    name_stats = next(f for f in dashboard.field_stats if f.label == "Name")

    assert name_stats.choice_breakdown is None
    assert name_stats.number_stats is None
    assert name_stats.answered_count == 1


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------


def test_export_rows_not_found_raises():
    service = AnalyticsService(make_repository([], []))
    with pytest.raises(NotFoundError):
        service.get_export_rows("does-not-exist", ORG_A)


def test_export_rows_contain_one_row_per_response_with_correct_answers():
    form = make_form()
    responses = [
        make_response(form, ORG_A, {"Name": "Asha", "Housing type": "Owned", "Age": "34"}),
        make_response(form, ORG_A, {"Name": "Ravi", "Housing type": "Rented"}),
    ]
    service = AnalyticsService(make_repository([form], responses))

    export_form, rows = service.get_export_rows(form.id, ORG_A)

    assert export_form.title == "Household Survey"
    assert len(rows) == 2
    name_field_id = next(f.id for f in form.fields if f.label == "Name")
    assert {row.answers_by_field_id[name_field_id] for row in rows} == {"Asha", "Ravi"}


def test_export_rows_from_another_org_raises_not_found():
    form = make_form(org_id=ORG_A)
    service = AnalyticsService(make_repository([form], []))

    with pytest.raises(NotFoundError):
        service.get_export_rows(form.id, ORG_B)
