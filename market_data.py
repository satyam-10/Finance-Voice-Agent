"""
Market data tools — backed by yfinance (free, no API key).

Indian tickers on Yahoo Finance:
  - NSE equities use the .NS suffix (e.g. RELIANCE.NS)
  - Indices use a ^ prefix (e.g. ^NSEI = Nifty 50, ^BSESN = Sensex)

Quotes are delayed by ~15 minutes — that's a Yahoo limitation. Fine for a demo.
"""

from __future__ import annotations

import logging
from typing import Any

import yfinance as yf

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Symbol resolution: turn natural-language names into Yahoo tickers.
# Add more as needed — this covers the most-asked names in a demo.
# ---------------------------------------------------------------------------

INDEX_MAP = {
    "nifty": "^NSEI",
    "nifty 50": "^NSEI",
    "nifty50": "^NSEI",
    "sensex": "^BSESN",
    "bse": "^BSESN",
    "bank nifty": "^NSEBANK",
    "banknifty": "^NSEBANK",
    "nifty bank": "^NSEBANK",
    "nifty it": "^CNXIT",
    "nifty auto": "^CNXAUTO",
    "nifty pharma": "^CNXPHARMA",
    "nifty fmcg": "^CNXFMCG",
    "nifty energy": "^CNXENERGY",
}

STOCK_MAP = {
    # Top names — extend freely
    "reliance": "RELIANCE.NS",
    "ril": "RELIANCE.NS",
    "tcs": "TCS.NS",
    "tata consultancy": "TCS.NS",
    "infosys": "INFY.NS",
    "infy": "INFY.NS",
    "hdfc bank": "HDFCBANK.NS",
    "hdfcbank": "HDFCBANK.NS",
    "hdfc amc": "HDFCAMC.NS",
    "icici bank": "ICICIBANK.NS",
    "icici": "ICICIBANK.NS",
    "sbi": "SBIN.NS",
    "state bank": "SBIN.NS",
    "axis bank": "AXISBANK.NS",
    "axis": "AXISBANK.NS",
    "kotak bank": "KOTAKBANK.NS",
    "kotak": "KOTAKBANK.NS",
    "itc": "ITC.NS",
    "hul": "HINDUNILVR.NS",
    "hindustan unilever": "HINDUNILVR.NS",
    "lt": "LT.NS",
    "l and t": "LT.NS",
    "larsen": "LT.NS",
    "bharti airtel": "BHARTIARTL.NS",
    "airtel": "BHARTIARTL.NS",
    "bajaj finance": "BAJFINANCE.NS",
    "bajfinance": "BAJFINANCE.NS",
    "asian paints": "ASIANPAINT.NS",
    "maruti": "MARUTI.NS",
    "maruti suzuki": "MARUTI.NS",
    "wipro": "WIPRO.NS",
    "tech mahindra": "TECHM.NS",
    "techm": "TECHM.NS",
    "hcl": "HCLTECH.NS",
    "hcl tech": "HCLTECH.NS",
    "tata motors": "TATAMOTORS.NS",
    "tata steel": "TATASTEEL.NS",
    "ongc": "ONGC.NS",
    "ntpc": "NTPC.NS",
    "powergrid": "POWERGRID.NS",
    "coal india": "COALINDIA.NS",
    "sun pharma": "SUNPHARMA.NS",
    "dr reddy": "DRREDDY.NS",
    "cipla": "CIPLA.NS",
    "nestle": "NESTLEIND.NS",
    "titan": "TITAN.NS",
    "ultratech": "ULTRACEMCO.NS",
    "adani enterprises": "ADANIENT.NS",
    "adani ports": "ADANIPORTS.NS",
    "jsw steel": "JSWSTEEL.NS",
    "grasim": "GRASIM.NS",
    "m and m": "M&M.NS",
    "mahindra": "M&M.NS",
    "indusind bank": "INDUSINDBK.NS",
    "indusind": "INDUSINDBK.NS",
}

# A representative basket per sector. For a demo this is plenty —
# real production would pull index constituents dynamically.
SECTOR_CONSTITUENTS = {
    "it": ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS"],
    "bank": [
        "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS",
        "AXISBANK.NS", "KOTAKBANK.NS", "INDUSINDBK.NS",
    ],
    "auto": ["MARUTI.NS", "TATAMOTORS.NS", "M&M.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS"],
    "pharma": ["SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS"],
    "fmcg": ["HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS", "BRITANNIA.NS"],
    "energy": ["RELIANCE.NS", "ONGC.NS", "NTPC.NS", "POWERGRID.NS", "COALINDIA.NS"],
}

SECTOR_ALIASES = {
    "tech": "it", "technology": "it", "software": "it", "it": "it",
    "banks": "bank", "banking": "bank", "bank": "bank", "financial": "bank",
    "cars": "auto", "automobile": "auto", "automotive": "auto", "auto": "auto",
    "drugs": "pharma", "pharmaceutical": "pharma", "pharma": "pharma",
    "consumer": "fmcg", "fmcg": "fmcg",
    "oil": "energy", "power": "energy", "energy": "energy",
}


def resolve_symbol(name: str) -> str | None:
    """Map a user-spoken name to a Yahoo ticker. None if not recognized."""
    if not name:
        return None
    key = name.strip().lower()
    if key in INDEX_MAP:
        return INDEX_MAP[key]
    if key in STOCK_MAP:
        return STOCK_MAP[key]
    # Last resort: assume the user said the actual ticker
    upper = name.strip().upper()
    if upper.startswith("^") or "." in upper:
        return upper
    return f"{upper}.NS"


# ---------------------------------------------------------------------------
# Core fetch helpers
# ---------------------------------------------------------------------------

def _fetch_quote(ticker: str) -> dict[str, Any] | None:
    """Pull a single quote from yfinance. Returns None on failure."""
    try:
        t = yf.Ticker(ticker)
        # fast_info is much faster than .info — perfect for voice latency
        fi = t.fast_info
        last = float(fi["last_price"])
        prev = float(fi["previous_close"])
        change = last - prev
        change_pct = (change / prev) * 100 if prev else 0.0
        return {
            "ticker": ticker,
            "last_price": round(last, 2),
            "previous_close": round(prev, 2),
            "change": round(change, 2),
            "change_pct": round(change_pct, 2),
            "day_high": round(float(fi.get("day_high") or 0), 2),
            "day_low": round(float(fi.get("day_low") or 0), 2),
            "currency": fi.get("currency", "INR"),
        }
    except Exception as e:
        logger.warning(f"yfinance fetch failed for {ticker}: {e}")
        return None


# ---------------------------------------------------------------------------
# Public tool implementations (called from agent.py)
# ---------------------------------------------------------------------------

def get_quote_data(symbol: str) -> dict[str, Any]:
    """Resolve a name and return a quote, or an error dict."""
    ticker = resolve_symbol(symbol)
    if not ticker:
        return {"error": f"I don't recognise {symbol!r}. Could you say it differently?"}

    data = _fetch_quote(ticker)
    if data is None:
        return {"error": f"I couldn't fetch a quote for {symbol} right now."}

    data["name"] = symbol
    data["delayed_minutes"] = 15
    return data


def get_market_overview_data() -> dict[str, Any]:
    """Return Nifty/Sensex/Bank Nifty + top gainers and losers from NIFTY 50 basket."""
    indices: dict[str, Any] = {}
    for label, ticker in [
        ("Nifty 50", "^NSEI"),
        ("Sensex", "^BSESN"),
        ("Bank Nifty", "^NSEBANK"),
    ]:
        q = _fetch_quote(ticker)
        if q:
            indices[label] = {
                "last": q["last_price"],
                "change": q["change"],
                "change_pct": q["change_pct"],
            }

    # Use the IT + Bank + Auto + FMCG baskets as a stand-in "watchlist" to
    # compute movers. Cheap, fast, good enough for a demo.
    basket = list({
        s
        for sector_list in SECTOR_CONSTITUENTS.values()
        for s in sector_list
    })
    movers: list[dict[str, Any]] = []
    for ticker in basket:
        q = _fetch_quote(ticker)
        if q:
            movers.append({
                "ticker": ticker.replace(".NS", ""),
                "last": q["last_price"],
                "change_pct": q["change_pct"],
            })

    movers.sort(key=lambda m: m["change_pct"], reverse=True)
    gainers = movers[:3]
    losers = movers[-3:][::-1]

    return {
        "indices": indices,
        "top_gainers": gainers,
        "top_losers": losers,
        "delayed_minutes": 15,
    }


def get_sector_movers_data(sector: str) -> dict[str, Any]:
    """Return movers within a sector basket."""
    key = SECTOR_ALIASES.get(sector.strip().lower())
    if not key:
        return {
            "error": (
                f"I don't have a basket for {sector!r}. Try IT, Bank, Auto, "
                f"Pharma, FMCG, or Energy."
            )
        }

    tickers = SECTOR_CONSTITUENTS[key]
    rows: list[dict[str, Any]] = []
    for ticker in tickers:
        q = _fetch_quote(ticker)
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
