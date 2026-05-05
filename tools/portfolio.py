"""
Portfolio tools — combine static holdings with live prices to produce P&L.

For a real product: replace MOCK_HOLDINGS in data/holdings.py with a
broker integration (Zerodha Console / Kite holdings API) or a database
query, and these functions will keep working unchanged.
"""

from __future__ import annotations

from typing import Any

from data.holdings import MOCK_HOLDINGS, Holding
from data.symbols import resolve_symbol
from providers.yfinance_provider import fetch_quote


def _enrich(holding: Holding) -> dict[str, Any]:
    """Combine a static holding with a live quote to produce P&L."""
    q = fetch_quote(holding["ticker"])
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
