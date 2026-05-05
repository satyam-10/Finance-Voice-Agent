"""
Mocked portfolio holdings — pure data, no logic.

Edit this list to personalize the demo. Each holding is combined with
a live price at runtime to produce realistic P&L.

For a real product: replace this with a call to your broker API,
your database, or your portfolio service.
"""

from typing import TypedDict


class Holding(TypedDict):
    name: str       # What the user calls it ("Reliance", "HDFC Bank")
    ticker: str     # Yahoo Finance ticker ("RELIANCE.NS")
    qty: int        # Number of shares held
    avg_price: float  # Average buy price in INR


MOCK_HOLDINGS: list[Holding] = [
    {"name": "Reliance",  "ticker": "RELIANCE.NS", "qty": 10, "avg_price": 2_350.00},
    {"name": "TCS",       "ticker": "TCS.NS",      "qty": 5,  "avg_price": 3_800.00},
    {"name": "HDFC Bank", "ticker": "HDFCBANK.NS", "qty": 25, "avg_price": 1_550.00},
    {"name": "Infosys",   "ticker": "INFY.NS",     "qty": 15, "avg_price": 1_420.00},
    {"name": "ITC",       "ticker": "ITC.NS",      "qty": 50, "avg_price": 410.00},
]
