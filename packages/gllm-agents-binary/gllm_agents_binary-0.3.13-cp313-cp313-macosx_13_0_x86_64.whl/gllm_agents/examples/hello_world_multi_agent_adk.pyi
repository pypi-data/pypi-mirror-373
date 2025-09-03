from gllm_agents.agent.google_adk_agent import GoogleADKAgent as GoogleADKAgent
from gllm_agents.examples.tools.adk_arithmetic_tools import sum_numbers as sum_numbers
from gllm_agents.examples.tools.adk_weather_tool import get_weather as get_weather

async def multi_agent_example() -> None:
    """Demonstrates multi-agent coordination with GoogleADKAgent."""
