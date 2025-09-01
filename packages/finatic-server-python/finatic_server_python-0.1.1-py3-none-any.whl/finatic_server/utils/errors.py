"""Custom exception classes for the Finatic Server SDK."""

from typing import Any, Dict, Optional


class FinaticError(Exception):
    """Base exception for all Finatic SDK errors."""
    
    def __init__(self, message: str, code: Optional[str] = None):
        self.message = message
        self.code = code or "UNKNOWN_ERROR"
        super().__init__(self.message)


class ApiError(FinaticError):
    """Raised when an API request fails."""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None
    ):
        self.status_code = status_code
        self.response_data = response_data or {}
        super().__init__(message, f"API_ERROR_{status_code}" if status_code else "API_ERROR")


class AuthenticationError(FinaticError):
    """Raised when authentication fails."""
    pass

class AuthorizationError(FinaticError):
    """Raised when access is denied due to insufficient permissions."""
    pass

class ValidationError(FinaticError):
    """Raised when request validation fails."""
    pass


class RateLimitError(ApiError):
    """Raised when rate limits are exceeded."""
    
    def __init__(self, message: str, retry_after: Optional[int] = None):
        self.retry_after = retry_after
        super().__init__(message, 429)
        self.code = "RATE_LIMIT_ERROR"


class NetworkError(FinaticError):
    """Raised when network connectivity issues occur."""
    
    def __init__(self, message: str):
        super().__init__(message, "NETWORK_ERROR")


class TimeoutError(FinaticError):
    """Raised when requests timeout."""
    
    def __init__(self, message: str):
        super().__init__(message, "TIMEOUT_ERROR")


class OrderError(ApiError):
    """Raised when order operations fail."""
    
    def __init__(self, message: str, response_data: Optional[Dict[str, Any]] = None):
        super().__init__(message, 500, response_data)
        self.code = "ORDER_ERROR"


class OrderValidationError(ApiError):
    """Raised when order validation fails."""
    
    def __init__(self, message: str, response_data: Optional[Dict[str, Any]] = None):
        super().__init__(message, 400, response_data)
        self.code = "ORDER_VALIDATION_ERROR"


class CompanyAccessError(ApiError):
    """Raised when no broker connections are found."""
    
    def __init__(self, message: str, response_data: Optional[Dict[str, Any]] = None):
        super().__init__(message, 403, response_data)
        self.code = "COMPANY_ACCESS_ERROR" 