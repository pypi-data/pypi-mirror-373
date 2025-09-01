"""Common type definitions used across the Finatic Server SDK."""

from typing import Optional, List, Dict, Any, Callable, Awaitable
from pydantic import BaseModel, Field


class DeviceInfo(BaseModel):
    """Device information for authentication and tracking."""
    
    ip_address: str = Field(..., description="Device IP address")
    user_agent: str = Field(..., description="User agent string")
    fingerprint: str = Field(..., description="Device fingerprint")


class ApiResponse(BaseModel):
    """Standard API response wrapper."""
    
    success: bool = Field(..., description="Request success status")
    message: str = Field(..., description="Response message")
    status_code: Optional[int] = Field(None, description="HTTP status code")


class ApiPaginationInfo(BaseModel):
    """API pagination information."""
    
    has_more: bool = Field(..., description="Whether there are more pages")
    next_offset: Optional[int] = Field(None, description="Next page offset")
    current_offset: int = Field(..., description="Current page offset")
    limit: int = Field(..., description="Items per page")


class PaginationMetadata(BaseModel):
    """Pagination metadata for client use."""
    
    has_more: bool = Field(..., description="Whether there are more pages")
    next_offset: Optional[int] = Field(None, description="Next page offset")
    current_offset: Optional[int] = Field(None, description="Current page offset")
    limit: Optional[int] = Field(None, description="Items per page")
    current_page: Optional[int] = Field(None, description="Current page number")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")


class TradingContext(BaseModel):
    """Trading context for order placement."""
    
    broker: Optional[str] = Field(None, description="Selected broker")
    account_number: Optional[str] = Field(None, description="Account number")
    account_id: Optional[str] = Field(None, description="Account ID")


class RequestHeaders(BaseModel):
    """Common request headers."""
    
    x_api_key: Optional[str] = Field(None, alias="X-API-Key", description="API key header")
    one_time_token: Optional[str] = Field(None, alias="One-Time-Token", description="One-time token header")
    x_device_info: Optional[str] = Field(None, alias="X-Device-Info", description="Device info header")
    x_session_id: Optional[str] = Field(None, alias="X-Session-ID", description="Session ID header")
    session_id: Optional[str] = Field(None, alias="Session-ID", description="Session ID header")
    x_company_id: Optional[str] = Field(None, alias="X-Company-ID", description="Company ID header")
    authorization: Optional[str] = Field(None, alias="Authorization", description="Authorization header")
    
    model_config = {"populate_by_name": True}


class PaginatedResult:
    """Paginated result with navigation capabilities."""
    
    def __init__(
        self,
        data: Any,
        pagination_info: ApiPaginationInfo,
        navigation_callback: Optional[Callable[[int, int], Awaitable['PaginatedResult']]] = None
    ):
        self.data = data
        self.navigation_callback = navigation_callback
        # Default to 0 if any are None
        next_offset = pagination_info.next_offset if pagination_info.next_offset is not None else 0
        current_offset = pagination_info.current_offset if pagination_info.current_offset is not None else 0
        limit = pagination_info.limit if pagination_info.limit is not None else 0
        current_page = (current_offset // limit + 1) if limit else 1
        # has_next: only if next_offset is not None and not equal to current_offset
        has_next = (
            pagination_info.next_offset is not None
            and pagination_info.next_offset != pagination_info.current_offset
        )
        # has_previous: only if current_offset is not None and > 0
        has_previous = (
            pagination_info.current_offset is not None
            and pagination_info.current_offset > 0
        )
        self.metadata = PaginationMetadata(
            has_more=pagination_info.has_more,
            next_offset=next_offset,
            current_offset=current_offset,
            limit=limit,
            current_page=current_page,
            has_next=has_next,
            has_previous=has_previous,
        )
    
    @property
    def has_next(self) -> bool:
        return self.metadata.has_next
    
    @property
    def has_previous(self) -> bool:
        return self.metadata.has_previous
    
    @property
    def current_page(self) -> int:
        return self.metadata.current_page or 1
    
    async def next_page(self) -> Optional['PaginatedResult']:
        if not self.has_next or not self.navigation_callback:
            return None
        try:
            return await self.navigation_callback(self.metadata.next_offset, self.metadata.limit)
        except Exception as e:
            print(f'Error fetching next page: {e}')
            return None
    
    async def previous_page(self) -> Optional['PaginatedResult']:
        if not self.has_previous or not self.navigation_callback:
            return None
        previous_offset = max(0, (self.metadata.current_offset or 0) - (self.metadata.limit or 0))
        try:
            return await self.navigation_callback(previous_offset, self.metadata.limit)
        except Exception as e:
            print(f'Error fetching previous page: {e}')
            return None
    
    async def go_to_page(self, page_number: int) -> Optional['PaginatedResult']:
        """Go to a specific page."""
        if not self.navigation_callback or page_number < 1:
            return None
        
        offset = (page_number - 1) * self.metadata.limit
        try:
            return await self.navigation_callback(offset, self.metadata.limit)
        except Exception as e:
            print(f'Error fetching page {page_number}: {e}')
            return None
    
    async def first_page(self) -> Optional['PaginatedResult']:
        """Get the first page."""
        if not self.navigation_callback:
            return None
        
        try:
            return await self.navigation_callback(0, self.metadata.limit)
        except Exception as e:
            print(f'Error fetching first page: {e}')
            return None
    
    async def last_page(self) -> Optional['PaginatedResult']:
        """Get the last page by navigating through all pages."""
        if not self.navigation_callback:
            return None
        
        async def find_last(page: PaginatedResult) -> PaginatedResult:
            if not page.has_next:
                return page
            next_page = await page.next_page()
            if not next_page:
                return page
            return await find_last(next_page)
        
        try:
            return await find_last(self)
        except Exception as e:
            print(f'Error fetching last page: {e}')
            return None
    
    def get_pagination_info(self) -> str:
        """Get pagination info as string."""
        return f"Page {self.current_page} ({self.metadata.current_offset + 1}-{self.metadata.current_offset + self.metadata.limit})" 