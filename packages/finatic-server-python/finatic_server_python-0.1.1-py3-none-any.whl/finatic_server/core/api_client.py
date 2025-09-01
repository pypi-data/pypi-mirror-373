"""Core API client for handling HTTP requests to the Finatic API."""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, TypeVar, Generic, List, Union
import aiohttp
from aiohttp import ClientSession, ClientTimeout

from ..types import (
    DeviceInfo,
    SessionResponse,
    OtpRequestResponse,
    OtpVerifyResponse,
    SessionAuthenticateResponse,
    PortalUrlResponse,
    SessionValidationResponse,
    UserToken,
    Holding,
    Order,
    Portfolio,
    BrokerInfo,
    BrokerAccount,
    BrokerOrder,
    BrokerPosition,
    BrokerConnection,
    BrokerDataOptions,
    OrdersFilter,
    PositionsFilter,
    AccountsFilter,
    OrderResponse,
    BrokerOrderParams,
    BrokerExtras,
    CryptoOrderOptions,
    OptionsOrderOptions,
    TradingContext,
    ApiPaginationInfo,
    PaginatedResult,
)
from ..utils.errors import (
    ApiError,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    NetworkError,
    TimeoutError,
    AuthorizationError,
    OrderError,
    OrderValidationError,
    CompanyAccessError,
)

T = TypeVar('T')


class ApiClient:
    """Handles all HTTP requests to the Finatic API with proper authentication and error handling."""
    
    def __init__(
        self,
        base_url: str,
        device_info: Optional[DeviceInfo] = None,
        timeout: int = 30
    ):
        """Initialize the API client.
        
        Args:
            base_url: Base URL for the API
            device_info: Device information for requests
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        if not self.base_url.endswith('/api/v1'):
            self.base_url = f"{self.base_url}/api/v1"
        
        self.device_info = device_info
        self.timeout = ClientTimeout(total=timeout)
        
        # Session state
        self.current_session_id: Optional[str] = None
        self.current_session_state: Optional[str] = None
        self.company_id: Optional[str] = None
        self.csrf_token: Optional[str] = None
        
        # Token management
        self.token_info: Optional[Dict[str, Any]] = None
        self.refresh_promise: Optional[asyncio.Future] = None
        self.refresh_buffer_minutes = 5
        
        # Trading context
        self.trading_context: TradingContext = TradingContext()
        
        # HTTP session
        self._session: Optional[ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self._session = ClientSession(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._session:
            await self._session.close()
    
    def _get_session(self) -> ClientSession:
        """Get the HTTP session, creating one if needed."""
        if self._session is None:
            raise RuntimeError("Client not initialized. Use async context manager or call _ensure_session()")
        return self._session
    
    async def _ensure_session(self):
        """Ensure HTTP session is available."""
        if self._session is None:
            self._session = ClientSession(timeout=self.timeout)
    
    def _build_headers(self, access_token: Optional[str] = None, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Build comprehensive headers for API requests.
        
        Args:
            access_token: Access token for authentication
            additional_headers: Additional headers to include
            
        Returns:
            Dictionary of headers
        """
        headers = {
            'Content-Type': 'application/json',
        }
        
        # Add device info if available
        if self.device_info:
            headers['X-Device-Info'] = json.dumps({
                'ip_address': self.device_info.ip_address,
                'user_agent': self.device_info.user_agent,
                'fingerprint': self.device_info.fingerprint,
            })
        
        # Add session headers if available
        if self.current_session_id:
            headers['X-Session-ID'] = self.current_session_id
            headers['Session-ID'] = self.current_session_id
        
        if self.company_id:
            headers['X-Company-ID'] = self.company_id
        
        if self.csrf_token:
            headers['X-CSRF-Token'] = self.csrf_token
        
        # Add authorization header
        if access_token:
            headers['Authorization'] = f'Bearer {access_token}'
        
        # Add additional headers
        if additional_headers:
            headers.update(additional_headers)
        
        return headers
    
    async def _request(
        self,
        method: str,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, str]] = None,
        access_token: Optional[str] = None,
        additional_headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Make an HTTP request to the API.
        
        Args:
            method: HTTP method
            path: API path
            data: Request body data
            params: Query parameters
            access_token: Access token for authentication
            additional_headers: Additional headers
            
        Returns:
            Response data
            
        Raises:
            ApiError: For API errors
            NetworkError: For network errors
            TimeoutError: For timeout errors
        """
        await self._ensure_session()
        session = self._get_session()
        
        # Build URL
        url = f"{self.base_url}{path}"
        
        # Build headers
        headers = self._build_headers(access_token, additional_headers)
        
        # Prepare request
        kwargs = {
            'headers': headers,
        }
        
        if data is not None:
            kwargs['json'] = data
        
        if params is not None:
            kwargs['params'] = params
        
        try:
            async with session.request(method, url, **kwargs) as response:
                response_text = await response.text()
                
                if not response.ok:
                    await self._handle_error_response(response.status, response_text)
                
                # Parse response
                try:
                    response_data = json.loads(response_text) if response_text else {}
                except json.JSONDecodeError:
                    raise ApiError(f"Invalid JSON response: {response_text}", response.status)
                
                # Check for API-level errors
                if isinstance(response_data, dict):
                    if response_data.get('success') is False:
                        raise ApiError(
                            response_data.get('message', 'API request failed'),
                            response_data.get('status_code', response.status),
                            response_data
                        )
                    
                    if response_data.get('status_code', 200) >= 400:
                        raise ApiError(
                            response_data.get('message', 'API request failed'),
                            response_data.get('status_code', response.status),
                            response_data
                        )
                
                return response_data
                
        except asyncio.TimeoutError:
            raise TimeoutError("Request timed out")
        except aiohttp.ClientError as e:
            raise NetworkError(f"Network error: {str(e)}")
    
    async def _handle_error_response(self, status: int, response_text: str):
        """Handle error responses from the API."""
        try:
            error_data = json.loads(response_text) if response_text else {}
        except json.JSONDecodeError:
            error_data = {"message": response_text or "Unknown error"}

        message = error_data.get("message", "Unknown error")
        
        # Provide more user-friendly error messages
        if status == 500:
            message = f"Server error: {message}. Please try again later or contact support."
        elif status == 401:
            message = f"Authentication failed: {message}. Please check your API key."
        elif status == 403:
            message = f"Access denied: {message}. Please check your permissions."
        elif status == 404:
            message = f"Resource not found: {message}. Please check the endpoint URL."
        elif status == 429:
            message = f"Rate limit exceeded: {message}. Please wait before retrying."
        elif status >= 500:
            message = f"Server error ({status}): {message}. Please try again later."
        elif status >= 400:
            message = f"Client error ({status}): {message}"

        if status == 401:
            raise AuthenticationError(message)
        elif status == 403:
            raise AuthorizationError(message)
        elif status == 422:
            raise ValidationError(message)
        elif status == 429:
            raise RateLimitError(message)
        elif status >= 500:
            raise NetworkError(message)
        else:
            raise ApiError(message, status, error_data)
    
    # Session management methods
    def set_session_context(self, session_id: str, company_id: str, csrf_token: Optional[str] = None):
        """Set session context for subsequent requests."""
        self.current_session_id = session_id
        self.company_id = company_id
        self.csrf_token = csrf_token
    
    def get_current_session_id(self) -> Optional[str]:
        """Get the current session ID."""
        return self.current_session_id
    
    def get_current_company_id(self) -> Optional[str]:
        """Get the current company ID."""
        return self.company_id
    
    def get_current_csrf_token(self) -> Optional[str]:
        """Get the current CSRF token."""
        return self.csrf_token
    
    # Token management methods
    def set_tokens(self, access_token: str, refresh_token: str, expires_at: str, user_id: Optional[str] = None):
        """Set authentication tokens."""
        self.token_info = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_at': expires_at,
            'user_id': user_id,
        }
    
    def get_token_info(self) -> Optional[Dict[str, Any]]:
        """Get current token info."""
        return self.token_info
    
    async def get_valid_access_token(self) -> str:
        """Get a valid access token, refreshing if necessary."""
        if not self.token_info:
            raise AuthenticationError("No tokens available. Please authenticate first.")
        
        # Check if token is expired or about to expire
        if self._is_token_expired():
            await self._refresh_tokens()
        
        return self.token_info['access_token']
    
    def _is_token_expired(self) -> bool:
        """Check if the current token is expired or about to expire."""
        if not self.token_info:
            return True
        
        expires_at = datetime.fromisoformat(self.token_info['expires_at'].replace('Z', '+00:00'))
        current_time = datetime.now(expires_at.tzinfo)
        buffer_time = timedelta(minutes=self.refresh_buffer_minutes)
        
        return current_time >= expires_at - buffer_time
    
    async def _refresh_tokens(self):
        """Refresh authentication tokens."""
        if not self.token_info:
            raise AuthenticationError("No refresh token available.")
        
        # If a refresh is already in progress, wait for it
        if self.refresh_promise:
            await self.refresh_promise
            return
        
        # Start a new refresh
        self.refresh_promise = self._perform_token_refresh()
        
        try:
            await self.refresh_promise
        finally:
            self.refresh_promise = None
    
    async def _perform_token_refresh(self):
        """Perform the actual token refresh request."""
        if not self.token_info:
            raise AuthenticationError("No refresh token available.")
        
        try:
            response = await self._request(
                method='POST',
                path='/company/auth/refresh',
                data={
                    'refresh_token': self.token_info['refresh_token']
                }
            )
            
            # Update stored tokens
            self.token_info = {
                'access_token': response['response_data']['access_token'],
                'refresh_token': response['response_data']['refresh_token'],
                'expires_at': response['response_data']['expires_at'],
                'user_id': self.token_info.get('user_id')
            }
            
            return self.token_info
            
        except Exception as e:
            # Clear tokens on refresh failure
            self.token_info = None
            raise AuthenticationError(f"Token refresh failed. Please re-authenticate: {str(e)}")
    
    def clear_tokens(self):
        """Clear stored tokens."""
        self.token_info = None
        self.refresh_promise = None
    
    def get_current_session_state(self) -> Optional[str]:
        """Get current session state."""
        return self.current_session_state
    
    # Simple methods that automatically use stored tokens
    async def get_holdings_auto(self) -> List[Holding]:
        """Get holdings using stored access token."""
        access_token = await self.get_valid_access_token()
        response = await self._request(
            method='GET',
            path='/portfolio/holdings',
            access_token=access_token
        )
        return [Holding(**holding) for holding in response.get('data', [])]
    
    async def get_orders_auto(self) -> List[Order]:
        """Get orders using stored access token."""
        access_token = await self.get_valid_access_token()
        response = await self._request(
            method='GET',
            path='/data/orders',
            access_token=access_token
        )
        return [Order(**order) for order in response.get('data', [])]
    
    async def get_portfolio_auto(self) -> Portfolio:
        """Get portfolio using stored access token."""
        access_token = await self.get_valid_access_token()
        response = await self._request(
            method='GET',
            path='/portfolio/',
            access_token=access_token
        )
        return Portfolio(**response.get('data', {}))
    
    async def get_broker_list_auto(self) -> List[BrokerInfo]:
        """Get broker list using stored access token."""
        access_token = await self.get_valid_access_token()
        response = await self._request(
            method='GET',
            path='/brokers/',
            access_token=access_token
        )
        return [BrokerInfo(**broker) for broker in response.get('response_data', [])]
    
    async def get_broker_accounts(self, page: int = 1, per_page: int = 100, options: Optional[BrokerDataOptions] = None, filters: Optional[AccountsFilter] = None) -> PaginatedResult:
        """Get broker accounts with pagination support."""
        access_token = await self.get_valid_access_token()
        offset = (page - 1) * per_page
        
        # Build query parameters
        params = {
            'limit': str(per_page),
            'offset': str(offset),
        }
        
        if options:
            if options.broker_name:
                params['broker_name'] = options.broker_name
            if options.account_id:
                params['account_id'] = options.account_id
        
        if filters:
            if filters.broker_id:
                params['broker_id'] = filters.broker_id
            if filters.connection_id:
                params['connection_id'] = filters.connection_id
            if filters.account_type:
                params['account_type'] = filters.account_type
            if filters.status:
                params['status'] = filters.status
            if filters.currency:
                params['currency'] = filters.currency
        
        response = await self._request(
            method='GET',
            path='/brokers/data/accounts',
            access_token=access_token,
            params=params
        )
        
        # Create navigation callback for pagination
        async def navigation_callback(new_offset: int, new_limit: int) -> PaginatedResult:
            new_params = {
                'limit': str(new_limit),
                'offset': str(new_offset),
            }
            
            if options:
                if options.broker_name:
                    new_params['broker_name'] = options.broker_name
                if options.account_id:
                    new_params['account_id'] = options.account_id
            
            if filters:
                if filters.broker_id:
                    new_params['broker_id'] = filters.broker_id
                if filters.connection_id:
                    new_params['connection_id'] = filters.connection_id
                if filters.account_type:
                    new_params['account_type'] = filters.account_type
                if filters.status:
                    new_params['status'] = filters.status
                if filters.currency:
                    new_params['currency'] = filters.currency
            
            new_response = await self._request(
                method='GET',
                path='/brokers/data/accounts',
                access_token=access_token,
                params=new_params
            )
            
            pagination_info = ApiPaginationInfo(
                has_more=new_response.get('pagination', {}).get('has_more', False),
                next_offset=new_response.get('pagination', {}).get('next_offset', new_offset),
                current_offset=new_response.get('pagination', {}).get('current_offset', new_offset),
                limit=new_response.get('pagination', {}).get('limit', new_limit),
            )
            
            return PaginatedResult(
                [BrokerAccount(**account) for account in new_response.get('response_data', [])],
                pagination_info,
                navigation_callback
            )
        
        pagination_info = ApiPaginationInfo(
            has_more=response.get('pagination', {}).get('has_more', False),
            next_offset=response.get('pagination', {}).get('next_offset', offset),
            current_offset=response.get('pagination', {}).get('current_offset', offset),
            limit=response.get('pagination', {}).get('limit', per_page),
        )
        
        return PaginatedResult(
            [BrokerAccount(**account) for account in response.get('response_data', [])],
            pagination_info,
            navigation_callback
        )
    
    async def get_broker_orders(self, page: int = 1, per_page: int = 100, options: Optional[BrokerDataOptions] = None, filters: Optional[OrdersFilter] = None) -> PaginatedResult:
        """Get broker orders with pagination support."""
        access_token = await self.get_valid_access_token()
        offset = (page - 1) * per_page
        
        # Build query parameters
        params = {
            'limit': str(per_page),
            'offset': str(offset),
        }
        
        if options:
            if options.broker_name:
                params['broker_name'] = options.broker_name
            if options.account_id:
                params['account_id'] = options.account_id
            if options.symbol:
                params['symbol'] = options.symbol
        
        if filters:
            if filters.broker_id:
                params['broker_id'] = filters.broker_id
            if filters.connection_id:
                params['connection_id'] = filters.connection_id
            if filters.account_id:
                params['account_id'] = filters.account_id
            if filters.symbol:
                params['symbol'] = filters.symbol
            if filters.status:
                params['status'] = filters.status
            if filters.side:
                params['side'] = filters.side
            if filters.asset_type:
                params['asset_type'] = filters.asset_type
            if filters.created_after:
                params['created_after'] = filters.created_after
            if filters.created_before:
                params['created_before'] = filters.created_before
        
        response = await self._request(
            method='GET',
            path='/brokers/data/orders',
            access_token=access_token,
            params=params
        )
        
        # Create navigation callback for pagination
        async def navigation_callback(new_offset: int, new_limit: int) -> PaginatedResult:
            new_params = {
                'limit': str(new_limit),
                'offset': str(new_offset),
            }
            
            if options:
                if options.broker_name:
                    new_params['broker_name'] = options.broker_name
                if options.account_id:
                    new_params['account_id'] = options.account_id
                if options.symbol:
                    new_params['symbol'] = options.symbol
            
            if filters:
                if filters.broker_id:
                    new_params['broker_id'] = filters.broker_id
                if filters.connection_id:
                    new_params['connection_id'] = filters.connection_id
                if filters.account_id:
                    new_params['account_id'] = filters.account_id
                if filters.symbol:
                    new_params['symbol'] = filters.symbol
                if filters.status:
                    new_params['status'] = filters.status
                if filters.side:
                    new_params['side'] = filters.side
                if filters.asset_type:
                    new_params['asset_type'] = filters.asset_type
                if filters.created_after:
                    new_params['created_after'] = filters.created_after
                if filters.created_before:
                    new_params['created_before'] = filters.created_before
            
            new_response = await self._request(
                method='GET',
                path='/brokers/data/orders',
                access_token=access_token,
                params=new_params
            )
            
            pagination_info = ApiPaginationInfo(
                has_more=new_response.get('pagination', {}).get('has_more', False),
                next_offset=new_response.get('pagination', {}).get('next_offset', new_offset),
                current_offset=new_response.get('pagination', {}).get('current_offset', new_offset),
                limit=new_response.get('pagination', {}).get('limit', new_limit),
            )
            
            return PaginatedResult(
                [BrokerOrder(**order) for order in new_response.get('response_data', [])],
                pagination_info,
                navigation_callback
            )
        
        pagination_info = ApiPaginationInfo(
            has_more=response.get('pagination', {}).get('has_more', False),
            next_offset=response.get('pagination', {}).get('next_offset', offset),
            current_offset=response.get('pagination', {}).get('current_offset', offset),
            limit=response.get('pagination', {}).get('limit', per_page),
        )
        
        return PaginatedResult(
            [BrokerOrder(**order) for order in response.get('response_data', [])],
            pagination_info,
            navigation_callback
        )
    
    async def get_broker_positions(self, page: int = 1, per_page: int = 100, options: Optional[BrokerDataOptions] = None, filters: Optional[PositionsFilter] = None) -> PaginatedResult:
        """Get broker positions with pagination support."""
        access_token = await self.get_valid_access_token()
        offset = (page - 1) * per_page
        
        # Build query parameters
        params = {
            'limit': str(per_page),
            'offset': str(offset),
        }
        
        if options:
            if options.broker_name:
                params['broker_name'] = options.broker_name
            if options.account_id:
                params['account_id'] = options.account_id
            if options.symbol:
                params['symbol'] = options.symbol
        
        if filters:
            if filters.broker_id:
                params['broker_id'] = filters.broker_id
            if filters.connection_id:
                params['connection_id'] = filters.connection_id
            if filters.account_id:
                params['account_id'] = filters.account_id
            if filters.symbol:
                params['symbol'] = filters.symbol
            if filters.side:
                params['side'] = filters.side
            if filters.asset_type:
                params['asset_type'] = filters.asset_type
            if filters.position_status:
                params['position_status'] = filters.position_status
            if filters.updated_after:
                params['updated_after'] = filters.updated_after
            if filters.updated_before:
                params['updated_before'] = filters.updated_before
        
        response = await self._request(
            method='GET',
            path='/brokers/data/positions',
            access_token=access_token,
            params=params
        )
        
        # Create navigation callback for pagination
        async def navigation_callback(new_offset: int, new_limit: int) -> PaginatedResult:
            new_params = {
                'limit': str(new_limit),
                'offset': str(new_offset),
            }
            
            if options:
                if options.broker_name:
                    new_params['broker_name'] = options.broker_name
                if options.account_id:
                    new_params['account_id'] = options.account_id
                if options.symbol:
                    new_params['symbol'] = options.symbol
            
            if filters:
                if filters.broker_id:
                    new_params['broker_id'] = filters.broker_id
                if filters.connection_id:
                    new_params['connection_id'] = filters.connection_id
                if filters.account_id:
                    new_params['account_id'] = filters.account_id
                if filters.symbol:
                    new_params['symbol'] = filters.symbol
                if filters.side:
                    new_params['side'] = filters.side
                if filters.asset_type:
                    new_params['asset_type'] = filters.asset_type
                if filters.position_status:
                    new_params['position_status'] = filters.position_status
                if filters.updated_after:
                    new_params['updated_after'] = filters.updated_after
                if filters.updated_before:
                    new_params['updated_before'] = filters.updated_before
            
            new_response = await self._request(
                method='GET',
                path='/brokers/data/positions',
                access_token=access_token,
                params=new_params
            )
            
            pagination_info = ApiPaginationInfo(
                has_more=new_response.get('pagination', {}).get('has_more', False),
                next_offset=new_response.get('pagination', {}).get('next_offset', new_offset),
                current_offset=new_response.get('pagination', {}).get('current_offset', new_offset),
                limit=new_response.get('pagination', {}).get('limit', new_limit),
            )
            
            return PaginatedResult(
                [BrokerPosition(**position) for position in new_response.get('response_data', [])],
                pagination_info,
                navigation_callback
            )
        
        pagination_info = ApiPaginationInfo(
            has_more=response.get('pagination', {}).get('has_more', False),
            next_offset=response.get('pagination', {}).get('next_offset', offset),
            current_offset=response.get('pagination', {}).get('current_offset', offset),
            limit=response.get('pagination', {}).get('limit', per_page),
        )
        
        return PaginatedResult(
            [BrokerPosition(**position) for position in response.get('response_data', [])],
            pagination_info,
            navigation_callback
        )
    
    # Helper methods to get all data across pages
    async def get_all_broker_accounts(self, options: Optional[BrokerDataOptions] = None, filters: Optional[AccountsFilter] = None) -> List[BrokerAccount]:
        """Get all broker accounts across all pages."""
        all_accounts = []
        page = 1
        per_page = 100
        
        while True:
            result = await self.get_broker_accounts(page, per_page, options, filters)
            if not result.data:
                break
            all_accounts.extend(result.data)
            if not result.has_next:
                break
            page += 1
        
        return all_accounts
    
    async def get_all_broker_orders(self, options: Optional[BrokerDataOptions] = None, filters: Optional[OrdersFilter] = None) -> List[BrokerOrder]:
        """Get all broker orders across all pages."""
        all_orders = []
        page = 1
        per_page = 100
        
        while True:
            result = await self.get_broker_orders(page, per_page, options, filters)
            if not result.data:
                break
            all_orders.extend(result.data)
            if not result.has_next:
                break
            page += 1
        
        return all_orders
    
    async def get_all_broker_positions(self, options: Optional[BrokerDataOptions] = None, filters: Optional[PositionsFilter] = None) -> List[BrokerPosition]:
        """Get all broker positions across all pages."""
        all_positions = []
        page = 1
        per_page = 100
        
        while True:
            result = await self.get_broker_positions(page, per_page, options, filters)
            if not result.data:
                break
            all_positions.extend(result.data)
            if not result.has_next:
                break
            page += 1
        
        return all_positions
    
    async def get_broker_connections_auto(self) -> List[BrokerConnection]:
        """Get broker connections using stored access token."""
        access_token = await self.get_valid_access_token()
        response = await self._request(
            method='GET',
            path='/brokers/connections',
            access_token=access_token
        )
        return [BrokerConnection(**connection) for connection in response.get('response_data', [])]
    
    # Trading context methods
    def set_broker(self, broker: str):
        """Set the current broker."""
        self.trading_context.broker = broker
    
    def set_account(self, account_number: str, account_id: Optional[str] = None):
        """Set the current account."""
        self.trading_context.account_number = account_number
        self.trading_context.account_id = account_id
    
    def get_trading_context(self) -> TradingContext:
        """Get the current trading context."""
        return self.trading_context
    
    def clear_trading_context(self):
        """Clear the trading context."""
        self.trading_context = TradingContext()
    
    def is_mock_client(self) -> bool:
        """Check if this is a mock client."""
        return False 

    async def get_portal_url(self, session_id: str) -> PortalUrlResponse:
        """Get portal URL for session."""
        response = await self._request(
            method='GET',
            path=f'/auth/session/portal',
            additional_headers={
                'X-Session-ID': session_id,
            }
        )
        return PortalUrlResponse(**response)

    async def get_session_user(self, session_id: str, company_id: str):
        """Get user and tokens for completed session.
        
        Args:
            session_id: Session ID to use as Bearer token
            company_id: Company ID for session validation
            
        Returns:
            SessionUserResponse with user info and tokens
        """
        response = await self._request(
            method='GET',
            path=f'/auth/session/{session_id}/user',
            additional_headers={
                'Authorization': f'Bearer {session_id}',
                'Company-ID': company_id,
            }
        )
        
        # Import here to avoid circular imports
        from ..types.auth import SessionUserResponse
        return SessionUserResponse(**response)

    # ============================================================================
    # TRADING METHODS
    # ============================================================================

    async def place_broker_order(
        self,
        params: Union[BrokerOrderParams, Dict[str, Any]],
        extras: Optional[BrokerExtras] = None,
        connection_id: Optional[str] = None
    ) -> OrderResponse:
        """Place a broker order.
        
        Args:
            params: Order parameters (BrokerOrderParams or dict)
            extras: Optional broker-specific extras
            connection_id: Optional connection ID for testing
            
        Returns:
            OrderResponse with order details
            
        Raises:
            OrderError: If order placement fails
            OrderValidationError: If order validation fails
        """
        access_token = await self.get_valid_access_token()
        
        # Convert dict to BrokerOrderParams if needed
        if isinstance(params, dict):
            params = BrokerOrderParams(**params)
        
        # Get broker and account from context or params
        broker = params.broker or self.trading_context.broker
        account_number = params.account_number or self.trading_context.account_number
        
        if not broker:
            raise ValidationError("Broker not set. Call set_broker() or pass broker parameter.")
        
        if not account_number:
            raise ValidationError("Account not set. Call set_account() or pass account_number parameter.")

        # Build request body
        request_body = self._build_order_request_body(params, extras)

        # Add query parameters if connection_id is provided
        query_params: Dict[str, str] = {}
        if connection_id:
            query_params['connection_id'] = connection_id

        response = await self._request(
            method='POST',
            path='/brokers/orders',
            data=request_body,
            params=query_params,
            access_token=access_token,
            additional_headers={
                'Authorization': f'Bearer {access_token}',
                'Session-ID': self.current_session_id or '',
                'X-Session-ID': self.current_session_id or '',
                'X-Device-Info': json.dumps(self.device_info) if self.device_info else '',
            }
        )

        return OrderResponse(**response)

    async def cancel_broker_order(
        self,
        order_id: str,
        broker: Optional[str] = None,
        extras: Optional[Dict[str, Any]] = None,
        connection_id: Optional[str] = None
    ) -> OrderResponse:
        """Cancel a broker order.
        
        Args:
            order_id: The order ID to cancel
            broker: Optional broker override
            extras: Optional extras for cancellation
            connection_id: Optional connection ID for testing
            
        Returns:
            OrderResponse with cancellation details
        """
        access_token = await self.get_valid_access_token()
        
        selected_broker = broker or self.trading_context.broker
        if not selected_broker:
            raise ValidationError("Broker not set. Call set_broker() or pass broker parameter.")

        account_number = self.trading_context.account_number

        # Build query parameters - order_id goes in URL path, not query params
        query_params: Dict[str, str] = {}

        # Add optional parameters if available
        if account_number:
            query_params['account_number'] = str(account_number)
        if connection_id:
            query_params['connection_id'] = connection_id

        # Build optional request body if extras are provided
        data: Optional[Dict[str, Any]] = None
        if extras:
            data = {
                'broker': selected_broker,
                'order': {
                    'order_id': order_id,
                    'account_number': account_number,
                    **extras
                }
            }

        response = await self._request(
            method='DELETE',
            path=f'/brokers/orders/{order_id}',  # Fixed: order_id in URL path
            data=data,
            params=query_params,
            access_token=access_token,
            additional_headers={
                'Authorization': f'Bearer {access_token}',
                'Session-ID': self.current_session_id or '',
                'X-Session-ID': self.current_session_id or '',
                'X-Device-Info': json.dumps(self.device_info) if self.device_info else '',
            }
        )

        return OrderResponse(**response)

    async def modify_broker_order(
        self,
        order_id: str,
        params: Union[Dict[str, Any], BrokerOrderParams],
        broker: Optional[str] = None,
        extras: Optional[Dict[str, Any]] = None,
        connection_id: Optional[str] = None
    ) -> OrderResponse:
        """Modify a broker order.
        
        Args:
            order_id: The order ID to modify
            params: Modification parameters
            broker: Optional broker override
            extras: Optional extras for modification
            connection_id: Optional connection ID for testing
            
        Returns:
            OrderResponse with modification details
        """
        access_token = await self.get_valid_access_token()
        
        selected_broker = broker or self.trading_context.broker
        if not selected_broker:
            raise ValidationError("Broker not set. Call set_broker() or pass broker parameter.")

        # Build request body with required fields
        request_body = self._build_modify_request_body(params, extras, selected_broker)
        
        # Ensure order_id is included in the request body
        if 'order' not in request_body:
            request_body['order'] = {}
        request_body['order']['order_id'] = order_id

        # Add query parameters if connection_id is provided
        query_params: Dict[str, str] = {}
        if connection_id:
            query_params['connection_id'] = connection_id

        response = await self._request(
            method='PATCH',
            path=f'/brokers/orders/{order_id}',
            data=request_body,
            params=query_params,
            access_token=access_token,
            additional_headers={
                'Authorization': f'Bearer {access_token}',
                'Session-ID': self.current_session_id or '',
                'X-Session-ID': self.current_session_id or '',
                'X-Device-Info': json.dumps(self.device_info) if self.device_info else '',
            }
        )

        return OrderResponse(**response)

    # ============================================================================
    # CONVENIENCE METHODS - STOCK
    # ============================================================================

    async def place_stock_market_order(
        self,
        symbol: str,
        quantity: float,
        side: str,
        broker: Optional[str] = None,
        account_number: Optional[Union[str, int]] = None,
        extras: Optional[BrokerExtras] = None,
        connection_id: Optional[str] = None
    ) -> OrderResponse:
        """Place a stock market order.
        
        Args:
            symbol: Trading symbol
            quantity: Order quantity
            side: 'buy' or 'sell'
            broker: Optional broker override
            account_number: Optional account number override
            extras: Optional broker-specific extras
            connection_id: Optional connection ID for testing
            
        Returns:
            OrderResponse with order details
        """
        action = "Buy" if side.lower() == "buy" else "Sell"
        
        params = BrokerOrderParams(
            broker=broker or self.trading_context.broker or "robinhood",
            account_number=account_number or self.trading_context.account_number or "",
            symbol=symbol,
            order_qty=quantity,
            action=action,
            order_type="Market",
            asset_type="Stock",
            time_in_force="day",
        )
        
        return await self.place_broker_order(params, extras, connection_id)

    async def place_stock_limit_order(
        self,
        symbol: str,
        quantity: float,
        side: str,
        price: float,
        time_in_force: str = "gtc",
        broker: Optional[str] = None,
        account_number: Optional[Union[str, int]] = None,
        extras: Optional[BrokerExtras] = None,
        connection_id: Optional[str] = None
    ) -> OrderResponse:
        """Place a stock limit order.
        
        Args:
            symbol: Trading symbol
            quantity: Order quantity
            side: 'buy' or 'sell'
            price: Limit price
            time_in_force: 'day' or 'gtc'
            broker: Optional broker override
            account_number: Optional account number override
            extras: Optional broker-specific extras
            connection_id: Optional connection ID for testing
            
        Returns:
            OrderResponse with order details
        """
        action = "Buy" if side.lower() == "buy" else "Sell"
        
        params = BrokerOrderParams(
            broker=broker or self.trading_context.broker or "robinhood",
            account_number=account_number or self.trading_context.account_number or "",
            symbol=symbol,
            order_qty=quantity,
            action=action,
            order_type="Limit",
            asset_type="Stock",
            time_in_force=time_in_force,
            price=price,
        )
        
        return await self.place_broker_order(params, extras, connection_id)

    async def place_stock_stop_order(
        self,
        symbol: str,
        quantity: float,
        side: str,
        stop_price: float,
        time_in_force: str = "day",
        broker: Optional[str] = None,
        account_number: Optional[Union[str, int]] = None,
        extras: Optional[BrokerExtras] = None,
        connection_id: Optional[str] = None
    ) -> OrderResponse:
        """Place a stock stop order.
        
        Args:
            symbol: Trading symbol
            quantity: Order quantity
            side: 'buy' or 'sell'
            stop_price: Stop price
            time_in_force: 'day' or 'gtc'
            broker: Optional broker override
            account_number: Optional account number override
            extras: Optional broker-specific extras
            connection_id: Optional connection ID for testing
            
        Returns:
            OrderResponse with order details
        """
        action = "Buy" if side.lower() == "buy" else "Sell"
        
        params = BrokerOrderParams(
            broker=broker or self.trading_context.broker or "robinhood",
            account_number=account_number or self.trading_context.account_number or "",
            symbol=symbol,
            order_qty=quantity,
            action=action,
            order_type="Stop",
            asset_type="Stock",
            time_in_force=time_in_force,
            stop_price=stop_price,
        )
        
        return await self.place_broker_order(params, extras, connection_id)

    # ============================================================================
    # CONVENIENCE METHODS - CRYPTO
    # ============================================================================

    async def place_crypto_market_order(
        self,
        symbol: str,
        quantity: float,
        side: str,
        options: Optional[CryptoOrderOptions] = None,
        broker: Optional[str] = None,
        account_number: Optional[Union[str, int]] = None,
        extras: Optional[BrokerExtras] = None,
        connection_id: Optional[str] = None
    ) -> OrderResponse:
        """Place a crypto market order.
        
        Args:
            symbol: Trading symbol
            quantity: Order quantity
            side: 'buy' or 'sell'
            options: Optional crypto-specific options
            broker: Optional broker override
            account_number: Optional account number override
            extras: Optional broker-specific extras
            connection_id: Optional connection ID for testing
            
        Returns:
            OrderResponse with order details
        """
        action = "Buy" if side.lower() == "buy" else "Sell"
        
        params = BrokerOrderParams(
            broker=broker or self.trading_context.broker or "robinhood",
            account_number=account_number or self.trading_context.account_number or "",
            symbol=symbol,
            order_qty=options.quantity if options and options.quantity else quantity,
            action=action,
            order_type="Market",
            asset_type="Crypto",
            time_in_force="gtc",  # Crypto typically uses GTC
        )
        
        return await self.place_broker_order(params, extras, connection_id)

    async def place_crypto_limit_order(
        self,
        symbol: str,
        quantity: float,
        side: str,
        price: float,
        time_in_force: str = "gtc",
        options: Optional[CryptoOrderOptions] = None,
        broker: Optional[str] = None,
        account_number: Optional[Union[str, int]] = None,
        extras: Optional[BrokerExtras] = None,
        connection_id: Optional[str] = None
    ) -> OrderResponse:
        """Place a crypto limit order.
        
        Args:
            symbol: Trading symbol
            quantity: Order quantity
            side: 'buy' or 'sell'
            price: Limit price
            time_in_force: 'day' or 'gtc'
            options: Optional crypto-specific options
            broker: Optional broker override
            account_number: Optional account number override
            extras: Optional broker-specific extras
            connection_id: Optional connection ID for testing
            
        Returns:
            OrderResponse with order details
        """
        action = "Buy" if side.lower() == "buy" else "Sell"
        
        params = BrokerOrderParams(
            broker=broker or self.trading_context.broker or "robinhood",
            account_number=account_number or self.trading_context.account_number or "",
            symbol=symbol,
            order_qty=options.quantity if options and options.quantity else quantity,
            action=action,
            order_type="Limit",
            asset_type="Crypto",
            time_in_force=time_in_force,
            price=price,
        )
        
        return await self.place_broker_order(params, extras, connection_id)

    # ============================================================================
    # CONVENIENCE METHODS - OPTIONS
    # ============================================================================

    async def place_options_market_order(
        self,
        symbol: str,
        quantity: float,
        side: str,
        options: OptionsOrderOptions,
        broker: Optional[str] = None,
        account_number: Optional[Union[str, int]] = None,
        extras: Optional[BrokerExtras] = None,
        connection_id: Optional[str] = None
    ) -> OrderResponse:
        """Place an options market order.
        
        Args:
            symbol: Trading symbol
            quantity: Order quantity
            side: 'buy' or 'sell'
            options: Options-specific parameters
            broker: Optional broker override
            account_number: Optional account number override
            extras: Optional broker-specific extras
            connection_id: Optional connection ID for testing
            
        Returns:
            OrderResponse with order details
        """
        action = "Buy" if side.lower() == "buy" else "Sell"
        
        params = BrokerOrderParams(
            broker=broker or self.trading_context.broker or "robinhood",
            account_number=account_number or self.trading_context.account_number or "",
            symbol=symbol,
            order_qty=quantity,
            action=action,
            order_type="Market",
            asset_type="Option",
            time_in_force="day",
        )
        
        return await self.place_broker_order(params, extras, connection_id)

    async def place_options_limit_order(
        self,
        symbol: str,
        quantity: float,
        side: str,
        price: float,
        options: OptionsOrderOptions,
        time_in_force: str = "gtc",
        broker: Optional[str] = None,
        account_number: Optional[Union[str, int]] = None,
        extras: Optional[BrokerExtras] = None,
        connection_id: Optional[str] = None
    ) -> OrderResponse:
        """Place an options limit order.
        
        Args:
            symbol: Trading symbol
            quantity: Order quantity
            side: 'buy' or 'sell'
            price: Limit price
            options: Options-specific parameters
            time_in_force: 'day' or 'gtc'
            broker: Optional broker override
            account_number: Optional account number override
            extras: Optional broker-specific extras
            connection_id: Optional connection ID for testing
            
        Returns:
            OrderResponse with order details
        """
        action = "Buy" if side.lower() == "buy" else "Sell"
        
        params = BrokerOrderParams(
            broker=broker or self.trading_context.broker or "robinhood",
            account_number=account_number or self.trading_context.account_number or "",
            symbol=symbol,
            order_qty=quantity,
            action=action,
            order_type="Limit",
            asset_type="Option",
            time_in_force=time_in_force,
            price=price,
        )
        
        return await self.place_broker_order(params, extras, connection_id)

    # ============================================================================
    # CONVENIENCE METHODS - FUTURES
    # ============================================================================

    async def place_futures_market_order(
        self,
        symbol: str,
        quantity: float,
        side: str,
        broker: Optional[str] = None,
        account_number: Optional[Union[str, int]] = None,
        extras: Optional[BrokerExtras] = None,
        connection_id: Optional[str] = None
    ) -> OrderResponse:
        """Place a futures market order.
        
        Args:
            symbol: Trading symbol
            quantity: Order quantity
            side: 'buy' or 'sell'
            broker: Optional broker override
            account_number: Optional account number override
            extras: Optional broker-specific extras
            connection_id: Optional connection ID for testing
            
        Returns:
            OrderResponse with order details
        """
        action = "Buy" if side.lower() == "buy" else "Sell"
        
        params = BrokerOrderParams(
            broker=broker or self.trading_context.broker or "robinhood",
            account_number=account_number or self.trading_context.account_number or "",
            symbol=symbol,
            order_qty=quantity,
            action=action,
            order_type="Market",
            asset_type="Futures",  # Fixed: use plural "Futures" as expected by server
            time_in_force="day",
        )
        
        return await self.place_broker_order(params, extras, connection_id)

    async def place_futures_limit_order(
        self,
        symbol: str,
        quantity: float,
        side: str,
        price: float,
        time_in_force: str = "gtc",
        broker: Optional[str] = None,
        account_number: Optional[Union[str, int]] = None,
        extras: Optional[BrokerExtras] = None,
        connection_id: Optional[str] = None
    ) -> OrderResponse:
        """Place a futures limit order.
        
        Args:
            symbol: Trading symbol
            quantity: Order quantity
            side: 'buy' or 'sell'
            price: Limit price
            time_in_force: 'day' or 'gtc'
            broker: Optional broker override
            account_number: Optional account number override
            extras: Optional broker-specific extras
            connection_id: Optional connection ID for testing
            
        Returns:
            OrderResponse with order details
        """
        action = "Buy" if side.lower() == "buy" else "Sell"
        
        params = BrokerOrderParams(
            broker=broker or self.trading_context.broker or "robinhood",
            account_number=account_number or self.trading_context.account_number or "",
            symbol=symbol,
            order_qty=quantity,
            action=action,
            order_type="Limit",
            asset_type="Futures",  # Fixed: use plural "Futures" as expected by server
            time_in_force=time_in_force,
            price=price,
        )
        
        return await self.place_broker_order(params, extras, connection_id)

    # ============================================================================
    # HELPER METHODS
    # ============================================================================

    def _build_order_request_body(
        self,
        params: BrokerOrderParams,
        extras: Optional[BrokerExtras] = None
    ) -> Dict[str, Any]:
        """Build the request body for order placement.
        
        Args:
            params: Order parameters
            extras: Optional broker-specific extras
            
        Returns:
            Request body dictionary
        """

        base_order: Dict[str, Any] = {
            'order_type': params.order_type,
            'asset_type': 'Equity',  # Fixed: API expects "Equity" not "Stock"
            'action': params.action,
            'time_in_force': params.time_in_force,
            'account_number': params.account_number,
            'symbol': params.symbol,
            'order_qty': params.order_qty,
        }
        
        # Only add order_id if it's not None
        if params.order_id is not None:
            base_order['order_id'] = params.order_id

        if params.price is not None:
            base_order['price'] = params.price
        if params.stop_price is not None:
            base_order['stop_price'] = params.stop_price

        # Apply broker-specific defaults - but only include valid fields
        broker_extras = self._apply_broker_defaults(params.broker, extras)
        
        # Get broker-specific extras and add them to the order
        broker_extras = self._apply_broker_defaults(params.broker, extras)
        
        # Add broker-specific extras to the base_order if they exist
        if broker_extras and isinstance(broker_extras, dict):
            # The broker extras should be nested under the broker name inside the order
            if params.broker in broker_extras:
                base_order[params.broker] = broker_extras[params.broker]
        
        # Debug logging - log the built request body
        final_request_body = {
            'broker': params.broker,
            'order': base_order,
        }
            
        print(f"🔍 DEBUG: _build_order_request_body - final_request_body: {final_request_body}")

        return final_request_body

    def _build_modify_request_body(
        self,
        params: Union[Dict[str, Any], BrokerOrderParams],
        extras: Optional[Dict[str, Any]],
        broker: str
    ) -> Dict[str, Any]:
        """Build the request body for order modification.
        
        Args:
            params: Modification parameters
            extras: Optional extras
            broker: Broker name
            
        Returns:
            Request body dictionary
        """
        order: Dict[str, Any] = {}

        # Handle both dict and BrokerOrderParams
        if isinstance(params, BrokerOrderParams):
            param_dict = params.model_dump(exclude_none=True)
        else:
            param_dict = params

        # Map parameters to order fields - ensure all required fields are included
        field_mapping = {
            'order_id': 'order_id',
            'order_type': 'order_type',
            'asset_type': 'asset_type',
            'action': 'action',
            'time_in_force': 'time_in_force',
            'account_number': 'account_number',
            'symbol': 'symbol',
            'order_qty': 'order_qty',
            'price': 'price',
            'stop_price': 'stop_price',
        }

        # Include all provided parameters
        for param_key, order_key in field_mapping.items():
            if param_key in param_dict and param_dict[param_key] is not None:
                order[order_key] = param_dict[param_key]

        # Apply broker-specific defaults
        broker_extras = self._apply_broker_defaults(broker, extras)

        return {
            'broker': broker,
            'order': {
                **order,
                **broker_extras,
            },
        }

    def _apply_broker_defaults(
        self,
        broker: str,
        extras: Optional[Union[BrokerExtras, Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Apply broker-specific defaults to extras.
        
        Args:
            broker: Broker name
            extras: Optional extras
            
        Returns:
            Processed extras dictionary
        """
        if not extras:
            extras = {}

        # Handle BrokerExtras model
        if isinstance(extras, BrokerExtras):
            extras_dict = extras.model_dump(exclude_none=True)
        else:
            extras_dict = extras or {}

        # If the caller provided a broker-scoped extras object, pull the nested object
        if extras_dict and isinstance(extras_dict, dict):
            scoped = None
            if broker == 'robinhood':
                scoped = extras_dict.get('robinhood')
            elif broker == 'ninja_trader':
                # JS SDK uses camelCase: ninjaTrader
                scoped = extras_dict.get('ninjaTrader') or extras_dict.get('ninja_trader')
            elif broker == 'tasty_trade':
                # JS SDK uses camelCase: tastyTrade
                scoped = extras_dict.get('tastyTrade') or extras_dict.get('tasty_trade')
            
            if scoped:
                extras_dict = scoped

        # Apply broker-specific defaults
        if broker == 'robinhood':
            return {
                **extras_dict,
                'extended_hours': extras_dict.get('extended_hours', extras_dict.get('extendedHours', True)),
                'market_hours': extras_dict.get('market_hours', extras_dict.get('market_hours', 'regular_hours')),
                'trail_type': extras_dict.get('trail_type', extras_dict.get('trailType', 'percentage')),
            }
        elif broker == 'ninja_trader':
            return {
                **extras_dict,
                'account_spec': extras_dict.get('account_spec', extras_dict.get('accountSpec', '')),
                'is_automated': extras_dict.get('is_automated', extras_dict.get('isAutomated', True)),
            }
        elif broker == 'tasty_trade':
            return {
                **extras_dict,
                'automated_source': extras_dict.get('automated_source', extras_dict.get('automatedSource', True)),
            }
        else:
            return extras_dict 