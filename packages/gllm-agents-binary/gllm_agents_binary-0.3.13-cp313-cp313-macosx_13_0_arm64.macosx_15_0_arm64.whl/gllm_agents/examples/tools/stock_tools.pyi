from _typeshed import Incomplete
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager
from pydantic import BaseModel
from typing import Any

logger: Incomplete

class StockPriceInput(BaseModel):
    """Input for the stock price tool."""
    symbol: str

def get_stock_price(symbol: str) -> dict[str, Any]:
    """Get current stock price and performance data for a given symbol."""

class StockNewsInput(BaseModel):
    """Input for the stock news tool."""
    symbol: str
    days: int

def get_stock_news(symbol: str, days: int = 7) -> dict[str, Any]:
    """Get recent news for a stock for a specified number of days."""
