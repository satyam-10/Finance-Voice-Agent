"""
Market data tools — orchestration layer.

These are the public functions called from MarketsAgent's @function_tool
methods. They orchestrate symbol resolution + provider fetches.

Note: this file does NOT import yfinance directly. All network calls go
through providers.yfinance_provider, so swapping data sources only touches
that one file.
"""

from __future__ import annotations

from typing import Any

from data.symbols import (
    SECTOR_ALIASES,
    SECTOR_CONSTITUENTS,
    resolve_symbol,
)
from providers.yfinance_provider import fetch_quote


def get_quote_data(symbol: str) -> dict[str, Any]:
    """Resolve a name and return a quote, or an error dict."""
    ticker = resolve_symbol(symbol)
    if not ticker:
        return {"error": f"I don't recognise {symbol!r}. Could you say it differently?"}

    data = fetch_quote(ticker)
    if data is None:
        return {"error": f"I couldn't fetch a quote for {symbol} right now."}

    return {**data, "name": symbol, "delayed_minutes": 15}


def get_market_overview_data() -> dict[str, Any]:
    """Return Nifty/Sensex/Bank Nifty + top movers across sector baskets."""
    indices: dict[str, Any] = {}
    for label, ticker in [
        ("Nifty 50", "^NSEI"),
        ("Sensex", "^BSESN"),
        ("Bank Nifty", "^NSEBANK"),
    ]:
        q = fetch_quote(ticker)
        if q:
            indices[label] = {
                "last": q["last_price"],
                "change": q["change"],
                "change_pct": q["change_pct"],
            }

    # Use the union of all sector baskets as a stand-in "watchlist" to
    # compute movers. Cheap, fast, good enough for a demo.
    basket = list({
        s
        for sector_list in SECTOR_CONSTITUENTS.values()
        for s in sector_list
    })
    movers: list[dict[str, Any]] = []
    for ticker in basket:
        q = fetch_quote(ticker)
        if q:
            movers.append({
                "ticker": ticker.replace(".NS", ""),
                "last": q["last_price"],
                "change_pct": q["change_pct"],
            })

    movers.sort(key=lambda m: m["change_pct"], reverse=True)

    return {
        "indices": indices,
        "top_gainers": movers[:3],
        "top_losers": movers[-3:][::-1],
        "delayed_minutes": 15,
    }


def get_sector_movers_data(sector: str) -> dict[str, Any]:
    """Return movers within a single sector basket."""
    key = SECTOR_ALIASES.get(sector.strip().lower())
    if not key:
        return {
            "error": (
                f"I don't have a basket for {sector!r}. Try IT, Bank, Auto, "
                f"Pharma, FMCG, or Energy."
            )
        }

    rows: list[dict[str, Any]] = []
    for ticker in SECTOR_CONSTITUENTS[key]:
        q = fetch_quote(ticker)
        if q:
            rows.append({
                "ticker": ticker.replace(".NS", ""),
                "last": q["last_price"],
                "change_pct": q["change_pct"],
            })

    rows.sort(key=lambda r: r["change_pct"], reverse=True)
    return {
        "sector": key.upper(),
        "movers": rows,
        "delayed_minutes": 15,
    }
