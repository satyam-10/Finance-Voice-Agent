# Indian Markets Voice Agent

A free, browser-based voice agent that answers questions about Indian equity markets — live quotes, market movers, and a mocked portfolio. Built on LiveKit Agents with Google Gemini Live (single multimodal model for speech-in and speech-out) and yfinance for market data.

> ⚠️ **Demo only.** This is for information / prototyping. It is not investment advice. Quotes are delayed by ~15 minutes. Do not deploy to real users without SEBI Investment Adviser / Research Analyst registration.

## What it does

You click a link, allow microphone access, and have a natural conversation:

- *"How is Reliance trading today?"*
- *"What's Nifty at?"*
- *"How are markets doing?"*
- *"Show me my portfolio."*
- *"How is my Infosys position?"*
- *"How's the IT sector today?"*

The agent politely refuses trade recommendations and order placement.

## Stack

| Layer | Choice | Cost |
|---|---|---|
| Voice orchestration + browser link | LiveKit Cloud (free tier) | Free, ~50 min/month |
| Speech-in + LLM + speech-out | Google Gemini 2.0 Flash Live | Free tier on AI Studio |
| Market data | yfinance (NSE tickers, ~15min delayed) | Free, no key |
| Portfolio | Hardcoded mock + live prices | Free |

Everything runs on your laptop. No phone number, no Twilio, no credit card.

## Project layout

```
markets-voice-agent/
├── agent.py              # The agent: instructions + tool definitions + entrypoint
├── tools/
│   ├── market_data.py    # Symbol resolution + yfinance quote/overview/sector
│   └── portfolio.py      # Mocked holdings, enriched with live prices
├── smoke_test.py         # Test the data tools without spinning up the agent
├── requirements.txt
├── .env.example          # Copy to .env, fill in keys
└── README.md
```

## Setup (5 minutes)

### 1. Get the two API keys

**LiveKit Cloud** — sign up at https://cloud.livekit.io. Create a project. Open the project, go to **Settings → Keys**, and copy the WebSocket URL, API Key, and API Secret.

**Google Gemini** — go to https://aistudio.google.com/app/apikey, click "Create API key", copy it.

### 2. Install

Requires Python 3.10+.

```bash
git clone <this-folder>  # or just cd into it
cd markets-voice-agent

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

Download the Silero VAD model (one-time, ~30 MB):

```bash
python agent.py download-files
```

### 3. Configure

```bash
cp .env.example .env
```

Then open `.env` and paste in your four values: `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`, `GOOGLE_API_KEY`.

### 4. Verify market data works

Before fighting with audio, make sure the data layer is healthy:

```bash
python smoke_test.py
```

You should see quotes for Reliance, Nifty levels, top movers, and a portfolio with realistic numbers. If yfinance fails, you'll see it here — that usually means a network issue or a temporarily-rate-limited Yahoo endpoint.

### 5. Talk to it

The simplest way — your laptop's mic and speakers, no browser:

```bash
python agent.py console
```

Or run it as a worker connected to LiveKit Cloud (recommended, lets you share a link):

```bash
python agent.py dev
```

Then open the **LiveKit Agents Playground** at https://agents-playground.livekit.io, connect using your project, and start the session. You'll be talking to the agent in your browser.

## Try saying

Things that work:

- "How's Reliance today?"
- "What's Nifty at right now?"
- "Give me a market overview."
- "How are banks doing?"
- "What's in my portfolio?"
- "How is my HDFC Bank position?"
- "Should I buy TCS?" → it will refuse politely.

Things that won't work yet (good places to extend):

- "Place an order for 10 shares of TCS." (intentionally refused)
- News / earnings dates (no news API wired up).
- Charts / technicals (out of scope for a voice demo).

## Customizing

**Add more stocks.** Open `tools/market_data.py`, add to `STOCK_MAP`:

```python
"paytm": "PAYTM.NS",
"zomato": "ZOMATO.NS",
```

**Change the mocked portfolio.** Edit `MOCK_HOLDINGS` in `tools/portfolio.py`.

**Different voice.** In `agent.py`, swap the `voice` parameter — Gemini Live offers `Aoede`, `Puck`, `Charon`, `Kore`, `Fenrir`. Each sounds noticeably different.

**Different personality.** Edit `SYSTEM_INSTRUCTIONS` in `agent.py`. Keep the refusal rules — they're what keep the demo defensible.

**Real-time (not delayed) data.** Swap yfinance for Zerodha Kite Connect (₹2,000/month, requires a Zerodha account) or Upstox API (free with an Upstox account). The function signatures in `tools/market_data.py` won't need to change — only the internals of `_fetch_quote`.

**Phone calls.** When you're ready, LiveKit's SIP integration plus a Twilio number lets you point a phone number at this same agent, no code changes.

## Troubleshooting

**"No module named livekit.plugins.google"** — `pip install -r requirements.txt` again, or install `livekit-agents[google]` directly.

**yfinance returns `None` for everything** — Yahoo occasionally rate-limits. Wait a minute and retry. Also check that you can reach `query1.finance.yahoo.com` from your network.

**The agent doesn't speak first** — your `GOOGLE_API_KEY` may be missing or invalid. Check the terminal logs from `python agent.py dev`.

**"Worker registered" but the playground can't find it** — make sure the `LIVEKIT_URL` in your `.env` matches the project you're connecting the playground to.

**Agent talks over me / cuts me off** — Gemini Live handles turn-taking automatically. If it's misbehaving, lower the model's `temperature` or try a different voice.

## What this demo intentionally avoids

- Storing real PII or KYC data. Don't put real account numbers in `MOCK_HOLDINGS`.
- Saying anything that sounds like investment advice. The system prompt enforces this.
- Real-time quotes. The 15-minute delay is acknowledged out loud when relevant.
- Order placement. Removing this would put you in regulated territory immediately.

## License

MIT. Use freely. Don't use it to give people financial advice.
