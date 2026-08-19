"""
Audio file persistence.

Kept separate from the transcriber on purpose: "where the file lives"
and "how it's transcribed" are different responsibilities. A future
phase storing uploads in S3 instead of local disk only needs a new
AudioStorage implementation.
"""

import uuid
from abc import ABC, abstractmethod
from pathlib import Path


class AudioStorage(ABC):
    @abstractmethod
    def save(self, content: bytes, original_filename: str) -> str:
        """Persist audio bytes and return a path/key the Transcriber can read."""
        ...


class LocalAudioStorage(AudioStorage):
    def __init__(self, base_dir: str) -> None:
        self._base_dir = Path(base_dir)
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, content: bytes, original_filename: str) -> str:
        suffix = Path(original_filename).suffix or ".wav"
        filename = f"{uuid.uuid4()}{suffix}"
        destination = self._base_dir / filename
        destination.write_bytes(content)
        return str(destination)
