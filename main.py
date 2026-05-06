"""
Top-level entrypoint.

This file should stay boring. All it does is:
  1. Load env vars
  2. Configure the AgentSession (model, voice, temperature from config.py)
  3. Attach the MarketsAgent (defined in agents/markets_agent.py)
  4. Trigger the opening greeting

If you find yourself adding business logic here, put it in tools/ or
agents/ instead. This is the "main" — it wires, nothing else.
"""

import logging

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, JobContext, RoomInputOptions
from livekit.plugins import google

from agents.markets_agent import MarketsAgent
from config import (
    GEMINI_MODEL,
    GEMINI_TEMPERATURE,
    GEMINI_VOICE,
    LOG_LEVEL,
)
from prompts import GREETING_INSTRUCTIONS

load_dotenv()
logging.basicConfig(level=LOG_LEVEL)


async def entrypoint(ctx: JobContext) -> None:
    await ctx.connect()

    session = AgentSession(
        llm=google.beta.realtime.RealtimeModel(
            model=GEMINI_MODEL,
            voice=GEMINI_VOICE,
            temperature=GEMINI_TEMPERATURE,
        ),
    )

    await session.start(
        room=ctx.room,
        agent=MarketsAgent(),
        room_input_options=RoomInputOptions(),
    )

    await session.generate_reply(instructions=GREETING_INSTRUCTIONS)


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
