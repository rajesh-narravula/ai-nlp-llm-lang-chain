# India Market Intelligence Agent

AI-powered agent that monitors global & Indian market news and suggests
NSE/BSE stocks and sectors to invest in — no manual stock input needed.

---

## What it does

- Searches the **live web** for global and Indian market news on every run
- Analyzes global triggers (US Fed, oil, DXY, China) and domestic triggers (RBI, FII/DII, policy)
- Gives **sector calls** (overweight/underweight/neutral) with NSE top picks
- Suggests **specific NSE stocks** with action (buy/watch/avoid), timeframe, trigger, and risk
- Tracks NIFTY50, BANKNIFTY, NIFTYMIDCAP, NIFTYIT outlook
- Saves every analysis to `market_analysis_log.jsonl` for history

---

## Setup

### 1. Install Python 3.9+
Make sure you have Python installed:
```bash
python --version
```

### 2. Get an Anthropic API Key
- Sign up at https://console.anthropic.com
- Create an API key

### 3. Set the API Key
**Mac/Linux:**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

Add this to your `~/.bashrc` or `~/.zshrc` to make it permanent.

**Windows (Command Prompt):**
```cmd
set ANTHROPIC_API_KEY=sk-ant-...
```

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-..."
```

### 4. Install dependencies
```bash
cd india_market_agent
pip install -r requirements.txt
```

---

## Usage

### Single on-demand analysis
```bash
python agent.py
```

### Continuous loop (every 15 minutes)
```bash
python agent.py --loop
```

### Continuous loop with custom interval (e.g., every 30 minutes)
```bash
python agent.py --loop --interval 30
```

### Set risk profile
```bash
python agent.py --risk conservative
python agent.py --risk moderate        # default
python agent.py --risk aggressive
```

### Combine options
```bash
python agent.py --loop --interval 20 --risk aggressive
```

---

## Output explained

| Section | What it shows |
|---|---|
| **Market Overview** | Overall bullish/bearish/neutral mood, NIFTY outlook, key risk |
| **Global Triggers** | US/China/oil/DXY events and their impact on India |
| **India Domestic Triggers** | RBI, policy, FII data, earnings |
| **Sector Calls** | Overweight/underweight sectors with NSE top pick per sector |
| **Stock Suggestions** | Specific NSE symbols with action, timeframe, trigger, risk |
| **Indices Watch** | NIFTY50, BANKNIFTY, NIFTYMIDCAP, NIFTYIT brief outlook |
| **FII/DII Signal** | Foreign/domestic institutional flow interpretation |

---

## Log file

Every run is saved to `market_analysis_log.jsonl` in the same folder.
Each line is a complete JSON analysis. You can parse it with:

```python
import json
with open("market_analysis_log.jsonl") as f:
    runs = [json.loads(line) for line in f]
```

---

## Disclaimer

This tool is for **educational and research purposes only**.
It is **not SEBI-registered investment advice**.
Always consult a qualified financial advisor before making investment decisions.

---

## Cost estimate

Each run makes ~8-12 web searches and one Claude API call (~3000-4000 tokens).
Approximate cost per run: **$0.02 - $0.05** depending on Claude model pricing.
