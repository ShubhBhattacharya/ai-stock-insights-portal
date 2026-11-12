"""Executive technical report generator (.txt)."""

from __future__ import annotations

import datetime
from typing import Any


def generate_text_report(metrics: dict[str, Any]) -> str:
    """Build a formatted plain-text technical summary report for download."""
    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = f"""================================================================================
AI STOCK INSIGHTS PORTAL - EXECUTIVE TECHNICAL REPORT
Academic Project: BCC 351 (Mini Project) | Dronacharya Group of Institutions
================================================================================
Ticker Symbol       : {metrics['symbol']}
Generated At        : {timestamp_str}
Current Market Price: INR {metrics['close']:,.2f}
Day Change          : INR {metrics['day_change']:+.2f} ({metrics['day_change_pct']:+.2f}%)
52-Week Range       : INR {metrics['low_52w']:,.2f} - INR {metrics['high_52w']:,.2f}
Trading Volume      : {metrics['volume']:,}

--------------------------------------------------------------------------------
1. TECHNICAL INDICATORS OVERVIEW
--------------------------------------------------------------------------------
- RSI (14 Periods)  : {metrics['rsi']}
- 50-Day SMA        : INR {metrics['sma50']:,.2f}
- 200-Day SMA       : INR {metrics['sma200']:,.2f}

--------------------------------------------------------------------------------
2. AI RULE-BASED DECISION & CONFIDENCE
--------------------------------------------------------------------------------
Final Signal        : {metrics['signal']}
Confidence Level    : {metrics['confidence']}%
Executive Rationale : {metrics['final_reason']}

--------------------------------------------------------------------------------
3. EXPLAINABLE TECHNICAL BREAKDOWN
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
        report += f"  * {cleaned}\n"

    report += """
================================================================================
DISCLAIMER:
This report is generated strictly for academic and educational purposes under
B.Tech Mini Project BCC 351 and must NOT be considered financial or investment advice.
================================================================================
"""
    return report
