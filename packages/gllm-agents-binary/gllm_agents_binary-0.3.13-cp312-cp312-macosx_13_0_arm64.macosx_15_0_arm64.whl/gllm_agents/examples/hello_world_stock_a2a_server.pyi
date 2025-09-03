from _typeshed import Incomplete
from gllm_agents.agent import LangGraphAgent as LangGraphAgent
from gllm_agents.examples.tools.stock_tools import StockNewsInput as StockNewsInput, StockPriceInput as StockPriceInput, get_stock_news as get_stock_news, get_stock_price as get_stock_price
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager
from langchain_core.tools import BaseTool as BaseTool

logger: Incomplete
SERVER_AGENT_NAME: str
stock_tools: list[BaseTool]

def main(host: str, port: int):
    """Runs the StockAgent A2A server."""
