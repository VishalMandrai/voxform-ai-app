"""
Domain exceptions.

Routers across all modules catch these and translate them to HTTP
responses (see each module's router.py). Services and repositories
raise these instead of generic Exception, so error handling stays
predictable as the app grows.
"""


class VoiceFormError(Exception):
    """Base class for all domain-level errors in this application."""


class NotAuthenticatedUser(VoiceFormError):
    """Raised when a user tries to open features before having itself properly authenticated."""
    
    
class SessionExpired(VoiceFormError):
    """Raised when user's Session Expires. User need to Log In again."""
    
    
class NotFoundError(VoiceFormError):
    """Raised when a requested entity does not exist."""


class ValidationError(VoiceFormError):
    """Raised when input fails a domain rule (not a framework-level schema check)."""


class TranscriptionError(VoiceFormError):
    """Raised when speech-to-text fails."""


class ExtractionError(VoiceFormError):
    """Raised when mapping a transcript onto form fields fails."""
