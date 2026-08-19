"""
HTTP layer for analytics.

Every route here is restricted to ORG_ADMIN — respondents fill forms,
they don't see aggregate stats about other respondents' answers. This
is enforced the same way as forms/templates: `Depends(require_role(...))`,
not a check inside the handler body.
"""

import json

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.analytics.csv_export import render_responses_csv
from app.analytics.repository import AnalyticsRepository, MySQLAnalyticsRepository
from app.analytics.schemas import FormDashboard, OrgOverview, AllResponsesForExp
from app.analytics.service import AnalyticsService
from app.auth.dependencies import require_role
from app.auth.schemas import UserRead
from app.auth.models import Role, User
from app.core.db import get_db
from app.core.exceptions import NotFoundError

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def get_analytics_repository(db: Session = Depends(get_db)) -> AnalyticsRepository:
    return MySQLAnalyticsRepository(db)


def get_analytics_service(
    repository: AnalyticsRepository = Depends(get_analytics_repository),
) -> AnalyticsService:
    return AnalyticsService(repository)


# ---------------------------------------------------------------------------
# JSON API
# ---------------------------------------------------------------------------


@router.get("/api/analytics/overview", response_model=OrgOverview, tags=["analytics"])
def get_org_overview(
    current_user: UserRead = Depends(require_role(Role.ORG_ADMIN)),
    service: AnalyticsService = Depends(get_analytics_service),
) -> OrgOverview:
    return service.get_org_overview(current_user.org_id)



## ----------  GET all responses for a particular Form  --------------------------------------------

@router.get("/api/analytics/forms/responses/{form_id}", tags=["analytics"])
def get_all_form_responses_for_export(
    form_id: str,
    current_user: UserRead = Depends(require_role(Role.ORG_ADMIN)),
    service: AnalyticsService = Depends(get_analytics_service),
) -> AllResponsesForExp:
    try:
        responses = service.get_response_rows(form_id, current_user.org_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    
    return AllResponsesForExp.model_validate(responses)



# @router.get("/api/analytics/forms/{form_id}", response_model=FormDashboard, tags=["analytics"])
# def get_form_dashboard(
#     form_id: str,
#     current_user: UserRead = Depends(require_role(Role.ORG_ADMIN)),
#     service: AnalyticsService = Depends(get_analytics_service),
# ) -> FormDashboard:
#     try:
#         return service.get_form_dashboard(form_id, current_user.org_id)
#     except NotFoundError as exc:
#         raise HTTPException(status_code=404, detail=str(exc)) from exc



# @router.get("/api/analytics/forms/{form_id}/export.csv", tags=["analytics"])
# def export_form_responses_csv(
#     form_id: str,
#     current_user: UserRead = Depends(require_role(Role.ORG_ADMIN)),
#     service: AnalyticsService = Depends(get_analytics_service),
# ) -> PlainTextResponse:
#     try:
#         form, rows = service.get_export_rows(form_id, current_user.org_id)
#     except NotFoundError as exc:
#         raise HTTPException(status_code=404, detail=str(exc)) from exc

#     csv_content = render_responses_csv(form, rows)
#     safe_title = "".join(c if c.isalnum() or c in "-_ " else "_" for c in form.title).strip() or "form"
#     filename = f"{safe_title}-responses.csv"
#     return PlainTextResponse(
#         content=csv_content,
#         media_type="text/csv",
#         headers={"Content-Disposition": f'attachment; filename="{filename}"'},
#     )
    
    


# ---------------------------------------------------------------------------
# HTML pages
# ---------------------------------------------------------------------------


# @router.get("/dashboard", response_class=HTMLResponse, tags=["pages"])
# def org_dashboard_page(
#     request: Request,
#     current_user: User = Depends(require_role(Role.ORG_ADMIN)),
#     service: AnalyticsService = Depends(get_analytics_service),
# ) -> HTMLResponse:
#     overview = service.get_org_overview(current_user.org_id)
#     return templates.TemplateResponse(
#         request,
#         "dashboard_overview.html",
#         {
#             "overview": overview,
#             "current_user": current_user,
#             "responses_by_day_json": json.dumps([d.model_dump() for d in overview.responses_by_day]),
#         },)


# @router.get("/dashboard/forms/{form_id}", response_class=HTMLResponse, tags=["pages"])
# def form_dashboard_page(
#     request: Request,
#     form_id: str,
#     current_user: User = Depends(require_role(Role.ORG_ADMIN)),
#     service: AnalyticsService = Depends(get_analytics_service),
# ) -> HTMLResponse:
#     try:
#         dashboard = service.get_form_dashboard(form_id, current_user.org_id)
#     except NotFoundError as exc:
#         raise HTTPException(status_code=404, detail=str(exc)) from exc
#     return templates.TemplateResponse(
#         request,
#         "dashboard_form.html",
#         {
#             "dashboard": dashboard,
#             "current_user": current_user,
#             "responses_by_day_json": json.dumps([d.model_dump() for d in dashboard.responses_by_day]),
#             "field_stats_json": json.dumps([f.model_dump() for f in dashboard.field_stats]),
#         },
#     )
