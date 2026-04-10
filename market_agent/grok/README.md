# India Market Intelligence Agent — Grok Edition

AI-powered agent using **xAI Grok** with native live web search.
Monitors global & Indian market news and suggests NSE/BSE stocks and sectors.

---

## Why Grok?

| Feature | Grok Edition | Claude Edition |
|---|---|---|
| AI model | xAI Grok-3 | Anthropic Claude |
| Live search | Native (built-in) | Tool-use based |
| API compatibility | OpenAI-compatible | Anthropic SDK |
| News freshness | Real-time (x.ai news) | Web search results |
| Key advantage | Deep X/Twitter news integration | Broader reasoning |

Grok has native access to X (Twitter) posts and news — useful for catching
breaking market news that may not be on traditional news sites yet.

---

## Setup

### 1. Get a Grok (xAI) API Key
- Sign up at **https://console.x.ai**
- Create an API key (starts with `xai-...`)

### 2. Set the API Key

**Mac/Linux:**
```bash
export XAI_API_KEY="xai-..."
```
Add to `~/.bashrc` or `~/.zshrc` to make permanent.

**Windows CMD:**
```cmd
set XAI_API_KEY=xai-...
```

**Windows PowerShell:**
```powershell
$env:XAI_API_KEY = "xai-..."
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

---

## Usage

```bash
# Single analysis
python agent.py

# Continuous loop every 15 min
python agent.py --loop

# Loop every 30 min
python agent.py --loop --interval 30

# With risk profile
python agent.py --risk aggressive
python agent.py --loop --interval 20 --risk conservative
```

---

## Output sections

| Section | What you get |
|---|---|
| Market Overview | Bullish/bearish/neutral mood, NIFTY outlook, key risk, confidence level |
| Global Triggers | US Fed, oil, DXY, China, geopolitics → India impact |
| India Domestic | RBI, FII/DII flows, policy, earnings, inflation |
| Sector Calls | Overweight/underweight/neutral + NSE top pick per sector |
| Stock Suggestions | NSE symbol, BUY/WATCH/AVOID, timeframe, trigger, downside risk |
| Indices Watch | NIFTY50, BANKNIFTY, NIFTYMIDCAP, NIFTYIT outlook |
| FII/DII Signal | Institutional flow interpretation |

---

## Log file

Each run is saved to `market_analysis_log.jsonl`. Read history with:

```python
import json
with open("market_analysis_log.jsonl") as f:
    runs = [json.loads(line) for line in f]
print(runs[-1]["summary"])  # latest run summary
```

---

## Disclaimer

For **educational and research purposes only**.
**Not SEBI-registered investment advice.**
Always consult a qualified financial advisor before investing.
