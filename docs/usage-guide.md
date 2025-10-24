# Usage Guidelines

## Getting Started

### Prerequisites

- **Python 3.10-3.12** (required for compatibility)
- **API Keys** for desired LLM providers
- **Internet Connection** for web-based tools

### Installation

```bash
pip install unisonai
```

### Basic Setup

1. **Import Required Modules**
```python
from unisonai import Agent, Clan
from unisonai.llms import Gemini, OpenAI, Anthropic
from unisonai.tools.memory import MemoryTool
from unisonai import config
```

2. **Configure API Keys**
```python
# Option 1: Environment Variables
import os
os.environ['GEMINI_API_KEY'] = 'your-gemini-key'
os.environ['OPENAI_API_KEY'] = 'your-openai-key'

# Option 2: Configuration System
config.set_api_key('gemini', 'your-gemini-key')
config.set_api_key('openai', 'your-openai-key')
```

## Agent Usage

### Creating a Basic Agent

```python
from unisonai import Agent
from unisonai.llms import Gemini

# Initialize LLM
llm = Gemini(model="gemini-2.0-flash", api_key="your-key")

# Create agent
agent = Agent(
    llm=llm,
    identity="Research Assistant",
    description="An AI assistant specialized in web research and analysis",
    verbose=True,
    history_folder="agent_history"
)

# Execute task
result = agent.unleash(task="Research the latest developments in quantum computing")
```

### Agent with Tools

```python
from unisonai.tools.memory import MemoryTool
from unisonai.tools.tool import BaseTool, Field
from unisonai.tools.types import ToolParameterType

class CalculatorTool(BaseTool):
    def __init__(self):
        self.name = "calculator"
        self.description = "Perform mathematical calculations"
        self.params = [
            Field(
                name="expression",
                description="Mathematical expression to evaluate",
                field_type=ToolParameterType.STRING,
                required=True
            )
        ]
        super().__init__()

    def _run(self, expression: str) -> str:
        try:
            result = eval(expression)
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {str(e)}"

# Create agent with tools
agent = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Math Assistant",
    description="Assistant for calculations and memory",
    tools=[MemoryTool, CalculatorTool],
    verbose=True
)

agent.unleash(task="Calculate the square root of 144 and store it in memory")
```

## Multi-Agent Usage

### Creating Specialized Agents

```python
from unisonai import Agent, Clan
from unisonai.tools.rag import RAGTool

# Research Agent
research_agent = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Research Specialist",
    description="Expert in gathering and synthesizing information from knowledge base",
    task="Conduct comprehensive research on assigned topics using stored documents",
    tools=[RAGTool],
    verbose=True
)

# Analysis Agent
analysis_agent = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Data Analyst",
    description="Expert in analyzing data and providing insights",
    task="Analyze research findings and provide detailed insights",
    tools=[CalculatorTool],
    verbose=True
)

# Writing Agent
writer_agent = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Content Writer",
    description="Expert in creating well-structured reports and summaries",
    task="Synthesize information into clear, comprehensive reports",
    verbose=True
)
```

### Creating and Using a Clan

```python
# Create clan with manager and members
clan = Clan(
    clan_name="Research Team",
    manager=research_agent,
    members=[research_agent, analysis_agent, writer_agent],
    shared_instruction="""
    Work together to produce comprehensive research reports.
    Research agent gathers information, analyst provides insights,
    and writer creates the final report.
    """,
    goal="Produce a comprehensive market analysis report on renewable energy trends",
    history_folder="clan_history",
    output_file="market_analysis.txt"
)

# Execute clan task
clan.unleash()
```

## Tool Development

### Creating Custom Tools

#### Basic Tool Structure

```python
from unisonai.tools.tool import BaseTool, Field
from unisonai.tools.types import ToolParameterType

class CustomTool(BaseTool):
    def __init__(self):
        self.name = "custom_tool"
        self.description = "Description of what your tool does"
        self.params = [
            Field(
                name="parameter_name",
                description="Description of the parameter",
                field_type=ToolParameterType.STRING,  # or other types
                default_value="default_value",  # optional
                required=True  # or False
            )
        ]
        super().__init__()

    def _run(self, **kwargs) -> Any:
        # Your tool logic here
        parameter_name = kwargs.get('parameter_name')

        # Perform your tool's function
        result = f"Processed: {parameter_name}"

        return result
```

#### Advanced Tool with Multiple Parameter Types

```python
class DataAnalysisTool(BaseTool):
    def __init__(self):
        self.name = "data_analyzer"
        self.description = "Analyze datasets with statistical operations"
        self.params = [
            Field(
                name="data",
                description="List of numerical data to analyze",
                field_type=ToolParameterType.LIST,
                required=True
            ),
            Field(
                name="operations",
                description="Statistical operations to perform",
                field_type=ToolParameterType.LIST,
                default_value=["mean", "median"],
                required=False
            ),
            Field(
                name="precision",
                description="Decimal places for results",
                field_type=ToolParameterType.INTEGER,
                default_value=2,
                required=False
            )
        ]
        super().__init__()

    def _run(self, data: list, operations: list = None, precision: int = 2) -> dict:
        if operations is None:
            operations = ["mean", "median"]

        import statistics
        results = {}

        for op in operations:
            if op == "mean":
                results["mean"] = round(statistics.mean(data), precision)
            elif op == "median":
                results["median"] = round(statistics.median(data), precision)
            elif op == "std":
                results["std_dev"] = round(statistics.stdev(data), precision)

        return results
```

### Tool Best Practices

1. **Clear Parameter Names**: Use descriptive, concise parameter names
2. **Type Safety**: Always specify appropriate `ToolParameterType` values
3. **Error Handling**: Implement proper error handling in `_run` methods
4. **Documentation**: Provide clear descriptions for tools and parameters
5. **Validation**: Use field validation for input sanitization

## LLM Provider Configuration

### Available Providers

#### Gemini (Google)
```python
from unisonai.llms import Gemini

llm = Gemini(
    model="gemini-2.0-flash",  # or gemini-pro, gemini-pro-vision
    api_key="your-gemini-key",
    temperature=0.7,
    max_tokens=2048
)
```

#### OpenAI
```python
from unisonai.llms import OpenAI

llm = OpenAI(
    model="gpt-4",  # or gpt-3.5-turbo, gpt-4-turbo
    api_key="your-openai-key",
    temperature=0.7,
    max_tokens=2048
)
```

#### Anthropic (Claude)
```python
from unisonai.llms import Anthropic

llm = Anthropic(
    model="claude-3-opus-20240229",  # or claude-3-sonnet-20240229
    api_key="your-anthropic-key",
    temperature=0.7,
    max_tokens=2048
)
```

### Custom LLM Provider

```python
from unisonai.llms.base import BaseLLM

class CustomLLM(BaseLLM):
    def __init__(self, model, api_key, **kwargs):
        super().__init__(model, **kwargs)
        self.api_key = api_key
        # Initialize your custom provider

    def run(self, messages, **kwargs):
        # Implement your LLM inference logic
        # Return response in expected format
        pass
```

## Configuration Management

### API Key Persistence

```python
from unisonai import config

# Set API keys (stored in ~/.unisonai/config.json)
config.set_api_key('gemini', 'your-gemini-key')
config.set_api_key('openai', 'your-openai-key')

# Keys persist across sessions
# Can also be set via environment variables
```

### Environment Variables

```bash
export GEMINI_API_KEY="your-gemini-key"
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
```

## Error Handling

### Tool Error Handling

```python
try:
    result = tool.run(param1="value1", param2="value2")
    if result.success:
        print(f"Success: {result.result}")
    else:
        print(f"Error: {result.error_message}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Agent Error Handling

```python
try:
    agent.unleash(task="your task here")
except Exception as e:
    print(f"Agent execution failed: {e}")
    # Check agent history for detailed error information
```

## Best Practices

### 1. Task Design
- **Clear Instructions**: Provide specific, well-defined tasks
- **Context Provision**: Include relevant context and constraints
- **Output Format**: Specify desired output format when possible

### 2. Agent Configuration
- **Descriptive Identities**: Use clear, descriptive agent identities
- **Appropriate Tools**: Only provide tools relevant to the agent's purpose
- **Reasonable History**: Configure appropriate history folder locations

### 3. Clan Management
- **Clear Roles**: Define distinct roles for each agent
- **Effective Manager**: Choose capable agents as clan managers
- **Shared Context**: Provide clear shared instructions for coordination

### 4. Tool Development
- **Single Responsibility**: Each tool should have one clear purpose
- **Robust Validation**: Implement thorough parameter validation
- **Error Recovery**: Handle edge cases and provide meaningful errors
- **Performance**: Consider tool execution time and resource usage

### 5. Production Deployment
- **API Key Security**: Use secure API key management practices
- **Logging**: Implement appropriate logging for monitoring
- **Monitoring**: Track agent performance and errors
- **Scaling**: Design for horizontal scaling when needed

## Troubleshooting

### Common Issues

#### 1. API Key Errors
- Verify API keys are correctly configured
- Check key permissions and quotas
- Ensure keys are valid and not expired

#### 2. Tool Execution Failures
- Check tool parameter types match field definitions
- Verify tool dependencies are installed
- Review tool error messages for specific issues

#### 3. History Management Issues
- Ensure history folder permissions are correct
- Check available disk space for history files
- Verify JSON format in history files

#### 4. Memory Issues
- Monitor memory usage for long-running agents
- Implement history cleanup for persistent agents
- Consider memory limits for tool operations

### Debug Mode

Enable verbose logging for detailed execution information:

```python
agent = Agent(
    llm=your_llm,
    identity="Debug Agent",
    description="Agent with detailed logging",
    verbose=True  # Enable debug mode
)
```

## Examples Directory

See the `examples/` folder for comprehensive usage examples:

- **[basic_agent.py](./examples/basic_agent.py)**: Simple single agent example
- **[tool_development.py](./examples/tool_development.py)**: Custom tool creation
- **[clan_coordination.py](./examples/clan_coordination.py)**: Multi-agent coordination

## Support

For additional help:

1. Check the [API Reference](./api-reference.md) for detailed parameter information
2. Review the [Architecture Guide](./architecture.md) for system understanding
3. Examine example files for practical implementations
4. Check the [Troubleshooting](#troubleshooting) section for common solutions

## Next Steps

After mastering these basics:

1. Explore [Tool Development](./tools-guide.md) for custom tool creation
2. Study advanced patterns for complex use cases
3. Contribute to the framework by creating custom tools and integrations

