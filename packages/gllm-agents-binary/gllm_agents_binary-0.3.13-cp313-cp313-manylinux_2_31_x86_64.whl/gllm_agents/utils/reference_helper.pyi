from _typeshed import Incomplete
from gllm_core.schema import Chunk
from typing import Any

logger: Incomplete

def validate_references(references: list[Any]) -> list[Chunk]:
    """Deduplicate reference data from agent state.

    Since the reducer function (add_references_chunks) already filters for valid Chunk objects,
    this function focuses on deduplication by content.

    Args:
        references: List of reference data from agent state (expected to be Chunk objects).

    Returns:
        List of deduplicated Chunk objects by content.
    """
def serialize_references_for_metadata(references: list[Any]) -> list[dict[str, Any]]:
    """Serialize references for inclusion in A2A metadata.

    Args:
        references: List of reference objects (typically Chunk objects).

    Returns:
        List of serialized reference dictionaries.
    """
def add_references_chunks(left: list[Chunk], right: list[Chunk]) -> list[Chunk]:
    """Reducer function to accumulate reference data from multiple tool calls.

    This is a LangGraph reducer function that should be forgiving and handle
    edge cases gracefully. Non-Chunk items are filtered out.

    Args:
        left: Existing list of reference chunks (or None/non-list)
        right: New list of reference chunks to add (or None/non-list)

    Returns:
        Combined list of valid Chunk objects
    """
def extract_references_from_agent_response(result: Any) -> list[dict[str, Any]] | None:
    """Extract references from agent response for delegation tools.

    Args:
        result: The result returned by the delegated agent.

    Returns:
        List of reference chunks if found, None otherwise.
    """
