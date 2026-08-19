"""
ORM models for submitted form responses.

A Response groups one submission; each AnswerValue holds one field's
answer. Kept normalised (one row per field) rather than a JSON blob so
Phase 3's analytics module can run real SQL aggregations per field
without parsing JSON in the database layer.
"""

"""
ORM models for submitted form responses.

A Response groups one submission; each AnswerValue holds one field's
answer. Kept normalised (one row per field) rather than a JSON blob so
Phase 3's analytics module can run real SQL aggregations per field
without parsing JSON in the database layer.

Phase 2 adds org_id (denormalized from the parent Form, so responses
can be filtered by tenant with a direct column match rather than a join
every time) and respondent_id (who submitted it — nullable, since Phase
1-style anonymous submission isn't supported anymore but the column
stays optional in case a future "public link, no login" mode returns).
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Response(Base):
    __tablename__ = "responses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    form_id: Mapped[str] = mapped_column(ForeignKey("forms.id"), nullable=False)
    response_schema: Mapped[dict] = mapped_column(JSON, nullable=False)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True)
    respondent_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)
    raw_transcript: Mapped[str | None] = mapped_column(Text, nullable=True)

    answers: Mapped[list["AnswerValue"]] = relationship(
        back_populates="response", cascade="all, delete-orphan"
    )

    def __init__(self, **kwargs) -> None:
        """Assign id/submitted_at eagerly — see forms.models.Form.__init__ for why."""
        kwargs.setdefault("id", str(uuid.uuid4()))
        kwargs.setdefault("submitted_at", _utcnow())
        super().__init__(**kwargs)



class AnswerValue(Base):
    __tablename__ = "answer_values"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    response_id: Mapped[str] = mapped_column(ForeignKey("responses.id"), nullable=False)
    field_id: Mapped[str] = mapped_column(ForeignKey("fields.id"), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)

    response: Mapped["Response"] = relationship(back_populates="answers")

    def __init__(self, **kwargs) -> None:
        """Assign id eagerly — see forms.models.Form.__init__ for why."""
        kwargs.setdefault("id", str(uuid.uuid4()))
        super().__init__(**kwargs)
