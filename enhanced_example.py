#!/usr/bin/env python3
"""
Enhanced UnisonAI Example
Demonstrates the improved typing, prompts, and tool system
"""

from unisonai import Single_Agent, Agent, Clan
from unisonai.llms.Basellm import BaseLLM
from unisonai.tools.tool import BaseTool, ToolParameter
from unisonai.types import ToolParameterType, ToolExecutionResult


# Create a mock LLM for demonstration
class MockLLM(BaseLLM):
    """Mock LLM for testing purposes"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = "mock-model"
        self.temperature = 0.7
        self.max_tokens = 1000
        self.verbose = True
    
    def run(self, prompt: str, save_messages: bool = True) -> str:
        # Simulate different responses based on prompt content
        if "plan" in prompt.lower():
            return """
<plan>
    <think>
        The task requires creating a simple demonstration. I'll assign basic roles:
        - Researcher: Gather information
        - Writer: Create documentation
        - Manager: Coordinate and deliver results
    </think>
    <step>1: Manager initiates research phase</step>
    <step>2: Researcher gathers information and sends to Writer</step>
    <step>3: Writer creates documentation and submits to Manager</step>
    <step>4: Manager reviews and delivers final result</step>
</plan>
"""
        else:
            return """```yaml
thoughts: >
  I need to execute this task step by step. Based on the context, I'll provide a structured response that demonstrates the enhanced capabilities.
name: "pass_result"
params:
  result: "Task completed successfully using enhanced UnisonAI framework with improved typing, better prompts, and robust tool system."
```"""


# Create an enhanced tool with strong typing
class CalculatorTool(BaseTool):
    """Enhanced calculator tool with strong typing"""
    
    def __init__(self):
        super().__init__()
        self.name = "calculator"
        self.description = "Perform basic mathematical calculations"
        
        # Define parameters with strong typing
        self.parameters = [
            ToolParameter(
                name="operation",
                description="Mathematical operation to perform",
                param_type=ToolParameterType.STRING,
                choices=["add", "subtract", "multiply", "divide"],
                required=True
            ),
            ToolParameter(
                name="num1",
                description="First number",
                param_type=ToolParameterType.FLOAT,
                required=True
            ),
            ToolParameter(
                name="num2", 
                description="Second number",
                param_type=ToolParameterType.FLOAT,
                required=True
            )
        ]
    
    def _run(self, operation: str, num1: float, num2: float) -> float:
        """Execute the calculation"""
        if operation == "add":
            return num1 + num2
        elif operation == "subtract":
            return num1 - num2
        elif operation == "multiply":
            return num1 * num2
        elif operation == "divide":
            if num2 == 0:
                raise ValueError("Cannot divide by zero")
            return num1 / num2
        else:
            raise ValueError(f"Unsupported operation: {operation}")


def main():
    """Demonstrate enhanced UnisonAI capabilities"""
    
    print("🚀 Enhanced UnisonAI Framework Demonstration")
    print("=" * 50)
    
    # 1. Demonstrate enhanced Single_Agent
    print("\n1. Enhanced Single_Agent Example")
    print("-" * 30)
    
    single_agent = Single_Agent(
        llm=MockLLM(),
        identity="Enhanced Calculator Agent",
        description="Demonstrates improved typing and tool system",
        tools=[CalculatorTool],
        verbose=True
    )
    
    print(f"✅ Created Single_Agent: {single_agent.identity}")
    print(f"📝 Description: {single_agent.description}")
    print(f"🔧 Tools available: {len(single_agent.tool_instances)}")
    print(f"⚙️  Max iterations: {single_agent.max_iterations}")
    
    # 2. Demonstrate enhanced tool system
    print("\n2. Enhanced Tool System Example")
    print("-" * 30)
    
    calc_tool = CalculatorTool()
    print(f"🧮 Tool name: {calc_tool.name}")
    print(f"📋 Parameters: {len(calc_tool.parameters)}")
    
    # Debug parameter types
    print("🔍 Parameter details:")
    for param in calc_tool.parameters:
        print(f"   {param.name}: {param.param_type.value} (required: {param.required})")
        if param.choices:
            print(f"     Choices: {param.choices}")
    
    # Test tool execution with validation
    print(f"🔍 Testing tool with operation='multiply', num1=15.5, num2=2.0")
    
    # Try manual validation first
    print("🔍 Manual parameter validation:")
    kwargs = {"operation": "multiply", "num1": 15.5, "num2": 2.0}
    for param in calc_tool.parameters:
        test_val = kwargs.get(param.name)
        is_valid = param.validate_value(test_val)
        print(f"   {param.name}: {test_val} (type: {type(test_val).__name__}) -> Valid: {is_valid}")
        if not is_valid:
            print(f"     Expected type: {param.param_type.value}")
            if param.choices:
                print(f"     Allowed choices: {param.choices}")
    
    try:
        result = calc_tool.execute(operation="multiply", num1=15.5, num2=2.0)
        print(f"✅ Tool execution successful: {result.success}")
        if result.success:
            print(f"📊 Result: {result.result}")
        else:
            print(f"❌ Error: {result.error}")
        print(f"⏱️  Execution time: {result.execution_time:.4f}s")
    except Exception as e:
        print(f"❌ Exception during tool execution: {e}")
    
    # 3. Demonstrate enhanced Agent and Clan
    print("\n3. Enhanced Clan Example")
    print("-" * 30)
    
    # Create agents with enhanced typing
    manager = Agent(
        llm=MockLLM(),
        identity="Strategic Manager",
        description="Coordinates team efforts and ensures quality delivery",
        task="Lead the team to accomplish project goals",
        verbose=True
    )
    
    researcher = Agent(
        llm=MockLLM(),
        identity="Research Specialist", 
        description="Gathers and analyzes information for informed decision-making",
        task="Conduct thorough research and provide insights",
        verbose=True
    )
    
    writer = Agent(
        llm=MockLLM(),
        identity="Documentation Expert",
        description="Creates clear, comprehensive documentation and reports",
        task="Transform research into professional documentation",
        verbose=True
    )
    
    # Create clan with strong typing
    clan = Clan(
        clan_name="Enhanced Development Team",
        manager=manager,
        members=[manager, researcher, writer],
        shared_instruction="Collaborate effectively using enhanced UnisonAI capabilities",
        goal="Demonstrate the improved framework with better typing and prompts"
    )
    
    print(f"🏢 Created Clan: {clan.clan_name}")
    print(f"👥 Team size: {len(clan.members)}")
    print(f"🎯 Goal: {clan.goal}")
    print(f"📁 History folder: {clan.history_folder}")
    
    # 4. Show configuration validation
    print("\n4. Configuration Validation Example")
    print("-" * 30)
    
    try:
        # This will pass validation
        valid_config = single_agent.config
        print(f"✅ Valid agent identity: '{valid_config.identity}'")
        print(f"✅ Valid description length: {len(valid_config.description)} chars")
        
        # Demonstrate type safety
        print(f"✅ Max iterations (int): {valid_config.max_iterations}")
        print(f"✅ Verbose flag (bool): {valid_config.verbose}")
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Enhanced UnisonAI Framework Ready!")
    print("✨ Features demonstrated:")
    print("   • Strong typing with Pydantic models")
    print("   • Enhanced prompts for better AI interactions")
    print("   • Improved tool system with validation")
    print("   • Better error handling and logging")
    print("   • Backward compatibility maintained")


if __name__ == "__main__":
    main()