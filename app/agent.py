import os
import asyncio
from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv()

REPORTS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "reports")
)

os.makedirs(REPORTS_DIR, exist_ok=True)

filesystem_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", REPORTS_DIR]
        ),
        timeout=30
    )
)

AGENT_INSTRUCTION = f"""
You are a Study Abroad Advisor.

Use only the Filesystem MCP tool.

When the student asks a question:
1. Give a short study abroad recommendation from your own knowledge.
2. Save a markdown report into this folder:
   {REPORTS_DIR}
3. Filename: filesystem_test_report.md
4. Do not use Tavily.
5. Do not use Google Maps.
6. Do not use Scholarship MCP.
"""

agent = LlmAgent(
    name="study_abroad_advisor",
    model="gemini-2.5-flash",
    instruction=AGENT_INSTRUCTION,
    tools=[
        filesystem_toolset,
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