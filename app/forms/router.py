"""
HTTP layer for the forms module.

Every route now depends on an authenticated user (via
`app.auth.dependencies.get_current_user`) and passes `current_user.org_id`
into FormService — the router never accepts an org_id from the request
body or query string, so a caller can never claim to act on behalf of a
different org than the one their session token says they belong to.

Creating/deleting forms is restricted to ORG_ADMIN via `require_role`.
Viewing/filling a form is open to any authenticated user in the org
(respondents need to view a form to fill it by voice).
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_role
from app.auth.models import Role, User
from app.auth.schemas import UserRead
from app.core.db import get_db
from app.core.exceptions import NotFoundError, ValidationError
from app.forms.repository import FormRepository, MySQLFormRepository
from app.forms.schemas import FormCreate, FormRead, FormSummary
from app.forms.service import FormService

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def get_form_repository(db: Session = Depends(get_db)) -> FormRepository:
    """The only line in the app that names a concrete repository class."""
    return MySQLFormRepository(db)


def get_form_service(repository: FormRepository = Depends(get_form_repository)) -> FormService:
    return FormService(repository)


# ---------------------------------------------------------------------------
# JSON API
# ---------------------------------------------------------------------------

## To save these Forms in correct schema
@router.post("/api/forms", response_model=FormRead, status_code=201, tags=["forms"])
def create_form(
    payload: FormCreate,
    current_user: UserRead = Depends(require_role(Role.ORG_ADMIN)),
    service: FormService = Depends(get_form_service),
) -> FormRead:
    form = service.create_form(current_user.org_id, payload)
    return FormRead.model_validate(form)


## To get all the forms for an organization
@router.get("/api/forms", response_model=list[FormSummary], tags=["forms"])
def list_forms(
    current_user: UserRead = Depends(get_current_user), 
    service: FormService = Depends(get_form_service)
) -> list[FormSummary]:
    try:
        return [FormSummary.model_validate(f) for f in service.list_forms(current_user.org_id)]
    except ValidationError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


## Get the Form based on Form ID
@router.get("/api/forms/{form_id}", response_model=FormRead, tags=["forms"])
def get_form(
    form_id: str,
    current_user: UserRead = Depends(get_current_user),
    service: FormService = Depends(get_form_service),
) -> FormRead:
    try:
        form = service.get_form(form_id, current_user.org_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FormRead.model_validate(form)


@router.delete("/api/forms/{form_id}", status_code=204, tags=["forms"])
def delete_form(
    form_id: str,
    current_user: UserRead = Depends(require_role(Role.ORG_ADMIN)),
    service: FormService = Depends(get_form_service),
) -> None:
    try:
        service.delete_form(form_id, current_user.org_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc




# ---------------------------------------------------------------------------
# HTML / HTMX pages
# ---------------------------------------------------------------------------


# @router.get("/", response_class=HTMLResponse, tags=["pages"])
# def home_page(
#     request: Request,
#     current_user: User = Depends(get_current_user),
#     service: FormService = Depends(get_form_service),
# ) -> HTMLResponse:
#     forms = service.list_forms(current_user.org_id)
#     return templates.TemplateResponse(
#         request, "home.html", {"forms": forms, "current_user": current_user}
#     )


# @router.get("/forms/new", response_class=HTMLResponse, tags=["pages"])
# def new_form_page(
#     request: Request, current_user: User = Depends(require_role(Role.ORG_ADMIN))
# ) -> HTMLResponse:
#     return templates.TemplateResponse(request, "form_builder.html", {"current_user": current_user})


# @router.get("/forms/{form_id}", response_class=HTMLResponse, tags=["pages"])
# def fill_form_page(
#     request: Request,
#     form_id: str,
#     current_user: User = Depends(get_current_user),
#     service: FormService = Depends(get_form_service),
# ) -> HTMLResponse:
#     try:
#         form = service.get_form(form_id, current_user.org_id)
#     except NotFoundError as exc:
#         raise HTTPException(status_code=404, detail=str(exc)) from exc
#     return templates.TemplateResponse(
#         request, "fill_form.html", {"form": form, "current_user": current_user}
#     )
