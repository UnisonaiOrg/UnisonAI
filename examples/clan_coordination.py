"""
Multi-Agent Clan Coordination Example

This example demonstrates how to create and coordinate multiple specialized agents
working together as a clan to accomplish complex tasks.
"""

from unisonai import Agent, Clan
from unisonai.llms import Gemini
from unisonai.tools.websearch import WebSearchTool
from unisonai.tools.tool import BaseTool, Field
from unisonai.tools.types import ToolParameterType
from unisonai import config
import json

class ResearchTool(BaseTool):
    """Specialized research tool for gathering information."""

    def __init__(self):
        self.name = "research_tool"
        self.description = "Conduct in-depth research on topics"
        self.params = [
            Field(
                name="topic",
                description="Research topic or question",
                field_type=ToolParameterType.STRING,
                required=True
            ),
            Field(
                name="depth",
                description="Research depth ('quick', 'detailed', 'comprehensive')",
                field_type=ToolParameterType.STRING,
                default_value="detailed",
                required=False
            ),
            Field(
                name="sources",
                description="Number of sources to consult",
                field_type=ToolParameterType.INTEGER,
                default_value=5,
                required=False
            )
        ]
        super().__init__()

    def _run(self, topic: str, depth: str = "detailed", sources: int = 5) -> dict:
        """Conduct research on the specified topic."""

        # Simulate research results (in real implementation, this would use WebSearchTool)
        research_findings = {
            "topic": topic,
            "depth": depth,
            "sources_consulted": sources,
            "findings": [
                f"Key finding 1 about {topic}",
                f"Key finding 2 about {topic}",
                f"Key finding 3 about {topic}"
            ],
            "conclusions": f"Based on {depth} research, {topic} shows significant importance in modern contexts."
        }

        return research_findings

class AnalysisTool(BaseTool):
    """Specialized analysis tool for data interpretation."""

    def __init__(self):
        self.name = "analysis_tool"
        self.description = "Analyze and interpret research findings"
        self.params = [
            Field(
                name="data",
                description="Research data to analyze",
                field_type=ToolParameterType.DICT,
                required=True
            ),
            Field(
                name="analysis_type",
                description="Type of analysis ('statistical', 'qualitative', 'comparative')",
                field_type=ToolParameterType.STRING,
                default_value="qualitative",
                required=False
            )
        ]
        super().__init__()

    def _run(self, data: dict, analysis_type: str = "qualitative") -> dict:
        """Analyze the provided research data."""

        analysis_results = {
            "input_data": data,
            "analysis_type": analysis_type,
            "insights": [
                f"Key insight 1 from {analysis_type} analysis",
                f"Key insight 2 from {analysis_type} analysis"
            ],
            "patterns": "Identified recurring patterns in the data",
            "recommendations": "Based on analysis, recommend specific actions"
        }

        return analysis_results

class WritingTool(BaseTool):
    """Specialized writing tool for report generation."""

    def __init__(self):
        self.name = "writing_tool"
        self.description = "Generate comprehensive reports from research and analysis"
        self.params = [
            Field(
                name="research_data",
                description="Research findings to include",
                field_type=ToolParameterType.DICT,
                required=True
            ),
            Field(
                name="analysis_results",
                description="Analysis results to incorporate",
                field_type=ToolParameterType.DICT,
                required=True
            ),
            Field(
                name="report_format",
                description="Output format ('summary', 'detailed', 'executive')",
                field_type=ToolParameterType.STRING,
                default_value="detailed",
                required=False
            ),
            Field(
                name="include_recommendations",
                description="Include actionable recommendations",
                field_type=ToolParameterType.BOOLEAN,
                default_value=True,
                required=False
            )
        ]
        super().__init__()

    def _run(self, research_data: dict, analysis_results: dict,
             report_format: str = "detailed", include_recommendations: bool = True) -> str:
        """Generate a comprehensive report."""

        report = f"""
# Research Report: {research_data.get('topic', 'Unknown Topic')}

## Executive Summary
This report presents {research_data.get('depth', 'detailed')} research findings on the specified topic.

## Research Findings
**Topic:** {research_data.get('topic', 'N/A')}
**Depth:** {research_data.get('depth', 'N/A')}
**Sources Consulted:** {research_data.get('sources_consulted', 0)}

### Key Findings
{chr(10).join(f'- {finding}' for finding in research_data.get('findings', []))}

## Analysis Results
**Analysis Type:** {analysis_results.get('analysis_type', 'N/A')}

### Key Insights
{chr(10).join(f'- {insight}' for insight in analysis_results.get('insights', []))}

### Identified Patterns
{analysis_results.get('patterns', 'No patterns identified')}

"""

        if include_recommendations:
            report += f"""
## Recommendations
{analysis_results.get('recommendations', 'No specific recommendations provided')}
"""

        report += """
## Conclusion
This report synthesizes research findings with analytical insights to provide a comprehensive understanding of the topic.

---
*Generated by UnisonAI Clan Coordination System*
"""

        return report

def create_research_clan():
    """Create a clan of specialized agents for research tasks."""

    # Configure API key
    config.set_api_key("gemini", "your-gemini-api-key")

    # Create specialized agents
    researcher = Agent(
        llm=Gemini(model="gemini-2.0-flash"),
        identity="Senior Researcher",
        description="Expert researcher specializing in comprehensive information gathering and analysis",
        task="Conduct thorough research on assigned topics using available tools and methodologies",
        tools=[WebSearchTool, ResearchTool],
        verbose=True
    )

    analyst = Agent(
        llm=Gemini(model="gemini-2.0-flash"),
        identity="Data Analyst",
        description="Expert analyst specializing in interpreting research data and identifying patterns",
        task="Analyze research findings to extract meaningful insights and trends",
        tools=[AnalysisTool],
        verbose=True
    )

    writer = Agent(
        llm=Gemini(model="gemini-2.0-flash"),
        identity="Technical Writer",
        description="Expert writer specializing in creating clear, comprehensive reports and documentation",
        task="Synthesize research findings and analysis into well-structured, actionable reports",
        tools=[WritingTool],
        verbose=True
    )

    # Create the research clan
    research_clan = Clan(
        clan_name="Research Excellence Team",
        manager=researcher,
        members=[researcher, analyst, writer],
        shared_instruction="""
        Work together systematically to produce comprehensive research reports:

        1. RESEARCHER: Gather comprehensive information on the topic
        2. ANALYST: Analyze findings and extract insights
        3. WRITER: Synthesize everything into a clear, actionable report

        Communicate clearly and build upon each other's work.
        """,
        goal="Produce high-quality, comprehensive research reports that combine thorough investigation, insightful analysis, and clear presentation",
        history_folder="research_clan_history",
        output_file="research_report.txt"
    )

    return research_clan

def demonstrate_clan_coordination():
    """Demonstrate how the clan coordinates on a complex research task."""

    print("🤝 Clan Coordination Example")
    print("=" * 50)

    # Create the research clan
    clan = create_research_clan()

    # Define a complex research task
    research_task = """
    Research the current state of artificial intelligence in healthcare.
    Include information about:
    - Current applications and use cases
    - Major technological advancements
    - Regulatory considerations
    - Future trends and predictions
    - Challenges and limitations

    Provide a comprehensive analysis with recommendations for implementation.
    """

    print(f"📋 Research Task: AI in Healthcare")
    print(f"📝 Task Description: {research_task.strip()}")
    print("\n🚀 Executing clan coordination...")

    try:
        # Execute the clan task
        clan.unleash()

        print("\n✅ Clan execution completed successfully!")
        print("📄 Check 'research_report.txt' for the complete report")
        print("📂 Check 'research_clan_history/' for detailed execution logs")

    except Exception as e:
        print(f"❌ Clan execution failed: {e}")
        print("This might be due to missing API keys or network issues")

def test_individual_agents():
    """Test individual agents to show their specialized capabilities."""

    print("\n🧪 Testing Individual Agent Capabilities")
    print("=" * 50)

    # Create individual agents for testing
    researcher = Agent(
        llm=Gemini(model="gemini-2.0-flash"),
        identity="Test Researcher",
        description="Test researcher for individual capabilities",
        task="Test research capabilities",
        tools=[ResearchTool],
        verbose=True
    )

    analyst = Agent(
        llm=Gemini(model="gemini-2.0-flash"),
        identity="Test Analyst",
        description="Test analyst for individual capabilities",
        task="Test analysis capabilities",
        tools=[AnalysisTool],
        verbose=True
    )

    writer = Agent(
        llm=Gemini(model="gemini-2.0-flash"),
        identity="Test Writer",
        description="Test writer for individual capabilities",
        task="Test writing capabilities",
        tools=[WritingTool],
        verbose=True
    )

    # Test research capabilities
    print("\n🔍 Testing Researcher:")
    try:
        research_result = researcher.unleash()
        print("✅ Researcher test completed")
    except Exception as e:
        print(f"❌ Researcher test failed: {e}")

    # Test analysis capabilities
    print("\n📊 Testing Analyst:")
    try:
        analysis_result = analyst.unleash()
        print("✅ Analyst test completed")
    except Exception as e:
        print(f"❌ Analyst test failed: {e}")

    # Test writing capabilities
    print("\n✍️  Testing Writer:")
    try:
        writing_result = writer.unleash()
        print("✅ Writer test completed")
    except Exception as e:
        print(f"❌ Writer test failed: {e}")

if __name__ == "__main__":
    # Set up API key for testing
    config.set_api_key("gemini", "your-gemini-api-key")

    # Demonstrate clan coordination
    demonstrate_clan_coordination()

    print("\n" + "=" * 50)
    print("💡 Tip: In a real scenario, replace the mock tools with actual")
    print("   implementations that connect to real APIs and services.")
    print("=" * 50)
