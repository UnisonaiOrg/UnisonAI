# Quick Start Guide

Get up and running with UnisonAI in minutes!

## Installation

```bash
pip install unisonai
```

## 1. Single Agent Setup (2 minutes)

### Basic Agent

```python
from unisonai import Single_Agent
from unisonai.llms import Gemini
from unisonai import config

# Set your API key
config.set_api_key("gemini", "your-gemini-api-key")

# Create and use an agent
agent = Single_Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Assistant",
    description="A helpful AI assistant",
    verbose=True
)

result = agent.unleash(task="Explain quantum computing in simple terms")
print(result)
```

### Agent with Web Search

```python
from unisonai.tools.websearch import WebSearchTool

# Create agent with web search capability
agent = Single_Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Research Assistant",
    description="AI assistant with web search capabilities",
    tools=[WebSearchTool],
    verbose=True
)

# Ask it to research something
agent.unleash(task="What are the latest developments in AI safety research?")
```

## 2. Multi-Agent Setup (5 minutes)

### Clan with Specialized Agents

```python
from unisonai import Agent, Clan

# Create specialized agents
researcher = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Researcher",
    description="Web research expert",
    task="Gather information from reliable sources",
    tools=[WebSearchTool]
)

analyst = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Analyst",
    description="Data analysis and insights expert",
    task="Analyze data and provide insights"
)

# Create a clan (team) of agents
team = Clan(
    clan_name="Research Team",
    manager=researcher,
    members=[researcher, analyst],
    shared_instruction="Work together to provide comprehensive answers",
    goal="Research and analyze topics thoroughly"
)

# Execute team task
team.unleash()
```

## 3. Custom Tools (10 minutes)

### Create Your First Tool

```python
from unisonai.tools.tool import BaseTool, Field
from unisonai.tools.types import ToolParameterType

class CalculatorTool(BaseTool):
    def __init__(self):
        self.name = "calculator"
        self.description = "Perform basic math operations"
        self.params = [
            Field(
                name="operation",
                description="Math operation (+, -, *, /)",
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

    def _run(self, operation: str, x: float, y: float) -> float:
        if operation == "+":
            return x + y
        elif operation == "-":
            return x - y
        elif operation == "*":
            return x * y
        elif operation == "/":
            return x / y if y != 0 else 0
        else:
            raise ValueError(f"Unknown operation: {operation}")

# Use the tool
calc = CalculatorTool()
result = calc.run(operation="+", x=10, y=5)
print(f"10 + 5 = {result.result}")
```

### Use Custom Tool with Agent

```python
# Create agent with your custom tool
agent = Single_Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Math Assistant",
    description="Assistant for math problems and calculations",
    tools=[CalculatorTool],
    verbose=True
)

# The agent can now use your calculator tool
agent.unleash(task="Calculate 15 * 7 + 3 - 12 / 4")
```

## 4. MCP Integration (15 minutes)

### Connect to External Services

```python
from unisonai.tools import MCPManager

# Configure MCP servers
mcp_config = {
    "mcpServers": {
        "time": {
            "command": "uvx",
            "args": ["mcp-server-time"]
        }
    }
}

# Initialize MCP tools
mcp_manager = MCPManager()
mcp_tools = mcp_manager.init_config(mcp_config)

# Create agent with MCP tools
agent = Single_Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Connected Assistant",
    description="AI assistant with external service connections",
    tools=mcp_tools,
    verbose=True
)

# Use external services through natural language
agent.unleash(task="What time is it right now?")
```

## 5. Configuration Options

### API Keys (Multiple Options)

```python
# Option 1: Environment Variables (Recommended for production)
import os
os.environ['GEMINI_API_KEY'] = 'your-key'
os.environ['OPENAI_API_KEY'] = 'your-key'

# Option 2: Configuration System
from unisonai import config
config.set_api_key('gemini', 'your-gemini-key')
config.set_api_key('openai', 'your-openai-key')

# Option 3: Direct LLM initialization
llm = Gemini(model="gemini-2.0-flash", api_key="your-key")
```

### Agent Configuration

```python
# Verbose logging for debugging
agent = Single_Agent(
    llm=your_llm,
    identity="Debug Assistant",
    verbose=True,  # See detailed execution logs
    history_folder="my_agent_history"  # Custom history location
)

# Production-ready agent
agent = Single_Agent(
    llm=your_llm,
    identity="Production Assistant",
    verbose=False,  # Minimal logging
    output_file="results.txt"  # Save results to file
)
```

## Common Patterns

### Research Assistant

```python
# Complete research assistant setup
research_agent = Single_Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Research Expert",
    description="Comprehensive research and analysis assistant",
    tools=[WebSearchTool, CalculatorTool],
    verbose=True
)

# Ask complex research questions
research_agent.unleash(task="""
    Research renewable energy trends in 2024.
    Include market size, key players, and growth projections.
    Calculate the percentage growth from 2023 data.
""")
```

### Task Automation

```python
# Automated task processor
automation_agent = Single_Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Task Automator",
    description="Automated task processing and execution",
    tools=[WebSearchTool, CalculatorTool],
    verbose=False
)

# Process multiple tasks
tasks = [
    "Find current weather in Tokyo",
    "Calculate 25% of 1000",
    "Search for Python best practices"
]

for task in tasks:
    result = automation_agent.unleash(task=task)
    print(f"Task: {task}")
    print(f"Result: {result}")
    print("---")
```

### Multi-Step Analysis

```python
# Create agents for different analysis phases
data_collector = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Data Collector",
    description="Collects and organizes data",
    task="Gather relevant data from multiple sources"
)

data_analyzer = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Data Analyst",
    description="Analyzes and interprets data",
    task="Perform statistical analysis and identify trends"
)

report_writer = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Report Writer",
    description="Creates comprehensive reports",
    task="Synthesize findings into clear reports"
)

# Create analysis team
analysis_team = Clan(
    clan_name="Analysis Team",
    manager=data_collector,
    members=[data_collector, data_analyzer, report_writer],
    shared_instruction="Work systematically through collection, analysis, and reporting phases",
    goal="Produce comprehensive market analysis report"
)

# Execute complex analysis
analysis_team.unleash()
```

## Troubleshooting

### Quick Fixes

1. **API Key Issues**
   ```python
   # Check if key is set
   from unisonai import config
   print(config.get_api_key('gemini'))  # Should show your key

   # Set key if missing
   config.set_api_key('gemini', 'your-actual-key')
   ```

2. **Tool Not Working**
   ```python
   # Test tool directly
   tool = WebSearchTool()
   result = tool.run(query="test query")
   print(result.result if result.success else result.error_message)
   ```

3. **Agent Not Responding**
   ```python
   # Enable verbose mode to see what's happening
   agent = Single_Agent(
       llm=your_llm,
       identity="Debug Assistant",
       verbose=True  # This will show detailed logs
   )
   ```

## What's Next?

Now that you're up and running:

1. **Explore Examples**: Check out `main.py`, `main2.py`, and `tool_example.py` in the project root
2. **Build Custom Tools**: See [Tool System Guide](./tools-guide.md)
3. **Connect External Services**: Learn about [MCP Integration](./mcp-integration.md)
4. **Advanced Patterns**: Study [Architecture Guide](./architecture.md)

## Need Help?

- **Documentation**: Full guides in the `docs/` folder
- **Examples**: Practical examples in the project root
- **API Reference**: Complete API documentation in [API Reference](./api-reference.md)

**Happy building with UnisonAI!** 🎉
