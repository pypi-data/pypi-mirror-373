from gllm_agents.agent import LangChainAgent as LangChainAgent
from gllm_agents.examples.tools.langchain_arithmetic_tools import add_numbers as add_numbers

async def langchain_stream_example() -> None:
    """Demonstrates the LangChainAgent's arun_stream method with async execution."""
