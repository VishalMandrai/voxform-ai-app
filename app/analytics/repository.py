"""
Persistence layer for analytics.

AnalyticsRepository has no create/update/delete methods — not "doesn't
expose them," they structurally do not exist on the interface. This is
deliberate: analytics is the one module in the app guaranteed to never
mutate state, and making that true at the type level (rather than just
"the implementation happens not to call .commit()") means a future
contributor can't accidentally wire a write path through this class
without first noticing the interface doesn't support it.

Every method takes org_id and filters on it — same tenant-isolation
discipline as FormRepository/ResponseRepository. Analytics reads
Form/Response/AnswerValue directly (it's allowed to know the schema,
same as any repository), but never imports FormService, ResponseService,
or their routers.

Number-field stats (min/max/avg) are computed in Python rather than via
SQL CAST, deliberately: VARCHAR->numeric casting behaves differently
across SQLite (used in tests) and MySQL (used in production), and the
row counts here (answers for one field, in one form) are small enough
that doing it in Python is both simpler and actually more portable than
chasing dialect-specific SQL functions.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.forms.models import Form
from app.responses.models import AnswerValue, Response


@dataclass(frozen=True)
class DayCountRow:
    date: str
    count: int


@dataclass(frozen=True)
class ChoiceCountRow:
    value: str
    count: int


@dataclass(frozen=True)
class NumberStatsRow:
    count: int
    minimum: float | None
    maximum: float | None
    average: float | None


class AnalyticsRepository(ABC):
    @abstractmethod
    def list_forms_with_response_counts(self, org_id: str) -> list[tuple[Form, int, str | None]]:
        """Returns (form, response_count, last_response_at_iso) for every non-template form in the org."""
        ...

    @abstractmethod
    def count_responses_for_org(self, org_id: str) -> int: ...

    @abstractmethod
    def responses_by_day_for_org(self, org_id: str, days: int) -> list[DayCountRow]: ...

    @abstractmethod
    def get_form_with_fields(self, form_id: str, org_id: str) -> Form | None: ...

    @abstractmethod
    def count_responses_for_form(self, form_id: str, org_id: str) -> int: ...

    @abstractmethod
    def responses_by_day_for_form(self, form_id: str, org_id: str, days: int) -> list[DayCountRow]: ...

    @abstractmethod
    def count_fully_answered_responses(self, form_id: str, org_id: str, required_field_ids: list[str]) -> int:
        """How many responses answered every field in required_field_ids."""
        ...

    @abstractmethod
    def answered_count_for_field(self, field_id: str, org_id: str) -> int: ...

    @abstractmethod
    def choice_breakdown_for_field(self, field_id: str, org_id: str) -> list[ChoiceCountRow]: ...

    @abstractmethod
    def number_stats_for_field(self, field_id: str, org_id: str) -> NumberStatsRow: ...

    @abstractmethod
    def list_responses_for_export(self, form_id: str, org_id: str) -> list[Response]: ...


class MySQLAnalyticsRepository(AnalyticsRepository):
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_forms_with_response_counts(self, org_id: str) -> list[tuple[Form, int, str | None]]:
        forms = (
            self._db.query(Form)
            .filter(Form.org_id == org_id, Form.is_template.is_(False))
            .order_by(Form.created_at.desc())
            .all()
        )

        results: list[tuple[Form, int, str | None]] = []
        for form in forms:
            count, latest = (
                self._db.query(func.count(Response.id), func.max(Response.submitted_at))
                .filter(Response.form_id == form.id, Response.org_id == org_id)
                .one()
            )
            results.append((form, count or 0, latest.isoformat() if latest else None))
        return results


    def count_responses_for_org(self, org_id: str) -> int:
        return self._db.query(func.count(Response.id)).filter(Response.org_id == org_id).scalar() or 0


    def responses_by_day_for_org(self, org_id: str, days: int) -> list[DayCountRow]:
        return self._responses_by_day(Response.org_id == org_id, days)


    def get_form_with_fields(self, form_id: str, org_id: str) -> Form | None:
        return (
            self._db.query(Form)
            .options(selectinload(Form.fields))
            .filter(Form.id == form_id, Form.org_id == org_id)
            .first()
        )


    def count_responses_for_form(self, form_id: str, org_id: str) -> int:
        return (
            self._db.query(func.count(Response.id))
            .filter(Response.form_id == form_id, Response.org_id == org_id)
            .scalar()
            or 0
        )


    def responses_by_day_for_form(self, form_id: str, org_id: str, days: int) -> list[DayCountRow]:
        return self._responses_by_day(
            (Response.form_id == form_id) & (Response.org_id == org_id), days
        )


    def count_fully_answered_responses(self, form_id: str, org_id: str, required_field_ids: list[str]) -> int:
        if not required_field_ids:
            # No required fields means every response trivially satisfies "answered all required fields".
            return self.count_responses_for_form(form_id, org_id)

        required_count = len(required_field_ids)
        rows = (
            self._db.query(AnswerValue.response_id, func.count(AnswerValue.field_id.distinct()))
            .join(Response, Response.id == AnswerValue.response_id)
            .filter(
                Response.form_id == form_id,
                Response.org_id == org_id,
                AnswerValue.field_id.in_(required_field_ids),
                AnswerValue.value != "",
            )
            .group_by(AnswerValue.response_id)
            .having(func.count(AnswerValue.field_id.distinct()) == required_count)
            .all()
        )
        return len(rows)

    def answered_count_for_field(self, field_id: str, org_id: str) -> int:
        return (
            self._db.query(func.count(AnswerValue.id))
            .join(Response, Response.id == AnswerValue.response_id)
            .filter(
                AnswerValue.field_id == field_id,
                Response.org_id == org_id,
                AnswerValue.value != "",
            )
            .scalar()
            or 0
        )

    def choice_breakdown_for_field(self, field_id: str, org_id: str) -> list[ChoiceCountRow]:
        rows = (
            self._db.query(AnswerValue.value, func.count(AnswerValue.id))
            .join(Response, Response.id == AnswerValue.response_id)
            .filter(AnswerValue.field_id == field_id, Response.org_id == org_id, AnswerValue.value != "")
            .group_by(AnswerValue.value)
            .order_by(func.count(AnswerValue.id).desc())
            .all()
        )
        return [ChoiceCountRow(value=value, count=count) for value, count in rows]

    def number_stats_for_field(self, field_id: str, org_id: str) -> NumberStatsRow:
        raw_values = (
            self._db.query(AnswerValue.value)
            .join(Response, Response.id == AnswerValue.response_id)
            .filter(AnswerValue.field_id == field_id, Response.org_id == org_id, AnswerValue.value != "")
            .all()
        )

        numbers: list[float] = []
        for (raw_value,) in raw_values:
            try:
                numbers.append(float(raw_value))
            except (TypeError, ValueError):
                continue  # defensively skip any malformed value rather than failing the whole dashboard

        if not numbers:
            return NumberStatsRow(count=0, minimum=None, maximum=None, average=None)

        return NumberStatsRow(
            count=len(numbers),
            minimum=min(numbers),
            maximum=max(numbers),
            average=sum(numbers) / len(numbers),
        )

    ## For CSV Export - get all the responses for a Form
    def list_responses_for_export(self, form_id: str, org_id: str) -> list[Response]:
        return (
            self._db.query(Response)
            .options(selectinload(Response.answers))
            .filter(Response.form_id == form_id, Response.org_id == org_id)
            .order_by(Response.submitted_at.asc())
            .all()
        )

    def _responses_by_day(self, filter_clause, days: int) -> list[DayCountRow]:
        cutoff = datetime.now(UTC) - timedelta(days=days)
        rows = (
            self._db.query(func.date(Response.submitted_at), func.count(Response.id))
            .filter(filter_clause, Response.submitted_at >= cutoff)
            .group_by(func.date(Response.submitted_at))
            .order_by(func.date(Response.submitted_at))
            .all()
        )
        return [DayCountRow(date=str(date), count=count) for date, count in rows]
