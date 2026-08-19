"""HTTP layer for form templates."""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth.dependencies import require_role
from app.auth.models import Role, User
from app.core.db import get_db
from app.core.exceptions import NotFoundError
from app.form_templates.schemas import CloneTemplateRequest, TemplateRead, TemplateSummary
from app.form_templates.service import TemplateService
from app.forms.repository import FormRepository, MySQLFormRepository
from app.forms.schemas import FormRead

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def get_form_repository(db: Session = Depends(get_db)) -> FormRepository:
    return MySQLFormRepository(db)


def get_template_service(repository: FormRepository = Depends(get_form_repository)) -> TemplateService:
    return TemplateService(repository)


# ---------------------------------------------------------------------------
# JSON API
# ---------------------------------------------------------------------------


# @router.get("/api/templates", response_model=list[TemplateSummary], tags=["templates"])
# def list_templates(
#     _current_user: User = Depends(require_role(Role.ORG_ADMIN)),
#     service: TemplateService = Depends(get_template_service),
# ) -> list[TemplateSummary]:
#     return [TemplateSummary.model_validate(t) for t in service.list_templates()]


# @router.get("/api/templates/{template_id}", response_model=TemplateRead, tags=["templates"])
# def get_template(
#     template_id: str,
#     _current_user: User = Depends(require_role(Role.ORG_ADMIN)),
#     service: TemplateService = Depends(get_template_service),
# ) -> TemplateRead:
#     try:
#         template = service.get_template(template_id)
#     except NotFoundError as exc:
#         raise HTTPException(status_code=404, detail=str(exc)) from exc
#     return TemplateRead.model_validate(template)


# @router.post("/api/templates/{template_id}/clone", response_model=FormRead, status_code=201, tags=["templates"])
# def clone_template(
#     template_id: str,
#     payload: CloneTemplateRequest,
#     current_user: User = Depends(require_role(Role.ORG_ADMIN)),
#     service: TemplateService = Depends(get_template_service),
# ) -> FormRead:
#     try:
#         form = service.clone_template(template_id, current_user.org_id, payload.title)
#     except NotFoundError as exc:
#         raise HTTPException(status_code=404, detail=str(exc)) from exc
#     return FormRead.model_validate(form)


# ---------------------------------------------------------------------------
# HTML pages
# ---------------------------------------------------------------------------


# @router.get("/templates", response_class=HTMLResponse, tags=["pages"])
# def template_gallery_page(
#     request: Request,
#     current_user: User = Depends(require_role(Role.ORG_ADMIN)),
#     service: TemplateService = Depends(get_template_service),
# ) -> HTMLResponse:
#     template_list = service.list_templates()
#     return templates.TemplateResponse(
#         request, "template_gallery.html", {"templates": template_list, "current_user": current_user}
#     )
