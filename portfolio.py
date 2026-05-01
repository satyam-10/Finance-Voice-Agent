"""
Mocked portfolio.

For a real product you'd plug in Zerodha Console / Kite, broker statements,
or a Postgres table. For the demo, we hardcode 5 holdings and combine them
with live prices from yfinance to get a realistic-feeling P&L every time.
"""

from __future__ import annotations

import logging
from typing import Any

from tools.market_data import _fetch_quote, resolve_symbol

logger = logging.getLogger(__name__)


# Edit this to make the demo feel personal — names you'll talk about.
MOCK_HOLDINGS = [
    {"name": "Reliance",   "ticker": "RELIANCE.NS",  "qty": 10, "avg_price": 2_350.00},
    {"name": "TCS",        "ticker": "TCS.NS",       "qty": 5,  "avg_price": 3_800.00},
    {"name": "HDFC Bank",  "ticker": "HDFCBANK.NS",  "qty": 25, "avg_price": 1_550.00},
    {"name": "Infosys",    "ticker": "INFY.NS",      "qty": 15, "avg_price": 1_420.00},
    {"name": "ITC",        "ticker": "ITC.NS",       "qty": 50, "avg_price": 410.00},
]


def _enrich(holding: dict[str, Any]) -> dict[str, Any]:
    """Combine a static holding with a live quote to produce P&L."""
    q = _fetch_quote(holding["ticker"])
    if q is None:
        return {**holding, "error": "price unavailable"}

    last = q["last_price"]
    invested = holding["qty"] * holding["avg_price"]
    current = holding["qty"] * last
    pnl = current - invested
    pnl_pct = (pnl / invested) * 100 if invested else 0.0

    return {
        "name": holding["name"],
        "qty": holding["qty"],
        "avg_price": round(holding["avg_price"], 2),
        "last_price": last,
        "invested": round(invested, 2),
        "current_value": round(current, 2),
        "pnl": round(pnl, 2),
        "pnl_pct": round(pnl_pct, 2),
        "day_change_pct": q["change_pct"],
    }


def get_portfolio_data() -> dict[str, Any]:
    """Return the full enriched portfolio + totals."""
    rows = [_enrich(h) for h in MOCK_HOLDINGS]
    valid = [r for r in rows if "error" not in r]

    invested = sum(r["invested"] for r in valid)
    current = sum(r["current_value"] for r in valid)
    pnl = current - invested
    pnl_pct = (pnl / invested) * 100 if invested else 0.0

    return {
        "holdings": rows,
        "totals": {
            "invested": round(invested, 2),
            "current_value": round(current, 2),
            "pnl": round(pnl, 2),
            "pnl_pct": round(pnl_pct, 2),
        },
        "note": "This is mocked demo data, not a real portfolio.",
    }


def get_position_data(symbol: str) -> dict[str, Any]:
    """Return P&L for a single named holding."""
    ticker = resolve_symbol(symbol)
    if not ticker:
        return {"error": f"I don't recognise {symbol!r}."}

    for h in MOCK_HOLDINGS:
        if h["ticker"] == ticker:
            return _enrich(h)

    return {
        "error": (
            f"You don't hold {symbol} in this demo portfolio. "
            f"Holdings are: {', '.join(h['name'] for h in MOCK_HOLDINGS)}."
        )
    }
