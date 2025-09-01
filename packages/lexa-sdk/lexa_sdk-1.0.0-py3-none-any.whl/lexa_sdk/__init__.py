"""
Python SDK for Lexa AI

This package provides both:
1. Provider-based interface for advanced usage
2. OpenAI-compatible interface for easy drop-in replacement
"""

from .client import Lexa
from .provider import LexaProvider
from .language_model import LexaLanguageModel
from .models import (
    LexaMessage,
    LexaResponse,
    LexaStreamChunk,
    ModelInfo,
    LexaUsage,
)
from .exceptions import (
    LexaError,
    LexaAPIError,
    LexaRateLimitError,
    LexaAuthenticationError,
    LexaValidationError,
)

__version__ = "1.0.0"
__all__ = [
    # Main classes
    "Lexa",
    "LexaProvider", 
    "LexaLanguageModel",
    
    # Type definitions
    "LexaMessage",
    "LexaResponse",
    "LexaStreamChunk",
    "ModelInfo",
    "LexaUsage",
    
    # Exceptions
    "LexaError",
    "LexaAPIError", 
    "LexaRateLimitError",
    "LexaAuthenticationError",
    "LexaValidationError",
]
