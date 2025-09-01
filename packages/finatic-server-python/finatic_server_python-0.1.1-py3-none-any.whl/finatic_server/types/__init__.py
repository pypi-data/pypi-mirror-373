"""Type definitions and data models for the Finatic Server SDK."""

# Common types
from .common import (
    DeviceInfo,
    ApiResponse,
    ApiPaginationInfo,
    PaginationMetadata,
    PaginatedResult,
    TradingContext,
    RequestHeaders,
)

# Authentication types
from .auth import (
    UserToken,
    SessionResponse,
    SessionInitResponse,
    OtpRequestResponse,
    OtpVerifyResponse,
    SessionAuthenticateResponse,
    PortalUrlResponse,
    SessionValidationResponse,
)

# Portfolio types
from .portfolio import (
    Portfolio,
    Holding,
    PerformanceMetrics,
    PortfolioSnapshot,
)

# Order types
from .orders import (
    Order,
    OptionsOrder,
    CryptoOrderOptions,
    OptionsOrderOptions,
    OrderResponse,
    BrokerOrderParams,
    BrokerExtras,
)

# Broker types
from .broker import (
    BrokerAccount,
    BrokerOrder,
    BrokerPosition,
    BrokerInfo,
    BrokerConnection,
    BrokerDataOptions,
    OrdersFilter,
    PositionsFilter,
    AccountsFilter,
)

__all__ = [
    # Common
    "DeviceInfo",
    "ApiResponse", 
    "ApiPaginationInfo",
    "PaginationMetadata",
    "PaginatedResult",
    "TradingContext",
    "RequestHeaders",
    
    # Auth
    "UserToken",
    "SessionResponse",
    "SessionInitResponse",
    "OtpRequestResponse",
    "OtpVerifyResponse",
    "SessionAuthenticateResponse",
    "PortalUrlResponse",
    "SessionValidationResponse",
    
    # Portfolio
    "Portfolio",
    "Holding",
    "PerformanceMetrics",
    "PortfolioSnapshot",
    
    # Orders
    "Order",
    "OptionsOrder",
    "CryptoOrderOptions",
    "OptionsOrderOptions",
    "OrderResponse",
    "BrokerOrderParams",
    "BrokerExtras",
    
    # Broker
    "BrokerAccount",
    "BrokerOrder",
    "BrokerPosition",
    "BrokerInfo",
    "BrokerConnection",
    "BrokerDataOptions",
    "OrdersFilter",
    "PositionsFilter",
    "AccountsFilter",
] 