"""
Pydantic schemas for the forms module.

These are the shapes that cross the HTTP boundary. Routers and services
talk in these types, never in raw ORM models — that keeps persistence
details (SQLAlchemy relationships, lazy loading) from leaking into the
API layer.
"""

from pydantic import BaseModel, Field, field_validator
from datetime import UTC, datetime

from app.forms.models import FieldType


class FieldCreate(BaseModel):
    label: str = Field(min_length=1, max_length=255)
    field_type: FieldType
    is_required: bool = True
    options: list[str] = Field(default_factory=list)

    @field_validator("options")
    @classmethod
    def choice_requires_options(cls, options: list[str], info) -> list[str]:
        field_type = info.data.get("field_type")
        if field_type == FieldType.CHOICE and len(options) < 2:
            raise ValueError("a 'choice' field needs at least two options")
        return options


class FieldRead(BaseModel):
    id: str
    label: str
    field_type: FieldType
    is_required: bool
    options: list[str]
    position: int

    model_config = {"from_attributes": True}


# Pydantic Model to validate "c.JSON" from Survey Form Save operation 
class FormCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    pages: list[dict] = Field(default_factory=list, min_length=1)


class FormRead(BaseModel):
    id: str
    title: str
    description: str | None
    schema_json: list

    model_config = {"from_attributes": True}


class FormSummary(BaseModel):
    """Lightweight shape for list views — avoids loading every field."""

    id: str
    title: str
    description: str | None
    schema_json: list
    total_questions: int
    created_at: datetime

    model_config = {"from_attributes": True}
