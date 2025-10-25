
<div align="center">
  <img src="https://github.com/UnisonaiOrg/UnisonAI/blob/main/assets/UnisonAI.jpg" alt="UnisonAI Banner" width="90%"/>
</div>

# Table of Contents

- [Overview](#overview)
- [Why UnisonAI?](#what-makes-unisonai-special)
- [Installation](#quick-start)
- [Core Components](#core-components)
- [Configuration](#configuration)
- [Parameter Reference Tables](#documentation-hub)
- [Usage Examples](#usage-examples)
- [FAQ](#faq)
- [Contributing And License](#contributing)


<div align="center">
  <h1>UnisonAI</h1>
  <p><em>Orchestrate the Future of Multi-Agent AI</em></p>
</div>

<p align="center">
  <a href="https://github.com/UnisonaiOrg/UnisonAI/stargazers"><img src="https://img.shields.io/github/stars/UnisonaiOrg/UnisonAI" alt="Stars"/></a>
  <a href="https://github.com/UnisonaiOrg/UnisonAI/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-green.svg" alt="License"/></a>
  <img src="https://img.shields.io/badge/Python-%3E=3.10,%3C3.13-blue?style=flat-square" alt="Python Version"/>
</p>

---

## Overview

UnisonAI is a flexible and extensible Python framework for building, coordinating, and scaling multiple AI agents—each powered by the LLM of your choice.

- **Agent:** For solo, focused tasks or as part of a clan for teamwork.
- **Clan:** For coordination and distributed problem-solving with multiple agents.
- **Tool System:** Easily augment agents with custom, pluggable tools (web search, time, APIs, your own logic).

Supports Cohere, Mixtral, Groq, Gemini, Grok, OpenAI, Anthropic, HelpingAI, and any custom model (just extend `BaseLLM`). UnisonAI is designed for real-world, production-grade multi-agent AI applications.

---

## Quick Start

```bash
pip install unisonai
```

```python
from unisonai import Agent
from unisonai.llms import Gemini
from unisonai import config

config.set_api_key("gemini", "your-api-key")
agent = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Assistant",
    description="A helpful AI assistant"
)
print(agent.unleash(task="Explain quantum computing"))
```

---

## What Makes UnisonAI Special

UnisonAI stands out with its unique **Agent-to-Agent (A2A) communication** architecture, enabling seamless coordination between AI agents as if they were human team members collaborating on complex tasks.

### A2A Communication Architecture

<div>
  <img src="https://github.com/UnisonaiOrg/UnisonAI/blob/main/assets/Example.jpg" alt="Example" width="60%"/>
</div>


### Latest Enhancements

- **🔒 Strong Type Validation**: All tool parameters validated against `ToolParameterType` enum before execution
- **🛡️ Enhanced Error Handling**: Comprehensive error catching with detailed metadata for debugging
- **📊 Standardized Results**: All tools return `ToolResult` objects with success status and metadata

---

### Perfect For:

- **Complex Research Tasks**: Multiple agents gathering, analyzing, and synthesizing information
- **Workflow Automation**: Coordinated agents handling multi-step business processes
- **Content Creation**: Specialized agents for research, writing, editing, and publishing
- **Data Analysis**: Distributed agents processing large datasets with different expertise

---

## Core Components

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| **Agent** | Standalone or clan member agent | Own history, tool integration, configurable LLMs, inter-agent messaging |
| **Clan** | Multi-agent orchestration | Team management, shared goals, coordinated execution |
| **Tool System** | Extensible capability framework | Type validation, error handling, standardized results |

---

## Usage Examples

### Individual Agent

```python
from unisonai import Agent
from unisonai.llms import Gemini
from unisonai.tools.memory import MemoryTool

agent = Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Research Assistant",
    description="An AI assistant with memory capabilities",
    tools=[MemoryTool]
)
agent.unleash(task="Store important project details")
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

## Configuration

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

---

## Documentation Hub

### 🚀 **Getting Started**
- **[Quick Start Guide](https://github.com/UnisonaiOrg/UnisonAI/blob/main/docs/quick-start.md)** - 5-minute setup guide
- **[Installation](https://github.com/UnisonaiOrg/UnisonAI/blob/main/docs/README.md#installation)** - Detailed installation options

### 📖 **Core Documentation**
- **[API Reference](https://github.com/UnisonaiOrg/UnisonAI/blob/main/docs/api-reference.md)** - Complete API documentation
- **[Architecture Guide](https://github.com/UnisonaiOrg/UnisonAI/blob/main/docs/architecture.md)** - System design and patterns
- **[Usage Guidelines](https://github.com/UnisonaiOrg/UnisonAI/blob/main/docs/usage-guide.md)** - Best practices and patterns

### 🛠️ **Advanced Features**
- **[Tool System Guide](https://github.com/UnisonaiOrg/UnisonAI/blob/main/docs/tools-guide.md)** - Custom tool creation and validation
- **[Parameter Reference](https://github.com/UnisonaiOrg/UnisonAI/blob/main/docs/README.md#parameter-reference-tables)** - Complete parameter documentation

### 💡 **Examples & Tutorials**
- **[Basic Examples](https://github.com/UnisonaiOrg/UnisonAI/blob/main/examples/basic_agent.py)** - Simple agent patterns
- **[Advanced Examples](https://github.com/UnisonaiOrg/UnisonAI/blob/main/examples/clan-agent_example.py)** - Multi-agent coordination
- **[Tool Examples](https://github.com/UnisonaiOrg/UnisonAI/blob/main/examples/tool_example.py)** - Custom tool implementations

---

## FAQ

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

## Contributing

Founder: Anant Sharma (E5Anant)[https://github.com/E5Anant]

PRs and issues welcome! See our [Contributing Guide](https://github.com/UnisonaiOrg/UnisonAI/issues).

<a href="https://github.com/UnisonaiOrg/UnisonAI/issues">Open Issues</a> •
<a href="https://github.com/UnisonaiOrg/UnisonAI/pulls">Submit PRs</a> •
<a href="https://github.com/UnisonaiOrg/UnisonAI">Suggest Features</a>

---



