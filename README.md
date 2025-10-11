# Table of Contents

- [Overview](#overview)
- [Why UnisonAI?](#why-unisonai)
- [Installation](#installation)
- [Core Components](#core-components)
- [Parameter Reference Tables](#parameter-reference-tables)
- [Usage Examples](#usage-examples)
- [FAQ](#faq)
- [Contributing And License](#contributing-and-license)

<div align="center">
  <img src="https://github.com/UnisonAIInc/UnisonAI/blob/main/assets/UnisonaiOrg.jpg" alt="UnisonAI Banner" width="100%"/>
</div>

<div align="center">
  <h1>UnisonAI</h1>
  <p><em>Orchestrate the Future of Multi-Agent AI</em></p>
</div>

<p align="center">
  <a href="https://github.com/UnisonAIInc/UnisonAI/stargazers"><img src="https://img.shields.io/github/stars/UnisonAIInc/UnisonAI" alt="Stars"/></a>
  <a href="https://github.com/UnisonAIInc/UnisonAI/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-green.svg" alt="License"/></a>
  <img src="https://img.shields.io/badge/Python-%3E=3.10,%3C3.13-blue?style=flat-square" alt="Python Version"/>
</p>

---

## 🚀 Quick Start

```bash
pip install unisonai
```

```python
from unisonai import Single_Agent
from unisonai.llms import Gemini
from unisonai import config

config.set_api_key("gemini", "your-api-key")
agent = Single_Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Assistant",
    description="A helpful AI assistant"
)
print(agent.unleash(task="Explain quantum computing"))
```

---

## 🌟 What Makes UnisonAI Special

UnisonAI stands out with its unique **Agent-to-Agent (A2A) communication** architecture, enabling seamless coordination between AI agents as if they were human team members collaborating on complex tasks.

### 🤝 A2A Communication Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Agent-to-Agent (A2A) Communication           │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  Message  ┌─────────────┐  Message  ┌─────────────┐  │
│  │   Agent 1   │◄─────────┤   Agent 2   │◄─────────┤   Agent 3   │  │
│  │             │ Channel  │             │ Channel  │             │  │
│  │ • Research  │─────────►│ • Analysis  │─────────►│ • Reporting │  │
│  │ • Planning  │          │ • Synthesis │          │ • Delivery  │  │
│  └─────────────┘           └─────────────┘           └─────────────┘  │
│         │                        │                        │         │
│         ▼                        ▼                        ▼         │
│  ┌─────────────┐           ┌─────────────┐           ┌─────────────┐  │
│  │   Single    │           │    Clan     │           │   Tool      │  │
│  │   Agent     │           │ Management  │           │  System     │  │
│  └─────────────┘           └─────────────┘           └─────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 🔥 Latest Enhancements

- **🔒 Strong Type Validation**: All tool parameters validated against `ToolParameterType` enum before execution
- **🛡️ Enhanced Error Handling**: Comprehensive error catching with detailed metadata for debugging
- **📊 Standardized Results**: All tools return `ToolResult` objects with success status and metadata
- **🔌 MCP Integration**: Connect to external tools via Model Context Protocol servers

---

## 💡 Why Choose UnisonAI?

<div align="center">

| Framework | Single Agent | Multi-Agent | A2A Communication | Type Safety | MCP Support |
|-----------|--------------|-------------|-------------------|-------------|-------------|
| **UnisonAI** | ✅ | ✅ | ✅ **Native** | ✅ | ✅ |
| AutoGen | ✅ | ✅ | ❌ | ⚠️ Limited | ❌ |
| LangChain | ✅ | ⚠️ Basic | ❌ | ⚠️ Limited | ❌ |
| CrewAI | ❌ | ✅ | ❌ | ⚠️ Limited | ❌ |

*Comparison with popular agent frameworks - UnisonAI leads in A2A communication and type safety*

</div>

### 🎯 Perfect For:

- **Complex Research Tasks**: Multiple agents gathering, analyzing, and synthesizing information
- **Workflow Automation**: Coordinated agents handling multi-step business processes
- **Content Creation**: Specialized agents for research, writing, editing, and publishing
- **Data Analysis**: Distributed agents processing large datasets with different expertise

---

## 🏗️ Core Components

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| **Single_Agent** | Standalone agent for focused tasks | Own history, tool integration, configurable LLMs |
| **Agent** | Clan member for team coordination | Inter-agent messaging, role-based tasks, specialized tools |
| **Clan** | Multi-agent orchestration | Team management, shared goals, coordinated execution |
| **Tool System** | Extensible capability framework | Type validation, error handling, standardized results |
| **MCP Integration** | External tool connectivity | MCP server support, protocol translation, service integration |

---

## 📋 Usage Examples

### Single Agent

```python
from unisonai.tools.websearch import WebSearchTool

agent = Single_Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Research Assistant",
    tools=[WebSearchTool]
)
agent.unleash(task="Latest AI trends")
```

### Multi-Agent Clan

```python
from unisonai import Agent, Clan

research_agent = Agent(llm=Gemini(), identity="Researcher", task="Gather information")
analysis_agent = Agent(llm=Gemini(), identity="Analyst", task="Analyze findings")

clan = Clan(
    clan_name="Research Team",
    manager=research_agent,
    members=[research_agent, analysis_agent],
    goal="Comprehensive market analysis"
)
clan.unleash()
```

### Custom Tools

```python
from unisonai.tools.tool import BaseTool, Field
from unisonai.tools.types import ToolParameterType

class CalculatorTool(BaseTool):
    def __init__(self):
        self.name = "calculator"
        self.description = "Mathematical operations"
        self.params = [
            Field(name="operation", field_type=ToolParameterType.STRING, required=True),
            Field(name="a", field_type=ToolParameterType.FLOAT, required=True),
            Field(name="b", field_type=ToolParameterType.FLOAT, required=True)
        ]
        super().__init__()

    def _run(self, operation: str, a: float, b: float) -> float:
        return a + b if operation == "add" else a * b
```

---

## 🔧 Configuration

### API Keys

```python
from unisonai import config

# Method 1: Configuration system
config.set_api_key("gemini", "your-key")
config.set_api_key("openai", "your-key")

# Method 2: Environment variables
export GEMINI_API_KEY="your-key"
export OPENAI_API_KEY="your-key"

# Method 3: Direct LLM initialization
llm = Gemini(api_key="your-key")
```

### MCP Servers

```python
MCP_CONFIG = {
    "mcpServers": {
        "time": {"command": "uvx", "args": ["mcp-server-time"]},
        "fetch": {"command": "uvx", "args": ["mcp-server-fetch"]}
    }
}
```

---

## 📚 Documentation Hub

### 🚀 **Getting Started**
- **[Quick Start Guide](https://github.com/UnisonAIInc/UnisonAI/blob/main/docs/quick-start.md)** - 5-minute setup guide
- **[Installation](https://github.com/UnisonAIInc/UnisonAI/blob/main/docs/README.md#installation)** - Detailed installation options

### 📖 **Core Documentation**
- **[API Reference](https://github.com/UnisonAIInc/UnisonAI/blob/main/docs/api-reference.md)** - Complete API documentation
- **[Architecture Guide](https://github.com/UnisonAIInc/UnisonAI/blob/main/docs/architecture.md)** - System design and patterns
- **[Usage Guidelines](https://github.com/UnisonAIInc/UnisonAI/blob/main/docs/usage-guide.md)** - Best practices and patterns

### 🛠️ **Advanced Features**
- **[Tool System Guide](https://github.com/UnisonAIInc/UnisonAI/blob/main/docs/tools-guide.md)** - Custom tool creation and validation
- **[MCP Integration](https://github.com/UnisonAIInc/UnisonAI/blob/main/docs/mcp-integration.md)** - External tool integration
- **[Parameter Reference](https://github.com/UnisonAIInc/UnisonAI/blob/main/docs/README.md#parameter-reference-tables)** - Complete parameter documentation

### 💡 **Examples & Tutorials**
- **[Basic Examples](https://github.com/UnisonAIInc/UnisonAI/blob/main/examples/basic_agent.py)** - Simple agent patterns
- **[Advanced Examples](https://github.com/UnisonAIInc/UnisonAI/blob/main/examples/clan-agent_example.py)** - Multi-agent coordination
- **[Tool Examples](https://github.com/UnisonAIInc/UnisonAI/blob/main/examples/tool_example.py)** - Custom tool implementations
- **[MCP Examples](https://github.com/UnisonAIInc/UnisonAI/blob/main/examples/mcp_example.py)** - External tool integration

---

## ❓ FAQ

<details>
<summary><b>What is UnisonAI?</b></summary>
Python framework for building and orchestrating AI agents with A2A communication.
</details>

<details>
<summary><b>When should I use a Clan?</b></summary>
For complex, multi-step tasks requiring specialized agents working together.
</details>

<details>
<summary><b>Can I add custom LLMs?</b></summary>
Yes! Extend <code>BaseLLM</code> class to integrate any model provider.
</details>

<details>
<summary><b>What are tools?</b></summary>
Reusable components that extend agent capabilities (web search, APIs, custom logic).
</details>

<details>
<summary><b>How do I manage API keys?</b></summary>
Use config system, environment variables, or pass directly to LLMs.
</details>

---

## 🤝 Contributing

PRs and issues welcome! See our [Contributing Guide](https://github.com/UnisonAIInc/UnisonAI/issues).

<a href="https://github.com/UnisonAIInc/UnisonAI/issues">Open Issues</a> •
<a href="https://github.com/UnisonAIInc/UnisonAI/pulls">Submit PRs</a> •
<a href="https://github.com/UnisonAIInc/UnisonAI">Suggest Features</a>

---
