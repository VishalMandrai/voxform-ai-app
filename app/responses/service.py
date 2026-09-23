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
        form = self._forms.get_by_id(form_id, org_id=org_id)
        if form is None:
            raise NotFoundError(f"Form '{form_id}' not found")
        
        # Current Form Schema for transformation:
        current_form_schema = form.schema_json

        # fields_by_id: dict[str, Field] = {f.id: f for f in form.fields}
        # submitted_field_ids = {a.field_id for a in payload.answers}
        # self._validate_required_fields(form, submitted_field_ids)

        # Transform Raw User Response to Useful Format for DB save:
        final_result = self.transform_form_response(form_schema=current_form_schema, 
                                                    response_body=payload.answers)

        response = Response(
            form_id=form_id,
            org_id=org_id,
            respondent_id=respondent_id,
            response_schema=final_result,
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
            
            
    @staticmethod
    def transform_form_response(form_schema, response_body):
        """
        Convert a SurveyJS response body from question names to question titles.

        Example:
            {"question1": "Vishal"}

        becomes:
            {"First Name": "Vishal"}

        For choice-based questions such as dropdown/radiogroup/checkbox/tagbox,
        the stored value is converted to its corresponding display text.
        """

        # ---------------------------------------------------------
        # 1. Build a lookup of question name -> question metadata
        # ---------------------------------------------------------
        question_map = {}

        for page in form_schema:
            for element in page.get("elements", []):
                question_name = element.get("name")

                if not question_name:
                    continue

                question_map[question_name] = element

        # ---------------------------------------------------------
        # 2. Transform the submitted response
        # ---------------------------------------------------------
        transformed_response = {}

        for question_name, response_value in response_body.items():

            # If response contains a field that is not present
            # in the schema, preserve it as-is.
            if question_name not in question_map:
                transformed_response[question_name] = response_value
                continue

            question = question_map[question_name]

            question_title = question.get("title", question_name)
            question_type = question.get("type")

            # -----------------------------------------------------
            # 3. Handle choice-based questions
            # -----------------------------------------------------
            if question_type in {
                "dropdown",
                "radiogroup",
                "checkbox",
                "tagbox",
                "ranking"
            }:

                choices = question.get("choices", [])

                # Create:
                # {
                #     "Item 1": "Male",
                #     "Item 2": "Female"
                # }
                choice_map = {}

                for choice in choices:
                    if isinstance(choice, dict):
                        value = choice.get("value")
                        text = choice.get("text", value)

                        choice_map[value] = text
                    else:
                        # SurveyJS also allows choices such as:
                        # ["Male", "Female", "Other"]
                        choice_map[choice] = choice

                # Checkbox / Tagbox / Ranking can return a list
                if isinstance(response_value, list):
                    converted_value = [
                        choice_map.get(value, value)
                        for value in response_value
                    ]

                else:
                    converted_value = choice_map.get(
                        response_value,
                        response_value
                    )

            # -----------------------------------------------------
            # 4. Handle matrix questions
            # -----------------------------------------------------
            elif question_type == "matrix":

                # Matrix responses are generally dictionaries:
                #
                # {
                #     "Row 1": "Column 1",
                #     "Row 2": "Column 3"
                # }
                #
                # Keep the structure intact but convert values
                # where appropriate.

                converted_value = response_value

            # -----------------------------------------------------
            # 5. Everything else
            # -----------------------------------------------------
            else:
                converted_value = response_value

            # -----------------------------------------------------
            # 6. Use question title as the new key
            # -----------------------------------------------------
            transformed_response[question_title] = converted_value

        return transformed_response


## ---------------------------------------------------------------------------------------
## Will Transform this:
# {
#     "question1": "Vishal",
#     "question2": "Mandrai",
#     "question3": "Item 1",
#     "question4": "2000-06-30",
#     "question5": "1234567891",
#     "question6": "vishal@gmail.com",
#     "question7": "B-85 Kotra Sultanabad",
#     "question8": "Bhopal",
#     "question9": "Madhy Pradesh",
#     "question10": "India",
#     "question11": 462003,
#     "question12": "Vishal M",
#     "question13": "9981651950",
#     "question14": "Item 1",
#     "question15": "Item 1",
#     "question16": "New Member!!!",
#     "question17": 2500,
#     "question18": "2026-06-01",
#     "question19": "1500",
#     "question20": "2026-07-01",
#     "question21": "Item 3"
# }

## INTO:
# {
#     "First Name": "Vishal",
#     "Last Name": "Mandrai",
#     "Gender": "Male",
#     "Date of Birth": "2000-06-30",
#     "Phone Number": "1234567891",
#     "Email": "vishal@gmail.com",
#     "Street": "B-85 Kotra Sultanabad",
#     "City": "Bhopal",
#     "State": "Madhy Pradesh",
#     "Country": "India",
#     "Postal Code": 462003,
#     "Emergency Contact Name": "Vishal M",
#     "Emergency Contact Phone": "9981651950",
#     "Plan": "Monthly",
#     "Membership Status": "Active",
#     "Description": "New Member!!!",
#     "Fee": 2500,
#     "Start Date": "2026-06-01",
#     "Amount Paid": "1500",
#     "Due Date": "2026-07-01",
#     "Payment Status": "Partially Paid"
# }

## ---------------------------------------------------------------------------------------
