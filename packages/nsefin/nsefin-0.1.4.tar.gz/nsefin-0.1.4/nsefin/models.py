
"""
Pydantic models for NSE Finance package data validation and type hints.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Union, Literal
from datetime import datetime
import pandas as pd


class SymbolSearchRequest(BaseModel):
    """Model for symbol search request parameters."""
    symbol: str = Field(..., description="Symbol name or pattern to search for")
    exchange: Literal['NSE', 'NFO'] = Field(default='NSE', description="Exchange to search in")
    exact_match: bool = Field(default=False, description="Whether to perform exact match or partial search")


class HistoricalDataRequest(BaseModel):
    """Model for historical data request parameters."""
    symbol: str = Field(..., description="Symbol name")
    exchange: Literal['NSE', 'NFO'] = Field(default='NSE', description="Exchange name")
    start_date: Optional[datetime] = Field(None, description="Start date for data")
    end_date: Optional[datetime] = Field(None, description="End date for data")
    interval: Literal['1m', '3m', '5m', '10m', '15m', '30m', '1h', '1d', '1w', '1M'] = Field(
        default='1d', description="Time interval for data"
    )


class PriceInfo(BaseModel):
    """Model for current price information."""
    symbol: str = Field(..., description="Stock symbol")
    last_traded_price: float = Field(..., description="Last traded price")
    previous_close: float = Field(..., description="Previous closing price")
    change: float = Field(..., description="Absolute price change")
    percent_change: float = Field(..., description="Percentage price change")
    open_price: float = Field(..., description="Opening price")
    close_price: float = Field(..., description="Closing price")
    high_price: float = Field(..., description="Day's high price")
    low_price: float = Field(..., description="Day's low price")
    vwap: float = Field(..., description="Volume weighted average price")
    upper_circuit: float = Field(..., description="Upper circuit limit")
    lower_circuit: float = Field(..., description="Lower circuit limit")


class TradingHolidayRequest(BaseModel):
    """Model for trading holiday check request."""
    date_str: Optional[str] = Field(None, description="Date in DD-MMM-YYYY format (e.g., '19-Feb-2025')")


class PreMarketRequest(BaseModel):
    """Model for pre-market data request."""
    category: Literal['NIFTY 50', 'Nifty Bank', 'Emerge', 'Securities in F&O', 'Others', 'All'] = Field(
        default='All', description="Pre-market category"
    )


class IndexDetailsRequest(BaseModel):
    """Model for index details request."""
    category: str = Field(..., description="Index category name")
    symbols_only: bool = Field(default=False, description="Return only symbol list if True")


class OptionChainRequest(BaseModel):
    """Model for option chain request."""
    symbol: str = Field(..., description="Symbol name")
    is_index: bool = Field(default=False, description="Whether symbol is an index")


class LiveOptionChainRequest(BaseModel):
    """Model for live option chain request."""
    symbol: str = Field(..., description="Symbol name")
    expiry_date: Optional[str] = Field(None, description="Expiry date in DD-MM-YYYY format")
    data_mode: Literal['full', 'compact'] = Field(default='full', description="Data detail level")
    is_index: bool = Field(default=False, description="Whether symbol is an index")


class CorporateActionsRequest(BaseModel):
    """Model for corporate actions request."""
    from_date: Optional[str] = Field(None, description="Start date in DD-MM-YYYY format")
    to_date: Optional[str] = Field(None, description="End date in DD-MM-YYYY format")
    action_filter: Optional[str] = Field(None, description="Filter by action type")


class BhavCopyRequest(BaseModel):
    """Model for bhav copy request."""
    trade_date: str = Field(..., description="Trading date in DD-MM-YYYY format")


class IndexHistoricalRequest(BaseModel):
    """Model for index historical data request."""
    index_name: str = Field(..., description="Index name")
    from_date: str = Field(..., description="Start date in DD-MM-YYYY format")
    to_date: str = Field(..., description="End date in DD-MM-YYYY format")
