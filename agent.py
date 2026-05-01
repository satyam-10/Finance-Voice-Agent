"""
Indian Markets Voice Agent
==========================

A voice agent that answers questions about Indian equity markets (NSE/BSE):
- Live (15-min delayed) quotes via yfinance
- Market overview: Nifty, Sensex, Bank Nifty, top movers
- Mocked portfolio queries (P&L, holdings)
- Polite refusal of trade recommendations / order placement

Stack:
- LiveKit Agents (orchestration, audio streaming, browser link)
- Google Gemini Live (single multimodal model: speech-in -> reasoning -> speech-out)
- yfinance (free Indian market data, no API key needed)

This is a DEMO. It is NOT investment advice. Not for production use without
SEBI Investment Adviser / Research Analyst registration.
"""

import logging
from dotenv import load_dotenv

from livekit import agents
from livekit.agents import Agent, AgentSession, JobContext, RoomInputOptions
from livekit.agents.llm import function_tool
from livekit.plugins import google

from tools.market_data import (
    get_quote_data,
    get_market_overview_data,
    get_sector_movers_data,
)
from tools.portfolio import (
    get_portfolio_data,
    get_position_data,
)

load_dotenv()

logger = logging.getLogger("markets-agent")
logger.setLevel(logging.INFO)


SYSTEM_INSTRUCTIONS = """
You are Meera, a friendly voice assistant for Indian equity markets (NSE and BSE).

WHAT YOU DO
- Answer questions about live stock quotes ("How is Reliance trading?")
- Give market overviews ("How are markets today?", "What's Nifty at?")
- Look up the user's portfolio (it is mocked demo data)
- Discuss sector movers ("How is IT today?")

WHAT YOU DO NOT DO
- You NEVER recommend buying or selling. If asked, say: "I can't recommend trades,
  but I can show you how it has been moving — want me to pull the data?"
- You NEVER place orders. If asked, say: "I can't place trades. You'll need your
  broker app for that."
- You NEVER predict prices.

HOW YOU SPEAK
- Short, conversational sentences. This is voice, not text.
- No markdown, no bullet points, no symbols.
- Pronounce ticker symbols as the company name. Say "Reliance", not "R-E-L-I-A-N-C-E".
- Read prices in words: "two thousand four hundred fifty rupees, up zero point eight percent".
- Round to one decimal place when speaking percentages.
- If the user is ambiguous (e.g. "HDFC"), ask which one — HDFC Bank or HDFC AMC.

DATA NOTES
- Quotes are delayed by about fifteen minutes. If the user asks if it's live, say so.
- If a tool fails or returns no data, say so plainly. Don't guess numbers.

OPENING
- Start with a short greeting, mention the disclaimer in one sentence:
  "Hi, I'm Meera. I can help with Indian market info and your demo portfolio.
  Quick note — this is for information only, not investment advice. What would
  you like to know?"
""".strip()


class MarketsAgent(Agent):
    """The markets voice agent. Tools are defined as methods with @function_tool."""

    def __init__(self) -> None:
        super().__init__(instructions=SYSTEM_INSTRUCTIONS)

    # ---------- Market data tools ----------

    @function_tool
    async def get_quote(self, symbol: str) -> dict:
        """Get the current quote for an Indian stock or index.

        Use this when the user asks about a specific stock or index — for
        example "how is Reliance", "what's Nifty at", "TCS price".
        Accepts company names ("Reliance", "TCS", "HDFC Bank") or index names
        ("Nifty", "Sensex", "Bank Nifty"). Server resolves to the correct ticker.

        Args:
            symbol: The company or index name as the user said it.
        """
        logger.info(f"[tool] get_quote(symbol={symbol!r})")
        result = get_quote_data(symbol)
        logger.info(f"[tool] get_quote result: {result}")
        return result

    @function_tool
    async def get_market_overview(self) -> dict:
        """Get an overview of the Indian markets right now.

        Returns Nifty 50, Sensex, Bank Nifty levels, and the top 3 gainers
        and losers from the Nifty 50. Use this when the user asks something
        broad like "how are markets today" or "what's happening in the market".
        """
        logger.info("[tool] get_market_overview()")
        result = get_market_overview_data()
        logger.info(f"[tool] get_market_overview result keys: {list(result.keys())}")
        return result

    @function_tool
    async def get_sector_movers(self, sector: str) -> dict:
        """Get top movers within a specific Indian market sector.

        Args:
            sector: One of "IT", "Bank", "Auto", "Pharma", "FMCG", "Energy".
                Be flexible with what the user says — "tech" means IT, "banks"
                means Bank, "cars" means Auto, etc.
        """
        logger.info(f"[tool] get_sector_movers(sector={sector!r})")
        result = get_sector_movers_data(sector)
        logger.info(f"[tool] get_sector_movers result: {result}")
        return result

    # ---------- Portfolio tools (mocked) ----------

    @function_tool
    async def get_portfolio(self) -> dict:
        """Get the user's full portfolio with current P&L.

        Use when the user asks "how is my portfolio", "what's my P&L",
        "show me my holdings". The portfolio is mocked demo data.
        """
        logger.info("[tool] get_portfolio()")
        result = get_portfolio_data()
        logger.info(f"[tool] get_portfolio: {len(result.get('holdings', []))} holdings")
        return result

    @function_tool
    async def get_position(self, symbol: str) -> dict:
        """Get details of a single holding in the user's mocked portfolio.

        Use when the user asks about a specific position — "how is my HDFC
        position", "what's my P&L on Infosys".

        Args:
            symbol: The company name as the user said it.
        """
        logger.info(f"[tool] get_position(symbol={symbol!r})")
        result = get_position_data(symbol)
        logger.info(f"[tool] get_position result: {result}")
        return result


async def entrypoint(ctx: JobContext) -> None:
    """Entry point for the LiveKit worker. Runs once per session."""
    await ctx.connect()

    # Gemini Live = single realtime model.
    # Handles speech-in -> reasoning -> speech-out natively. Lowest latency,
    # zero cost on the free tier of Google AI Studio.
    session = AgentSession(
        llm=google.beta.realtime.RealtimeModel(
            model="gemini-2.0-flash-exp",
            voice="Aoede",        # try also: "Puck", "Charon", "Kore", "Fenrir"
            temperature=0.6,      # low-ish: we want accurate numbers, not creativity
        ),
    )

    await session.start(
        room=ctx.room,
        agent=MarketsAgent(),
        room_input_options=RoomInputOptions(),  # noise cancellation off (self-host friendly)
    )

    # Speak first so the user knows the agent is listening.
    await session.generate_reply(
        instructions=(
            "Greet the user warmly as Meera. In one short sentence, mention you "
            "help with Indian market info and a demo portfolio, and that this is "
            "for information only, not investment advice. Then ask what they'd "
            "like to know."
        )
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
