"""
India Market Intelligence Agent — ChatGPT Edition
==================================================
Uses OpenAI GPT-4o + built-in web search tool to analyze
global & Indian market news and suggest NSE/BSE stocks/sectors.

GPT-4o has a native web_search_preview tool for real-time news.

Run modes:
  python agent.py                         → single on-demand analysis
  python agent.py --loop                  → continuous loop (every 15 min)
  python agent.py --loop --interval 30    → loop every 30 minutes
  python agent.py --risk aggressive       → change risk profile
"""

import os
import json
import time
import argparse
import sys
from datetime import datetime
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.rule import Rule
from rich import box
from rich.columns import Columns

console = Console()

# ── OpenAI client ──────────────────────────────────────────────────────────────
def get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        console.print(Panel(
            "[red]OPENAI_API_KEY not set.[/red]\n\n"
            "Get your key at [bold]https://platform.openai.com/api-keys[/bold]\n\n"
            "Then run:\n"
            "  [bold]export OPENAI_API_KEY='sk-...'[/bold]   (Mac/Linux)\n"
            "  [bold]set OPENAI_API_KEY=sk-...[/bold]         (Windows CMD)",
            title="Missing API Key",
            border_style="red"
        ))
        sys.exit(1)
    return OpenAI(api_key=api_key)


# ── Prompts ────────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert Indian stock market analyst with deep knowledge of NSE and BSE markets.
You have access to live web search. Use it extensively to get the LATEST news right now.

You monitor:
- Global macro: US Fed, US markets, China, Europe, crude oil, DXY, gold, commodities
- Indian macro: RBI policy, government spending, inflation (CPI/WPI), GST collections, IIP data
- FII/DII flows into Indian equities
- Sector rotation, earnings, M&A, regulatory changes on NSE/BSE
- Geopolitical events impacting risk sentiment and commodities

Your job:
1. Search and read the latest global + Indian market news RIGHT NOW
2. Identify sector and stock opportunities on NSE/BSE driven by current news
3. Give smart, specific, data-backed investment suggestions

STRICT RULES:
- Suggest ONLY NSE/BSE listed stocks (use NSE symbols)
- Every suggestion must be tied to a specific current event or data point
- Cover at minimum 5 sectors and 6 stock suggestions
- Be specific, timely, and actionable

OUTPUT FORMAT:
Respond ONLY in valid JSON. No markdown. No backticks. No explanation outside JSON.
Use exactly this structure:

{
  "timestamp": "<ISO 8601 datetime>",
  "global_triggers": [
    {
      "event": "<what happened globally>",
      "impact_on_india": "<how this hits Indian equities>",
      "sentiment": "positive|negative|neutral"
    }
  ],
  "domestic_triggers": [
    {
      "event": "<India-specific news>",
      "impact": "<market impact>",
      "sentiment": "positive|negative|neutral"
    }
  ],
  "market_mood": {
    "overall": "bullish|bearish|neutral",
    "nifty_outlook": "<brief NIFTY50 outlook this session/week>",
    "key_risk": "<biggest macro or market risk right now>",
    "confidence": "high|medium|low"
  },
  "sector_calls": [
    {
      "sector": "<sector name>",
      "call": "overweight|underweight|neutral",
      "reason": "<reason tied directly to current news>",
      "top_pick": "<NSE_SYMBOL>"
    }
  ],
  "stock_suggestions": [
    {
      "symbol": "<NSE_SYMBOL>",
      "company": "<Full Company Name>",
      "action": "buy|watch|avoid",
      "timeframe": "intraday|short-term|medium-term",
      "trigger": "<specific news or event driving this call>",
      "risk": "<key downside risk for this pick>"
    }
  ],
  "indices_watch": {
    "NIFTY50": "<brief comment>",
    "BANKNIFTY": "<brief comment>",
    "NIFTYMIDCAP": "<brief comment>",
    "NIFTYIT": "<brief comment>"
  },
  "fii_dii_signal": "<brief summary of FII/DII flows and what it signals>",
  "summary": "<2-3 sentence executive summary of the overall market picture right now>"
}"""


def get_user_prompt(risk_profile: str) -> str:
    now = datetime.now()
    return f"""Today is {now.strftime('%A, %B %d, %Y')} at {now.strftime('%I:%M %p IST')}.
Risk appetite: {risk_profile}.

Search the web RIGHT NOW for the following and then give your full analysis:

GLOBAL:
- US stock market latest — S&P 500, NASDAQ, Dow levels and direction today
- US Fed — any recent statements, rate decisions, or minutes
- Crude oil price (Brent + WTI) — current level and recent trend
- Dollar Index (DXY) — current level and direction
- Gold price — current level
- China economic news — PMI, stimulus, property sector, trade tensions
- Any major geopolitical event (Middle East, Russia, US-China tariffs)
- Asian markets today — Nikkei, Hang Seng, SGX Nifty

INDIA:
- NIFTY50 and SENSEX — current performance today
- RBI — any recent announcements, rate decisions, or governor statements
- FII and DII net buy/sell data — most recent available
- India inflation data (CPI/WPI) — latest reading
- India GDP or IIP data if recent
- Government policy news — PLI schemes, infrastructure, defence, divestment
- Top NSE/BSE gainers and losers today
- Major corporate results, earnings surprises, or guidance changes
- Any sector-specific news — banking, IT, pharma, auto, metals, FMCG, energy, realty

After your research, give me your complete investment analysis and NSE stock suggestions."""


# ── Core analysis runner ───────────────────────────────────────────────────────
def run_analysis(risk_profile: str = "moderate") -> dict | None:
    client = get_client()

    console.print()
    console.rule("[bold cyan]India Market Intelligence Agent  •  ChatGPT Edition[/bold cyan]")
    console.print(f"  [dim]Run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}[/dim]")
    console.print(f"  [dim]Model: gpt-4o  |  Risk profile: {risk_profile}  |  Live search: ON[/dim]")
    console.print()

    with console.status("[cyan]GPT-4o searching live market data...[/cyan]", spinner="dots") as status:
        try:
            # GPT-4o with web_search_preview tool for real-time news
            response = client.responses.create(
                model="gpt-4o",
                tools=[{"type": "web_search_preview"}],
                instructions=SYSTEM_PROMPT,
                input=get_user_prompt(risk_profile),
            )
            status.update("[cyan]Analyzing market data...[/cyan]")

            # Extract text from the response output
            full_response = ""
            for block in response.output:
                if hasattr(block, "type") and block.type == "message":
                    for content in block.content:
                        if hasattr(content, "type") and content.type == "output_text":
                            full_response += content.text

        except Exception as e:
            err = str(e)
            if "authentication" in err.lower() or "api key" in err.lower() or "401" in err:
                console.print("[red]Authentication failed. Check your OPENAI_API_KEY.[/red]")
            elif "connection" in err.lower() or "timeout" in err.lower():
                console.print("[red]Connection error. Check your internet.[/red]")
            elif "quota" in err.lower() or "billing" in err.lower() or "429" in err:
                console.print("[red]Quota exceeded or billing issue. Check https://platform.openai.com[/red]")
            elif "model" in err.lower():
                console.print(f"[red]Model error: {err}[/red]")
            else:
                console.print(f"[red]API error: {err}[/red]")
            return None

    # ── Parse JSON ────────────────────────────────────────────────────────────
    clean = full_response.strip()
    if "```" in clean:
        parts = clean.split("```")
        for part in parts:
            candidate = part.strip()
            if candidate.startswith("json"):
                candidate = candidate[4:].strip()
            if candidate.startswith("{"):
                clean = candidate
                break
    start = clean.find("{")
    end   = clean.rfind("}") + 1
    if start != -1 and end > start:
        clean = clean[start:end]

    try:
        data = json.loads(clean)
        display_analysis(data)
        save_to_log(data)
        return data
    except json.JSONDecodeError as e:
        console.print(f"[red]JSON parse error: {e}[/red]")
        console.print("[dim]Raw response (first 600 chars):[/dim]")
        console.print(full_response[:600])
        return None


# ── Display helpers ────────────────────────────────────────────────────────────
def sentiment_color(s: str) -> str:
    return {"positive": "green", "negative": "red", "neutral": "yellow"}.get(s.lower(), "white")


def action_color(a: str) -> str:
    return {
        "buy": "bold green", "watch": "bold yellow", "avoid": "bold red",
        "overweight": "bold green", "underweight": "bold red", "neutral": "yellow",
        "bullish": "bold green", "bearish": "bold red"
    }.get(a.lower(), "white")


def display_analysis(data: dict):
    # ── Market Overview ────────────────────────────────────────────────────────
    mood       = data.get("market_mood", {})
    overall    = mood.get("overall", "neutral").upper()
    confidence = mood.get("confidence", "medium")
    mc         = action_color(mood.get("overall", "neutral"))

    console.print(Panel(
        f"[{mc}]{overall}[/{mc}]  [dim]|[/dim]  Confidence: [bold]{confidence.upper()}[/bold]\n\n"
        f"[italic]{data.get('summary', '')}[/italic]\n\n"
        f"[dim]NIFTY50 outlook:[/dim]  {mood.get('nifty_outlook', '')}\n"
        f"[dim]Key risk:[/dim]         [yellow]{mood.get('key_risk', '')}[/yellow]",
        title="[bold]Market Overview[/bold]",
        border_style="cyan",
        padding=(1, 2)
    ))

    # ── Global Triggers ────────────────────────────────────────────────────────
    if data.get("global_triggers"):
        console.print(Rule("[bold]Global Triggers[/bold]"))
        t = Table(show_header=True, header_style="bold dim", box=box.SIMPLE, expand=True)
        t.add_column("Event", ratio=4)
        t.add_column("Impact on India", ratio=4)
        t.add_column("Sentiment", ratio=1, justify="center")
        for g in data["global_triggers"]:
            s = g.get("sentiment", "neutral")
            t.add_row(
                g.get("event", ""),
                g.get("impact_on_india", ""),
                f"[{sentiment_color(s)}]{s.upper()}[/{sentiment_color(s)}]"
            )
        console.print(t)

    # ── Domestic Triggers ─────────────────────────────────────────────────────
    if data.get("domestic_triggers"):
        console.print(Rule("[bold]India Domestic Triggers[/bold]"))
        t = Table(show_header=True, header_style="bold dim", box=box.SIMPLE, expand=True)
        t.add_column("Event", ratio=5)
        t.add_column("Market Impact", ratio=4)
        t.add_column("Sentiment", ratio=1, justify="center")
        for d in data["domestic_triggers"]:
            s = d.get("sentiment", "neutral")
            t.add_row(
                d.get("event", ""),
                d.get("impact", ""),
                f"[{sentiment_color(s)}]{s.upper()}[/{sentiment_color(s)}]"
            )
        console.print(t)

    # ── Sector Calls ──────────────────────────────────────────────────────────
    if data.get("sector_calls"):
        console.print(Rule("[bold]Sector Calls[/bold]"))
        t = Table(show_header=True, header_style="bold dim", box=box.SIMPLE, expand=True)
        t.add_column("Sector",   ratio=2)
        t.add_column("Call",     ratio=1, justify="center")
        t.add_column("Reason",   ratio=5)
        t.add_column("Top Pick", ratio=1, justify="center")
        for s in data["sector_calls"]:
            call = s.get("call", "neutral")
            c = action_color(call)
            t.add_row(
                s.get("sector", ""),
                f"[{c}]{call.upper()}[/{c}]",
                s.get("reason", ""),
                f"[bold cyan]{s.get('top_pick', '')}[/bold cyan]"
            )
        console.print(t)

    # ── Stock Suggestions ─────────────────────────────────────────────────────
    if data.get("stock_suggestions"):
        console.print(Rule("[bold]Stock Suggestions (NSE)[/bold]"))
        t = Table(show_header=True, header_style="bold dim", box=box.SIMPLE, expand=True)
        t.add_column("Symbol",    ratio=1)
        t.add_column("Company",   ratio=2)
        t.add_column("Action",    ratio=1, justify="center")
        t.add_column("Timeframe", ratio=1, justify="center")
        t.add_column("Trigger",   ratio=4)
        t.add_column("Risk",      ratio=3)
        for s in data["stock_suggestions"]:
            action = s.get("action", "watch")
            ac = action_color(action)
            t.add_row(
                f"[bold cyan]{s.get('symbol', '')}[/bold cyan]",
                s.get("company", ""),
                f"[{ac}]{action.upper()}[/{ac}]",
                f"[dim]{s.get('timeframe', '')}[/dim]",
                s.get("trigger", ""),
                f"[yellow]{s.get('risk', '')}[/yellow]"
            )
        console.print(t)

    # ── Indices Watch ─────────────────────────────────────────────────────────
    console.print(Rule("[bold]Indices & FII/DII[/bold]"))
    indices = data.get("indices_watch", {})
    if indices:
        idx_panels = [
            Panel(f"[dim]{comment}[/dim]", title=f"[bold cyan]{idx}[/bold cyan]", border_style="dim")
            for idx, comment in indices.items()
        ]
        console.print(Columns(idx_panels))

    fii_dii = data.get("fii_dii_signal", "")
    if fii_dii:
        console.print(Panel(fii_dii, title="[bold]FII/DII Signal[/bold]", border_style="dim", padding=(0, 2)))

    console.print()
    console.print(
        "[dim]⚠  DISCLAIMER: AI-generated analysis for educational purposes only. "
        "Not SEBI-registered investment advice. Consult a qualified financial advisor.[/dim]"
    )
    console.print()


def save_to_log(data: dict):
    log_file = "market_analysis_log.jsonl"
    with open(log_file, "a") as f:
        f.write(json.dumps(data) + "\n")
    console.print(f"[dim]Saved to {log_file}[/dim]")


# ── Continuous loop ────────────────────────────────────────────────────────────
def run_loop(interval_minutes: int = 15, risk_profile: str = "moderate"):
    console.print(Panel(
        f"[bold green]Auto-refresh every {interval_minutes} minutes[/bold green]\n"
        "Press [bold]Ctrl+C[/bold] to stop.",
        title="Continuous Mode",
        border_style="green"
    ))
    run_count = 0
    while True:
        run_count += 1
        console.print(f"\n[bold cyan]── Run #{run_count} ──────────────────────────────────────[/bold cyan]")
        run_analysis(risk_profile)
        console.print(f"\n[dim]Next analysis in {interval_minutes} minutes. Press Ctrl+C to stop.[/dim]")
        try:
            for remaining in range(interval_minutes * 60, 0, -1):
                mins, secs = divmod(remaining, 60)
                sys.stdout.write(f"\r  Next run in: {mins:02d}:{secs:02d}   ")
                sys.stdout.flush()
                time.sleep(1)
            print()
        except KeyboardInterrupt:
            console.print("\n[yellow]Stopped by user.[/yellow]")
            break


# ── Entry point ────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="India Market Intelligence Agent (ChatGPT Edition) — NSE/BSE suggestions via OpenAI"
    )
    parser.add_argument("--loop",     action="store_true", help="Run continuously")
    parser.add_argument("--interval", type=int, default=15,
                        help="Minutes between runs in loop mode (default: 15)")
    parser.add_argument("--risk",     choices=["conservative", "moderate", "aggressive"],
                        default="moderate", help="Risk appetite (default: moderate)")
    args = parser.parse_args()

    console.print(Panel(
        "[bold]India Market Intelligence Agent[/bold]\n"
        "[dim]Powered by OpenAI GPT-4o + Native Web Search[/dim]\n\n"
        "Analyzes global + Indian market news in real time\n"
        "and suggests NSE/BSE stocks & sectors to invest in.",
        border_style="cyan",
        padding=(1, 4)
    ))

    if args.loop:
        run_loop(interval_minutes=args.interval, risk_profile=args.risk)
    else:
        run_analysis(risk_profile=args.risk)


if __name__ == "__main__":
    main()
