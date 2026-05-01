# Indian Markets Voice Agent

A free, browser-based voice agent that answers questions about Indian equity markets — live quotes, market movers, and a mocked portfolio. Built on LiveKit Agents with Google Gemini Live and yfinance.

> ⚠️ **Demo only.** Not investment advice. Quotes delayed ~15 minutes. Don't deploy to real users without SEBI registration.

## Project layout

The codebase is organized in **layers**. Each layer only depends on the layers below it. This makes it easy to swap pieces (e.g. yfinance → Zerodha Kite) without rewrites.

```
markets-voice-agent/
│
├── agent.py                      # ENTRYPOINT — wires session and agent. Stays boring.
├── config.py                     # Voice, model, temperature — all knobs in one place.
├── prompts.py                    # System instructions and greeting — content, not code.
│
├── agents/
│   └── markets_agent.py          # MarketsAgent class. Tool methods are thin wrappers.
│
├── tools/                        # Orchestration: combine data + provider.
│   ├── market_data.py            # get_quote, get_market_overview, get_sector_movers
│   └── portfolio.py              # get_portfolio, get_position (mocked + live prices)
│
├── providers/                    # External services. ONE file per provider.
│   └── yfinance_provider.py      # The only file that imports yfinance.
│
├── data/                         # Pure data. No logic, no imports from project.
│   ├── symbols.py                # STOCK_MAP, INDEX_MAP, SECTOR_CONSTITUENTS, resolve_symbol
│   └── holdings.py               # MOCK_HOLDINGS — the demo portfolio.
│
├── smoke_test.py                 # Verify data layer works without the agent.
├── requirements.txt
└── .env.example                  # Copy to .env, fill in 4 values.
```

### The dependency direction (one-way)

```
agent.py
   │
   ▼
agents/markets_agent.py
   │
   ▼
tools/        (market_data, portfolio)
   │
   ▼
providers/    (yfinance_provider)
   │
   ▼
data/         (symbols, holdings)  ← imports nothing from the project
```

A higher layer can import from any lower layer. A lower layer **never** imports up. If you feel the urge to do so, there's probably a piece of shared logic that needs to move down.

## Where to make common changes

| You want to... | Edit this file |
|---|---|
| Try a different voice | `config.py` |
| Tweak the agent's personality / refusal rules | `prompts.py` |
| Add a new stock the user can ask about | `data/symbols.py` (`STOCK_MAP`) |
| Change the demo portfolio | `data/holdings.py` (`MOCK_HOLDINGS`) |
| Swap yfinance for Zerodha Kite | Write `providers/kite_provider.py`, change one import in `tools/` |
| Add a new tool (e.g. earnings dates) | Add a function in `tools/`, add a `@function_tool` method in `agents/markets_agent.py` |
| Change the greeting | `prompts.py` (`GREETING_INSTRUCTIONS`) |

## Setup

Requires Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python agent.py download-files     # one-time, downloads VAD model
cp .env.example .env               # then fill in your 4 keys
```

Get the keys:
- **LiveKit Cloud** — https://cloud.livekit.io → create project → Settings → Keys
- **Google Gemini** — https://aistudio.google.com/app/apikey

## Run

**Verify the data layer first:**
```bash
python smoke_test.py
```
You should see real prices for Reliance, Nifty, etc. If you see error dicts, that's a network or yfinance issue — easier to debug here than mid-call.

**Talk to it via terminal:**
```bash
python agent.py console
```

**Talk to it in a browser** (recommended — share-able link):
```bash
python agent.py dev
```
Then open https://agents-playground.livekit.io and connect your project.

## Try saying

- "How's Reliance today?"
- "What's Nifty at?"
- "Give me a market overview."
- "How are banks doing?"
- "What's in my portfolio?"
- "How's my HDFC Bank position?"
- "Should I buy TCS?" → it refuses politely.

## Adding a new tool — full walkthrough

Suppose you want to add a `get_52_week_range` tool.

**1. Add the data function** (in `tools/market_data.py`):
```python
def get_52_week_range_data(symbol: str) -> dict:
    ticker = resolve_symbol(symbol)
    if not ticker:
        return {"error": f"I don't recognise {symbol!r}."}
    # ... use fetch_quote or extend the provider
    return {"name": symbol, "high": ..., "low": ...}
```

**2. Expose it as a tool method** (in `agents/markets_agent.py`):
```python
from tools.market_data import get_52_week_range_data  # add to imports

@function_tool
async def get_52_week_range(self, symbol: str) -> dict:
    """Get the 52-week high and low for a stock.

    Args:
        symbol: The company name as the user said it.
    """
    return get_52_week_range_data(symbol)
```

That's it. No changes to `agent.py`, `config.py`, or `prompts.py` needed. (You may want to mention the new capability in the system prompt, but it's optional — the docstring is what the LLM uses to decide when to call the tool.)

## Swapping providers — full walkthrough

Suppose you want real-time data from Zerodha Kite instead of delayed yfinance.

**1. Write a new provider** (`providers/kite_provider.py`):
```python
from kiteconnect import KiteConnect
# ... auth setup ...

def fetch_quote(ticker: str) -> Quote | None:
    # call Kite, return the same Quote TypedDict shape
    ...
```

**2. Change one import** in `tools/market_data.py` and `tools/portfolio.py`:
```python
# from providers.yfinance_provider import fetch_quote
from providers.kite_provider import fetch_quote
```

Done. The rest of the codebase doesn't notice. *This* is what modular structure buys you.

## License

MIT. Don't use it to give people financial advice.
