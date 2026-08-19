"""
HTTP layer for the voice module.

This is the one place in the app that decides which concrete
Transcriber/FieldExtractor/AudioStorage implementations to use. The
heavy objects (Whisper model, OpenAI client) are cached at module level
via lru_cache so the model loads once per process, not once per
request — VoiceService itself stays stateless-per-call.
"""

from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from pydantic import BaseModel

from app.auth.dependencies import get_current_user
from app.auth.schemas import UserRead
from app.auth.models import User
from app.core.config import Settings, get_settings
from app.core.exceptions import ExtractionError, NotFoundError, TranscriptionError
from app.core.db import get_db
from app.forms.repository import FormRepository, MySQLFormRepository
from app.forms.service import FormService
from app.voice.extractor import FieldExtractor, GroqOpenAIFieldExtractor
from app.voice.service import VoiceService
from app.voice.storage import AudioStorage, LocalAudioStorage
from app.voice.transcriber import FasterWhisperTranscriber, GroqWhisperTranscriber, Transcriber
from sqlalchemy.orm import Session

router = APIRouter()


# ---------------------------------------------------------------------------
# Dependency wiring — singletons for expensive objects, request-scoped for the rest
# ---------------------------------------------------------------------------


@lru_cache
def get_transcriber_model() -> Transcriber:
    settings = get_settings()
    return FasterWhisperTranscriber(
        model_size=settings.whisper_model_size,
        device=settings.whisper_device,
        compute_type=settings.whisper_compute_type,
        language=settings.whisper_allowed_language,
    )


@lru_cache
def get_transcriber_groq_api() -> Transcriber:
    settings = get_settings()
    return GroqWhisperTranscriber(
        api_key=settings.whisper_api_key,
        model=settings.whisper_api_model,
        language=settings.whisper_api_language,
        temperature=settings.whisper_api_temperature,
    )
    

@lru_cache
def get_extractor() -> FieldExtractor:
    settings = get_settings()
    return GroqOpenAIFieldExtractor(api_key=settings.LLM_api_key, model=settings.LLM_model)


@lru_cache
def get_audio_storage() -> AudioStorage:
    settings = get_settings()
    return LocalAudioStorage(base_dir=settings.audio_upload_dir)


def get_voice_service(
    transcriber: Transcriber = Depends(get_transcriber_groq_api),
    extractor: FieldExtractor = Depends(get_extractor),
    storage: AudioStorage = Depends(get_audio_storage),
) -> VoiceService:
    return VoiceService(storage=storage, transcriber=transcriber, extractor=extractor)


def get_form_repository(db: Session = Depends(get_db)) -> FormRepository:
    return MySQLFormRepository(db)


def get_form_service(repository: FormRepository = Depends(get_form_repository)) -> FormService:
    return FormService(repository)


# ---------------------------------------------------------------------------
# Response schema
# ---------------------------------------------------------------------------


class ExtractedFieldOut(BaseModel):
    field_id: str
    value: str
    confidence: float


class VoiceFillResponse(BaseModel):
    transcript: str
    extracted: list[dict]


class CHECKVoiceFillResponse(BaseModel):
    transcript: str

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.post("/api/voice/forms/{form_id}/fill", response_model=VoiceFillResponse, tags=["voice"])
async def fill_form_from_audio(
    form_id: str,
    audio: UploadFile,
    settings: Settings = Depends(get_settings),
    current_user: UserRead = Depends(get_current_user),
    form_service: FormService = Depends(get_form_service),
    voice_service: VoiceService = Depends(get_voice_service),
) -> VoiceFillResponse:
    ## Get the Survey Form - Later be used for getting Form Schema & other details
    try:
        form = form_service.get_form(form_id, current_user.org_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    ## Process Audio and get it ready for transcription
    audio_bytes = await audio.read()
    size_mb = len(audio_bytes) / (1024 * 1024)
    if size_mb > settings.max_audio_size_mb:
        raise HTTPException(
            status_code=413,
            detail=f"Audio file too large ({size_mb:.1f}MB) — limit is {settings.max_audio_size_mb}MB",
        )
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio upload")

    
    ## Voice transcription & LLM based info extraction
    try:
        result = voice_service.fill_form_from_audio(
            audio_bytes=audio_bytes,
            filename=audio.filename or "audio.wav",
            schema=form.schema_json,
            tot_quest=form.total_questions,
        )
    except TranscriptionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ExtractionError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return VoiceFillResponse(
        transcript=result.transcript,
        extracted=result.extracted_values,
    )



# ---------------------------------------------------------------------------
# @router.post("/api/voice/forms/{form_id}/fill", response_model=VoiceFillResponse, tags=["voice"])
# async def fill_form_from_audio(
#     form_id: str,
#     audio: UploadFile,
#     settings: Settings = Depends(get_settings),
#     current_user: dict = Depends(get_current_user),
#     form_service: FormService = Depends(get_form_service),
#     voice_service: VoiceService = Depends(get_voice_service),
# ) -> VoiceFillResponse:
#     try:
#         form = form_service.get_form(form_id, current_user["org_id"])
#     except NotFoundError as exc:
#         raise HTTPException(status_code=404, detail=str(exc)) from exc

#     audio_bytes = await audio.read()
#     size_mb = len(audio_bytes) / (1024 * 1024)
#     if size_mb > settings.max_audio_size_mb:
#         raise HTTPException(
#             status_code=413,
#             detail=f"Audio file too large ({size_mb:.1f}MB) — limit is {settings.max_audio_size_mb}MB",
#         )
#     if not audio_bytes:
#         raise HTTPException(status_code=400, detail="Empty audio upload")

#     try:
#         result = voice_service.fill_form_from_audio(
#             audio_bytes=audio_bytes,
#             filename=audio.filename or "audio.wav",
#             fields=form.fields,
#         )
#     except TranscriptionError as exc:
#         raise HTTPException(status_code=422, detail=str(exc)) from exc
#     except ExtractionError as exc:
#         raise HTTPException(status_code=502, detail=str(exc)) from exc

#     return VoiceFillResponse(
#         transcript=result.transcript,
#         extracted=[
#             ExtractedFieldOut(field_id=v.field_id, value=v.value, confidence=v.confidence)
#             for v in result.extracted_values
#         ],
#     )

