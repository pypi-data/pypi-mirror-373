from gllm_agents.agent import LangGraphAgent as LangGraphAgent
from gllm_agents.agent.types import A2AClientConfig as A2AClientConfig

async def main() -> None:
    """Main function demonstrating the Three-Level Agent Hierarchy client."""
async def test_research_task(client_agent, coordinator_card) -> None:
    """Test a research-only task that flows through research specialists and workers."""
async def test_content_task(client_agent, coordinator_card) -> None:
    """Test a content-only task that flows through content specialists and workers."""
async def test_complex_task(client_agent, coordinator_card) -> None:
    """Test a complex task requiring both research and content specialists."""
async def test_artifact_generation(client_agent, coordinator_card) -> None:
    """Test artifact generation across the hierarchy."""
def handle_artifacts(result, test_name) -> None:
    """Handle and display information about artifacts from the result."""
def print_artifact_info(artifact: dict) -> None:
    """Print information about an artifact.

    Args:
        artifact: Dictionary containing artifact information.
    """
def print_hierarchy_info() -> None:
    """Print information about the 3-level hierarchy being tested."""
