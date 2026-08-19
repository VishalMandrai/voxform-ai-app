"""
In-memory fakes for the repository and auth-primitive interfaces.

These exist because every service (FormService, ResponseService,
AuthService, TemplateService) depends on abstract interfaces, never on
concrete MySQL/bcrypt/JWT classes. That means tests can swap in trivial
dict-backed or deterministic fakes and verify business logic with zero
database, zero real crypto, zero network — the payoff of having done
dependency inversion properly in the app code.
"""

from app.analytics.repository import AnalyticsRepository, ChoiceCountRow, DayCountRow, NumberStatsRow
from app.auth.jwt_handler import TokenIssuer, TokenPayload
from app.auth.models import InviteToken, Organization, User
from app.auth.password_hasher import PasswordHasher
from app.auth.repository import InviteTokenRepository, OrganizationRepository, UserRepository
from app.forms.models import Form
from app.forms.repository import FormRepository
from app.responses.models import Response
from app.responses.repository import ResponseRepository


class FakeFormRepository(FormRepository):
    def __init__(self) -> None:
        self._forms: dict[str, Form] = {}

    def create(self, form: Form) -> Form:
        self._forms[form.id] = form
        return form

    def get_by_id(self, form_id: str, org_id: str | None) -> Form | None:
        form = self._forms.get(form_id)
        if form is None:
            return None
        if org_id is not None and form.org_id != org_id:
            return None
        return form

    def list_for_org(self, org_id: str) -> list[Form]:
        return [f for f in self._forms.values() if f.org_id == org_id and not f.is_template]

    def list_templates(self) -> list[Form]:
        return [f for f in self._forms.values() if f.is_template]

    def delete(self, form_id: str, org_id: str) -> bool:
        form = self._forms.get(form_id)
        if form is None or form.org_id != org_id:
            return False
        del self._forms[form_id]
        return True


class FakeResponseRepository(ResponseRepository):
    def __init__(self) -> None:
        self._responses: dict[str, Response] = {}

    def create(self, response: Response) -> Response:
        self._responses[response.id] = response
        return response

    def get_by_id(self, response_id: str, org_id: str) -> Response | None:
        response = self._responses.get(response_id)
        if response is None or response.org_id != org_id:
            return None
        return response

    def list_for_form(self, form_id: str, org_id: str) -> list[Response]:
        return [
            r for r in self._responses.values() if r.form_id == form_id and r.org_id == org_id
        ]


class FakeOrganizationRepository(OrganizationRepository):
    def __init__(self) -> None:
        self._orgs: dict[str, Organization] = {}

    def create(self, organization: Organization) -> Organization:
        self._orgs[organization.id] = organization
        return organization

    def get_by_id(self, org_id: str) -> Organization | None:
        return self._orgs.get(org_id)


class FakeUserRepository(UserRepository):
    def __init__(self) -> None:
        self._users: dict[str, User] = {}

    def create(self, user: User) -> User:
        self._users[user.id] = user
        return user

    def get_by_id(self, user_id: str) -> User | None:
        return self._users.get(user_id)

    def get_by_email(self, email: str) -> User | None:
        return next((u for u in self._users.values() if u.email == email), None)

    def list_for_org(self, org_id: str) -> list[User]:
        return [u for u in self._users.values() if u.org_id == org_id]


class FakeInviteTokenRepository(InviteTokenRepository):
    def __init__(self) -> None:
        self._invites: dict[str, InviteToken] = {}

    def create(self, invite: InviteToken) -> InviteToken:
        self._invites[invite.token] = invite
        return invite

    def get_by_token(self, token: str) -> InviteToken | None:
        return self._invites.get(token)

    def mark_accepted(self, invite: InviteToken) -> InviteToken:
        from datetime import UTC, datetime

        invite.accepted_at = datetime.now(UTC)
        return invite


class FakePasswordHasher(PasswordHasher):
    """Deterministic, non-cryptographic stand-in — never use outside tests."""

    def hash(self, plain_password: str) -> str:
        return f"hashed:{plain_password}"

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return hashed_password == f"hashed:{plain_password}"


class FakeTokenIssuer(TokenIssuer):
    """In-memory token issuer — encodes the payload as a plain string, no real JWT involved."""

    def __init__(self) -> None:
        self._issued: dict[str, TokenPayload] = {}
        self._counter = 0

    def issue(self, payload: TokenPayload) -> str:
        self._counter += 1
        token = f"fake-token-{self._counter}"
        self._issued[token] = payload
        return token

    def verify(self, token: str) -> TokenPayload:
        from app.core.exceptions import ValidationError

        payload = self._issued.get(token)
        if payload is None:
            raise ValidationError("Invalid or expired session token")
        return payload


class FakeAnalyticsRepository(AnalyticsRepository):
    """
    Computes the same aggregations as MySQLAnalyticsRepository, but over
    plain Python Form/Response objects held in memory — built by sharing
    the same underlying dicts a FakeFormRepository/FakeResponseRepository
    would use, so tests can set up realistic scenarios without any DB.
    """

    def __init__(self, forms: dict[str, Form], responses: dict[str, Response]) -> None:
        self._forms = forms
        self._responses = responses

    def list_forms_with_response_counts(self, org_id: str) -> list[tuple[Form, int, str | None]]:
        results = []
        for form in self._forms.values():
            if form.org_id != org_id or form.is_template:
                continue
            form_responses = [r for r in self._responses.values() if r.form_id == form.id]
            latest = max((r.submitted_at for r in form_responses), default=None)
            results.append((form, len(form_responses), latest.isoformat() if latest else None))
        return results

    def count_responses_for_org(self, org_id: str) -> int:
        return len([r for r in self._responses.values() if r.org_id == org_id])

    def responses_by_day_for_org(self, org_id: str, days: int) -> list[DayCountRow]:
        return self._group_by_day([r for r in self._responses.values() if r.org_id == org_id])

    def get_form_with_fields(self, form_id: str, org_id: str) -> Form | None:
        form = self._forms.get(form_id)
        if form is None or form.org_id != org_id:
            return None
        return form

    def count_responses_for_form(self, form_id: str, org_id: str) -> int:
        return len(
            [r for r in self._responses.values() if r.form_id == form_id and r.org_id == org_id]
        )

    def responses_by_day_for_form(self, form_id: str, org_id: str, days: int) -> list[DayCountRow]:
        return self._group_by_day(
            [r for r in self._responses.values() if r.form_id == form_id and r.org_id == org_id]
        )

    def count_fully_answered_responses(self, form_id: str, org_id: str, required_field_ids: list[str]) -> int:
        responses = [r for r in self._responses.values() if r.form_id == form_id and r.org_id == org_id]
        if not required_field_ids:
            return len(responses)

        required = set(required_field_ids)
        count = 0
        for r in responses:
            answered = {a.field_id for a in r.answers if a.value != ""}
            if required.issubset(answered):
                count += 1
        return count

    def answered_count_for_field(self, field_id: str, org_id: str) -> int:
        count = 0
        for r in self._responses.values():
            if r.org_id != org_id:
                continue
            for a in r.answers:
                if a.field_id == field_id and a.value != "":
                    count += 1
        return count

    def choice_breakdown_for_field(self, field_id: str, org_id: str) -> list[ChoiceCountRow]:
        counts: dict[str, int] = {}
        for r in self._responses.values():
            if r.org_id != org_id:
                continue
            for a in r.answers:
                if a.field_id == field_id and a.value != "":
                    counts[a.value] = counts.get(a.value, 0) + 1
        rows = [ChoiceCountRow(value=v, count=c) for v, c in counts.items()]
        return sorted(rows, key=lambda row: row.count, reverse=True)

    def number_stats_for_field(self, field_id: str, org_id: str) -> NumberStatsRow:
        numbers: list[float] = []
        for r in self._responses.values():
            if r.org_id != org_id:
                continue
            for a in r.answers:
                if a.field_id == field_id and a.value != "":
                    try:
                        numbers.append(float(a.value))
                    except ValueError:
                        continue
        if not numbers:
            return NumberStatsRow(count=0, minimum=None, maximum=None, average=None)
        return NumberStatsRow(
            count=len(numbers), minimum=min(numbers), maximum=max(numbers), average=sum(numbers) / len(numbers)
        )

    def list_responses_for_export(self, form_id: str, org_id: str) -> list[Response]:
        responses = [
            r for r in self._responses.values() if r.form_id == form_id and r.org_id == org_id
        ]
        return sorted(responses, key=lambda r: r.submitted_at)

    @staticmethod
    def _group_by_day(responses: list[Response]) -> list[DayCountRow]:
        counts: dict[str, int] = {}
        for r in responses:
            day = r.submitted_at.date().isoformat()
            counts[day] = counts.get(day, 0) + 1
        return [DayCountRow(date=d, count=c) for d, c in sorted(counts.items())]
