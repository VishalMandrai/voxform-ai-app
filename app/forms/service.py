"""
Form business logic.

FormService depends only on the FormRepository ABSTRACTION — same
dependency-inversion seam as Phase 1. What's new in Phase 2 is that
every method now takes an org_id and passes it straight to the
repository, which is the actual enforcement point for tenant isolation.
FormService doesn't re-implement that filtering itself; it trusts the
repository contract, same as it always has.
"""

from app.core.exceptions import NotFoundError
from app.forms.models import Field, Form
from app.forms.repository import FormRepository
from app.responses.repository import ResponseRepository
from app.forms.schemas import FormCreate


class FormService:
    def __init__(self, 
                 repository: FormRepository,
                 form_repository: ResponseRepository) -> None:
        self._repository = repository
        self._form_repository = form_repository

    def create_form(self, org_id: str, payload: FormCreate) -> Form:
        # Calculating total questions in the survey form
        tot_ques = 0
        for page in payload.pages:
            tot_ques += len(page["elements"])
        
        form = Form(org_id=org_id, 
                    title=payload.title, 
                    description=payload.description,
                    schema_json=payload.pages,
                    total_questions=tot_ques,
                    )
        
        return self._repository.create(form)


    def get_form(self, form_id: str, org_id: str) -> Form:
        form = self._repository.get_by_id(form_id, org_id=org_id)
        if form is None:
            raise NotFoundError(f"Form '{form_id}' not found")
        return form


    def list_forms(self, org_id: str) -> list[Form]:
        return self._repository.list_for_org(org_id)


    def delete_form(self, form_id: str, org_id: str) -> None:
        ## First delete the responses and then the Form definition
        self._form_repository.delete(form_id, org_id)
        
        if not self._repository.delete(form_id, org_id):
            raise NotFoundError(f"Form '{form_id}' not found")
