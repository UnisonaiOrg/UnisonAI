# Tool System Guide

## Overview

UnisonAI's tool system provides a robust framework for extending agent capabilities with custom, type-safe, and validated tools. The system supports strong typing, automatic parameter validation, standardized results, and comprehensive error handling.

## Core Components

### BaseTool Class

The foundation for all custom tools in UnisonAI.

#### Structure

```python
from unisonai.tools.tool import BaseTool, Field
from unisonai.tools.types import ToolParameterType

class MyTool(BaseTool):
    def __init__(self):
        self.name = "my_tool"
        self.description = "Description of what my tool does"
        self.params = [
            Field(
                name="parameter_name",
                description="Description of the parameter",
                field_type=ToolParameterType.STRING,
                default_value="default",
                required=True
            )
        ]
        super().__init__()

    def _run(self, **kwargs) -> Any:
        # Tool implementation
        return "result"
```

### Field Definition

Defines tool parameters with type validation.

#### Parameters

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `name` | str | Parameter identifier | Yes |
| `description` | str | Parameter purpose description | Yes |
| `field_type` | ToolParameterType | Parameter data type | No (defaults to STRING) |
| `default_value` | Any | Default value if not provided | No |
| `required` | bool | Whether parameter is mandatory | No (defaults to True) |

### ToolParameterType Enum

Supported parameter types for validation:

- **`STRING`**: Text/string values
- **`INTEGER`**: Whole number values
- **`FLOAT`**: Decimal number values
- **`BOOLEAN`**: True/false values
- **`LIST`**: Array/list values
- **`DICT`**: Dictionary/object values
- **`ANY`**: Any type (fallback)

### ToolResult Class

Standardized tool execution result.

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `success` | bool | Whether execution succeeded |
| `result` | Any | Execution result (None if failed) |
| `error_message` | str | Error description if failed |
| `metadata` | dict | Additional execution information |

## Creating Custom Tools

### Step 1: Define Tool Structure

```python
class CalculatorTool(BaseTool):
    def __init__(self):
        self.name = "calculator"
        self.description = "Perform mathematical calculations"
        self.params = [
            Field(
                name="operation",
                description="Mathematical operation (+, -, *, /)",
                field_type=ToolParameterType.STRING,
                required=True
            ),
            Field(
                name="x",
                description="First number",
                field_type=ToolParameterType.FLOAT,
                required=True
            ),
            Field(
                name="y",
                description="Second number",
                field_type=ToolParameterType.FLOAT,
                required=True
            )
        ]
        super().__init__()
```

### Step 2: Implement Tool Logic

```python
def _run(self, operation: str, x: float, y: float) -> float:
    """Execute mathematical operation with validation."""

    if operation == "+":
        return x + y
    elif operation == "-":
        return x - y
    elif operation == "*":
        return x * y
    elif operation == "/":
        if y == 0:
            raise ValueError("Division by zero")
        return x / y
    else:
        raise ValueError(f"Unsupported operation: {operation}")
```

### Step 3: Use the Tool

```python
# Create tool instance
calc_tool = CalculatorTool()

# Execute with validation
result = calc_tool.run(operation="+", x=10, y=5)

if result.success:
    print(f"Result: {result.result}")
else:
    print(f"Error: {result.error_message}")
```

## Advanced Tool Features

### Optional Parameters

```python
class WeatherTool(BaseTool):
    def __init__(self):
        self.name = "weather"
        self.description = "Get weather information"
        self.params = [
            Field(
                name="city",
                description="City name",
                field_type=ToolParameterType.STRING,
                required=True
            ),
            Field(
                name="include_forecast",
                description="Include 5-day forecast",
                field_type=ToolParameterType.BOOLEAN,
                default_value=False,
                required=False
            )
        ]
        super().__init__()

    def _run(self, city: str, include_forecast: bool = False) -> str:
        # Tool implementation
        return f"Weather for {city}"
```

### List Parameters

```python
class BatchProcessorTool(BaseTool):
    def __init__(self):
        self.name = "batch_processor"
        self.description = "Process multiple items"
        self.params = [
            Field(
                name="items",
                description="List of items to process",
                field_type=ToolParameterType.LIST,
                required=True
            ),
            Field(
                name="operation",
                description="Operation to perform on each item",
                field_type=ToolParameterType.STRING,
                required=True
            )
        ]
        super().__init__()

    def _run(self, items: list, operation: str) -> list:
        results = []
        for item in items:
            # Process each item
            results.append(f"{operation}: {item}")
        return results
```

### Dictionary Parameters

```python
class DatabaseQueryTool(BaseTool):
    def __init__(self):
        self.name = "database_query"
        self.description = "Query database with filters"
        self.params = [
            Field(
                name="table",
                description="Table name",
                field_type=ToolParameterType.STRING,
                required=True
            ),
            Field(
                name="filters",
                description="Query filters",
                field_type=ToolParameterType.DICT,
                required=False
            )
        ]
        super().__init__()

    def _run(self, table: str, filters: dict = None) -> str:
        if filters is None:
            filters = {}
        return f"Querying {table} with filters: {filters}"
```

## Tool Validation System

### Automatic Validation

Tools automatically validate parameters before execution:

```python
# This will fail validation
result = tool.run(invalid_param="value")  # Missing required parameter

# This will succeed
result = tool.run(required_param="value")
```

### Custom Validation

```python
class AdvancedTool(BaseTool):
    def __init__(self):
        self.name = "advanced_tool"
        self.description = "Tool with custom validation"
        self.params = [
            Field(
                name="email",
                description="Email address",
                field_type=ToolParameterType.STRING,
                required=True
            )
        ]
        super().__init__()

    def _run(self, email: str) -> str:
        # Custom validation logic
        if "@" not in email:
            raise ValueError("Invalid email format")
        return f"Processing: {email}"
```

## Error Handling

### ToolResult Error Information

```python
result = tool.run(invalid_param="value")

if not result.success:
    print(f"Error: {result.error_message}")
    print(f"Metadata: {result.metadata}")  # Additional error context
```

### Exception Handling in Tools

```python
def _run(self, **kwargs) -> Any:
    try:
        # Tool logic here
        return result
    except ValueError as e:
        # Return error message instead of raising
        return f"Validation error: {str(e)}"
    except Exception as e:
        # Handle unexpected errors
        return f"Unexpected error: {str(e)}"
```

## Built-in Tools

### WebSearchTool

Web search capabilities with multiple search engines.

```python
from unisonai.tools.websearch import WebSearchTool

# Create and use web search tool
search_tool = WebSearchTool()
result = search_tool.run(
    query="latest AI developments",
    num_results=5,
    search_engine="duckduckgo"  # or "google"
)
```

**Parameters:**
- `query` (str): Search query
- `num_results` (int): Number of results to return
- `search_engine` (str): Search engine to use

### MemoryTool

Conversation memory management.

```python
from unisonai.tools.memory import MemoryTool

memory_tool = MemoryTool()
result = memory_tool.run(
    action="add",
    content="Important information to remember",
    metadata={"category": "research"}
)
```

**Parameters:**
- `action` (str): "add", "get", "search", "clear"
- `content` (str): Content for add action
- `metadata` (dict): Additional metadata

### RAGTool

Retrieval-Augmented Generation for document search.

```python
from unisonai.tools.rag import RAGTool

rag_tool = RAGTool(documents=["doc1.txt", "doc2.txt"])
result = rag_tool.run(
    query="Find information about X",
    top_k=3
)
```

**Parameters:**
- `query` (str): Search query
- `top_k` (int): Number of top results to return

## Tool Integration Patterns

### Single Agent with Multiple Tools

```python
from unisonai import Single_Agent

agent = Single_Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Multi-Tool Assistant",
    description="Assistant with web search, calculation, and weather capabilities",
    tools=[WebSearchTool, CalculatorTool, WeatherTool],
    verbose=True
)

agent.unleash(task="""
    Search for current weather in New York,
    then calculate the average temperature for the week,
    and finally search for good restaurants in the area.
""")
```

### Clan with Specialized Tools

```python
# Research agent with web search
research_agent = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Researcher",
    description="Web research specialist",
    task="Gather information from web sources",
    tools=[WebSearchTool],
    verbose=True
)

# Analysis agent with calculation tools
analysis_agent = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Analyst",
    description="Data analysis and calculation expert",
    task="Analyze data and perform calculations",
    tools=[CalculatorTool, DataAnalysisTool],
    verbose=True
)
```

## Tool Development Best Practices

### 1. Design Principles

- **Single Responsibility**: Each tool should do one thing well
- **Clear Interface**: Intuitive parameter names and descriptions
- **Error Handling**: Comprehensive error handling and user feedback
- **Performance**: Efficient execution, especially for frequent use

### 2. Parameter Design

- **Required vs Optional**: Only mark parameters as required when truly necessary
- **Default Values**: Provide sensible defaults for optional parameters
- **Type Safety**: Use appropriate ToolParameterType values
- **Validation**: Implement custom validation for complex requirements

### 3. Implementation Guidelines

- **Idempotent Operations**: Tools should produce consistent results for same inputs
- **Stateless**: Avoid maintaining state between executions when possible
- **Resource Management**: Properly manage external resources and connections
- **Logging**: Provide meaningful execution information

### 4. Testing Considerations

- **Unit Tests**: Test tool logic independently
- **Integration Tests**: Test tool integration with agents
- **Error Scenarios**: Test error handling and edge cases
- **Performance Tests**: Verify execution time and resource usage

## Advanced Tool Patterns

### Async Tools

```python
import asyncio
from typing import Awaitable

class AsyncTool(BaseTool):
    def __init__(self):
        self.name = "async_tool"
        self.description = "Asynchronous operation tool"
        self.params = [
            Field(
                name="delay",
                description="Delay in seconds",
                field_type=ToolParameterType.INTEGER,
                required=True
            )
        ]
        super().__init__()

    async def _run_async(self, delay: int) -> str:
        """Async implementation of tool logic."""
        await asyncio.sleep(delay)
        return f"Completed after {delay} seconds"

    def _run(self, delay: int) -> Awaitable[str]:
        """Sync wrapper for async tool."""
        return self._run_async(delay)
```

### Tool Composition

```python
class CompositeTool(BaseTool):
    def __init__(self):
        self.name = "composite_tool"
        self.description = "Tool that uses other tools"
        self.params = [
            Field(
                name="operation",
                description="Operation to perform",
                field_type=ToolParameterType.STRING,
                required=True
            )
        ]

        # Initialize sub-tools
        self.calculator = CalculatorTool()
        self.search_tool = WebSearchTool()

        super().__init__()

    def _run(self, operation: str) -> str:
        if operation == "search_and_calculate":
            # Use search tool
            search_result = self.search_tool.run(query="latest data")

            # Use calculator tool
            calc_result = self.calculator.run(operation="+", x=10, y=5)

            return f"Search: {search_result.result}, Calc: {calc_result.result}"

        return "Unknown operation"
```

### Tool with External APIs

```python
import requests

class APITool(BaseTool):
    def __init__(self):
        self.name = "api_tool"
        self.description = "Interact with external APIs"
        self.params = [
            Field(
                name="endpoint",
                description="API endpoint",
                field_type=ToolParameterType.STRING,
                required=True
            ),
            Field(
                name="method",
                description="HTTP method",
                field_type=ToolParameterType.STRING,
                default_value="GET",
                required=False
            )
        ]
        super().__init__()

    def _run(self, endpoint: str, method: str = "GET") -> dict:
        try:
            if method.upper() == "GET":
                response = requests.get(endpoint)
            elif method.upper() == "POST":
                response = requests.post(endpoint)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            raise ValueError(f"API request failed: {str(e)}")
```

## Tool Registry and Discovery

### Manual Tool Registration

```python
# Create tools
tools = [WebSearchTool, CalculatorTool, CustomTool]

# Use with agent
agent = Single_Agent(
    llm=your_llm,
    identity="Tool-Rich Agent",
    description="Agent with multiple tool capabilities",
    tools=tools
)
```

### Dynamic Tool Loading

```python
import importlib
import inspect

def load_tools_from_module(module_name: str) -> list:
    """Dynamically load tools from a module."""
    module = importlib.import_module(module_name)
    tools = []

    for name, obj in inspect.getmembers(module):
        if (inspect.isclass(obj) and
            issubclass(obj, BaseTool) and
            obj != BaseTool):
            tools.append(obj)

    return tools

# Load tools dynamically
custom_tools = load_tools_from_module("my_tools")
```

## Performance Optimization

### Tool Caching

```python
from functools import lru_cache

class CachedTool(BaseTool):
    def __init__(self):
        self.name = "cached_tool"
        self.description = "Tool with result caching"
        self.params = [
            Field(
                name="input_data",
                description="Input for computation",
                field_type=ToolParameterType.STRING,
                required=True
            )
        ]
        super().__init__()

    @lru_cache(maxsize=100)
    def _expensive_computation(self, data: str) -> str:
        # Expensive operation here
        return f"Processed: {data}"

    def _run(self, input_data: str) -> str:
        return self._expensive_computation(input_data)
```

### Batch Processing

```python
class BatchTool(BaseTool):
    def __init__(self):
        self.name = "batch_processor"
        self.description = "Process multiple items efficiently"
        self.params = [
            Field(
                name="items",
                description="List of items to process",
                field_type=ToolParameterType.LIST,
                required=True
            )
        ]
        super().__init__()

    def _run(self, items: list) -> list:
        # Process items in batches for efficiency
        batch_size = 10
        results = []

        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_results = self._process_batch(batch)
            results.extend(batch_results)

        return results

    def _process_batch(self, batch: list) -> list:
        # Process a batch of items
        return [f"processed_{item}" for item in batch]
```

## Debugging and Monitoring

### Tool Debugging

```python
class DebugTool(BaseTool):
    def __init__(self):
        self.name = "debug_tool"
        self.description = "Tool with detailed logging"
        self.params = [
            Field(
                name="data",
                description="Data to process",
                field_type=ToolParameterType.ANY,
                required=True
            )
        ]
        super().__init__()

    def _run(self, data) -> str:
        import logging

        # Log execution details
        logging.info(f"Processing data: {data}")

        try:
            result = self._process_data(data)
            logging.info(f"Success: {result}")
            return result
        except Exception as e:
            logging.error(f"Error: {str(e)}")
            raise

    def _process_data(self, data):
        # Tool logic with error handling
        return f"Debug processed: {data}"
```

### Performance Monitoring

```python
import time

class MonitoredTool(BaseTool):
    def __init__(self):
        self.name = "monitored_tool"
        self.description = "Tool with performance monitoring"
        self.params = [
            Field(
                name="operation",
                description="Operation to perform",
                field_type=ToolParameterType.STRING,
                required=True
            )
        ]
        super().__init__()

    def _run(self, operation: str) -> dict:
        start_time = time.time()

        try:
            result = self._perform_operation(operation)

            execution_time = time.time() - start_time

            return {
                "result": result,
                "execution_time": execution_time,
                "success": True
            }

        except Exception as e:
            execution_time = time.time() - start_time

            return {
                "error": str(e),
                "execution_time": execution_time,
                "success": False
            }
```

## Tool Examples

See the `examples/` folder for complete tool implementations:

- **[basic_tools.py](./examples/basic_tools.py)**: Simple tool examples
- **[advanced_tools.py](./examples/advanced_tools.py)**: Complex tool patterns
- **[api_tools.py](./examples/api_tools.py)**: External API integration
- **[async_tools.py](./examples/async_tools.py)**: Asynchronous tool examples

## Troubleshooting

### Common Issues

1. **Parameter Validation Errors**
   - Check parameter types match Field definitions
   - Verify required parameters are provided
   - Ensure default values are appropriate

2. **Tool Execution Failures**
   - Implement proper error handling in `_run` methods
   - Check for external dependencies and permissions
   - Verify tool logic handles edge cases

3. **Performance Issues**
   - Monitor tool execution time
   - Implement caching for expensive operations
   - Consider batch processing for multiple items

4. **Integration Problems**
   - Ensure tools are properly instantiated
   - Check tool registration with agents
   - Verify tool schemas are correctly formatted

For more help, see the [Usage Guidelines](./usage-guide.md) and [API Reference](./api-reference.md).
