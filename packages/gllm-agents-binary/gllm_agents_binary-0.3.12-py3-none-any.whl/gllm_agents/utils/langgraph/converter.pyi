from gllm_inference.schema import MultimodalOutput as MultimodalOutput, MultimodalPrompt as MultimodalPrompt, ToolCall as GllmToolCall
from langchain_core.messages import AIMessage, BaseMessage as BaseMessage
from langchain_core.messages.tool import ToolCall as LangChainToolCall
from typing import Sequence

def convert_langchain_messages_to_multimodal_prompt(messages: Sequence[BaseMessage], instruction: str) -> MultimodalPrompt:
    """Convert LangChain messages to MultimodalPrompt format.

    This function transforms a sequence of LangChain messages into the MultimodalPrompt
    format expected by LM Invoker. It handles system messages, human messages, AI messages
    with tool calls, and tool result messages.

    Args:
        messages: Sequence of LangChain BaseMessage objects to convert.
        instruction: System instruction to prepend if not already present in messages.

    Returns:
        MultimodalPrompt containing the converted message sequence.
    """
def convert_lm_output_to_langchain_message(response: MultimodalOutput) -> AIMessage:
    """Convert LM Invoker output to LangChain AIMessage.

    This function transforms the output from LM Invoker back into LangChain's
    AIMessage format, handling both text responses and tool calls.

    Args:
        response: The response from LM Invoker (MultimodalOutput).

    Returns:
        AIMessage containing the converted response.
    """
def convert_langchain_tool_call_to_gllm_tool_call(lc_tool_call: LangChainToolCall) -> GllmToolCall:
    """Convert LangChain tool call to gllm ToolCall.

    Args:
        lc_tool_call: LangChain ToolCall (TypedDict).

    Returns:
        GllmToolCall object for gllm-inference.
    """
def convert_gllm_tool_call_to_langchain_tool_call(gllm_tool_call: GllmToolCall) -> LangChainToolCall:
    """Convert gllm ToolCall to LangChain ToolCall format.

    Args:
        gllm_tool_call: GllmToolCall object from gllm-inference.

    Returns:
        LangChain ToolCall (TypedDict) with proper type annotation.
    """
