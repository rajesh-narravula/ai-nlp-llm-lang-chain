# India Market Intelligence Agent — ChatGPT Edition

AI-powered agent using **OpenAI GPT-4o** with native web search (`web_search_preview`).
Monitors global & Indian market news and suggests NSE/BSE stocks and sectors.

---

## Why GPT-4o?

| Feature | ChatGPT Edition | Grok Edition | Claude Edition |
|---|---|---|---|
| AI model | GPT-4o | Grok-3 | Claude Opus |
| Live search | Native (Responses API) | Native (search_parameters) | Tool-use based |
| API | OpenAI Responses API | OpenAI-compatible | Anthropic SDK |
| Key advantage | Strongest reasoning + Bing news | X/Twitter real-time | Broadest web search |

GPT-4o uses the **Responses API** with `web_search_preview` — this is OpenAI's
latest search-grounded API, pulling from Bing News for fresh financial data.

---

## Setup

### 1. Get an OpenAI API Key
- Sign up at **https://platform.openai.com**
- Go to **API Keys** → Create new key (starts with `sk-...`)
- Make sure your account has **billing enabled** (web search requires credits)

### 2. Set the API Key

**Mac/Linux:**
```bash
export OPENAI_API_KEY="sk-..."
```
Add to `~/.bashrc` or `~/.zshrc` to make permanent.

**Windows CMD:**
```cmd
set OPENAI_API_KEY=sk-...
```

**Windows PowerShell:**
```powershell
$env:OPENAI_API_KEY = "sk-..."
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

---

## Usage

```bash
# Single on-demand analysis
python agent.py

# Continuous loop every 15 min (default)
python agent.py --loop

# Loop every 30 min
python agent.py --loop --interval 30

# With risk profile
python agent.py --risk aggressive
python agent.py --risk conservative
python agent.py --loop --interval 20 --risk moderate
```

---

## Output sections

| Section | What you get |
|---|---|
| Market Overview | Bullish/bearish/neutral mood, NIFTY outlook, key risk, confidence |
| Global Triggers | US Fed, oil, DXY, China, geopolitics → India impact |
| India Domestic | RBI, FII/DII flows, policy, earnings, inflation |
| Sector Calls | Overweight / Underweight / Neutral + NSE top pick per sector |
| Stock Suggestions | NSE symbol, BUY/WATCH/AVOID, timeframe, trigger, downside risk |
| Indices Watch | NIFTY50, BANKNIFTY, NIFTYMIDCAP, NIFTYIT outlook |
| FII/DII Signal | Institutional flow interpretation |

---

## Log file

Each run is appended to `market_analysis_log.jsonl`. Read it with:

```python
import json
with open("market_analysis_log.jsonl") as f:
    runs = [json.loads(line) for line in f]
print(runs[-1]["summary"])   # latest summary
print(runs[-1]["stock_suggestions"])  # latest stock picks
```

---

## API used

This agent uses OpenAI's **Responses API** (not the older Chat Completions API).
The `web_search_preview` tool is only available via `client.responses.create()`.

```python
response = client.responses.create(
    model="gpt-4o",
    tools=[{"type": "web_search_preview"}],
    instructions=SYSTEM_PROMPT,
    input=user_prompt,
)
```

---

## Disclaimer

For **educational and research purposes only**.
**Not SEBI-registered investment advice.**
Always consult a qualified financial advisor before investing.
