from unisonai import Single_Agent
from unisonai.llms import Gemini
from unisonai.tools.websearch import WebSearchTool

web_agent = Single_Agent(
    llm=Gemini(model="gemini-2.0-flash"),
    identity="Web Explorer",
    description="Web Searcher for multiple queries",
    tools=[WebSearchTool],
    history_folder="history",
    output_file="output.txt"
)

web_agent.unleash(task="Find out what is the age of trump")