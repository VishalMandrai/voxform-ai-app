"""
Template business logic.

Deliberately depends on the SAME FormRepository abstraction that
FormService uses — a template is a Form (is_template=True, org_id=NULL),
so there's no need for a separate repository or a separate ORM table.
This keeps the templates feature from duplicating forms' persistence
logic; it only adds a different *operation* (clone) on the same store.

TemplateService never mutates a template in place — cloning always
creates a brand new Form/Field set owned by the requesting org, so one
org editing "their copy" can never affect the shared template or any
other org's copy.
"""

from app.core.exceptions import NotFoundError
from app.forms.models import Field, Form
from app.forms.repository import FormRepository


class TemplateService:
    def __init__(self, repository: FormRepository) -> None:
        self._repository = repository

    def list_templates(self) -> list[Form]:
        return self._repository.list_templates()

    def get_template(self, template_id: str) -> Form:
        template = self._repository.get_by_id(template_id, org_id=None)
        if template is None or not template.is_template:
            raise NotFoundError(f"Template '{template_id}' not found")
        return template

    def clone_template(self, template_id: str, org_id: str, title_override: str | None = None) -> Form:
        """Creates a new, org-owned Form by copying a template's fields."""
        template = self.get_template(template_id)

        cloned_form = Form(
            org_id=org_id,
            title=title_override or template.title,
            description=template.description,
            is_template=False,
        )
        for field in template.fields:
            cloned_form.fields.append(
                Field(
                    label=field.label,
                    field_type=field.field_type,
                    is_required=field.is_required,
                    options_csv=field.options_csv,
                    position=field.position,
                )
            )
        return self._repository.create(cloned_form)
