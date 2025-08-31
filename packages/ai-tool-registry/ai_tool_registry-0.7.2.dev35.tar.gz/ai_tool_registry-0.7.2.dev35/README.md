# Universal Tool Registry Module

Advanced tool registration system for multiple AI providers with automatic schema generation, validation, and error handling. Supports **Anthropic Claude**, **OpenAI**, **Mistral AI**, **AWS Bedrock**, and **Google Gemini**.

## Features

- **Multi-provider support** - Works with all major AI providers
- **Automatic JSON schema generation** from function signatures
- **Pydantic model integration** and validation
- **ToolContext parameter filtering** - Automatic exclusion of context parameters with type safety
- **Legacy parameter filtering** for internal/context parameters
- **Unified interface** across different AI providers
- **Comprehensive error handling** and logging
- **Type safety** with full type hints
- **Optional dependencies** - Install only what you need

## Installation

### Basic Installation

```bash
# Using UV (recommended)
uv add ai-tool-registry

# Using pip
pip install ai-tool-registry
```

### Provider-Specific Installation

```bash
# For Anthropic Claude
uv add ai-tool-registry[anthropic]

# For OpenAI
uv add ai-tool-registry[openai]

# For Mistral AI 
uv add ai-tool-registry[mistral]

# For AWS Bedrock
uv add ai-tool-registry[bedrock]

# For Google Gemini
uv add ai-tool-registry[gemini]

# Install all providers
uv add ai-tool-registry[all]
```

## Quick Start

```python
from tool_registry_module import tool, build_registry_openai, build_registry_anthropic, ToolContext
from pydantic import BaseModel
from typing import Annotated


class UserData(BaseModel):
    name: str
    age: int


@tool(description="Process user information")
def process_user(
    input: UserData, 
    context: ToolContext[dict] = None  # Automatically excluded from schema
) -> UserData:
    # context parameter is available for use but won't appear in AI tool schema
    return input


# Build registries for different providers
openai_registry = build_registry_openai([process_user])
anthropic_registry = build_registry_anthropic([process_user])

# Use with respective APIs
openai_tools = [entry["representation"] for entry in openai_registry.values()]
anthropic_tools = [entry["representation"] for entry in anthropic_registry.values()]
```

## Multi-Provider Examples

### OpenAI Function Calling

```python
from tool_registry_module import tool, build_registry_openai
import openai

@tool(description="Get weather information")
def get_weather(location: str, unit: str = "celsius") -> str:
    return f"Weather in {location}: 22°{unit[0].upper()}"

# Build OpenAI registry
registry = build_registry_openai([get_weather])
tools = [entry["representation"] for entry in registry.values()]

# Use with OpenAI
client = openai.OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
    tools=tools
)
```

### Anthropic Claude

```python
from tool_registry_module import tool, build_registry_anthropic
import anthropic

registry = build_registry_anthropic([get_weather])
tools = [entry["representation"] for entry in registry.values()]

# Use with Anthropic
client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-3-sonnet-20240229",
    max_tokens=1000,
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
    tools=tools
)
```

### AWS Bedrock

```python
from tool_registry_module import tool, build_registry_bedrock
import boto3

registry = build_registry_bedrock([get_weather])
tools = [entry["representation"] for entry in registry.values()]

# Use with Bedrock
client = boto3.client("bedrock-runtime")
# Use tools in your Bedrock converse API calls
```

### Google Gemini

```python
from tool_registry_module import tool, build_registry_gemini
import google.generativeai as genai

registry = build_registry_gemini([get_weather])
tools = [entry["representation"] for entry in registry.values()]

# Use with Gemini
model = genai.GenerativeModel('gemini-pro')
# Use tools in your Gemini function calling
```

### Mistral AI

```python
from tool_registry_module import tool, build_registry_mistral
from mistralai.client import MistralClient

registry = build_registry_mistral([get_weather])
tools = [entry["representation"] for entry in registry.values()]

# Use with Mistral
client = MistralClient()
# Use tools in your Mistral function calling
```

## Advanced Usage

### Parameter Filtering

#### Using ToolContext (Recommended)

Use `ToolContext` to mark parameters that should be automatically excluded from schemas:

```python
from tool_registry_module import tool, ToolContext
from typing import Annotated

@tool(description="Process user data with context")
def process_data(
    user_input: str,
    context: ToolContext[dict],  # Direct ToolContext generic
    session: Annotated[str, ToolContext],  # Annotated ToolContext
    debug_flag: bool = False
) -> str:
    # context and session parameters are automatically excluded from the schema
    # but available for use in your function
    return f"Processed: {user_input}"
```

**ToolContext Features:**
- **Automatic exclusion** - No need to manually specify `ignore_in_schema`
- **Type safety** - Full type hints with generic support
- **Reference preservation** - Objects maintain their references for mutation within functions
- **Multiple forms** - Both direct (`ToolContext[T]`) and annotated (`Annotated[T, ToolContext]`) syntax
- **Union validation** - Prevents incorrect usage in union types

**Supported ToolContext patterns:**
```python
# Direct generic types
param1: ToolContext[dict]
param2: ToolContext[str] 

# Annotated types
param3: Annotated[str, ToolContext]
param4: Annotated[dict, ToolContext, "description"]

# Union types will raise TypeError (prevented for safety)
# param5: Union[str, ToolContext[dict]]  # ❌ Not allowed
```

**Reference Preservation Example:**
```python
from tool_registry_module import tool, ToolContext

# Context objects maintain their references for mutation
@tool(description="Track user interactions")
def track_interaction(
    action: str,
    user_context: ToolContext[dict]  # This dict can be modified
) -> str:
    # Modify the context object - changes persist outside function
    user_context["actions"] = user_context.get("actions", [])
    user_context["actions"].append(action)
    user_context["last_action"] = action
    return f"Tracked: {action}"

# Usage
context = {"user_id": "123"}
track_interaction("login", user_context=context)
track_interaction("view_profile", user_context=context)

# Context object is modified:
print(context)  
# {'user_id': '123', 'actions': ['login', 'view_profile'], 'last_action': 'view_profile'}
```

#### Legacy Parameter Filtering

You can still manually exclude parameters using `ignore_in_schema`:

```python
@tool(
    description="Calculate area with debug output",
    ignore_in_schema=["debug_mode", "context"]
)
def calculate_area(length: float, width: float, debug_mode: bool = False, context: str = "calc") -> float:
    if debug_mode:
        print(f"Calculating area for {length} x {width}")
    return length * width
```

### Cache Control (Anthropic)

Add cache control for better performance with Anthropic:

```python
@tool(
    description="Expensive computation",
    cache_control={"type": "ephemeral"}
)
def expensive_function(data: str) -> str:
    # Expensive computation here
    return processed_data
```

#### Registry Utilities

```python
from tool_registry_module import get_tool_info, validate_registry

# Get information about a specific tool
info = get_tool_info(registry, "process_user")
print(info["description"])

# Validate registry structure
is_valid = validate_registry(registry)
```

### Tool Use Handling

The registry is a dictionary that enables dynamic function calling for AI tool responses:

```python
from tool_registry_module import tool, build_registry_anthropic

@tool(description="Add two numbers")
def add_numbers(a: int, b: int) -> int:
    return a + b

@tool(description="Get weather info")
def get_weather(city: str, units: str = "celsius") -> str:
    return f"Weather in {city}: 22°{units[0].upper()}"

# Build registry
registry = build_registry_anthropic([add_numbers, get_weather])

# Handle tool use responses dynamically
def handle_tool_calls(tool_calls, registry):
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.name
        tool_args = tool_call.input
        
        if tool_name in registry:
            try:
                # Get function from registry and execute
                tool_func = registry[tool_name]["tool"]
                result = tool_func(**tool_args)
                results.append({
                    "tool_use_id": tool_call.id,
                    "content": str(result)
                })
            except Exception as e:
                results.append({
                    "tool_use_id": tool_call.id,
                    "error": f"Error: {e}"
                })
        else:
            results.append({
                "tool_use_id": tool_call.id,
                "error": f"Tool '{tool_name}' not found"
            })
    
    return results

# Registry structure: {tool_name: {"tool": callable, "representation": provider_format}}
# Use registry[tool_name]["tool"] for dynamic function calling
```

## Supported Providers

| Provider | Function | Format |
|----------|----------|---------|
| **Anthropic Claude** | `build_registry_anthropic()` | Claude ToolParam |
| **OpenAI** | `build_registry_openai()` | OpenAI Function Call |
| **Mistral AI** | `build_registry_mistral()` | Mistral Function Call |
| **AWS Bedrock** | `build_registry_bedrock()` | Bedrock ToolSpec |
| **Google Gemini** | `build_registry_gemini()` | Gemini FunctionDeclaration |

## Requirements

- **Python 3.12+**
- **pydantic >= 2.0.0** (required)

### Optional Provider Dependencies

- **anthropic >= 0.52.2** (for Anthropic Claude)
- **openai >= 1.0.0** (for OpenAI)
- **mistralai >= 0.4.0** (for Mistral AI)  
- **boto3 >= 1.34.0** (for AWS Bedrock)
- **google-generativeai >= 0.3.0** (for Google Gemini)

## Migration from v2.x

The old `build_registry_anthropic_tool_registry()` function is still available for backward compatibility but deprecated. Use `build_registry_anthropic()` instead.

## License

MIT License

## Development

### Setup

```bash
# Clone and install with dev dependencies
git clone https://github.com/kazmer97/ai-tool-registry.git
cd ai-tool-registry
uv sync --extra dev

# Run linting
uv run ruff check .
uv run ruff format .
```

### Testing

```bash
# Run tests (when available)
uv run pytest

# Type checking
uv run mypy tool_registry_module/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Run linting: `uv run ruff check . && uv run ruff format .`
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request