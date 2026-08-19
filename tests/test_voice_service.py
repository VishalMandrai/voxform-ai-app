"""
Tests for VoiceService.

Notice that none of these tests touch faster_whisper or openai — they
inject trivial fakes implementing Transcriber/FieldExtractor/AudioStorage.
If VoiceService could only be tested by loading a real Whisper model,
that would be a sign the abstraction had leaked; here it hasn't.
"""

from app.forms.models import Field, FieldType
from app.voice.extractor import ExtractedValue, FieldExtractor
from app.voice.service import VoiceService
from app.voice.storage import AudioStorage
from app.voice.transcriber import Transcriber, TranscriptionResult


class FakeAudioStorage(AudioStorage):
    def __init__(self) -> None:
        self.saved: list[bytes] = []

    def save(self, content: bytes, original_filename: str) -> str:
        self.saved.append(content)
        return f"/fake/path/{original_filename}"


class FakeTranscriber(Transcriber):
    def __init__(self, text: str = "my name is Asha and I am 34 years old") -> None:
        self._text = text

    def transcribe(self, audio_path: str) -> TranscriptionResult:
        return TranscriptionResult(text=self._text, language="en")


class FakeExtractor(FieldExtractor):
    def extract(self, transcript: str, fields: list[Field]) -> list[ExtractedValue]:
        # Trivial fake: pretend we found a value for every field.
        return [ExtractedValue(field_id=f.id, value="stub-value", confidence=0.9) for f in fields]


def make_field(label: str, field_type: FieldType = FieldType.TEXT) -> Field:
    field = Field(label=label, field_type=field_type)
    field.id = f"field-{label}"
    return field


def test_fill_form_from_audio_returns_transcript_and_extracted_values():
    storage = FakeAudioStorage()
    service = VoiceService(storage=storage, transcriber=FakeTranscriber(), extractor=FakeExtractor())
    fields = [make_field("Name"), make_field("Age", FieldType.NUMBER)]

    result = service.fill_form_from_audio(b"fake-audio-bytes", "recording.webm", fields)

    assert result.transcript == "my name is Asha and I am 34 years old"
    assert len(result.extracted_values) == 2
    assert storage.saved == [b"fake-audio-bytes"]


def test_fill_form_from_audio_with_no_fields_extracts_nothing():
    service = VoiceService(
        storage=FakeAudioStorage(), transcriber=FakeTranscriber(), extractor=FakeExtractor()
    )

    result = service.fill_form_from_audio(b"audio", "f.webm", fields=[])

    assert result.extracted_values == []
