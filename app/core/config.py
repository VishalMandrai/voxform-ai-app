"""
Centralised application configuration.

Every other module reads settings from here rather than calling
os.environ directly. This means configuration sourcing (env vars today,
maybe a secrets manager tomorrow) can change without touching any
business logic — a small but real application of the
Single Responsibility / Dependency Inversion mindset.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- Database ----------------------------------------------------- 
    database_url: str = "mysql+pymysql://voiceform:voiceform@localhost:3306/voiceform"

    # --- Voice / Whisper ----------------------------------------------
    whisper_model_size: str = "small"          # tiny | base | small | medium | large-v3
    whisper_device: str = "cpu"                # cpu | cuda
    whisper_compute_type: str = "int8"         # int8 | float16 | float32
    whisper_allowed_language: str = "en"       # en - English | None - to detect and transcribe on the go
    audio_upload_dir: str = "./uploaded_audio"
    max_audio_size_mb: int = 25
    
    
    # --- Groq Whisper API ---------------------------------------------  
    whisper_api_key: str = ""
    whisper_api_model: str = "whisper-large-v3-turbo"
    whisper_api_language: str = "en"
    whisper_api_temperature: float = 0.0


    # --- Field extraction (OpenAI) -----------------------------------
    LLM_api_key: str = ""
    LLM_model: str = "openai/gpt-oss-20b"


    # --- Auth / JWT --------------------------------------------------
    jwt_secret_key: str = ""
    jwt_expires_minutes: int = 60 * 24 * 7                  # 7 days


    # --- App ---------------------------------------------------------
    app_name: str = "VoxForm_AI"
    debug: bool = True



@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor — avoids re-parsing env on every call."""
    return Settings()
