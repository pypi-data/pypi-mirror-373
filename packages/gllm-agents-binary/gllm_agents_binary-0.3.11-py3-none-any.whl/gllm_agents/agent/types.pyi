from a2a.types import AgentCard as AgentCard
from enum import StrEnum
from gllm_core.utils.retry import RetryConfig as RetryConfig
from pydantic import BaseModel
from typing import Any

class StreamMode(StrEnum):
    """LangGraph stream modes for astream operations.

    These modes control what data is included in the streaming output.
    """
    VALUES = 'values'
    CUSTOM = 'custom'

class HttpxClientOptions(BaseModel):
    """Options for the HTTP client.

    Args:
        timeout: The timeout for the HTTP client.
    """
    timeout: float | None
    class Config:
        """Config for HttpxClientOptions."""
        extra: str

class A2AClientConfig(BaseModel):
    """Configuration for A2A client.

    Args:
        discovery_urls: A list of base URLs to discover agents from using .well-known/agent.json.
        known_agents: A dictionary of known agents, keyed by AgentCard.name,
                      storing the parsed AgentCard objects. Can be pre-populated or
                      augmented by discovery.
        httpx_client_options: Options for the HTTP client.
    """
    discovery_urls: list[str] | None
    known_agents: dict[str, AgentCard]
    httpx_client_options: HttpxClientOptions | None

class BaseAgentConfig(BaseModel):
    """Base configuration for agent implementations.

    This class provides common configuration fields that all agent implementations
    can use. It serves as a foundation for more specific configuration classes.

    Args:
        tools: List of tools available to the agent.
        default_hyperparameters: Default hyperparameters for the language model.
    """
    tools: list[Any] | None
    default_hyperparameters: dict[str, Any] | None
    class Config:
        """Config for BaseAgentConfig."""
        extra: str

class AgentConfig(BaseAgentConfig):
    """Configuration for agent implementations with language model settings.

    This class extends BaseAgentConfig with language model specific configuration
    fields including provider, model name, API settings, and hyperparameters.

    Args:
        lm_name: The name of the language model to use.
        lm_hyperparameters: Hyperparameters for the language model.
        lm_provider: The provider of the language model (e.g., 'openai', 'google').
        lm_base_url: The base URL for the language model API.
        lm_api_key: The API key for the language model service.
        lm_retry_config: Retry configuration for the language model.
    """
    lm_name: str | None
    lm_hyperparameters: dict[str, Any] | None
    lm_provider: str | None
    lm_base_url: str | None
    lm_api_key: str | None
    lm_retry_config: RetryConfig | None
