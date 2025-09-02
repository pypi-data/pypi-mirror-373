from langchain_core.messages.ai import AIMessage as AIMessage, UsageMetadata as UsageMetadata
from langchain_core.messages.tool import ToolMessage as ToolMessage
from langgraph.types import Command
from typing import Any

USAGE_METADATA_KEY: str
TOTAL_USAGE_KEY: str
STEP_USAGE_KEY: str

def add_usage_metadata(cur_accumulated_token_usage: UsageMetadata | None, new_token_usage: UsageMetadata | None) -> UsageMetadata | None:
    """Reducer function to accumulate UsageMetadata across agent runs.

    Args:
        cur_accumulated_token_usage: The current accumulated token usage metadata.
        new_token_usage: New token usage metadata to add.

    Returns:
        Accumulated usage metadata or None if both inputs are None.
    """
def extract_and_update_token_usage_from_ai_message(ai_message: AIMessage) -> dict[str, Any]:
    """Extract token usage from AI message and prepare state update.

    Args:
        ai_message: The AI message containing usage metadata.

    Returns:
        Dictionary with accumulated_usage_metadata update if usage metadata is available.
    """
def extract_token_usage_from_tool_output(tool_output: Any) -> UsageMetadata | None:
    """Extract token usage from various tool output formats.

    Supports multiple tool output formats:
    1. Dictionary with 'usage_metadata' field
    2. Command with 'usage_metadata' attribute
    3. Any object with 'usage_metadata' attribute

    Args:
        tool_output: The output from a tool execution.

    Returns:
        UsageMetadata if found, None otherwise.
    """
def extract_token_usage_from_command(command: Command) -> UsageMetadata | None:
    """Extract token usage from Command object.

    Args:
        command: The Command object to extract token usage from.

    Returns:
        UsageMetadata if found, None otherwise.
    """
def extract_token_usage_from_agent_response(agent_response: dict[str, Any]) -> UsageMetadata | None:
    """Extract accumulated token usage from agent response.

    Args:
        agent_response: The agent response to extract token usage from.

    Returns:
        UsageMetadata if found, None otherwise.
    """
