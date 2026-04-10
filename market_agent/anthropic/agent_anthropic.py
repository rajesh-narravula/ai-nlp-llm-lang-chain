"""
India Market Intelligence Agent
================================
Uses Claude AI + web search to analyze global & Indian market news
and suggest NSE/BSE stocks/sectors to invest in.

Run modes:
  python agent.py           → single on-demand analysis
  python agent.py --loop    → continuous loop (every N minutes)
  python agent.py --loop --interval 30  → loop every 30 minutes
"""

import anthropic
import json
import time
import argparse
import sys
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.rule import Rule
from rich import box
from rich.live import Live
from rich.spinner import Spinner
from rich.columns import Columns
from rich.padding import Padding

console = Console()

SYSTEM_PROMPT = """You are an expert Indian stock market analyst with deep knowledge of NSE and BSE markets.
You monitor global macroeconomic events, geopolitical developments, FII/DII flows, RBI policy, commodity prices,
currency movements, US Fed decisions, and their impact on Indian equities.

Your job is to:
1. Search and analyze the LATEST global and Indian market news RIGHT NOW
2. Identify which sectors and stocks on NSE/BSE are likely to benefit or suffer
3. Give smart, timely investment suggestions purely based on current affairs

RULES:
- Focus ONLY on Indian stock market (NSE/BSE listed stocks and indices)
- Cover both global triggers (US markets, China, oil, dollar index) and domestic triggers (RBI, budget, earnings, monsoon, inflation)
- Suggest specific NSE/BSE stock symbols with reasoning tied to current news
- Identify top sectors to overweight/underweight right now
- Be specific, data-driven, and timely

Respond ONLY in valid JSON (absolutely no markdown, no backticks, no extra text) with this exact structure:
{
  "timestamp": "ISO timestamp",
  "global_triggers": [
    {"event": "event description", "impact_on_india": "how it affects Indian markets", "sentiment": "positive|negative|neutral"}
  ],
  "domestic_triggers": [
    {"event": "event description", "impact": "market impact", "sentiment": "positive|negative|neutral"}
  ],
  "market_mood": {
    "overall": "bullish|bearish|neutral",
    "nifty_outlook": "brief outlook for NIFTY50 today/this week",
    "key_risk": "biggest risk to watch",
    "confidence": "high|medium|low"
  },
  "sector_calls": [
    {"sector": "sector name", "call": "overweight|underweight|neutral", "reason": "reason tied to current news", "top_pick": "NSE_SYMBOL"},
    {"sector": "sector name", "call": "overweight|underweight|neutral", "reason": "reason tied to current news", "top_pick": "NSE_SYMBOL"},
    {"sector": "sector name", "call": "overweight|underweight|neutral", "reason": "reason tied to current news", "top_pick": "NSE_SYMBOL"},
    {"sector": "sector name", "call": "overweight|underweight|neutral", "reason": "reason tied to current news", "top_pick": "NSE_SYMBOL"},
    {"sector": "sector name", "call": "overweight|underweight|neutral", "reason": "reason tied to current news", "top_pick": "NSE_SYMBOL"}
  ],
  "stock_suggestions": [
    {"symbol": "NSE_SYMBOL", "company": "Full Company Name", "action": "buy|watch|avoid", "timeframe": "intraday|short-term|medium-term", "trigger": "specific news/event driving this", "risk": "key risk for this pick"},
    {"symbol": "NSE_SYMBOL", "company": "Full Company Name", "action": "buy|watch|avoid", "timeframe": "intraday|short-term|medium-term", "trigger": "specific news/event driving this", "risk": "key risk for this pick"},
    {"symbol": "NSE_SYMBOL", "company": "Full Company Name", "action": "buy|watch|avoid", "timeframe": "intraday|short-term|medium-term", "trigger": "specific news/event driving this", "risk": "key risk for this pick"},
    {"symbol": "NSE_SYMBOL", "company": "Full Company Name", "action": "buy|watch|avoid", "timeframe": "intraday|short-term|medium-term", "trigger": "specific news/event driving this", "risk": "key risk for this pick"},
    {"symbol": "NSE_SYMBOL", "company": "Full Company Name", "action": "buy|watch|avoid", "timeframe": "intraday|short-term|medium-term", "trigger": "specific news/event driving this", "risk": "key risk for this pick"},
    {"symbol": "NSE_SYMBOL", "company": "Full Company Name", "action": "buy|watch|avoid", "timeframe": "intraday|short-term|medium-term", "trigger": "specific news/event driving this", "risk": "key risk for this pick"}
  ],
  "indices_watch": {
    "NIFTY50": "brief comment",
    "BANKNIFTY": "brief comment",
    "NIFTYMIDCAP": "brief comment",
    "NIFTYIT": "brief comment"
  },
  "fii_dii_signal": "brief comment on FII/DII activity and what it means",
  "summary": "2-3 sentence executive summary of the overall market picture right now"
}"""


def get_user_prompt() -> str:
    now = datetime.now()
    day_of_week = now.strftime("%A")
    date_str = now.strftime("%B %d, %Y")
    time_str = now.strftime("%I:%M %p IST")
    
    return f"""Today is {day_of_week}, {date_str} at {time_str}.

Please search the web right now for:
1. Latest global market news — US markets, Asian markets, European markets
2. Crude oil prices, Dollar Index (DXY), Gold prices — current levels and direction
3. US Fed latest statements or decisions
4. China economic news or geopolitical tensions
5. India-specific news — RBI announcements, government policy, budget updates, inflation data, GST collections
6. FII/DII data for Indian markets (recent flows)
7. Top performing and worst performing NSE/BSE sectors today
8. Any major corporate earnings, M&A, or sector news on NSE/BSE
9. Monsoon updates if relevant to agri/FMCG sectors
10. Any geopolitical events (Middle East, Russia-Ukraine, US-China) affecting commodity or risk sentiment

After gathering all this, analyze the combined global + Indian macro picture and give me your best investment suggestions for the Indian stock market right now. Be specific about NSE symbols."""


def run_analysis(risk_profile: str = "moderate") -> dict | None:
    """Run a single market analysis cycle."""
    client = anthropic.Anthropic()
    
    console.print()
    console.rule("[bold cyan]India Market Intelligence Agent[/bold cyan]")
    console.print(f"  [dim]Analysis run at {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}[/dim]")
    console.print(f"  [dim]Risk profile: {risk_profile}[/dim]")
    console.print()

    full_response = ""
    
    with console.status("[cyan]Agent searching live market news...[/cyan]", spinner="dots") as status:
        try:
            with client.messages.stream(
                model="claude-opus-4-5",
                max_tokens=4000,
                system=SYSTEM_PROMPT,
                tools=[{"type": "web_search_20250305", "name": "web_search"}],
                messages=[{"role": "user", "content": get_user_prompt()}]
            ) as stream:
                tool_use_count = 0
                for event in stream:
                    event_type = type(event).__name__
                    
                    if event_type == "RawContentBlockStartEvent":
                        block = event.content_block
                        if hasattr(block, 'type') and block.type == "tool_use":
                            tool_use_count += 1
                            status.update(f"[cyan]Searching web... (query {tool_use_count})[/cyan]")
                    
                    elif event_type == "RawContentBlockDeltaEvent":
                        delta = event.delta
                        if hasattr(delta, 'type') and delta.type == "text_delta":
                            full_response += delta.text
                
                status.update("[cyan]Analyzing market data...[/cyan]")
        
        except anthropic.APIConnectionError:
            console.print("[red]Connection error. Check your internet connection.[/red]")
            return None
        except anthropic.AuthenticationError:
            console.print("[red]Invalid API key. Set ANTHROPIC_API_KEY environment variable.[/red]")
            return None
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            return None

    # Parse JSON
    clean = full_response.strip()
    if clean.startswith("```"):
        clean = clean.split("```")[1]
        if clean.startswith("json"):
            clean = clean[4:]
    clean = clean.strip()

    try:
        data = json.loads(clean)
        display_analysis(data)
        save_to_log(data)
        return data
    except json.JSONDecodeError:
        console.print("[red]Could not parse agent response as JSON.[/red]")
        console.print("[dim]Raw response:[/dim]")
        console.print(clean[:500])
        return None


def sentiment_color(s: str) -> str:
    return {"positive": "green", "negative": "red", "neutral": "yellow"}.get(s.lower(), "white")


def action_color(a: str) -> str:
    return {"buy": "bold green", "watch": "bold yellow", "avoid": "bold red",
            "overweight": "bold green", "underweight": "bold red", "neutral": "yellow",
            "bullish": "bold green", "bearish": "bold red"}.get(a.lower(), "white")


def display_analysis(data: dict):
    """Pretty-print the analysis to terminal."""

    # ── Executive Summary ─────────────────────────────────────────────────────
    mood = data.get("market_mood", {})
    overall = mood.get("overall", "neutral").upper()
    confidence = mood.get("confidence", "medium")
    mood_color = action_color(mood.get("overall", "neutral"))

    console.print(Panel(
        f"[{mood_color}]{overall}[/{mood_color}]  [dim]|[/dim]  Confidence: [bold]{confidence.upper()}[/bold]\n\n"
        f"[italic]{data.get('summary', '')}[/italic]\n\n"
        f"[dim]NIFTY50:[/dim] {mood.get('nifty_outlook', '')}\n"
        f"[dim]Key risk:[/dim] [yellow]{mood.get('key_risk', '')}[/yellow]",
        title="[bold]Market Overview[/bold]",
        border_style="cyan",
        padding=(1, 2)
    ))

    # ── Global Triggers ───────────────────────────────────────────────────────
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
        t.add_column("Sector", ratio=2)
        t.add_column("Call", ratio=1, justify="center")
        t.add_column("Reason", ratio=5)
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
        t.add_column("Symbol", ratio=1)
        t.add_column("Company", ratio=2)
        t.add_column("Action", ratio=1, justify="center")
        t.add_column("Timeframe", ratio=1, justify="center")
        t.add_column("Trigger", ratio=4)
        t.add_column("Risk", ratio=3)
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

    # ── Indices + FII/DII ─────────────────────────────────────────────────────
    console.print(Rule("[bold]Indices & FII/DII[/bold]"))
    indices = data.get("indices_watch", {})
    idx_panels = []
    for idx, comment in indices.items():
        idx_panels.append(Panel(f"[dim]{comment}[/dim]", title=f"[bold cyan]{idx}[/bold cyan]", border_style="dim"))
    if idx_panels:
        console.print(Columns(idx_panels))

    fii_dii = data.get("fii_dii_signal", "")
    if fii_dii:
        console.print(Panel(fii_dii, title="[bold]FII/DII Signal[/bold]", border_style="dim", padding=(0, 2)))

    console.print()
    console.print(
        "[dim]⚠  DISCLAIMER: This is AI-generated analysis for educational purposes only. "
        "Not SEBI-registered advice. Consult a qualified financial advisor before investing.[/dim]"
    )
    console.print()


def save_to_log(data: dict):
    """Append analysis to a JSON-lines log file."""
    import os
    log_file = "market_analysis_log.jsonl"
    with open(log_file, "a") as f:
        f.write(json.dumps(data) + "\n")
    console.print(f"[dim]Saved to {log_file}[/dim]")


def run_loop(interval_minutes: int = 15, risk_profile: str = "moderate"):
    """Run analysis in a continuous loop."""
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
        
        next_run = datetime.now().strftime
        console.print(f"\n[dim]Next analysis in {interval_minutes} minutes. Press Ctrl+C to stop.[/dim]")
        
        try:
            for remaining in range(interval_minutes * 60, 0, -1):
                mins, secs = divmod(remaining, 60)
                sys.stdout.write(f"\r[dim]Next run in: {mins:02d}:{secs:02d}[/dim]")
                sys.stdout.flush()
                time.sleep(1)
            print()
        except KeyboardInterrupt:
            console.print("\n[yellow]Stopped by user.[/yellow]")
            break


def main():
    parser = argparse.ArgumentParser(
        description="India Market Intelligence Agent — AI-powered NSE/BSE investment suggestions"
    )
    parser.add_argument(
        "--loop", action="store_true",
        help="Run continuously instead of once"
    )
    parser.add_argument(
        "--interval", type=int, default=15,
        help="Minutes between runs in loop mode (default: 15)"
    )
    parser.add_argument(
        "--risk", choices=["conservative", "moderate", "aggressive"],
        default="moderate",
        help="Your risk appetite (default: moderate)"
    )
    args = parser.parse_args()

    console.print(Panel(
        "[bold]India Market Intelligence Agent[/bold]\n"
        "[dim]Powered by Claude AI + Live Web Search[/dim]\n\n"
        "Analyzes global + Indian market news and suggests\n"
        "NSE/BSE stocks and sectors to invest in.",
        border_style="cyan",
        padding=(1, 4)
    ))

    if args.loop:
        run_loop(interval_minutes=args.interval, risk_profile=args.risk)
    else:
        run_analysis(risk_profile=args.risk)


if __name__ == "__main__":
    main()
    