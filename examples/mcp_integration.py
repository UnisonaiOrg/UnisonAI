"""
MCP (Model Context Protocol) Integration Example

This example demonstrates how to integrate UnisonAI agents with external
services and tools using the Model Context Protocol (MCP).
"""

from unisonai import Single_Agent
from unisonai.llms import Gemini
from unisonai.tools import MCPManager
from unisonai import config
import json
import asyncio

class CustomMCPServer:
    """Example custom MCP server for demonstration."""

    def __init__(self):
        self.name = "custom_calculator_server"
        self.version = "1.0.0"

    def get_capabilities(self):
        """Return server capabilities."""
        return {
            "tools": {
                "advanced_calculator": {
                    "description": "Perform advanced mathematical calculations",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string",
                                "description": "Mathematical expression to evaluate"
                            },
                            "precision": {
                                "type": "integer",
                                "description": "Decimal precision for results",
                                "default": 2
                            }
                        },
                        "required": ["expression"]
                    }
                },
                "data_processor": {
                    "description": "Process and analyze data arrays",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "data": {
                                "type": "array",
                                "items": {"type": "number"},
                                "description": "Array of numbers to process"
                            },
                            "operation": {
                                "type": "string",
                                "enum": ["sum", "average", "min", "max", "stats"],
                                "description": "Operation to perform"
                            }
                        },
                        "required": ["data", "operation"]
                    }
                }
            }
        }

def setup_mcp_servers():
    """Set up MCP server configurations."""

    # Configuration for time server
    time_server_config = {
        "mcpServers": {
            "time_server": {
                "command": "uvx",
                "args": ["mcp-server-time"]
            }
        }
    }

    # Configuration for fetch server
    fetch_server_config = {
        "mcpServers": {
            "fetch_server": {
                "command": "uvx",
                "args": ["mcp-server-fetch"]
            }
        }
    }

    # Configuration for custom server (if available)
    custom_server_config = {
        "mcpServers": {
            "custom_server": {
                "command": "python",
                "args": ["custom_mcp_server.py"],
                "cwd": "/path/to/custom/server"
            }
        }
    }

    return {
        "time": time_server_config,
        "fetch": fetch_server_config,
        "custom": custom_server_config
    }

def initialize_mcp_manager(server_configs):
    """Initialize MCP manager with server configurations."""

    print("🔧 Initializing MCP Manager...")
    print("=" * 50)

    mcp_manager = MCPManager()
    initialized_servers = {}

    for server_name, config in server_configs.items():
        try:
            print(f"\n🌐 Setting up {server_name} server...")
            tools = mcp_manager.init_config(config)
            initialized_servers[server_name] = {
                "config": config,
                "tools": tools,
                "status": "success",
                "tool_count": len(tools)
            }
            print(f"✅ {server_name} server initialized with {len(tools)} tools")

        except Exception as e:
            print(f"❌ Failed to initialize {server_name} server: {e}")
            initialized_servers[server_name] = {
                "config": config,
                "status": "failed",
                "error": str(e)
            }

    return mcp_manager, initialized_servers

def create_mcp_enabled_agent(mcp_tools):
    """Create an agent with MCP capabilities."""

    # Configure API key
    config.set_api_key("gemini", "your-gemini-api-key")

    # Create agent with MCP tools
    agent = Single_Agent(
        llm=Gemini(model="gemini-2.0-flash"),
        identity="MCP-Enabled Assistant",
        description="""
        An AI assistant with access to external services through MCP.
        I can fetch current time, retrieve web content, and perform calculations
        using external tools and services.
        """,
        tools=mcp_tools,
        verbose=True,
        history_folder="mcp_agent_history"
    )

    return agent

def demonstrate_mcp_capabilities(agent):
    """Demonstrate various MCP capabilities."""

    print("\n🚀 Demonstrating MCP Capabilities")
    print("=" * 50)

    # Test cases for different MCP tools
    test_tasks = [
        {
            "name": "Time Query",
            "task": "What is the current time and date?",
            "expected_tools": ["time"]
        },
        {
            "name": "Web Fetch",
            "task": "Fetch the latest news from a technology website and summarize the main stories.",
            "expected_tools": ["fetch"]
        },
        {
            "name": "Combined Services",
            "task": "Get the current time, then fetch information about Python programming, and calculate something.",
            "expected_tools": ["time", "fetch"]
        }
    ]

    for test_case in test_tasks:
        print(f"\n🧪 Test: {test_case['name']}")
        print(f"📝 Task: {test_case['task']}")
        print("-" * 40)

        try:
            result = agent.unleash(task=test_case['task'])
            print(f"✅ Success: {str(result)[:200]}...")

        except Exception as e:
            print(f"❌ Failed: {e}")

        print()

def test_mcp_error_handling():
    """Test MCP error handling scenarios."""

    print("\n🛠️  Testing MCP Error Handling")
    print("=" * 50)

    # Test with invalid server configuration
    invalid_config = {
        "mcpServers": {
            "nonexistent_server": {
                "command": "nonexistent_command",
                "args": ["invalid_args"]
            }
        }
    }

    try:
        mcp_manager = MCPManager()
        tools = mcp_manager.init_config(invalid_config)
        print("❌ Expected error but got success")
    except Exception as e:
        print(f"✅ Correctly caught error: {type(e).__name__}: {e}")

def demonstrate_advanced_mcp_patterns():
    """Demonstrate advanced MCP integration patterns."""

    print("\n🎯 Advanced MCP Patterns")
    print("=" * 50)

    # Pattern 1: Multiple server types
    print("\n1️⃣ Multiple Server Types:")

    multi_server_config = {
        "mcpServers": {
            "time_service": {
                "command": "uvx",
                "args": ["mcp-server-time"]
            },
            "fetch_service": {
                "command": "uvx",
                "args": ["mcp-server-fetch"]
            }
        }
    }

    try:
        manager = MCPManager()
        tools = manager.init_config(multi_server_config)
        print(f"✅ Initialized {len(tools)} tools from multiple servers")
    except Exception as e:
        print(f"❌ Multi-server initialization failed: {e}")

    # Pattern 2: Custom server integration
    print("\n2️⃣ Custom Server Integration:")

    # This would typically connect to a custom MCP server
    # For demonstration, we'll show the structure
    custom_config = {
        "mcpServers": {
            "custom_calculator": {
                "command": "python",
                "args": ["path/to/custom_mcp_server.py"],
                "env": {
                    "CUSTOM_CONFIG": json.dumps({"precision": 3})
                }
            }
        }
    }

    print("📋 Custom server configuration structure:")
    print(json.dumps(custom_config, indent=2))

def main():
    """Main demonstration function."""

    print("🌐 UnisonAI MCP Integration Example")
    print("=" * 60)
    print("This example demonstrates how to integrate external services")
    print("using the Model Context Protocol (MCP).")

    # Setup MCP server configurations
    server_configs = setup_mcp_servers()

    # Initialize MCP manager
    mcp_manager, server_status = initialize_mcp_manager(server_configs)

    # Show server status
    print("\n📊 Server Status Summary:")
    for server_name, status in server_status.items():
        print(f"  {server_name}: {status['status']} ({status.get('tool_count', 0)} tools)")

    # Create MCP-enabled agent if we have tools
    successful_servers = [name for name, status in server_status.items() if status['status'] == 'success']

    if successful_servers:
        # Get all tools from successful servers
        all_tools = []
        for server_name in successful_servers:
            server_info = server_status[server_name]
            all_tools.extend(server_info['tools'])

        if all_tools:
            # Create agent with MCP tools
            agent = create_mcp_enabled_agent(all_tools)

            # Demonstrate MCP capabilities
            demonstrate_mcp_capabilities(agent)

    # Test error handling
    test_mcp_error_handling()

    # Demonstrate advanced patterns
    demonstrate_advanced_mcp_patterns()

    print("\n" + "=" * 60)
    print("✨ MCP Integration demonstration completed!")
    print("\n💡 Key takeaways:")
    print("   • MCP enables seamless integration with external services")
    print("   • Tools are automatically converted to UnisonAI format")
    print("   • Error handling ensures robust operation")
    print("   • Multiple servers can be combined for comprehensive capabilities")
    print("=" * 60)

if __name__ == "__main__":
    # Note: This example requires actual MCP servers to be installed and running
    # In a real environment, you would need to install MCP server packages like:
    # pip install mcp-server-time mcp-server-fetch

    print("⚠️  Note: This example requires MCP servers to be installed.")
    print("   Install with: pip install mcp-server-time mcp-server-fetch")
    print("   Or run actual MCP servers for full functionality.\n")

    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Demonstration interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        print("This might be due to missing MCP server installations")
