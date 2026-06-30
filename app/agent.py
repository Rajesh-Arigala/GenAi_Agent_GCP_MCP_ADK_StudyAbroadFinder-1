import os
import asyncio
from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

tavily_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}"
    )
)

AGENT_INSTRUCTION = """
You are a Study Abroad Advisor.

Use only Tavily MCP for web search.

When the student asks about universities:
1. Search the web using Tavily.
2. Find top universities for the requested field and country.
3. Summarize the top 3 universities.
4. Include location, ranking if available, and why each university is strong.
5. Do not use Scholarship MCP.
6. Do not use Filesystem MCP.
7. Do not use Google Maps MCP.
8. Do not save files.
"""

agent = LlmAgent(
    name="study_abroad_advisor",
    model="gemini-2.5-flash",
    instruction=AGENT_INSTRUCTION,
    tools=[
        tavily_toolset,
    ]
)


async def run_query(question):
    session_service = InMemorySessionService()

    await session_service.create_session(
        app_name="study_abroad_finder",
        user_id="student",
        session_id="session_1"
    )

    runner = Runner(
        agent=agent,
        app_name="study_abroad_finder",
        session_service=session_service
    )

    message = types.Content(
        role="user",
        parts=[types.Part(text=question)]
    )

    final_response = ""

    async for event in runner.run_async(
        user_id="student",
        session_id="session_1",
        new_message=message
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_response = event.content.parts[0].text

    return final_response


def ask(question):
    return asyncio.run(run_query(question))