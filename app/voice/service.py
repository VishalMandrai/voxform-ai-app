"""
Voice processing orchestration.

VoiceService is constructed with three abstractions — AudioStorage,
Transcriber, FieldExtractor — and knows nothing about faster-whisper,
OpenAI, or the local filesystem. It only calls methods defined by those
interfaces. This is the clearest dependency-inversion seam in the app:
every one of those three concrete choices can change independently.
"""

from dataclasses import dataclass

from app.forms.models import Field
from app.voice.extractor import ExtractedValue, FieldExtractor
from app.voice.storage import AudioStorage
from app.voice.transcriber import Transcriber


@dataclass(frozen=True)
class VoiceFillResult:
    transcript: str
    extracted_values: list[dict]


class VoiceService:
    def __init__(
        self,
        storage: AudioStorage,
        transcriber: Transcriber,
        extractor: FieldExtractor,
    ) -> None:
        self._storage = storage
        self._transcriber = transcriber
        self._extractor = extractor

    def fill_form_from_audio(self, 
                             audio_bytes: bytes, 
                             filename: str, 
                             schema: list[dict], 
                             tot_quest: int,
                             ) -> VoiceFillResult:
        ## STEP 1: Save the Audio File in defined file location and get the file path
        audio_path = self._storage.save(audio_bytes, filename)
        
        ## STEP 2: Use Whisper Model to get the transcript from recorded audio
        transcription = self._transcriber.transcribe(audio_path)
        
        ## STEP 3: Now use LLM to fill in Survey Questionnaire from transcribed text        
        extracted = self._extractor.extract(transcription.text, schema, tot_quest)
        
        return VoiceFillResult(transcript=transcription.text, extracted_values=extracted)
