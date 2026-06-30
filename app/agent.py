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

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

maps_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://mapstools.googleapis.com/mcp",
        headers={
            "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
    )
)

AGENT_INSTRUCTION = """
You are a Study Abroad Advisor.

Use only Google Maps MCP.

When the student asks about a city or university location:
1. Use Google Maps MCP to get current weather if available.
2. Use Google Maps MCP to find nearby places of interest.
3. Do not use Tavily.
4. Do not use Scholarship MCP.
5. Do not use Filesystem MCP.
6. Do not save files.
"""

agent = LlmAgent(
    name="study_abroad_advisor",
    model="gemini-2.5-flash",
    instruction=AGENT_INSTRUCTION,
    tools=[
        maps_toolset,
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