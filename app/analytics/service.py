"""
Analytics business logic.

AnalyticsService depends only on AnalyticsRepository — same dependency-
inversion seam as every other service in this app. It additionally never
imports FormRepository or ResponseRepository: everything it needs about
forms/fields/responses is exposed through AnalyticsRepository's own
methods (get_form_with_fields, list_responses_for_export, etc.), so this
module's only coupling to the forms/responses schema is "knows the
table shapes," not "depends on their services."

Nothing in this file calls .commit(), .add(), or .delete() — and
because AnalyticsRepository's interface has no such methods, there is
no way for a mistake here to mutate state even if someone tried.
"""

from dataclasses import dataclass, field as dataclass_field

from app.analytics.repository import AnalyticsRepository
from app.analytics.schemas import (
    ChoiceBreakdown,
    DayCount,
    FieldStats,
    FormDashboard,
    FormOverview,
    NumberFieldStats,
    OrgOverview,
)
from app.core.exceptions import NotFoundError
from app.forms.models import Field, FieldType

DEFAULT_TREND_WINDOW_DAYS = 30


@dataclass(frozen=True)
class FormForExport:
    form_id: str
    title: str
    fields: list[Field]


@dataclass(frozen=True)
class ResponseRow:
    response_id: str
    submitted_at: str
    answers_by_field_id: dict[str, str] = dataclass_field(default_factory=dict)


class AnalyticsService:
    def __init__(self, repository: AnalyticsRepository) -> None:
        self._repository = repository

    def get_org_overview(self, org_id: str) -> OrgOverview:
        forms_with_counts = self._repository.list_forms_with_response_counts(org_id)
        total_responses = self._repository.count_responses_for_org(org_id)
        day_rows = self._repository.responses_by_day_for_org(org_id, DEFAULT_TREND_WINDOW_DAYS)

        top_4_forms = forms_with_counts[0:4]
        
        return OrgOverview(
            total_forms=len(forms_with_counts),
            total_responses=total_responses,
            forms=[
                FormOverview(
                    form_id=form.id,
                    title=form.title,
                    description=form.description,
                    response_count=count,
                    last_response_at=last_response_at,
                )
                for form, count, last_response_at in top_4_forms
            ],
            responses_by_day=[DayCount(date=row.date, count=row.count) for row in day_rows],
        )


    def get_form_dashboard(self, form_id: str, org_id: str) -> FormDashboard:
        form = self._repository.get_form_with_fields(form_id, org_id)
        if form is None:
            raise NotFoundError(f"Form '{form_id}' not found")

        total_responses = self._repository.count_responses_for_form(form_id, org_id)
        day_rows = self._repository.responses_by_day_for_form(form_id, org_id, DEFAULT_TREND_WINDOW_DAYS)

        required_field_ids = [f.id for f in form.fields if f.is_required]
        fully_answered_count = self._repository.count_fully_answered_responses(
            form_id, org_id, required_field_ids
        )
        completion_rate = (fully_answered_count / total_responses) if total_responses > 0 else 0.0

        field_stats = [self._build_field_stats(field, org_id) for field in form.fields]

        return FormDashboard(
            form_id=form.id,
            title=form.title,
            total_responses=total_responses,
            completion_rate=completion_rate,
            responses_by_day=[DayCount(date=row.date, count=row.count) for row in day_rows],
            field_stats=field_stats,
        )


    
    def get_export_rows(self, form_id: str, org_id: str) -> tuple[FormForExport, list[ResponseRow]]:
        """
        Returns the form (for header construction) and one row per response,
        each row a dict of field_id -> answer value. Used by the CSV export
        endpoint — kept here rather than in the router so the "shape the
        data for export" logic is testable without going through HTTP.
        """
        form = self._repository.get_form_with_fields(form_id, org_id)
        if form is None:
            raise NotFoundError(f"Form '{form_id}' not found")

        responses = self._repository.list_responses_for_export(form_id, org_id)
        rows = [
            ResponseRow(
                response_id=r.id,
                submitted_at=r.submitted_at.isoformat(),
                answers_by_field_id={a.field_id: a.value for a in r.answers},
            )
            for r in responses
        ]
        return FormForExport(form_id=form.id, title=form.title, fields=form.fields), rows


    ## Returns a ALL form responses:
    def get_response_rows(self, form_id: str, org_id: str) -> dict:
            """
            Returns all the responses for the form
            """
            responses = self._repository.list_responses_for_export(form_id, org_id)
            
            # 1. Get all Field names from Form Schema
            # 2. Get values corresponding to each Field name from Responses
            
            answers = []
            for resp in responses:
                answers.append(resp.response_schema)
            
            return {"form_id": form_id, "org_id": org_id, "answers": answers}



    def _build_field_stats(self, field: Field, org_id: str) -> FieldStats:
        answered_count = self._repository.answered_count_for_field(field.id, org_id)

        choice_breakdown = None
        number_stats = None

        if field.field_type == FieldType.CHOICE:
            rows = self._repository.choice_breakdown_for_field(field.id, org_id)
            choice_breakdown = [ChoiceBreakdown(option=row.value, count=row.count) for row in rows]
        elif field.field_type == FieldType.NUMBER:
            row = self._repository.number_stats_for_field(field.id, org_id)
            number_stats = NumberFieldStats(
                count=row.count, minimum=row.minimum, maximum=row.maximum, average=row.average
            )

        return FieldStats(
            field_id=field.id,
            label=field.label,
            field_type=field.field_type,
            answered_count=answered_count,
            choice_breakdown=choice_breakdown,
            number_stats=number_stats,
        )
