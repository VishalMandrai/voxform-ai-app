"""
Speech-to-text.

`Transcriber` is the abstraction every caller depends on. Today there is
one implementation, `FasterWhisperTranscriber`, running a self-hosted
model. If a later phase needs a cloud STT API instead (or a queue-backed
async transcriber for scale), that becomes a new class implementing this
same interface — VoiceService and the router below it do not change.
"""
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.core.exceptions import TranscriptionError


@dataclass(frozen=True)
class TranscriptionResult:
    text: str
    language: str | None = None


class Transcriber(ABC):
    """Abstract contract: turn an audio file on disk into text."""

    @abstractmethod
    def transcribe(self, audio_path: str) -> TranscriptionResult: ...


class FasterWhisperTranscriber(Transcriber):
    """
    Self-hosted transcription using faster-whisper.

    The underlying WhisperModel is loaded lazily on first use and cached
    on the instance — model loading is expensive and we want exactly one
    load per process, not once per request.
    """

    def __init__(self, 
                 model_size: str = "base", 
                 device: str = "cpu", 
                 compute_type: str = "int8",
                 language: str = None) -> None:
        self._model_size = model_size
        self._device = device
        self._compute_type = compute_type
        self._lang= language
        self._model = None  # lazy-loaded

    def _get_model(self):
        if self._model is None:
            from faster_whisper import WhisperModel  # imported lazily: heavy dependency

            self._model = WhisperModel(
                self._model_size, device=self._device, compute_type=self._compute_type
            )
        
        return self._model

    def transcribe(self, audio_path: str) -> TranscriptionResult:
        try:
            model = self._get_model()
            segments, info = model.transcribe(audio_path, 
                                              language=self._lang,    # we can keep it "en" as default in settings
                                              beam_size=5,            # Higher = more accurate but slower
                                              vad_filter=False,       # Voice Activity Detection: skip silence
                                              vad_parameters=dict(
                                                    min_silence_duration_ms=500,   # Ignore silences < 500ms
                                                    speech_pad_ms=400,             # Pad speech boundaries by 400ms
                                                ),
                                              )
            text = " ".join(segment.text.strip() for segment in segments).strip()
        except Exception as exc:  # noqa: BLE001 — re-raised as a domain error below
            raise TranscriptionError(f"Failed to transcribe audio: {exc}") from exc

        if not text:
            raise TranscriptionError("Transcription produced no text — audio may be empty or unclear")

        return TranscriptionResult(text=text, language=getattr(info, "language", None))



## -----------------------------------------------------------------------------------------
## --------------------------------------- API ---------------------------------------------

class GroqWhisperTranscriber(Transcriber):
    """
    Self-hosted transcription using faster-whisper.

    The underlying WhisperModel is loaded lazily on first use and cached
    on the instance — model loading is expensive and we want exactly one
    load per process, not once per request.
    """

    def __init__(self, 
                    api_key: str, 
                    model: str = "whisper-large-v3-turbo",
                    language: str = "en",
                    temperature: float = 0.0,
                    ) -> None:
        self._api_key = api_key
        self._model = model
        self._lang= language
        self._temp = temperature
        self._client = None                 # lazy-loaded

    def _get_client(self):
        if self._client is None:
            from groq import Groq  # imported lazily: avoid import cost when unused

            self._client = Groq(api_key=self._api_key)
        return self._client
    
    
    def transcribe(self, audio_path: str) -> TranscriptionResult:
        try:
            client = self._get_client()
            
            ## Open the audio file
            with open(audio_path, "rb") as file:
                # Create a transcription of the audio file
                transcription = client.audio.transcriptions.create(
                                        file=file,                           # Required audio file
                                        model=self._model,                   # Model for transcription
                                        prompt="Transcribe the speech in English",     # Optional
                                        response_format="verbose_json",                # Optional
                                        timestamp_granularities = ["word", "segment"], # Optional (must set response_format to "json" to use and can specify "word", "segment" (default), or both)
                                        language=self._lang,                           # Optional
                                        temperature=self._temp,                        # Optional
                                        )
                ## To print only the transcription text, you'd use print(transcription.text)
            
            ## Delete Audio File 
            os.remove(audio_path)
                
        except Exception as exc:  # noqa: BLE001 — re-raised as a domain error below
            raise TranscriptionError(f"Failed to transcribe audio: {exc}") from exc

        if not transcription.text:
            raise TranscriptionError("Transcription produced no text — audio may be empty or unclear")

        return TranscriptionResult(text=transcription.text, language=self._lang)