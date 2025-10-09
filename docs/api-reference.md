# API Reference

## Core Classes

### Single_Agent

Standalone agent for independent tasks.

#### Constructor Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `llm` | BaseLLM | LLM provider instance | **Required** |
| `identity` | str | Agent's unique identifier | **Required** |
| `description` | str | Agent's purpose and capabilities | **Required** |
| `verbose` | bool | Enable verbose logging | `True` |
| `tools` | list | List of tool classes or instances | `[]` |
| `output_file` | str | Path for output file | `None` |
| `history_folder` | str | Directory for conversation history | `"history"` |

#### Methods

##### `unleash(task: str)`

Execute a task using the agent.

**Parameters:**
- `task` (str): The task description to execute

**Behavior:**
- Loads conversation history if available
- Configures LLM with appropriate system prompt
- Executes the task and saves conversation history

---

### Agent

Multi-agent clan member with specialized capabilities.

#### Constructor Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `llm` | BaseLLM | LLM provider instance | **Required** |
| `identity` | str | Agent's unique identifier | **Required** |
| `description` | str | Agent's responsibilities | **Required** |
| `task` | str | Agent's core objective | **Required** |
| `verbose` | bool | Enable verbose logging | `True` |
| `tools` | list | List of tool classes or instances | `[]` |

#### Methods

##### `unleash()`

Execute the agent's assigned task within a clan context.

**Behavior:**
- Coordinates with other clan members
- Uses inter-agent messaging for collaboration
- Contributes to shared clan objectives

---

### Clan

Multi-agent orchestration and coordination system.

#### Constructor Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `clan_name` | str | Name identifier for the clan | **Required** |
| `manager` | Agent | Lead agent coordinating the clan | **Required** |
| `members` | list | List of Agent instances | **Required** |
| `shared_instruction` | str | Common instructions for all agents | **Required** |
| `goal` | str | Unified clan objective | **Required** |
| `history_folder` | str | Directory for clan history | `"history"` |
| `output_file` | str | Path for final output | `None` |

#### Methods

##### `unleash()`

Execute the coordinated clan task.

**Behavior:**
- Manager agent plans and delegates tasks
- Member agents collaborate and contribute
- Produces unified output based on shared goal

---

## Tool System

### BaseTool

Abstract base class for creating custom tools.

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `name` | str | Tool identifier (auto-generated from class name) |
| `description` | str | Tool functionality description |
| `params` | list | List of Field objects defining parameters |

#### Abstract Methods

##### `_run(**kwargs)`

Implement tool-specific logic.

**Parameters:**
- `**kwargs`: Tool parameters as keyword arguments

**Returns:**
- Tool result (will be wrapped in ToolResult)

#### Public Methods

##### `run(**kwargs) -> ToolResult`

Execute tool with validation and error handling.

**Returns:**
- `ToolResult` object with success status, result, and metadata

##### `validate_parameters(kwargs) -> bool`

Validate input parameters against field definitions.

##### `get_schema() -> dict`

Get tool schema for documentation and introspection.

---

### Field

Parameter definition for tools with type validation.

#### Constructor Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `name` | str | Parameter identifier | **Required** |
| `description` | str | Parameter purpose and usage | **Required** |
| `field_type` | ToolParameterType | Parameter data type | `ToolParameterType.STRING` |
| `default_value` | Any | Default value if not provided | `None` |
| `required` | bool | Whether parameter is mandatory | `True` |

#### Methods

##### `format() -> str`

Format field information for display.

---

### ToolParameterType

Enumeration of supported parameter types.

#### Values

| Type | Description |
|------|-------------|
| `STRING` | Text/string values |
| `INTEGER` | Whole number values |
| `FLOAT` | Decimal number values |
| `BOOLEAN` | True/false values |
| `LIST` | Array/list values |
| `DICT` | Dictionary/object values |
| `ANY` | Any type (fallback) |

---

### ToolResult

Standardized tool execution result.

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `success` | bool | Whether tool execution succeeded |
| `result` | Any | Tool execution result (None if failed) |
| `error_message` | str | Error description if execution failed |
| `metadata` | dict | Additional execution metadata |

---

## LLM Providers

### BaseLLM

Abstract base class for LLM providers.

#### Constructor Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `model` | str | Model identifier | **Required** |
| `temperature` | float | Response creativity (0.0-1.0) | `0.7` |
| `max_tokens` | int | Maximum response length | `2048` |
| `api_key` | str | Provider API key | `None` |
| `verbose` | bool | Enable detailed logging | `False` |

#### Methods

##### `run(messages, **kwargs)`

Execute LLM inference.

**Parameters:**
- `messages`: Conversation history
- `**kwargs`: Provider-specific parameters

**Returns:**
- LLM response

---

### Gemini

Google Gemini LLM provider.

#### Constructor Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `model` | str | Gemini model name | `"gemini-pro"` |
| `temperature` | float | Response creativity | `0.7` |
| `max_tokens` | int | Maximum response length | `2048` |
| `api_key` | str | Google AI API key | `None` |
| `verbose` | bool | Enable detailed logging | `False` |

---

### OpenAI

OpenAI GPT models provider.

#### Constructor Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `model` | str | OpenAI model name | `"gpt-3.5-turbo"` |
| `temperature` | float | Response creativity | `0.7` |
| `max_tokens` | int | Maximum response length | `2048` |
| `api_key` | str | OpenAI API key | `None` |
| `verbose` | bool | Enable detailed logging | `False` |

---

## Configuration

### config Module

API key and configuration management.

#### Functions

##### `set_api_key(provider: str, api_key: str)`

Set API key for specified provider.

**Parameters:**
- `provider` (str): Provider name ("gemini", "openai", "anthropic", etc.)
- `api_key` (str): API key value

**Behavior:**
- Stores key in `~/.unisonai/config.json`
- Makes key available for LLM initialization

---

## MCP Integration

### MCPManager

Model Context Protocol server management.

#### Methods

##### `init_config(config: dict) -> list`

Initialize MCP servers and return available tools.

**Parameters:**
- `config` (dict): MCP server configuration

**Returns:**
- List of MCPTool instances

#### Configuration Format

```python
{
    "mcpServers": {
        "server_name": {
            "command": "server_command",
            "args": ["arg1", "arg2"],
            "env": {"ENV_VAR": "value"}  # Optional
        }
    }
}
```

---

## Error Classes

### MCPError

Base exception for MCP-related errors.

### MCPConnectionError

Raised when MCP server connection fails.

### MCPToolExecutionError

Raised when MCP tool execution fails.

### MCPConfigurationError

Raised when MCP configuration is invalid.

---

## Utility Functions

### create_tools(tools: list) -> str

Format tool information for LLM prompts.

**Parameters:**
- `tools` (list): List of tool classes or instances

**Returns:**
- Formatted string describing available tools
