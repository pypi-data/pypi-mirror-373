"""Utility functions and classes for the Finatic Server SDK."""

from .errors import (
    FinaticError,
    ApiError,
    AuthenticationError,
    ValidationError,
    RateLimitError,
)

__all__ = [
    "FinaticError",
    "ApiError", 
    "AuthenticationError",
    "ValidationError",
    "RateLimitError",
] 