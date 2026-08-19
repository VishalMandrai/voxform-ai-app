"""
ORM models for the forms domain.

Phase 1 deliberately has no `organization_id` column yet — multi-tenancy
arrives in Phase 2. Keeping that out now avoids half-built scoping logic
that would need to be redone anyway once auth/orgs exist.
"""

"""
ORM models for the forms domain.

Phase 2 adds two columns that didn't exist in Phase 1:
  - org_id: which organization owns this form. NULL for global templates
    (see app.form_templates), since templates aren't owned by any one org.
  - is_template: marks a form as a reusable template rather than a form
    org admins fill in/collect responses against directly. Cloning a
    template (see form_templates/service.py) copies its fields into a
    new, org-owned, is_template=False Form.

Multi-tenant scoping is enforced at the repository layer (every list/get
call takes an org_id and filters by it) — see repository.py. Routers and
services never construct raw queries themselves, so there's exactly one
place a missing org_id filter could slip through, and it's covered by
tests.
"""

import enum
import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Form(Base):
    __tablename__ = "forms"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    org_id: Mapped[str | None] = mapped_column(
        ForeignKey("organizations.id"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    schema_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    total_questions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_template: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)

    fields: Mapped[list["Field"]] = relationship(
        back_populates="form",
        cascade="all, delete-orphan",
        order_by="Field.position",
    )

    def __init__(self, **kwargs) -> None:
        """
        Assign the primary key eagerly on construction.

        SQLAlchemy's column-level `default=` only fires at INSERT/flush
        time, so a bare `Form(...)` built in plain Python (e.g. in a unit
        test against a fake repository, with no session involved) would
        otherwise have `id is None` until persisted. Domain objects should
        be valid the moment they're constructed, regardless of whether a
        database is involved — so the id is set here explicitly.
        """
        kwargs.setdefault("id", str(uuid.uuid4()))
        kwargs.setdefault("created_at", _utcnow())
        kwargs.setdefault("is_template", False)
        super().__init__(**kwargs)



class FieldType(str, enum.Enum):
    TEXT = "text"          # free text, e.g. name, address
    NUMBER = "number"       # numeric value, e.g. age, quantity
    CHOICE = "choice"        # single choice from a fixed set of options



class Field(Base):
    __tablename__ = "fields"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    form_id: Mapped[str] = mapped_column(ForeignKey("forms.id"), nullable=False)

    
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    field_type: Mapped[FieldType] = mapped_column(
        Enum(FieldType, values_callable=lambda enum_cls: [member.value for member in enum_cls]),
        nullable=False,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_required: Mapped[bool] = mapped_column(default=True)

    # Only populated when field_type == CHOICE. Stored as a comma-separated
    # string to keep Phase 1 simple — revisit as a child table if choice
    # options need their own metadata later.
    options_csv: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    form: Mapped["Form"] = relationship(back_populates="fields")

    def __init__(self, **kwargs) -> None:
        """Assign the primary key eagerly — see Form.__init__ for why."""
        kwargs.setdefault("id", str(uuid.uuid4()))
        super().__init__(**kwargs)

    @property
    def options(self) -> list[str]:
        if not self.options_csv:
            return []
        return [opt.strip() for opt in self.options_csv.split(",") if opt.strip()]
