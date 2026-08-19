"""
Schemas for the analytics module.

These are read models only — there is no Create/Update schema in this
module, on purpose. Analytics never writes anything; if a schema named
"...Create" ever shows up here, that's a sign analytics scope is
creeping into territory that belongs to forms/responses instead.
"""

from pydantic import BaseModel, Field

from app.forms.models import FieldType


class FormOverview(BaseModel):
    """One row in the org-wide dashboard: a single form's headline numbers."""

    form_id: str
    title: str
    description: str = Field(default = "")
    response_count: int
    last_response_at: str | None


class OrgOverview(BaseModel):
    total_forms: int
    total_responses: int
    forms: list[FormOverview]
    responses_by_day: list["DayCount"]


class AllResponsesForExp(BaseModel):
    form_id: str
    org_id: str
    answers: list[dict]
    

class DayCount(BaseModel):
    date: str  # ISO date, e.g. "2026-06-18"
    count: int


class ChoiceBreakdown(BaseModel):
    option: str
    count: int


class NumberFieldStats(BaseModel):
    count: int
    minimum: float | None
    maximum: float | None
    average: float | None


class FieldStats(BaseModel):
    field_id: str
    label: str
    field_type: FieldType
    answered_count: int
    """How many responses provided a non-empty value for this field."""

    choice_breakdown: list[ChoiceBreakdown] | None = None
    number_stats: NumberFieldStats | None = None


class FormDashboard(BaseModel):
    form_id: str
    title: str
    total_responses: int
    completion_rate: float
    """Fraction (0.0-1.0) of responses that answered every required field."""

    responses_by_day: list[DayCount]
    field_stats: list[FieldStats]


OrgOverview.model_rebuild()
