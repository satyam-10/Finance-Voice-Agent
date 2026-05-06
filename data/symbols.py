"""
Symbol resolution data — pure dictionaries, no logic.

Add new stocks/indices here. Nothing in this file imports from the rest
of the project, so it's safe to edit freely.

Indian tickers on Yahoo Finance:
  - NSE equities use the .NS suffix (e.g. RELIANCE.NS)
  - Indices use a ^ prefix (e.g. ^NSEI = Nifty 50, ^BSESN = Sensex)
"""

INDEX_MAP: dict[str, str] = {
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

STOCK_MAP: dict[str, str] = {
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

# Representative basket per sector. For a demo this is plenty —
# real production would pull index constituents dynamically.
SECTOR_CONSTITUENTS: dict[str, list[str]] = {
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

# What the user might say -> canonical sector key in SECTOR_CONSTITUENTS.
SECTOR_ALIASES: dict[str, str] = {
    "tech": "it", "technology": "it", "software": "it", "it": "it",
    "banks": "bank", "banking": "bank", "bank": "bank", "financial": "bank",
    "cars": "auto", "automobile": "auto", "automotive": "auto", "auto": "auto",
    "drugs": "pharma", "pharmaceutical": "pharma", "pharma": "pharma",
    "consumer": "fmcg", "fmcg": "fmcg",
    "oil": "energy", "power": "energy", "energy": "energy",
}


def resolve_symbol(name: str) -> str | None:
    """Map a user-spoken name to a Yahoo ticker. None if unrecognizable.

    This is pure lookup logic — no network, no side effects. Lives here
    because it only depends on the maps above.
    """
    if not name:
        return None
    key = name.strip().lower()
    if key in INDEX_MAP:
        return INDEX_MAP[key]
    if key in STOCK_MAP:
        return STOCK_MAP[key]
    upper = name.strip().upper()
    if upper.startswith("^") or "." in upper:
        return upper
    return f"{upper}.NS"
