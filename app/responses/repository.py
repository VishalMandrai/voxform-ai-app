"""
Persistence layer for form responses.

Mirrors the forms module's pattern exactly: an abstract
ResponseRepository plus one MySQL implementation. `list_for_form` now
takes org_id and filters on it directly (the column is denormalized
onto Response — see models.py) so listing a form's responses can never
return another org's data even if a form_id were guessed/leaked.
"""

from abc import ABC, abstractmethod

from sqlalchemy.orm import Session, selectinload

from app.responses.models import Response


class ResponseRepository(ABC):
    @abstractmethod
    def create(self, response: Response) -> Response: ...

    @abstractmethod
    def get_by_id(self, response_id: str, org_id: str) -> Response | None: ...

    @abstractmethod
    def list_for_form(self, form_id: str, org_id: str) -> list[Response]: ...


class MySQLResponseRepository(ResponseRepository):
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, response: Response) -> Response:
        self._db.add(response)
        self._db.commit()
        self._db.refresh(response)
        return response

    def get_by_id(self, response_id: str, org_id: str) -> Response | None:
        return (
            self._db.query(Response)
            .options(selectinload(Response.answers))
            .filter(Response.id == response_id, Response.org_id == org_id)
            .first()
        )

    def list_for_form(self, form_id: str, org_id: str) -> list[Response]:
        return (
            self._db.query(Response)
            .options(selectinload(Response.answers))
            .filter(Response.form_id == form_id, Response.org_id == org_id)
            .order_by(Response.submitted_at.desc())
            .all()
        )
