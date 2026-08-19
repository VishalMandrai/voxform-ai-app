"""
Application entrypoint.

This is the project's composition root: the one file that knows about
every module's router. Individual modules never import each other's
routers — they're assembled here and nowhere else, so each module stays
independently testable and could be split into a separate service later
without restructuring its internals.

Phase 3 adds the analytics router alongside Phase 1's
forms/voice/responses and Phase 2's auth/form_templates. analytics
introduces no new ORM tables — it reads forms/responses/answer_values,
already imported below — so there's nothing new to add to create_all.
Every protected route's auth enforcement lives in each module's own
router (via Depends(get_current_user) / require_role) — main.py only
assembles, it never adds cross-cutting auth logic itself.
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.analytics.router import router as analytics_router
from app.auth.router import router as auth_router
from app.core.config import get_settings
from app.core.db import Base, engine
from app.core.exceptions import NotAuthenticatedUser, SessionExpired, ValidationError

from app.form_templates.router import router as templates_router
from app.forms.router import router as forms_router
from app.responses.router import router as responses_router
from app.voice.router import router as voice_router

# Import models so SQLAlchemy's metadata knows about every table before "create_all".
from app.auth import models as _auth_models  # noqa: F401
from app.forms import models as _forms_models  # noqa: F401
from app.responses import models as _responses_models  # noqa: F401

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Create tables on startup for local development convenience.

    Phase 3 (or earlier, if real data shows up sooner) should replace
    this with proper Alembic migrations — auto create_all is fine for a
    prototype but unsafe once there's real data to preserve across
    schema changes.

    This deliberately swallows connection failures rather than crashing
    the whole app on boot: integration tests construct their own
    SQLite-backed session via dependency override and never touch this
    module-level `engine` at all, so a missing MySQL server in that
    context is expected, not an error.
    """
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:  # noqa: BLE001 — startup convenience, not a hard requirement
        logger.warning(
            "Could not create tables against the configured database. "
            "If you're running tests with an overridden DB session this is expected; "
            "otherwise check DATABASE_URL in your .env.",
            exc_info=True,
        )
    yield


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)


# ── CORS ─────────────────────────────────────────────────────────
if settings.debug:
    ## Permissive in Development; lock down origins in Production via ENV var.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        )

# ─────────────────────────────────────────────────────────────────
# Add routers to the App
# ─────────────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(forms_router)
app.include_router(templates_router)
app.include_router(voice_router)
app.include_router(responses_router)
app.include_router(analytics_router)


# ─────────────────────────────────────────────────────────────────
# Next.js static frontend
# ─────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend" / "out"

app.frontend(
    "/",
    directory=FRONTEND_DIR,
)


# ─────────────────────────────────────────────────────────────────
# Health Checker
# ─────────────────────────────────────────────────────────────────
@app.get("/health", tags=["meta"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}

print("-----------------------------------------------")
print(settings.whisper_api_key , settings.LLM_api_key)
print("-----------------------------------------------")

# ─────────────────────────────────────────────────────────────────
# App level Error Handlers
# ─────────────────────────────────────────────────────────────────
@app.exception_handler(NotAuthenticatedUser)
async def Not_Authenticated_User(request: Request, exc: NotAuthenticatedUser):
    response = JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "user_not_authenticated_error", "detail": str(exc)},
    )
    return response


@app.exception_handler(SessionExpired)
async def User_sesssion_expired(request: Request, exc: SessionExpired):
    response = JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"error": "user_session_expired", "detail": str(exc)},
    )
    return response


@app.exception_handler(ValidationError)
async def User_JWT_validation_failed(request: Request, exc: ValidationError):
    response = JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": "user_jwt_validation_failed", "detail": str(exc)},
    )
    return response