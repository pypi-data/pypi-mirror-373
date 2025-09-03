from langchain_core.tools import BaseTool
from pydantic import BaseModel
from typing import TypeVar

__all__ = ['inject_config_methods_into_tool', 'CONFIG_SCHEMA_ATTR', 'CONFIG_ATTR', 'TOOL_CONFIG_SCHEMA_ATTR', 'TOOL_CONFIGS_KEY']

ConfigSchema = TypeVar('ConfigSchema', bound=BaseModel)
CONFIG_SCHEMA_ATTR: str
CONFIG_ATTR: str
TOOL_CONFIG_SCHEMA_ATTR: str
TOOL_CONFIGS_KEY: str

def inject_config_methods_into_tool(tool: BaseTool, config_schema: type[ConfigSchema]) -> None:
    """Inject configuration methods into a tool.

    This function is used by the SDK to automatically inject configuration capabilities
    into tools that have a tool_config_schema attribute. It can also be used directly
    by developers who want to add configuration support to their tools.

    Args:
        tool: The tool to inject configuration capabilities into.
        config_schema: Pydantic model class for configuration validation.

    Raises:
        ValueError: If tool is not a BaseTool instance or config_schema is not a Pydantic BaseModel subclass.
    """
