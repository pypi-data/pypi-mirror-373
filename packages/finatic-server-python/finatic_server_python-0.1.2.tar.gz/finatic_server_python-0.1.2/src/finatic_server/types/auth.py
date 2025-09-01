"""Authentication-related type definitions."""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class UserToken(BaseModel):
    """User authentication token information."""
    
    access_token: str = Field(..., description="Access token")
    refresh_token: str = Field(..., description="Refresh token")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user_id: str = Field(..., description="User ID")
    token_type: str = Field(default="Bearer", description="Token type")
    scope: str = Field(default="", description="Token scope")


class SessionResponseData(BaseModel):
    """Session response data structure."""
    
    session_id: str = Field(..., description="Unique session identifier")
    state: Optional[str] = Field(None, description="Session state (PENDING, ACTIVE, etc.)")
    device_info: Optional[Dict[str, str]] = Field(None, description="Device information")
    company_id: Optional[str] = Field(None, description="Company ID")
    status: Optional[str] = Field(None, description="Session status")
    expires_at: Optional[str] = Field(None, description="Session expiration time")
    user_id: Optional[str] = Field(None, description="User ID")
    auto_login: Optional[bool] = Field(None, description="Auto login flag")
    access_token: Optional[str] = Field(None, description="Access token")
    refresh_token: Optional[str] = Field(None, description="Refresh token")
    expires_in: Optional[int] = Field(None, description="Token expiration time in seconds")
    token_type: Optional[str] = Field(None, description="Token type")
    scope: Optional[str] = Field(None, description="Token scope")


class SessionResponse(BaseModel):
    """Session initialization response."""
    
    # Handle both nested data structure and flat structure
    data: Optional[SessionResponseData] = Field(None, description="Session data (nested)")
    message: Optional[str] = Field(None, description="Response message")
    
    # Flat structure fields (for direct API responses)
    session_id: Optional[str] = Field(None, description="Session ID (flat structure)")
    auto_login: Optional[bool] = Field(None, description="Auto login flag (flat structure)")
    company_id: Optional[str] = Field(None, description="Company ID (flat structure)")
    state: Optional[str] = Field(None, description="Session state (flat structure)")
    
    model_config = {"populate_by_name": True}


class SessionInitResponse(BaseModel):
    """Session initialization response from API key."""
    
    success: bool = Field(..., description="Request success status")
    message: str = Field(..., description="Response message")
    data: Dict[str, Any] = Field(..., description="Response data containing one_time_token")


class OtpRequestResponse(BaseModel):
    """OTP request response."""
    
    success: bool = Field(..., description="Request success status")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")


class OtpVerifyResponse(BaseModel):
    """OTP verification response."""
    
    success: bool = Field(..., description="Request success status")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data with tokens")


class SessionAuthenticateResponse(BaseModel):
    """Session authentication response."""
    
    success: bool = Field(..., description="Request success status")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data with tokens")


class PortalUrlResponse(BaseModel):
    """Portal URL response."""
    
    success: bool = Field(..., description="Request success status")
    message: str = Field(..., description="Response message")
    data: Dict[str, str] = Field(..., description="Response data containing portal_url")


class SessionValidationResponse(BaseModel):
    """Session validation response."""
    
    valid: bool = Field(..., description="Whether the session is valid")
    company_id: str = Field(..., description="Company ID")
    status: str = Field(..., description="Session status")


class SessionUserResponse(BaseModel):
    """Response when getting user info from completed session."""
    
    success: bool = Field(..., description="Request success status")
    message: str = Field(..., description="Response message")
    data: Dict[str, Any] = Field(..., description="Response data containing user info and tokens")
    
    def get_user_id(self) -> str:
        """Get user ID from the data object."""
        return self.data['user_id']
    
    def get_access_token(self) -> str:
        """Get access token from the data object."""
        return self.data['access_token']
    
    def get_refresh_token(self) -> str:
        """Get refresh token from the data object."""
        return self.data['refresh_token']
    
    def get_expires_in(self) -> int:
        """Get expires_in from the data object."""
        return self.data['expires_in']
    
    def get_token_type(self) -> str:
        """Get token type from the data object."""
        return self.data['token_type']
    
    def get_scope(self) -> str:
        """Get scope from the data object."""
        return self.data['scope']
    
    def get_company_id(self) -> str:
        """Get company ID from the data object."""
        return self.data['company_id']


class DeviceInfo(BaseModel):
    """Device information for authentication."""
    
    ip_address: str = Field(..., description="Device IP address")
    user_agent: str = Field(..., description="User agent string")
    fingerprint: str = Field(..., description="Device fingerprint") 