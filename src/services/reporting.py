"""Lester's Underground Intel — Executive Technical Dossier Generator (.txt)."""

from __future__ import annotations

import datetime
from typing import Any


def generate_text_report(metrics: dict[str, Any]) -> str:
    """Build a classified Vice City / Lester's Underground Intel dossier for download."""
    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = f"""================================================================================
🌴 LESTER'S UNDERGROUND INTEL // CLASSIFIED BAWSAQ DOSSIER [CLEARANCE: VI]
AI STOCK INSIGHTS PORTAL | BCC 351 MINI PROJECT | DRONACHARYA GROUP (AKTU)
================================================================================
TARGET TICKER       : {metrics['symbol']}
INTERCEPT TIMESTAMP : {timestamp_str}
LIVE MARKET QUOTE   : INR {metrics['close']:,.2f}
24H VOLATILITY      : INR {metrics['day_change']:+.2f} ({metrics['day_change_pct']:+.2f}%)
52-WEEK PERIMETER   : INR {metrics['low_52w']:,.2f} - INR {metrics['high_52w']:,.2f}
DETECTED VOLUME     : {metrics['volume']:,}

--------------------------------------------------------------------------------
[01] TELEMETRY & TECHNICAL SCANS
--------------------------------------------------------------------------------
- RSI (14 Periods)  : {metrics['rsi']}
- 50-Day SMA        : INR {metrics['sma50']:,.2f}
- 200-Day SMA       : INR {metrics['sma200']:,.2f}

--------------------------------------------------------------------------------
[02] SYNDICATE DECISION ENGINE & CONFIDENCE RATING
--------------------------------------------------------------------------------
ACTION DIRECTIVE    : {metrics['signal']}
CONFIDENCE LEVEL    : {metrics['confidence']}%
MISSION BRIEFING    : {metrics['final_reason']}

--------------------------------------------------------------------------------
[03] EXPLAINABLE SIGNAL TRIGGERS
--------------------------------------------------------------------------------
"""
    for reason in metrics["reasons"]:
        cleaned = (
            reason.replace("🟢", "")
            .replace("🔴", "")
            .replace("🟡", "")
            .replace("**", "")
            .strip()
        )
        report += f"  >> {cleaned}\n"

    report += """
================================================================================
DISCLAIMER:
This dossier is generated strictly for academic and educational purposes under
B.Tech Mini Project BCC 351 and must NOT be considered financial or investment advice.
================================================================================
"""
    return report
