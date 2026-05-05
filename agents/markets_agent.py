"""
MarketsAgent — defines the agent's tools.

Each method is a thin wrapper: it logs, calls into tools/, and returns
the result. The actual data work lives in tools/, which lives on top of
providers/ and data/. This file only knows about "what tools exist and
what they're for" — not how they're implemented.
"""

from __future__ import annotations

import logging

from livekit.agents import Agent
from livekit.agents.llm import function_tool

from prompts import SYSTEM_INSTRUCTIONS
from tools.market_data import (
    get_market_overview_data,
    get_quote_data,
    get_sector_movers_data,
)
from tools.portfolio import get_portfolio_data, get_position_data

logger = logging.getLogger("markets-agent")


class MarketsAgent(Agent):
    """The markets voice agent. Tools are methods with @function_tool."""

    def __init__(self) -> None:
        super().__init__(instructions=SYSTEM_INSTRUCTIONS)

    # ---------- Market data tools ----------

    @function_tool
    async def get_quote(self, symbol: str) -> dict:
        """Get the current quote for an Indian stock or index.

        Use this when the user asks about a specific stock or index — for
        example "how is Reliance", "what's Nifty at", "TCS price".
        Accepts company names ("Reliance", "TCS", "HDFC Bank") or index
        names ("Nifty", "Sensex", "Bank Nifty"). Server resolves to ticker.

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
        and losers. Use this when the user asks something broad like "how
        are markets today" or "what's happening in the market".
        """
        logger.info("[tool] get_market_overview()")
        result = get_market_overview_data()
        logger.info(f"[tool] get_market_overview keys: {list(result.keys())}")
        return result

    @function_tool
    async def get_sector_movers(self, sector: str) -> dict:
        """Get top movers within a specific Indian market sector.

        Args:
            sector: One of "IT", "Bank", "Auto", "Pharma", "FMCG", "Energy".
                Be flexible — "tech" means IT, "banks" means Bank, "cars"
                means Auto, etc.
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
