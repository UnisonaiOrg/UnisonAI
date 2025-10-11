# UnisonAI Documentation

## Overview

UnisonAI is a flexible and extensible Python framework for building, coordinating, and scaling multiple AI agents—each powered by the LLM of your choice. It supports both single agents for focused tasks and multi-agent clans for complex, coordinated problem-solving using Agent-to-Agent (A2A) communication.

### Key Features

- **🔗 Multi-LLM Support**: Compatible with Cohere, Mixtral, Groq, Gemini, Grok, OpenAI, Anthropic, HelpingAI, and custom models
- **🛠️ Enhanced Tool System**: Strong type validation, automatic parameter validation, standardized responses
- **🤖 Agent Types**: Single_Agent for solo tasks, Agent for team-based coordination, Clan for multi-agent orchestration
- **📚 Production-Ready**: Robust error handling, logging, and comprehensive documentation
- **🔒 Model Context Protocol (MCP) Integration**: Connect to external tools and services via MCP servers

## Architecture

### Core Components

#### 1. Single_Agent Class
Standalone agent for independent tasks with:
- Conversation history management
- Tool integration capabilities
- Configurable LLM providers
- Customizable prompts and behavior

#### 2. Agent Class
Multi-agent clan member with:
- Inter-agent messaging capabilities
- Role-based task execution
- Specialized tool usage
- Coordinated problem-solving

#### 3. Clan Class
Multi-agent orchestration with:
- Team management and leadership
- Shared instructions and goals
- Coordinated task distribution
- Unified objective achievement

#### 4. Enhanced Tool System
Robust tool framework featuring:
- **BaseTool**: Abstract base class for custom tools
- **Field**: Parameter definitions with type validation
- **ToolParameterType**: Enum for type safety
- **ToolResult**: Standardized response objects

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          UnisonAI Framework                     │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ Single_Agent│  │    Agent    │  │    Clan     │              │
│  │             │  │             │  │             │              │
│  │ • Solo tasks│  │ • Team work │  │ • Multi-    │              │
│  │ • History   │  │ • Messaging │  │   agent     │              │
│  │ • Tools     │  │ • Roles     │  │   coord.    │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   LLM       │  │    Tool     │  │     MCP     │              │
│  │  Providers  │  │   System    │  │ Integration │              │
│  │             │  │             │  │             │              │
│  │ • OpenAI    │  │ • Type      │  │ • External  │              │
│  │ • Gemini    │  │   validation│  │   tools     │              │
│  │ • Anthropic │  │ • Error     │  │ • Services  │              │
│  │ • Cohere    │  │   handling  │  │ • Protocols │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start Guide

### Installation

```bash
pip install unisonai
```

### Basic Single Agent Usage

```python
from unisonai import Single_Agent
from unisonai.llms import Gemini
from unisonai.tools.websearch import WebSearchTool
from unisonai import config

# Configure API key
config.set_api_key("gemini", "your-api-key")

# Create agent
agent = Single_Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Research Assistant",
    description="Web research and analysis expert",
    tools=[WebSearchTool],
    verbose=True
)

# Execute task
agent.unleash(task="Research latest AI trends and summarize findings")
```

### Multi-Agent Clan Usage

```python
from unisonai import Agent, Clan
from unisonai.llms import Gemini

# Create specialized agents
research_agent = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Research Specialist",
    description="Web research expert",
    task="Gather comprehensive information",
    tools=[WebSearchTool]
)

analysis_agent = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Data Analyst",
    description="Data analysis and insights expert",
    task="Analyze and interpret research findings"
)

# Create clan
clan = Clan(
    clan_name="Research Team",
    manager=research_agent,
    members=[research_agent, analysis_agent],
    shared_instruction="Collaborate on research tasks",
    goal="Produce comprehensive market analysis"
)

clan.unleash()
```

## Documentation Structure

- **[API Reference](./api-reference.md)**: Complete API documentation for all classes and methods
- **[Architecture Guide](./architecture.md)**: Detailed architecture and system design
- **[Usage Guidelines](./usage-guide.md)**: Comprehensive usage patterns and best practices
- **[Tool System Guide](./tools-guide.md)**: Creating and using custom tools
- **[MCP Integration](./mcp-integration.md)**: Model Context Protocol setup and usage
- **[Examples](./examples/)**: Practical examples and use cases

## Requirements

- **Python**: 3.10-3.12
- **Dependencies**: See [requirements.txt](../requirements.txt)

## Contributing

We welcome contributions! Please see our [Contributing Guide](./contributing.md) for details.

## License

Apache 2.0 License - see [LICENSE](../LICENSE) for details.

---

**UnisonAI**: Orchestrate the Future of Multi-Agent AI.
