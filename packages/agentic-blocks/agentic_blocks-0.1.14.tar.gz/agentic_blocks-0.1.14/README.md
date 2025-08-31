# Agentic Blocks

Building blocks for agentic systems with a focus on simplicity and ease of use.

## Overview

Agentic Blocks provides clean, simple components for building AI agent systems, specifically focused on:

- **MCP Client**: Connect to Model Control Protocol (MCP) endpoints with a sync-by-default API
- **Messages**: Manage LLM conversation history with OpenAI-compatible format
- **LLM**: Simple function for calling OpenAI-compatible completion APIs

All components follow principles of simplicity, maintainability, and ease of use.

## Installation

```bash
pip install -e .
```

For development:
```bash
pip install -e ".[dev]"
```

## Quick Start

### MCPClient - Connect to MCP Endpoints

The MCPClient provides a unified interface for connecting to different types of MCP endpoints:

```python
from agentic_blocks import MCPClient

# Connect to an SSE endpoint (sync by default)
client = MCPClient("https://example.com/mcp/server/sse")

# List available tools
tools = client.list_tools()
print(f"Available tools: {len(tools)}")

# Call a tool
result = client.call_tool("search", {"query": "What is MCP?"})
print(result)
```

**Supported endpoint types:**
- **SSE endpoints**: URLs with `/sse` in the path
- **HTTP endpoints**: URLs with `/mcp` in the path  
- **Local scripts**: File paths to Python MCP servers

**Async support for advanced users:**
```python
# Async versions available
tools = await client.list_tools_async()
result = await client.call_tool_async("search", {"query": "async example"})
```

### Messages - Manage Conversation History

The Messages class helps build and manage LLM conversations in OpenAI-compatible format:

```python
from agentic_blocks import Messages

# Initialize with system prompt
messages = Messages(
    system_prompt="You are a helpful assistant.",
    user_prompt="Hello, how can you help me?",
    add_date_and_time=True
)

# Add assistant response
messages.add_assistant_message("I can help you with various tasks!")

# Add tool calls
tool_call = {
    "id": "call_123",
    "type": "function", 
    "function": {"name": "get_weather", "arguments": '{"location": "Paris"}'}
}
messages.add_tool_call(tool_call)

# Add tool response
messages.add_tool_response("call_123", "The weather in Paris is sunny, 22°C")

# Get messages for LLM API
conversation = messages.get_messages()

# View readable format
print(messages)
```

### LLM - Call OpenAI-Compatible APIs

The `call_llm` function provides a simple interface for calling LLM completion APIs:

```python
from agentic_blocks import call_llm, Messages

# Method 1: Using with Messages object
messages = Messages(
    system_prompt="You are a helpful assistant.",
    user_prompt="What is the capital of France?"
)

response = call_llm(messages, temperature=0.7)
print(response)  # "The capital of France is Paris."
```

```python
# Method 2: Using with raw message list  
messages_list = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is 2+2?"}
]

response = call_llm(messages_list, model="gpt-4o-mini")
print(response)  # "2+2 equals 4."
```

```python
# Method 3: Using with tools (for function calling)
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"}
                },
                "required": ["location"]
            }
        }
    }
]

messages = Messages(user_prompt="What's the weather like in Stockholm?")
response = call_llm(messages, tools=tools)
print(response)
```

**Environment Setup:**
Create a `.env` file in your project root:
```
OPENAI_API_KEY=your_api_key_here
```

Or pass the API key directly:
```python
response = call_llm(messages, api_key="your_api_key_here")
```

## Complete Example - Tool Calling with Weather API

This example demonstrates a complete workflow using function calling with an LLM. For a full interactive notebook version, see `notebooks/agentic_example.ipynb`.

```python
from agentic_blocks import call_llm, Messages

# Define tools in OpenAI function calling format
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather information for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA"
                    },
                    "unit": {
                        "type": "string", 
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature unit"
                    }
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Perform a mathematical calculation",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate"
                    }
                },
                "required": ["expression"]
            }
        }
    }
]

# Create conversation with system and user prompts
messages = Messages(
    system_prompt="You are a helpful assistant with access to weather and calculation tools.",
    user_prompt="What is the weather in Stockholm?"
)

# Call LLM with tools - it will decide which tools to call
model = "gpt-4o-mini"  # or your preferred model
response = call_llm(model=model, messages=messages, tools=tools)

# Add the LLM's response (including any tool calls) to conversation
messages.add_response_message(response)

# Display the conversation so far
for message in messages.get_messages():
    print(message)

# Check if there are pending tool calls that need execution
print("Has pending tool calls:", messages.has_pending_tool_calls())

# In a real implementation, you would:
# 1. Execute the actual tool calls (get_weather, calculate, etc.)
# 2. Add tool responses using messages.add_tool_response()
# 3. Call the LLM again to get the final user-facing response
```

**Expected Output:**
```
{'role': 'system', 'content': 'You are a helpful assistant with access to weather and calculation tools.'}
{'role': 'user', 'content': 'What is the weather in Stockholm?'}
{'role': 'assistant', 'content': '', 'tool_calls': [{'id': 'call_abc123', 'type': 'function', 'function': {'name': 'get_weather', 'arguments': '{"location": "Stockholm, Sweden", "unit": "celsius"}'}}]}
Has pending tool calls: True
```

**Key Features Demonstrated:**
- **Messages management**: Clean conversation history with system/user prompts
- **Tool calling**: LLM automatically decides to call the `get_weather` function
- **Response handling**: `add_response_message()` handles both content and tool calls
- **Pending detection**: `has_pending_tool_calls()` identifies when tools need execution

**Next Steps:**
After the LLM makes tool calls, you would implement the actual tool functions and continue the conversation:

```python
# Implement actual weather function
def get_weather(location, unit="celsius"):
    # Your weather API implementation here
    return f"The weather in {location} is sunny, 22°{unit[0].upper()}"

# Execute pending tool calls
if messages.has_pending_tool_calls():
    last_message = messages.get_messages()[-1]
    for tool_call in last_message.get("tool_calls", []):
        if tool_call["function"]["name"] == "get_weather":
            import json
            args = json.loads(tool_call["function"]["arguments"])
            result = get_weather(**args)
            messages.add_tool_response(tool_call["id"], result)
    
    # Get final response from LLM
    final_response = call_llm(model=model, messages=messages)
    messages.add_assistant_message(final_response)
    print(f"Final response: {final_response}")
```

## Development Principles

This project follows these core principles:

- **Simplicity First**: Keep code simple, readable, and focused on core functionality
- **Sync-by-Default**: Primary methods are synchronous for ease of use, with optional async versions
- **Minimal Dependencies**: Avoid over-engineering and complex error handling unless necessary  
- **Clean APIs**: Prefer straightforward method names and clear parameter expectations
- **Maintainable Code**: Favor fewer lines of clear code over comprehensive edge case handling

## API Reference

### MCPClient

```python
MCPClient(endpoint: str, timeout: int = 30)
```

**Methods:**
- `list_tools() -> List[Dict]`: Get available tools (sync)
- `call_tool(name: str, args: Dict) -> Dict`: Call a tool (sync)
- `list_tools_async() -> List[Dict]`: Async version of list_tools
- `call_tool_async(name: str, args: Dict) -> Dict`: Async version of call_tool

### Messages

```python
Messages(system_prompt=None, user_prompt=None, add_date_and_time=False)
```

**Methods:**
- `add_system_message(content: str)`: Add system message
- `add_user_message(content: str)`: Add user message
- `add_assistant_message(content: str)`: Add assistant message
- `add_tool_call(tool_call: Dict)`: Add tool call to assistant message
- `add_tool_calls(tool_calls)`: Add multiple tool calls from ChatCompletionMessageFunctionToolCall objects
- `add_response_message(message)`: Add ChatCompletionMessage response to conversation
- `add_tool_response(call_id: str, content: str)`: Add tool response
- `get_messages() -> List[Dict]`: Get all messages
- `has_pending_tool_calls() -> bool`: Check for pending tool calls

### call_llm

```python
call_llm(messages, tools=None, api_key=None, model="gpt-4o-mini", **kwargs) -> str
```

**Parameters:**
- `messages`: Either a `Messages` instance or list of message dictionaries
- `tools`: Optional list of tools in OpenAI function calling format
- `api_key`: OpenAI API key (defaults to OPENAI_API_KEY from .env)
- `model`: Model name to use for completion
- `**kwargs`: Additional parameters passed to OpenAI API (temperature, max_tokens, etc.)

**Returns:** The assistant's response content as a string

## Requirements

- Python >= 3.11
- Dependencies: `mcp`, `requests`, `python-dotenv`, `openai`

## License

MIT