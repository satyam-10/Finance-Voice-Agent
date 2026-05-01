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

