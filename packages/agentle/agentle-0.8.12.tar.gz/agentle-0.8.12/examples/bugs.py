from duckduckgo_search import DDGS
import httpx
from pydantic import HttpUrl
from agentle.agents.agent import Agent
from agentle.agents.agent_config import AgentConfig
from agentle.agents.agent_team import AgentTeam
from agentle.generations.providers.google.google_generation_provider import (
    GoogleGenerationProvider,
)
from agentle.generations.tools.tool import Tool


def search_web(query: str, max_results: int = 10) -> str:
    """
    Search the web for the given query using DuckDuckGo.
    parameters:
        query: The query to search the web for
        max_results: The maximum number of results to return
    """
    print(f"Searching the web for: {query}")
    results = DDGS().text(query, max_results=max_results)
    print(results)
    return str(results)


search_web_tool = Tool.from_callable(search_web)


async def get_product_information(page_url: HttpUrl) -> str:
    """
    Get the product information from the given page URL.
    parameters:
        page_url: The URL of the page to get the product information from
    """
    print(f"Getting product information from: {page_url}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(str(page_url))
            return response.text
    except Exception as e:
        print(f"Error getting product information from {page_url}: {e}")
        return "COULD NOT GET PRODUCT INFORMATION FROM THE URL"


get_product_information_tool = Tool.from_callable(get_product_information)

data_agent = Agent(
    name="Data Agent",
    description="""
    The agent that performs a web search for the given query.
    Returns a list of URLs of the results.
    """,
    tools=[search_web_tool],
    generation_provider=GoogleGenerationProvider(),
    model="gemini-2.5-flash",
    instructions="""
    You are a web search agent that searches the web for the given query using DuckDuckGo.
    """,
    debug=True,
)

data_verification_agent = Agent(
    name="Data Verification Agent",
    description="""
    The agent that verifies the data from the web search.
    Returns a list of URLs and subject information of the results that meet the criteria.
    """,
    tools=[get_product_information_tool],
    generation_provider=GoogleGenerationProvider(),
    model="gemini-2.5-flash",
    instructions="...",
    debug=True,
)
analysis_agent = Agent(
    name="Analysis Agent",
    description="""
    The agent that analyzes the data from the verified results of the web search.
    Returns a comprehensive analysis.
    """,
    generation_provider=GoogleGenerationProvider(),
    model="gemini-2.5-flash",
    instructions="...",
    debug=True,
)

team = AgentTeam(
    agents=[data_agent, data_verification_agent, analysis_agent],
    orchestrator_provider=GoogleGenerationProvider(),
    orchestrator_model="gemini-2.5-flash",
    team_config=AgentConfig(maxIterations=5, maxToolCalls=20),
)

print(team.run("What is the valuation of Tesla?"))
