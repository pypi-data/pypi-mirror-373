"""
Simplified LLM client for calling completion APIs.
"""

import os
from typing import List, Dict, Any, Optional, Union

from dotenv import load_dotenv
from openai import OpenAI

from agentic_blocks.messages import Messages
from agentic_blocks.utils.tools_utils import langchain_tools_to_openai_format


class LLMError(Exception):
    """Exception raised when there's an error calling the LLM API."""

    pass


def call_llm(
    messages: Union[Messages, List[Dict[str, Any]]],
    tools: Optional[Union[List[Dict[str, Any]], List]] = None,
    api_key: Optional[str] = None,
    model: str = "gpt-4o-mini",
    base_url: Optional[str] = None,
    **kwargs,
) -> Any:
    """
    Call an LLM completion API with the provided messages.

    Args:
        messages: Either a Messages instance or a list of message dicts
        tools: Optional list of tools in OpenAI function calling format or LangChain StructuredTools
        api_key: OpenAI API key (if not provided, loads from .env OPENAI_API_KEY)
        model: Model name to use for completion
        base_url: Base URL for the API (useful for VLLM or other OpenAI-compatible servers)
        **kwargs: Additional parameters to pass to OpenAI API

    Returns:
        The complete message object from the OpenAI API response

    Raises:
        LLMError: If API call fails or configuration is invalid
    """
    # Load environment variables
    load_dotenv()

    # Get API key
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key and not base_url:
        raise LLMError(
            "API key not found. Set OPENROUTER_API_KEY or OPENAI_API_KEY environment variable or pass api_key parameter."
        )

    if api_key and api_key.startswith("sk-or"):
        base_url = "https://openrouter.ai/api/v1"

    if base_url and not api_key:
        api_key = "EMPTY"

    # Initialize OpenAI client
    client_kwargs = {}
    if api_key:
        client_kwargs["api_key"] = api_key
    if base_url:
        client_kwargs["base_url"] = base_url
    client = OpenAI(**client_kwargs)

    # Handle different message input types
    if isinstance(messages, Messages):
        conversation_messages = messages.get_messages()
    else:
        conversation_messages = messages

    if not conversation_messages:
        raise LLMError("No messages provided for completion.")

    # Handle tools parameter - convert LangChain tools if needed
    openai_tools = None
    if tools:
        # Check if it's a list of LangChain StructuredTools
        if tools and hasattr(tools[0], 'args_schema'):
            openai_tools = langchain_tools_to_openai_format(tools)
        else:
            openai_tools = tools

    try:
        # Prepare completion parameters
        completion_params = {
            "model": model,
            "messages": conversation_messages,
            **kwargs,
        }

        if openai_tools:
            completion_params["tools"] = openai_tools
            completion_params["tool_choice"] = "auto"

        # Make completion request
        response = client.chat.completions.create(**completion_params)

        # Return the complete message object
        return response.choices[0].message

    except Exception as e:
        raise LLMError(f"Failed to call LLM API: {e}")


def example_usage():
    """Example of how to use the call_llm function."""
    # Example 1: Using with Messages object
    messages_obj = Messages(
        system_prompt="You are a helpful assistant.",
        user_prompt="What is the capital of France?",
    )

    # Example 2: Using with raw message list
    messages_list = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"},
    ]

    # Example tools
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get current weather for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City and state, e.g. San Francisco, CA",
                        }
                    },
                    "required": ["location"],
                },
            },
        }
    ]

    try:
        # Call with Messages object
        print("Using Messages object:")
        response1 = call_llm(messages_obj, temperature=0.7)
        print(f"Response: {response1.content}")

        # Call with raw message list
        print("\nUsing raw message list:")
        response2 = call_llm(messages_list, tools=tools, temperature=0.5)
        if hasattr(response2, "tool_calls") and response2.tool_calls:
            print(f"Tool calls requested: {len(response2.tool_calls)}")
            for i, tool_call in enumerate(response2.tool_calls):
                print(
                    f"  {i + 1}. {tool_call.function.name}({tool_call.function.arguments})"
                )
        else:
            print(f"Response: {response2.content}")

    except LLMError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    example_usage()
