"""
Persistence layer for forms.

`FormRepository` is the abstract interface — it defines WHAT the rest of
the app can do with form storage, not HOW. `MySQLFormRepository` is the
only implementation today.

Phase 2 multi-tenancy note: every read method takes `org_id` and filters
by it at the query level — this is the single enforcement point for "an
org can only see its own forms." Routers/services never bypass this by
querying the DB directly, so there is exactly one place to audit for
tenant isolation correctness (see tests/test_forms_org_scoping.py).

`get_by_id` accepts org_id=None to mean "look this form up regardless of
owner" — used only for template lookups (templates have org_id=NULL by
definition) and is never exposed on a route that takes a caller-supplied
org_id, so it can't be used to read across tenants.
"""

from abc import ABC, abstractmethod

from sqlalchemy.orm import Session, selectinload

from app.forms.models import Field, Form


class FormRepository(ABC):
    """Abstract contract for form persistence. Depend on this, not on a concrete DB class."""

    @abstractmethod
    def create(self, form: Form) -> Form: ...

    @abstractmethod
    def get_by_id(self, form_id: str, org_id: str | None) -> Form | None: ...

    @abstractmethod
    def list_for_org(self, org_id: str) -> list[Form]: ...

    @abstractmethod
    def list_templates(self) -> list[Form]: ...

    @abstractmethod
    def delete(self, form_id: str, org_id: str) -> bool: ...


class MySQLFormRepository(FormRepository):
    """SQLAlchemy/MySQL implementation of FormRepository."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, form: Form) -> Form:
        self._db.add(form)
        self._db.commit()
        self._db.refresh(form)
        return form

    def get_by_id(self, form_id: str, org_id: str | None) -> Form | None:
        query = self._db.query(Form).options(selectinload(Form.fields)).filter(Form.id == form_id)
        if org_id is not None:
            query = query.filter(Form.org_id == org_id)
        return query.first()

    def list_for_org(self, org_id: str) -> list[Form]:
        return (
            self._db.query(Form)
            .filter(Form.org_id == org_id, Form.is_template.is_(False))
            .order_by(Form.created_at.desc())
            .all()
        )

    def list_templates(self) -> list[Form]:
        return (
            self._db.query(Form)
            .options(selectinload(Form.fields))
            .filter(Form.is_template.is_(True))
            .order_by(Form.created_at.desc())
            .all()
        )

    def delete(self, form_id: str, org_id: str) -> bool:
        form = self._db.query(Form).filter(Form.id == form_id, Form.org_id == org_id).first()
        if form is None:
            return False
        self._db.delete(form)
        self._db.commit()
        return True


__all__ = ["FormRepository", "MySQLFormRepository", "Field"]
