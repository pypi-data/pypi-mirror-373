from langchain_core.runnables import RunnableConfig as RunnableConfig
from langchain_core.tools import BaseTool
from pydantic import BaseModel

class CurrencyConfig(BaseModel):
    """Tool configuration schema."""
    tenant_id: str
    auth_key: str

class CurrencyInput(BaseModel):
    """Input schema for currency exchange."""
    amount: float
    from_currency: str
    to_currency: str

class CurrencyExchangeTool(BaseTool):
    """Simple currency exchange tool with SDK auto-injection configuration."""
    name: str
    description: str
    args_schema: type[BaseModel]
    tool_config_schema: type[BaseModel]
