import os
import asyncio
from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StdioConnectionParams,
    StreamableHTTPConnectionParams,
)
from mcp import StdioServerParameters
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

REPORTS_DIR = os.getenv("REPORTS_DIR") or os.path.join(BASE_DIR, "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

SCHOLARSHIP_SERVER = os.path.join(
    BASE_DIR,
    "scholarship_mcp_server",
    "scholarship_server.py"
)

tavily_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}"
    )
)

maps_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://mapstools.googleapis.com/mcp",
        headers={
            "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        },
    )
)

scholarship_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="python",
            args=[SCHOLARSHIP_SERVER],
        ),
        timeout=30,
    )
)

filesystem_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=[
                "-y",
                "@modelcontextprotocol/server-filesystem",
                REPORTS_DIR,
            ],
        ),
        timeout=30,
    )
)

AGENT_INSTRUCTION = f"""
You are a Study Abroad Advisor.

You have access to 4 MCP tool groups:

1. Tavily MCP
Use this FIRST for:
- finding universities
- rankings
- tuition fees
- official websites
- program information
- current web information

2. Scholarship MCP
Use this AFTER Tavily for:
- scholarships
- cost of living
- visa requirements

3. Google Maps MCP
Use this ONLY after universities/cities are known.
Use it for:
- current weather
- nearby places of interest
- campus/city location information

Never use Google Maps to search for universities.

4. Filesystem MCP
Use this LAST to save a markdown report.

Workflow:
Step 1 - Use Tavily to find top 3 universities for the requested field and country.
Step 2 - Use Scholarship MCP for scholarships, cost of living, and visa requirements.
Step 3 - Use Google Maps MCP for weather and 2 nearby places for each university city.
Step 4 - Save a markdown report using Filesystem MCP in this folder:
{REPORTS_DIR}

Final response:
- Give a clean summary to the student.
- Mention that the report was saved.
"""

agent = LlmAgent(
    name="study_abroad_advisor",
    model="gemini-2.5-flash",
    instruction=AGENT_INSTRUCTION,
    tools=[
        tavily_toolset,
        scholarship_toolset,
        maps_toolset,
        filesystem_toolset,
    ],
)


async def run_query(question):
    session_service = InMemorySessionService()

    await session_service.create_session(
        app_name="study_abroad_finder",
        user_id="student",
        session_id="session_1",
    )

    runner = Runner(
        agent=agent,
        app_name="study_abroad_finder",
        session_service=session_service,
    )

    message = types.Content(
        role="user",
        parts=[types.Part(text=question)],
    )

    final_response = ""

    async for event in runner.run_async(
        user_id="student",
        session_id="session_1",
        new_message=message,
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_response = event.content.parts[0].text

    return final_response


def ask(question):
    return asyncio.run(run_query(question))