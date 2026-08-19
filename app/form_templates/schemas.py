from pydantic import BaseModel

from app.forms.schemas import FieldRead


class TemplateSummary(BaseModel):
    id: str
    title: str
    description: str | None

    model_config = {"from_attributes": True}


class TemplateRead(BaseModel):
    id: str
    title: str
    description: str | None
    fields: list[FieldRead]

    model_config = {"from_attributes": True}


class CloneTemplateRequest(BaseModel):
    title: str | None = None
    """Optional override — if omitted, the cloned form keeps the template's title."""
