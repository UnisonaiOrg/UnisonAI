# UnisonAI Documentation

## Overview

UnisonAI is a flexible and extensible Python framework for building, coordinating, and scaling multiple AI agents—each powered by the LLM of your choice. It supports both single agents for focused tasks and multi-agent clans for complex, coordinated problem-solving using Agent-to-Agent (A2A) communication.

### Key Features

- **🔗 Multi-LLM Support**: Compatible with Cohere, Mixtral, Groq, Gemini, Grok, OpenAI, Anthropic, HelpingAI, and custom models
- **🛠️ Enhanced Tool System**: Strong type validation, automatic parameter validation, standardized responses
- **🤖 Agent Types**: Agent for both solo and team-based tasks, Clan for multi-agent orchestration
- **📚 Production-Ready**: Robust error handling, logging, and comprehensive documentation

## Architecture

### Core Components

#### 1. Agent Class
Flexible agent for standalone or clan-based tasks with:
- Conversation history management
- Tool integration capabilities
- Configurable LLM providers
- Inter-agent messaging (in clan mode)
- Role-based task execution
- Customizable prompts and behavior

#### 2. Clan Class
Multi-agent orchestration with:
- Team management and leadership
- Shared instructions and goals
- Coordinated task distribution
- Unified objective achievement

#### 3. Enhanced Tool System
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
│  ┌─────────────┐  ┌─────────────┐                               │
│  │    Agent    │  │    Clan     │                               │
│  │             │  │             │                               │
│  │ • Solo mode │  │ • Multi-    │                               │
│  │ • Clan mode │  │   agent     │                               │
│  │ • History   │  │   coord.    │                               │
│  │ • Tools     │  │ • Messaging │                               │
│  │ • Messaging │  │             │                               │
│  └─────────────┘  └─────────────┘                               │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐                               │
│  │   LLM       │  │    Tool     │                               │
│  │  Providers  │  │   System    │                               │
│  │             │  │             │                               │
│  │ • OpenAI    │  │ • Type      │                               │
│  │ • Gemini    │  │   validation│                               │
│  │ • Anthropic │  │ • Error     │                               │
│  │ • Cohere    │  │   handling  │                               │
│  │ • Groq      │  │ • Memory    │                               │
│  │ • Mixtral   │  │ • RAG       │                               │
│  └─────────────┘  └─────────────┘                               │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start Guide

### Installation

```bash
pip install unisonai
```

### Basic Agent Usage

```python
from unisonai import Agent
from unisonai.llms import Gemini
from unisonai.tools.memory import MemoryTool
from unisonai import config

# Configure API key
config.set_api_key("gemini", "your-api-key")

# Create agent
agent = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Research Assistant",
    description="Research and analysis expert with memory",
    tools=[MemoryTool],
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
