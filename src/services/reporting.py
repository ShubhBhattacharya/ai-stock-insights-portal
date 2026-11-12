"""Theme-Adaptive Equity Technical Dossier & Report Generator (.txt)."""

from __future__ import annotations

import datetime
from typing import Any


def generate_text_report(metrics: dict[str, Any], edition: str = "GTA VI") -> str:
    """Build a theme-adaptive equity technical analysis report (.txt) for download."""
    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ed_norm = str(edition).strip().upper()

    symbol = str(metrics.get("symbol", "N/A"))
    close = float(metrics.get("close", 0.0))
    day_change = float(metrics.get("day_change", 0.0))
    day_change_pct = float(metrics.get("day_change_pct", 0.0))
    low_52w = float(metrics.get("low_52w", 0.0))
    high_52w = float(metrics.get("high_52w", 0.0))
    volume = int(metrics.get("volume", 0))
    rsi = float(metrics.get("rsi", 50.0))
    sma50 = float(metrics.get("sma50", close))
    sma200 = float(metrics.get("sma200", close))
    signal = str(metrics.get("signal", "HOLD"))
    confidence = int(metrics.get("confidence", 65))
    final_reason = str(metrics.get("final_reason", ""))
    reasons = list(metrics.get("reasons", []))

    if ed_norm in {"DEFAULT", "PRO", "STANDARD"}:
        banner_title = "EQUITY TECHNICAL & ML RESEARCH REPORT // PRO STANDARD"
        ts_label = "REPORT TIMESTAMP    "
        range_label = "52-WEEK RANGE       "
        vol_label = "TRADING VOLUME      "
        sec1 = "[01] MARKET TELEMETRY & TECHNICAL INDICATORS"
        sec2 = "[02] RULE-BASED SIGNAL ENGINE & CONFIDENCE RATING"
        action_lbl = "SIGNAL DIRECTIVE    "
        reason_lbl = "SIGNAL RATIONALE    "
        sec3 = "[03] EXPLAINABLE SIGNAL TRIGGERS"
    elif ed_norm == "DOOMSDAY":
        banner_title = "BUNKER.NET TACTICAL INTEL // DEFCON-1 EQUITY DOSSIER"
        ts_label = "SCAN TIMESTAMP      "
        range_label = "52-WEEK PERIMETER   "
        vol_label = "DETECTED VOLUME     "
        sec1 = "[01] SECTOR TELEMETRY & TECHNICAL SCANS"
        sec2 = "[02] BUNKER DECISION ENGINE & CONFIDENCE RATING"
        action_lbl = "TACTICAL DIRECTIVE  "
        reason_lbl = "BUNKER BRIEFING     "
        sec3 = "[03] EXPLAINABLE SIGNAL TRIPWIRES"
    else:
        banner_title = "🌴 LESTER'S UNDERGROUND INTEL // CLASSIFIED BAWSAQ DOSSIER [CLEARANCE: VI]"
        ts_label = "INTERCEPT TIMESTAMP "
        range_label = "52-WEEK PERIMETER   "
        vol_label = "DETECTED VOLUME     "
        sec1 = "[01] TELEMETRY & TECHNICAL SCANS"
        sec2 = "[02] SYNDICATE DECISION ENGINE & CONFIDENCE RATING"
        action_lbl = "ACTION DIRECTIVE    "
        reason_lbl = "MISSION BRIEFING    "
        sec3 = "[03] EXPLAINABLE SIGNAL TRIGGERS"

    report = f"""================================================================================
{banner_title}
AI STOCK INSIGHTS PORTAL | BCC 351 MINI PROJECT | DRONACHARYA GROUP (AKTU)
================================================================================
TARGET TICKER       : {symbol}
{ts_label}: {timestamp_str}
LIVE MARKET QUOTE   : INR {close:,.2f}
24H VOLATILITY      : INR {day_change:+.2f} ({day_change_pct:+.2f}%)
{range_label}: INR {low_52w:,.2f} - INR {high_52w:,.2f}
{vol_label}: {volume:,}

--------------------------------------------------------------------------------
{sec1}
--------------------------------------------------------------------------------
- RSI (14 Periods)  : {rsi}
- 50-Day SMA        : INR {sma50:,.2f}
- 200-Day SMA       : INR {sma200:,.2f}

--------------------------------------------------------------------------------
{sec2}
--------------------------------------------------------------------------------
{action_lbl}: {signal}
CONFIDENCE LEVEL    : {confidence}%
{reason_lbl}: {final_reason}

--------------------------------------------------------------------------------
{sec3}
--------------------------------------------------------------------------------
"""
    for reason in reasons:
        cleaned = (
            str(reason)
            .replace("🟢", "")
            .replace("🔴", "")
            .replace("🟡", "")
            .replace("**", "")
            .strip()
        )
        report += f"  >> {cleaned}\n"

    report += """
================================================================================
DISCLAIMER:
This report is generated strictly for academic and educational purposes under
B.Tech Mini Project BCC 351 and must NOT be considered financial or investment advice.
================================================================================
"""
    return report
