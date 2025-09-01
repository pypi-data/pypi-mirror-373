"""Order-related type definitions."""

from typing import Optional, Literal, Union
from pydantic import BaseModel, Field


class Order(BaseModel):
    """Basic order structure."""
    
    symbol: str = Field(..., description="Trading symbol")
    side: Literal["buy", "sell"] = Field(..., description="Order side")
    quantity: float = Field(..., description="Order quantity")
    type_: Literal["market", "limit", "stop", "stop_limit"] = Field(..., alias="type", description="Order type")
    price: Optional[float] = Field(None, description="Order price")
    stop_price: Optional[float] = Field(None, description="Stop price")
    time_in_force: Literal["day", "gtc", "opg", "cls", "ioc", "fok"] = Field(..., description="Time in force")
    
    model_config = {"populate_by_name": True}


class OptionsOrder(Order):
    """Options-specific order."""
    
    option_type: Literal["call", "put"] = Field(..., description="Option type")
    strike_price: float = Field(..., description="Strike price")
    expiration_date: str = Field(..., description="Expiration date")


class CryptoOrderOptions(BaseModel):
    """Crypto order options."""
    
    quantity: Optional[float] = Field(None, description="Quantity")
    notional: Optional[float] = Field(None, description="Notional value")


class OptionsOrderOptions(BaseModel):
    """Options order options."""
    
    strike_price: float = Field(..., description="Strike price")
    expiration_date: str = Field(..., description="Expiration date")
    option_type: Literal["call", "put"] = Field(..., description="Option type")
    contract_size: Optional[int] = Field(None, description="Contract size")


class OrderResponse(BaseModel):
    """Order response from API."""
    
    success: bool = Field(..., description="Order success status")
    response_data: dict = Field(..., description="Order response data")
    message: str = Field(..., description="Response message")
    status_code: int = Field(..., description="HTTP status code")


class BrokerOrderParams(BaseModel):
    """Broker order parameters - matches JavaScript SDK exactly."""
    
    broker: Literal["robinhood", "tasty_trade", "ninja_trader"] = Field(..., description="Broker name")
    order_id: Optional[str] = Field(None, description="Optional order ID for modify operations")
    order_type: Literal["Market", "Limit", "Stop", "StopLimit"] = Field(..., description="Order type")
    asset_type: Literal["Stock", "Option", "Crypto", "Futures"] = Field(..., description="Asset type")
    action: Literal["Buy", "Sell"] = Field(..., description="Order action")
    time_in_force: Literal["day", "gtc", "gtd", "ioc", "fok"] = Field(..., description="Time in force")
    account_number: Union[str, int] = Field(..., description="Account number (string or int)")
    symbol: str = Field(..., description="Trading symbol")
    order_qty: float = Field(..., description="Order quantity")
    price: Optional[float] = Field(None, description="Order price")
    stop_price: Optional[float] = Field(None, description="Stop price")


class BrokerExtras(BaseModel):
    """Broker-specific extras for orders - matches JavaScript SDK exactly."""
    
    robinhood: Optional[dict] = Field(None, description="Robinhood-specific options")
    ninjaTrader: Optional[dict] = Field(None, alias="ninja_trader", description="NinjaTrader-specific options")
    tastyTrade: Optional[dict] = Field(None, alias="tasty_trade", description="TastyTrade-specific options")
    
    model_config = {"populate_by_name": True} 