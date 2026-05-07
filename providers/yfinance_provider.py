"""
yfinance provider — the ONLY file in the project that imports yfinance.

If you swap to Zerodha Kite / Upstox / Angel One, write a new provider
here (e.g. kite_provider.py) that exposes the same `fetch_quote` function
signature, and the rest of the codebase won't need to change.

Public contract:
    fetch_quote(ticker: str) -> Quote | None

Quote is a TypedDict so callers know exactly what fields exist.
"""

from __future__ import annotations

import logging
from typing import TypedDict

import yfinance as yf

logger = logging.getLogger(__name__)


class Quote(TypedDict):
    ticker: str
    last_price: float
    previous_close: float
    change: float
    change_pct: float
    day_high: float
    day_low: float
    currency: str


def fetch_quote(ticker: str) -> Quote | None:
    """Pull a single quote from yfinance. Returns None on any failure."""
    res = fetch_quotes([ticker])
    return res.get(ticker)


def fetch_quotes(tickers: list[str]) -> dict[str, Quote]:
    """Pull multiple quotes from yfinance in batch.
    
    Returns a mapping of ticker -> Quote. If a ticker fails, it's omitted.
    Uses yf.Tickers for batching and fast_info for low latency.
    """
    if not tickers:
        return {}

    try:
        # yf.Tickers handles batching more efficiently than individual Ticker objects.
        ts = yf.Tickers(" ".join(tickers))
        results: dict[str, Quote] = {}

        for ticker in tickers:
            try:
                # Access individual ticker from the batch
                fi = ts.tickers[ticker].fast_info
                last = float(fi["last_price"])
                prev = float(fi["previous_close"])
                change = last - prev
                change_pct = (change / prev) * 100 if prev else 0.0
                
                results[ticker] = Quote(
                    ticker=ticker,
                    last_price=round(last, 2),
                    previous_close=round(prev, 2),
                    change=round(change, 2),
                    change_pct=round(change_pct, 2),
                    day_high=round(float(fi.get("day_high") or 0), 2),
                    day_low=round(float(fi.get("day_low") or 0), 2),
                    currency=fi.get("currency", "INR"),
                )
            except Exception as e:
                logger.warning(f"yfinance fetch failed for {ticker}: {e}")

        return results
    except Exception as e:
        logger.error(f"Global yfinance batch fetch failed: {e}")
        return {}
