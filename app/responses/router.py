"""HTTP layer for the responses module."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.schemas import UserRead
from app.core.db import get_db
from app.core.exceptions import NotFoundError, ValidationError
from app.forms.repository import FormRepository, MySQLFormRepository
from app.responses.repository import MySQLResponseRepository, ResponseRepository
from app.responses.schemas import ResponseCreate, ResponseRead, TotalResponses
from app.responses.service import ResponseService

router = APIRouter()


def get_form_repository(db: Session = Depends(get_db)) -> FormRepository:
    return MySQLFormRepository(db)


def get_response_repository(db: Session = Depends(get_db)) -> ResponseRepository:
    return MySQLResponseRepository(db)


def get_response_service(
    response_repository: ResponseRepository = Depends(get_response_repository),
    form_repository: FormRepository = Depends(get_form_repository),
) -> ResponseService:
    return ResponseService(response_repository, form_repository)




## ---- Endpoints -------------------------------------------------------------

@router.post("/api/forms/{form_id}/responses", 
             response_model=ResponseRead, 
             status_code=201, 
             tags=["responses"])
def submit_response(
    form_id: str,
    payload: ResponseCreate,
    current_user: UserRead = Depends(get_current_user),
    service: ResponseService = Depends(get_response_service),
) -> ResponseRead:
    try:
        response = service.submit_response(form_id, current_user.org_id, current_user.id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ResponseRead.model_validate(response)


@router.get("/api/forms/{form_id}/responses", response_model=list[ResponseRead], tags=["responses"])
def list_responses(
    form_id: str,
    current_user: UserRead = Depends(get_current_user),
    service: ResponseService = Depends(get_response_service),
) -> list[ResponseRead]:
    return [ResponseRead.model_validate(r) for r in service.list_responses(form_id, current_user.org_id)]


## Returns Total response count to user
@router.get("/api/forms/{form_id}/responsecount", response_model=TotalResponses, tags=["responses"])
def total_responses(
    form_id: str,
    current_user: UserRead = Depends(get_current_user),
    service: ResponseService = Depends(get_response_service),
) -> list[ResponseRead]:
    tot_resp = len([ResponseRead.model_validate(r) for r in service.list_responses(form_id, 
                                                                                   current_user.org_id)])
    
    return TotalResponses(form_id=form_id, count=tot_resp)