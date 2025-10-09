# MCP Integration Guide

## Overview

The Model Context Protocol (MCP) integration allows UnisonAI agents to connect to external tools and services through standardized MCP servers. This enables agents to leverage capabilities from external systems while maintaining the framework's type safety and validation features.

## What is MCP?

The Model Context Protocol (MCP) is an open standard that enables AI models to securely interact with external tools, data sources, and services. MCP servers expose capabilities through a standardized interface that UnisonAI can consume and convert into native tools.

## Architecture

### MCP Integration Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    MCP Integration Flow                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐       ┌─────────────┐       ┌─────────────┐    │
│  │  UnisonAI   │       │   MCP       │       │   MCP       │    │
│  │  Framework  │◀─────▶│  Manager    │◀─────▶│  Servers    │    │
│  └─────────────┘       └─────────────┘       └─────────────┘    │
│         │                     │                     │            │
│         ▼                     ▼                     ▼            │
│  ┌─────────────┐       ┌─────────────┐       ┌─────────────┐    │
│  │  Tool       │       │  Protocol   │       │  External   │    │
│  │ Conversion  │       │ Translation │       │  Services   │    │
│  └─────────────┘       └─────────────┘       └─────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## Setup and Configuration

### 1. Install MCP Support

Ensure MCP is installed:

```bash
pip install mcp>=1.0.0
```

### 2. Configure MCP Servers

Create an MCP configuration file or define it programmatically:

```python
MCP_CONFIG = {
    "mcpServers": {
        "time": {
            "command": "uvx",
            "args": ["mcp-server-time"]
        },
        "fetch": {
            "command": "uvx",
            "args": ["mcp-server-fetch"]
        },
        "filesystem": {
            "command": "node",
            "args": ["/path/to/mcp-server-filesystem", "/allowed/path"]
        }
    }
}
```

### 3. Initialize MCP Manager

```python
from unisonai.tools import MCPManager

# Create MCP manager
mcp_manager = MCPManager()

# Initialize with configuration
try:
    mcp_tools = mcp_manager.init_config(MCP_CONFIG)
    print(f"Loaded {len(mcp_tools)} MCP tools")
except Exception as e:
    print(f"MCP initialization failed: {e}")
```

### 4. Use with Agents

```python
from unisonai import Single_Agent

# Create agent with MCP tools
agent = Single_Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="MCP-Enabled Assistant",
    description="AI assistant with external tool capabilities",
    tools=mcp_tools,  # Include MCP tools
    verbose=True
)

# Use MCP tools through natural language
agent.unleash(task="What time is it right now?")
agent.unleash(task="Fetch the content from https://example.com")
```

## MCP Server Types

### Stdio-based Servers

Communicate with MCP servers via standard input/output:

```python
{
    "mcpServers": {
        "time_server": {
            "command": "python",
            "args": ["mcp-server-time.py"],
            "env": {
                "API_KEY": "your-api-key"  # Optional environment variables
            }
        }
    }
}
```

### HTTP-based Servers

Connect to MCP servers via HTTP:

```python
{
    "mcpServers": {
        "api_server": {
            "url": "http://localhost:8000/mcp",
            "headers": {
                "Authorization": "Bearer your-token"
            },
            "type": "sse"  # or "streamable-http"
        }
    }
}
```

## Built-in MCP Tools

### Time Tool

Provides current time and date functionality:

```python
# MCP server configuration for time
{
    "mcpServers": {
        "current_time": {
            "command": "uvx",
            "args": ["mcp-server-time"]
        }
    }
}

# Usage with agent
agent.unleash(task="What is the current time in New York?")
```

**Available Operations:**
- Get current time
- Get current date
- Timezone conversions
- Time formatting

### Fetch Tool

Web content fetching capabilities:

```python
# MCP server configuration for web fetch
{
    "mcpServers": {
        "web_fetch": {
            "command": "uvx",
            "args": ["mcp-server-fetch"]
        }
    }
}

# Usage with agent
agent.unleash(task="Fetch the latest news from CNN and summarize it")
```

**Available Operations:**
- HTTP GET requests
- Content extraction
- Link following
- Content summarization

### Filesystem Tool

File system operations:

```python
# MCP server configuration for filesystem
{
    "mcpServers": {
        "filesystem": {
            "command": "node",
            "args": ["/path/to/mcp-server-filesystem", "/allowed/directory"]
        }
    }
}

# Usage with agent
agent.unleash(task="List all files in the documents folder and read the latest one")
```

**Available Operations:**
- File listing
- File reading
- File writing
- Directory operations

## Creating Custom MCP Servers

### Python MCP Server

```python
#!/usr/bin/env python3
"""
Example MCP server for custom functionality
"""

import asyncio
import json
from mcp.server import Server
from mcp.types import TextContent, LoggingLevel
import logging

# Configure logging
logging.basicConfig(level=LoggingLevel.INFO)

# Create server instance
server = Server("custom-server")

@server.tool()
async def custom_calculation(x: float, y: float, operation: str) -> str:
    """Perform custom calculations."""
    if operation == "add":
        result = x + y
    elif operation == "multiply":
        result = x * y
    elif operation == "power":
        result = x ** y
    else:
        raise ValueError(f"Unknown operation: {operation}")

    return TextContent(
        type="text",
        text=f"Result: {result}"
    )

async def main():
    # Run the server
    async with server.run() as (read_stream, write_stream):
        # Server loop
        while True:
            message = await read_stream.read()
            if message is None:
                break

            # Process message and write response
            response = await server.process_message(message)
            await write_stream.write(response)

if __name__ == "__main__":
    asyncio.run(main())
```

### Node.js MCP Server

```javascript
#!/usr/bin/env node
/**
 * Example MCP server in Node.js
 */

const { Server } = require("@modelcontextprotocol/sdk/server/index.js");

const server = new Server(
    {
        name: "custom-js-server",
        version: "0.1.0",
    },
    {
        capabilities: {
            tools: {},
        },
    }
);

server.setRequestHandler("tools/call", async (request) => {
    const { name, arguments: args } = request.params;

    switch (name) {
        case "custom_operation":
            const result = await performCustomOperation(args);
            return {
                content: [{ type: "text", text: `Result: ${result}` }]
            };

        default:
            throw new Error(`Unknown tool: ${name}`);
    }
});

async function performCustomOperation(args) {
    // Custom operation logic
    return `Processed: ${JSON.stringify(args)}`;
}

server.run();
```

## Advanced MCP Integration

### Error Handling

```python
from unisonai.tools import MCPConnectionError, MCPConfigurationError

try:
    mcp_tools = mcp_manager.init_config(MCP_CONFIG)
except MCPConnectionError as e:
    print(f"Failed to connect to MCP server: {e}")
    # Handle connection errors
except MCPConfigurationError as e:
    print(f"Invalid MCP configuration: {e}")
    # Handle configuration errors
except Exception as e:
    print(f"Unexpected MCP error: {e}")
    # Handle other errors
```

### Dynamic Server Management

```python
class MCPServerManager:
    def __init__(self):
        self.mcp_manager = MCPManager()
        self.active_servers = {}

    def add_server(self, name: str, config: dict):
        """Add a new MCP server dynamically."""
        try:
            # Update configuration
            if not hasattr(self, '_config'):
                self._config = {"mcpServers": {}}

            self._config["mcpServers"][name] = config

            # Reinitialize with new configuration
            new_tools = self.mcp_manager.init_config(self._config)

            # Update active servers
            self.active_servers[name] = True

            return new_tools

        except Exception as e:
            print(f"Failed to add server {name}: {e}")
            return []

    def remove_server(self, name: str):
        """Remove an MCP server."""
        if name in self._config.get("mcpServers", {}):
            del self._config["mcpServers"][name]
            self.active_servers.pop(name, None)

            # Reinitialize without removed server
            return self.mcp_manager.init_config(self._config)

        return []
```

### Tool Discovery and Inspection

```python
def inspect_mcp_tools(mcp_manager: MCPManager):
    """Inspect available MCP tools and their schemas."""

    tools = mcp_manager.get_available_tools()

    for tool in tools:
        print(f"Tool: {tool.name}")
        print(f"Description: {tool.description}")

        # Get tool schema
        schema = tool.get_schema()
        print(f"Parameters: {schema.get('parameters', {})}")
        print("---")

# Usage
inspect_mcp_tools(mcp_manager)
```

## Security Considerations

### Server Authentication

```python
# Secure MCP server configuration
SECURE_MCP_CONFIG = {
    "mcpServers": {
        "secure_api": {
            "url": "https://secure-api.example.com/mcp",
            "headers": {
                "Authorization": "Bearer ${API_TOKEN}",
                "X-API-Key": "${API_KEY}"
            },
            "type": "sse"
        }
    }
}

# Use environment variables for sensitive data
import os
config_with_secrets = {
    "mcpServers": {
        "secure_api": {
            "url": "https://secure-api.example.com/mcp",
            "headers": {
                "Authorization": f"Bearer {os.getenv('MCP_API_TOKEN')}",
                "X-API-Key": f"{os.getenv('MCP_API_KEY')}"
            }
        }
    }
}
```

### Access Control

```python
# Restrict MCP server access to specific directories
RESTRICTED_CONFIG = {
    "mcpServers": {
        "filesystem": {
            "command": "mcp-server-filesystem",
            "args": ["/restricted/path/only"],
            "env": {
                "ALLOWED_PATHS": "/restricted/path/only"
            }
        }
    }
}
```

## Performance Optimization

### Connection Pooling

```python
class MCPConnectionPool:
    def __init__(self, config: dict, pool_size: int = 5):
        self.config = config
        self.pool_size = pool_size
        self.managers = []

        # Initialize connection pool
        for _ in range(pool_size):
            manager = MCPManager()
            manager.init_config(config)
            self.managers.append(manager)

    def get_tool_result(self, tool_name: str, **kwargs):
        """Get tool result using connection pool."""
        # Simple round-robin load balancing
        manager = self.managers[len(self.managers) % self.pool_size]

        # Find and execute tool
        for tool in manager.tools:
            if tool.name == tool_name:
                return tool.run(**kwargs)

        raise ValueError(f"Tool {tool_name} not found")
```

### Caching MCP Results

```python
from functools import lru_cache
import hashlib
import json

class CachedMCPManager:
    def __init__(self, config: dict):
        self.mcp_manager = MCPManager()
        self.mcp_manager.init_config(config)
        self.cache = {}

    def _get_cache_key(self, tool_name: str, **kwargs) -> str:
        """Generate cache key for tool call."""
        key_data = f"{tool_name}:{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def execute_tool(self, tool_name: str, use_cache: bool = True, **kwargs):
        """Execute tool with optional caching."""
        cache_key = self._get_cache_key(tool_name, **kwargs)

        if use_cache and cache_key in self.cache:
            return self.cache[cache_key]

        # Find and execute tool
        for tool in self.mcp_manager.tools:
            if tool.name == tool_name:
                result = tool.run(**kwargs)

                if use_cache:
                    self.cache[cache_key] = result

                return result

        raise ValueError(f"Tool {tool_name} not found")
```

## Troubleshooting

### Common Issues

#### 1. Connection Failures

**Problem:** MCP server connection fails

**Solutions:**
- Verify server is running and accessible
- Check network connectivity and firewall settings
- Validate server configuration and parameters
- Review server logs for error messages

#### 2. Tool Not Found

**Problem:** Agent cannot find MCP tools

**Solutions:**
- Ensure MCP servers are properly initialized
- Check tool naming conventions (may include server prefix)
- Verify tool registration with MCP manager
- Review MCP server capability advertisements

#### 3. Authentication Errors

**Problem:** MCP server authentication fails

**Solutions:**
- Verify API keys and tokens are correct
- Check token expiration and refresh if needed
- Validate authentication headers and format
- Ensure proper environment variable configuration

#### 4. Performance Issues

**Problem:** MCP tool execution is slow

**Solutions:**
- Implement connection pooling for frequent operations
- Add caching for deterministic operations
- Monitor server response times
- Consider async execution for long-running tools

### Debug Mode

Enable detailed MCP logging:

```python
import logging

# Enable MCP debug logging
logging.getLogger("mcp").setLevel(logging.DEBUG)

# Initialize with debug output
mcp_manager = MCPManager()
mcp_manager.init_config(MCP_CONFIG)
```

### Health Checks

```python
def check_mcp_health(mcp_manager: MCPManager) -> dict:
    """Check health of MCP servers and tools."""
    health_status = {
        "servers": {},
        "tools": {}
    }

    # Check each tool
    for tool in mcp_manager.tools:
        try:
            # Simple health check (tool-dependent)
            if hasattr(tool, 'health_check'):
                health = tool.health_check()
            else:
                # Generic health check
                health = {"status": "unknown"}

            health_status["tools"][tool.name] = health

        except Exception as e:
            health_status["tools"][tool.name] = {
                "status": "error",
                "error": str(e)
            }

    return health_status

# Usage
health = check_mcp_health(mcp_manager)
print(f"MCP Health: {health}")
```

## Examples

See the `examples/` folder for complete MCP integration examples:

- **[basic_mcp.py](./examples/basic_mcp.py)**: Simple MCP server setup
- **[advanced_mcp.py](./examples/advanced_mcp.py)**: Advanced MCP patterns
- **[custom_mcp_server.py](./examples/custom_mcp_server.py)**: Custom MCP server implementation
- **[mcp_security.py](./examples/mcp_security.py)**: Secure MCP configurations

## Best Practices

### 1. Server Design
- **Idempotent Operations**: Ensure operations produce consistent results
- **Error Handling**: Implement comprehensive error handling and reporting
- **Resource Management**: Properly manage connections and resources
- **Logging**: Provide meaningful logs for debugging and monitoring

### 2. Client Integration
- **Connection Management**: Implement proper connection lifecycle management
- **Error Recovery**: Handle connection failures gracefully
- **Performance Monitoring**: Track tool execution metrics
- **Security**: Follow security best practices for authentication and access

### 3. Production Deployment
- **Health Monitoring**: Implement health checks for MCP servers
- **Load Balancing**: Use connection pooling for high-traffic scenarios
- **Caching Strategy**: Cache results for expensive or deterministic operations
- **Logging and Alerting**: Set up proper logging and alerting for issues

## Support

For additional help with MCP integration:

1. Check the [MCP Specification](https://github.com/modelcontextprotocol/specification)
2. Review the [Troubleshooting](#troubleshooting) section
3. Examine example implementations in the `examples/` folder
4. Consult the [API Reference](./api-reference.md) for MCP manager details

## Next Steps

After mastering MCP integration:

1. Create custom MCP servers for specific use cases
2. Implement advanced patterns like caching and connection pooling
3. Explore integration with other external systems
4. Contribute MCP servers to the ecosystem
