"""Broker-related type definitions."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class BrokerDataOptions(BaseModel):
    """Options for filtering broker data."""
    
    broker_name: Optional[str] = Field(None, description="Filter by broker name")
    account_id: Optional[str] = Field(None, description="Filter by account ID")
    symbol: Optional[str] = Field(None, description="Filter by symbol")


class BrokerInfo(BaseModel):
    """Broker information."""
    
    id: str = Field(..., description="Broker ID")
    name: str = Field(..., description="Broker name")
    display_name: str = Field(..., description="Display name")
    description: str = Field(..., description="Broker description")
    website: str = Field(..., description="Broker website")
    features: List[str] = Field(..., description="Available features")
    auth_type: str = Field(..., description="Authentication type (oauth, api_key, username_password, etc.)")
    logo_path: str = Field(..., description="Logo path")
    is_active: bool = Field(..., description="Whether broker is active")


class BrokerAccount(BaseModel):
    """Broker account information."""
    
    id: str = Field(..., description="Account ID")
    user_broker_connection_id: str = Field(..., description="User broker connection ID")
    broker_provided_account_id: str = Field(..., description="Broker provided account ID")
    account_name: str = Field(..., description="Account name")
    account_type: Optional[str] = Field(None, description="Account type")
    currency: Optional[str] = Field(None, description="Account currency")
    cash_balance: Optional[float] = Field(None, description="Cash balance")
    buying_power: Optional[float] = Field(None, description="Buying power")
    status: Optional[str] = Field(None, description="Account status")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    last_synced_at: str = Field(..., description="Last sync timestamp")


class BrokerOrder(BaseModel):
    """Broker order information."""
    
    id: str = Field(..., description="Order ID")
    user_broker_connection_id: str = Field(..., description="User broker connection ID")
    broker_provided_account_id: str = Field(..., description="Broker provided account ID")
    order_id: Optional[str] = Field(None, description="Order ID")
    symbol: str = Field(..., description="Trading symbol")
    order_type: str = Field(..., description="Order type")
    side: str = Field(..., description="Order side (buy/sell)")
    quantity: float = Field(..., description="Order quantity")
    price: Optional[float] = Field(None, description="Order price")
    status: str = Field(..., description="Order status")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    filled_at: Optional[str] = Field(None, description="Fill timestamp")
    filled_quantity: Optional[float] = Field(None, description="Filled quantity")
    filled_avg_price: Optional[float] = Field(None, description="Filled average price")


class BrokerPosition(BaseModel):
    """Broker position information."""
    
    id: str = Field(..., description="Position ID")
    user_broker_connection_id: str = Field(..., description="User broker connection ID")
    broker_provided_account_id: str = Field(..., description="Broker provided account ID")
    symbol: str = Field(..., description="Trading symbol")
    asset_type: str = Field(..., description="Asset type")
    quantity: float = Field(..., description="Position quantity")
    average_price: Optional[float] = Field(None, description="Average price")
    market_value: float = Field(..., description="Market value")
    cost_basis: float = Field(..., description="Cost basis")
    unrealized_gain_loss: Optional[float] = Field(None, description="Unrealized gain/loss")
    unrealized_gain_loss_percent: Optional[float] = Field(None, description="Unrealized gain/loss percentage")
    current_price: Optional[float] = Field(None, description="Current price")
    last_price: Optional[float] = Field(None, description="Last price")
    last_price_updated_at: Optional[str] = Field(None, description="Last price update timestamp")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")


class BrokerConnection(BaseModel):
    """Broker connection information."""
    
    id: str = Field(..., description="Connection ID")
    broker_id: str = Field(..., description="Broker ID")
    user_id: str = Field(..., description="User ID")
    company_id: Optional[str] = Field(None, description="Company ID")
    status: str = Field(..., description="Connection status")
    connected_at: Optional[str] = Field(None, description="Connection timestamp")
    last_synced_at: Optional[str] = Field(None, description="Last sync timestamp")
    permissions: Optional[Dict[str, bool]] = Field(None, description="Connection permissions")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Connection metadata")
    needs_reauth: Optional[bool] = Field(None, description="Whether re-authentication is needed")


# Filter types for pagination
class OrdersFilter(BaseModel):
    """Filter options for orders pagination."""
    
    broker_id: Optional[str] = Field(None, description="Filter by broker ID")
    connection_id: Optional[str] = Field(None, description="Filter by connection ID")
    account_id: Optional[str] = Field(None, description="Filter by account ID")
    symbol: Optional[str] = Field(None, description="Filter by symbol")
    status: Optional[str] = Field(None, description="Filter by status")
    side: Optional[str] = Field(None, description="Filter by side")
    asset_type: Optional[str] = Field(None, description="Filter by asset type")
    limit: Optional[int] = Field(None, description="Result limit")
    offset: Optional[int] = Field(None, description="Result offset")
    created_after: Optional[str] = Field(None, description="Filter by creation date after (ISO 8601)")
    created_before: Optional[str] = Field(None, description="Filter by creation date before (ISO 8601)")
    with_metadata: Optional[bool] = Field(None, description="Include metadata")


class PositionsFilter(BaseModel):
    """Filter options for positions pagination."""
    
    broker_id: Optional[str] = Field(None, description="Filter by broker ID")
    connection_id: Optional[str] = Field(None, description="Filter by connection ID")
    account_id: Optional[str] = Field(None, description="Filter by account ID")
    symbol: Optional[str] = Field(None, description="Filter by symbol")
    side: Optional[str] = Field(None, description="Filter by side")
    asset_type: Optional[str] = Field(None, description="Filter by asset type")
    position_status: Optional[str] = Field(None, description="Filter by position status")
    limit: Optional[int] = Field(None, description="Result limit")
    offset: Optional[int] = Field(None, description="Result offset")
    updated_after: Optional[str] = Field(None, description="Filter by update date after (ISO 8601)")
    updated_before: Optional[str] = Field(None, description="Filter by update date before (ISO 8601)")
    with_metadata: Optional[bool] = Field(None, description="Include metadata")


class AccountsFilter(BaseModel):
    """Filter options for accounts pagination."""
    
    broker_id: Optional[str] = Field(None, description="Filter by broker ID")
    connection_id: Optional[str] = Field(None, description="Filter by connection ID")
    account_type: Optional[str] = Field(None, description="Filter by account type")
    status: Optional[str] = Field(None, description="Filter by status")
    currency: Optional[str] = Field(None, description="Filter by currency")
    limit: Optional[int] = Field(None, description="Result limit")
    offset: Optional[int] = Field(None, description="Result offset")
    with_metadata: Optional[bool] = Field(None, description="Include metadata") 