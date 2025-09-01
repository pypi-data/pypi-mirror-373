"""Portfolio-related type definitions."""

from typing import List, Optional
from pydantic import BaseModel, Field


class Holding(BaseModel):
    """Individual holding/position in portfolio."""
    
    symbol: str = Field(..., description="Trading symbol")
    quantity: float = Field(..., description="Quantity held")
    average_price: float = Field(..., description="Average purchase price")
    current_price: float = Field(..., description="Current market price")
    market_value: float = Field(..., description="Current market value")
    unrealized_pnl: float = Field(..., description="Unrealized profit/loss")
    realized_pnl: float = Field(..., description="Realized profit/loss")
    cost_basis: float = Field(..., description="Total cost basis")
    currency: str = Field(..., description="Currency")


class PerformanceMetrics(BaseModel):
    """Portfolio performance metrics."""
    
    total_return: float = Field(..., description="Total return percentage")
    daily_return: float = Field(..., description="Daily return percentage")
    weekly_return: float = Field(..., description="Weekly return percentage")
    monthly_return: float = Field(..., description="Monthly return percentage")
    yearly_return: float = Field(..., description="Yearly return percentage")
    max_drawdown: float = Field(..., description="Maximum drawdown")
    sharpe_ratio: float = Field(..., description="Sharpe ratio")
    beta: float = Field(..., description="Beta")
    alpha: float = Field(..., description="Alpha")


class Portfolio(BaseModel):
    """Portfolio information."""
    
    id: str = Field(..., description="Portfolio ID")
    name: str = Field(..., description="Portfolio name")
    type: str = Field(..., description="Portfolio type")
    status: str = Field(..., description="Portfolio status")
    cash: float = Field(..., description="Available cash")
    buying_power: float = Field(..., description="Buying power")
    equity: float = Field(..., description="Total equity")
    long_market_value: float = Field(..., description="Long market value")
    short_market_value: float = Field(..., description="Short market value")
    initial_margin: float = Field(..., description="Initial margin requirement")
    maintenance_margin: float = Field(..., description="Maintenance margin requirement")
    last_equity: float = Field(..., description="Last equity value")
    positions: List[Holding] = Field(..., description="Portfolio positions")
    performance: PerformanceMetrics = Field(..., description="Performance metrics")


class PortfolioSnapshot(BaseModel):
    """Portfolio snapshot at a point in time."""
    
    timestamp: str = Field(..., description="Snapshot timestamp")
    total_value: float = Field(..., description="Total portfolio value")
    cash: float = Field(..., description="Available cash")
    equity: float = Field(..., description="Total equity")
    positions: List[dict] = Field(..., description="Position data") 