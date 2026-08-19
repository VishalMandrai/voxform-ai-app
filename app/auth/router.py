"""HTTP layer for the auth module."""

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.auth.dependencies import (
    SESSION_COOKIE_NAME,
    get_auth_service,
    get_current_user,
    get_optional_current_user,
    require_role,
)
from app.auth.models import Role, User
from app.auth.schemas import (InviteAccept, 
                              InviteCreate, 
                              InviteRead, 
                              LoginRequest, 
                              SignUpRequest, 
                              UserRead,
                              UserFullDetails,
                              InviteStats, 
                              InviteTokenDetails)

from app.auth.service import AuthService
from app.core.config import get_settings
from app.core.exceptions import NotFoundError, ValidationError

router = APIRouter()
templates = Jinja2Templates(directory="templates")

COOKIE_MAX_AGE_SECONDS = 60 * 60 * 24 * 7  # 7 days, matches default JWT expiry


def _set_session_cookie(response: Response, token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=not settings.debug,  # secure cookies require HTTPS; relax only in local dev
        samesite="lax",
        max_age=COOKIE_MAX_AGE_SECONDS,
    )


# ---------------------------------------------------------------------------
# JSON API
# ---------------------------------------------------------------------------

@router.post("/api/auth/signup", response_model=UserRead, tags=["auth"])
def signup(
    payload: SignUpRequest, 
    auth_service: AuthService = Depends(get_auth_service)
) -> UserRead:
    try:
        user = auth_service.signup(payload.full_name,
                                    payload.org_name,
                                    payload.email, 
                                    payload.password)
    except ValidationError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    return UserRead(id=user.id, 
                    org_id=user.org_id,
                    role=user.role)


@router.post("/api/auth/login", response_model=UserRead, tags=["auth"])
def login(
    payload: LoginRequest, response: Response, 
    auth_service: AuthService = Depends(get_auth_service)
) -> UserRead:
    try:
        token = auth_service.login(payload.email, payload.password)
    except ValidationError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    _set_session_cookie(response, token)
    user = auth_service.get_current_user(token)
    return UserRead.model_validate(user)


@router.post("/api/auth/logout", status_code=204, tags=["auth"])
def logout(response: Response) -> None:
    response.delete_cookie(SESSION_COOKIE_NAME)


## For Authenticating User if it is in Session:
@router.get("/api/auth/me", response_model=UserRead, tags=["auth"])
def get_me(current_user: UserRead = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)


## For fetching complete User Details:
@router.get("/api/auth/userfulldet", response_model=UserFullDetails, tags=["auth"])
def get_user_details(current_user: UserRead = Depends(get_current_user),
                     auth_service: AuthService = Depends(get_auth_service)) -> UserFullDetails:
    try:
        details = auth_service.get_user_full_details(current_user.id)
    except ValidationError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
    
    return UserFullDetails.model_validate(details)


## ------------------------------------------------------------------------------------------------
## ------------------------------------------ INVITE Routes ---------------------------------------

@router.post("/api/auth/invites", response_model=InviteRead, status_code=201, tags=["auth"])
def create_invite(
    payload: InviteCreate,
    current_user: UserRead = Depends(require_role(Role.ORG_ADMIN)),
    auth_service: AuthService = Depends(get_auth_service),
) -> InviteRead:
    try:
        invite = auth_service.create_invite(current_user.org_id, current_user, payload)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return InviteRead(
        token=invite.token,
        email=invite.email,
        full_name=invite.full_name,
        role=invite.role,
        expires_at=invite.expires_at.isoformat())


@router.get("/api/auth/invites/accept/{token}", response_model=InviteTokenDetails, tags=["auth"])
def get_token_details(
    token: str,
    auth_service: AuthService = Depends(get_auth_service),
) -> InviteTokenDetails:
    try:
        new_member = auth_service.get_token_details(token)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return InviteTokenDetails.model_validate(new_member)


@router.post("/api/auth/invites/accept", response_model=UserRead, tags=["auth"])
def accept_invite(
    payload: InviteAccept, 
    response: Response, 
    auth_service: AuthService = Depends(get_auth_service)
) -> UserRead:
    try:
        token = auth_service.accept_invite(payload.token, payload.password)
    except (NotFoundError, ValidationError) as exc:
        status_code = 404 if isinstance(exc, NotFoundError) else 400
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc

    _set_session_cookie(response, token)
    user = auth_service.get_current_user(token)
    return UserRead.model_validate(user)


## Fetch total sent invites by the Organization:
@router.get("/api/auth/invites/all", response_model=InviteStats, tags=["auth"])
def get_me(current_user: UserRead = Depends(get_current_user),
           auth_service: AuthService = Depends(get_auth_service)) -> InviteStats:
    return auth_service.total_invites(current_user.org_id)


@router.get("/api/auth/users", response_model=list[UserFullDetails], tags=["auth"])
def list_org_users(
    current_user: UserRead = Depends(require_role(Role.ORG_ADMIN)),
    auth_service: AuthService = Depends(get_auth_service),
) -> list[UserFullDetails]:
    
    users_list = [UserFullDetails(id = u.id, 
                                  org_id = u.org_id, 
                                  org_name = "org",
                                  email = u.email,
                                  full_name = u.full_name,
                                  role = u.role) for u in auth_service.list_org_users(current_user.org_id)]

    users = sorted(
        users_list, 
        key=lambda u: (u.role, u.full_name)
    )
    
    return users


# ---------------------------------------------------------------------------
# HTML pages
# ---------------------------------------------------------------------------


# @router.get("/login", response_class=HTMLResponse, tags=["pages"])
# def login_page(
#     request: Request, current_user: User | None = Depends(get_optional_current_user)
# ) -> HTMLResponse:
#     return templates.TemplateResponse(request, "login.html", {"current_user": current_user})


# @router.get("/logout", tags=["pages"])
# def logout_page() -> RedirectResponse:
#     response = RedirectResponse(url="/login", status_code=302)
#     response.delete_cookie(SESSION_COOKIE_NAME)
#     return response


# @router.get("/invite/{token}", response_class=HTMLResponse, tags=["pages"])
# def accept_invite_page(
#     request: Request, token: str, current_user: User | None = Depends(get_optional_current_user)
# ) -> HTMLResponse:
#     return templates.TemplateResponse(
#         request, "accept_invite.html", {"token": token, "current_user": current_user}
#     )


# @router.get("/team", response_class=HTMLResponse, tags=["pages"])
# def team_page(
#     request: Request,
#     current_user: User = Depends(require_role(Role.ORG_ADMIN)),
#     auth_service: AuthService = Depends(get_auth_service),
# ) -> HTMLResponse:
#     users = auth_service.list_org_users(current_user.org_id)
#     return templates.TemplateResponse(request, "team.html", {"users": users, "current_user": current_user})
