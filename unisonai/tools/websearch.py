from unisonai.tools.tool import BaseTool, Field
from duckduckgo_search import DDGS
from googlesearch import search as netsearch

class WebSearchTool(BaseTool):
    name = "web_search"
    description = "Useful for when you need to answer questions about current events. You should ask targeted questions."
    params = [Field(name="query", description="The query to search for.", required=True)]

    def _run(query: str) -> str:
        output = ""
        print("via google search...")
        results = list(netsearch(query, advanced=True, num_results=3))
        if results:
            print("got results")
            for i, result in enumerate(results):
                output += f"{i+1}. \nTitle: {result.title}\nDescription: {result.description}\nSource: {result.url}\n\n"    
        else:
            print(f"Error using google search: No results found trying...")

        # If Online_Scraper fails or is not found use DuckDuckGo
            try:
                ddg = DDGS()
                ddg_results = ddg.text(query, max_results=3)
                
                if ddg_results:
                    for result in ddg_results:
                        output+=f"TITLE:\n{result.get('title', 'No Title Found')}\n\nBODY:\n{result.get('body', 'No Body Found')}\n\n"
                else:
                    print("No results from DuckDuckGo")
                    return "Failed to retrieve search results"

            except Exception as e:
                print(f"Error using DuckDuckGo Search: {e}")
                return "Failed to retrieve search results"

        return output