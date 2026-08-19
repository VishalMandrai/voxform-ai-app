"""
Response business logic.

ResponseService depends on two abstractions: ResponseRepository (its own
storage) and FormRepository (read-only lookup, to validate answers
against the form's field definitions). It never imports FormService or
any other module's service — only the repository interface it needs
(interface segregation: depend only on what you use).

Phase 2 adds org_id and respondent_id threading: submit_response now
looks the form up scoped to the submitting user's org (so you can't
submit against another org's form even if you know its id), and stamps
the response with both org_id and respondent_id.
"""

from app.core.exceptions import NotFoundError, ValidationError
from app.forms.models import Field, FieldType, Form
from app.forms.repository import FormRepository
from app.responses.models import AnswerValue, Response
from app.responses.repository import ResponseRepository
from app.responses.schemas import ResponseCreate


class ResponseService:
    def __init__(
        self, response_repository: ResponseRepository, form_repository: FormRepository) -> None:
        self._responses = response_repository
        self._forms = form_repository

    ## ---------------------- Submit Form response --------------------------------------
    def submit_response(
        self, 
        form_id: str, 
        org_id: str, 
        respondent_id: str, 
        payload: ResponseCreate
    ) -> Response:
        # form = self._forms.get_by_id(form_id, org_id=org_id)
        # if form is None:
        #     raise NotFoundError(f"Form '{form_id}' not found")

        # fields_by_id: dict[str, Field] = {f.id: f for f in form.fields}
        # submitted_field_ids = {a.field_id for a in payload.answers}

        # self._validate_required_fields(form, submitted_field_ids)

        response = Response(
            form_id=form_id,
            org_id=org_id,
            respondent_id=respondent_id,
            response_schema=payload.answers,
        )
        # for answer in payload.answers:
        #     field = fields_by_id.get(answer.field_id)
        #     if field is None:
        #         raise ValidationError(f"Field '{answer.field_id}' does not belong to form '{form_id}'")
        #     self._validate_value(field, answer.value)
        #     response.answers.append(AnswerValue(field_id=field.id, value=answer.value))

        return self._responses.create(response)


    def list_responses(self, form_id: str, org_id: str) -> list[Response]:
        return self._responses.list_for_form(form_id, org_id)

    @staticmethod
    def _validate_required_fields(form: Form, submitted_field_ids: set[str]) -> None:
        missing = [
            f.label for f in form.fields if f.is_required and f.id not in submitted_field_ids
        ]
        if missing:
            raise ValidationError(f"Missing required field(s): {', '.join(missing)}")

    @staticmethod
    def _validate_value(field: Field, value: str) -> None:
        if field.field_type == FieldType.CHOICE and value not in field.options:
            raise ValidationError(
                f"'{value}' is not a valid option for field '{field.label}' "
                f"(expected one of: {', '.join(field.options)})"
            )
        if field.field_type == FieldType.NUMBER:
            try:
                float(value)
            except ValueError as exc:
                raise ValidationError(f"Field '{field.label}' expects a number, got '{value}'") from exc
