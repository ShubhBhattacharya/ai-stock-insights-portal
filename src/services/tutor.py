"""Vice City Cyber-Broker AI Tutor — Live NSE Analyzer, Hinglish/English Persona & Curriculum."""

from __future__ import annotations

import re
from typing import Any

from src.constants import NSE_STOCKS
from src.services.market_data import get_stock_analysis

CURRICULUM_MODULES: dict[str, str] = {
    "1. BAWSAQ & NSE Fundamentals (Equities, Exchanges & Bulls/Bears)": """
### 🏢 [FILE 01] Market Street Fundamentals
- **Shares & Equities:** Grabbing a share gives you fractional ownership in a company's turf, assets, and cash flow.
- **NSE & BSE (Real-World BAWSAQ & LCN):** India's primary regulated exchanges under SEBI surveillance.
- **Market Regimes:**
  - 🟢 **Bull Run:** High-octane upward momentum backed by greed and strong earnings.
  - 🔴 **Bear Raid:** Prolonged market bleed (>20% drop from peak highs).
""",
    "2. Cyber Scanners (RSI, 50 SMA, 200 SMA & Golden Cross)": """
### 📈 [FILE 02] Technical Scanner Telemetry
- **Relative Strength Index (RSI - 14):** A momentum radar bounded between 0 and 100.
  - *Oversold (< 35):* Sellers are gassed out — prime dip-buying radar.
  - *Overbought (> 70):* Engine is redlining — high risk of a sharp pullback.
- **50-Day & 200-Day Simple Moving Averages (SMA):**
  - **50 SMA:** Mid-range street trend line.
  - **200 SMA:** Heavyweight institutional support/resistance floor.
  - **Golden Cross:** 50 SMA slicing *above* 200 SMA — maximum bullish heat!
""",
    "3. Syndicate Heuristics (Rules behind BUY, SELL & HOLD)": """
### 🎯 [FILE 03] Rule-Based Decision Matrix (BCC 351 Specs)
No black boxes here, runner — pure transparent logic:
- **BUY (88% Confidence):** `RSI < 40` AND `Close > 95% of SMA_50`.
- **SELL (82% Confidence):** `RSI > 65` OR `Close < 92% of SMA_50`.
- **HOLD (65% Confidence):** Sideways chop — keep your powder dry.
""",
    "4. Corporate Valuation Intel (P/E Ratio, Market Cap, EPS)": """
### 📊 [FILE 04] Valuation & Fundamentals Recon
- **P/E (Price-to-Earnings):** Share Price divided by EPS. Shows how many rupees the street pays per ₹1 of profit.
- **Market Capitalization:** Total shares multiplied by share price (Large-cap > ₹20,000 Cr).
- **EPS (Earnings Per Share):** Net profit divided by outstanding shares.
""",
    "5. Heist Survival Rules (Risk Management & Allocation)": """
### 🛡️ [FILE 05] Risk & Stash Protection
- **Diversify Your Drops:** Never dump your whole stash into one ticker or one sector.
- **Stop-Loss Perimeter:** Cut bad trades fast (5–8% max drawdown rule).
- **Preserve Capital:** You can't run tomorrow's heist if you blow the vault today.
""",
}

QUICK_PROMPTS: list[str] = [
    "Analyze Reliance & TCS live",
    "How does the BUY signal trigger?",
    "Suggest a ₹10,000 budget allocation",
    "Infosys ka RSI aur trend batao",
]

_HINGLISH_CUES = (
    "batao", "kaise", "kya", "chahiye", "khareed", "bech", "yaar", "bhai",
    "karu", "kare", "kaisa", "kaunsa", "kaunse", "samjhao", "mera", "apna",
    "paisa", "kitna", "achha", "sahi", "lagta", "pooch", "abhi", "mein", "aur",
)

_STOCK_ALIASES: list[tuple[str, str]] = [
    ("tata motors", "TMPV.NS"),
    ("tata consultancy", "TCS.NS"),
    ("tata consumer", "TATACONSUM.NS"),
    ("tata power", "TATAPOWER.NS"),
    ("tata steel", "TATASTEEL.NS"),
    ("state bank", "SBIN.NS"),
    ("sbi life", "SBILIFE.NS"),
    ("sbi", "SBIN.NS"),
    ("reliance", "RELIANCE.NS"),
    ("infosys", "INFY.NS"),
    ("hdfc bank", "HDFCBANK.NS"),
    ("hdfc life", "HDFCLIFE.NS"),
    ("hdfc", "HDFCBANK.NS"),
    ("icici bank", "ICICIBANK.NS"),
    ("icici", "ICICIBANK.NS"),
    ("axis bank", "AXISBANK.NS"),
    ("kotak", "KOTAKBANK.NS"),
    ("yes bank", "YESBANK.NS"),
    ("indusind", "INDUSINDBK.NS"),
    ("bank of baroda", "BANKBARODA.NS"),
    ("canara bank", "CANBK.NS"),
    ("punjab national", "PNB.NS"),
    ("bajaj finance", "BAJFINANCE.NS"),
    ("bajaj finserv", "BAJAJFINSV.NS"),
    ("bajaj auto", "BAJAJ-AUTO.NS"),
    ("bharti airtel", "BHARTIARTL.NS"),
    ("airtel", "BHARTIARTL.NS"),
    ("maruti", "MARUTI.NS"),
    ("asian paints", "ASIANPAINT.NS"),
    ("hindustan unilever", "HINDUNILVR.NS"),
    ("hul", "HINDUNILVR.NS"),
    ("hindustan aeronautics", "HAL.NS"),
    ("sun pharma", "SUNPHARMA.NS"),
    ("dr reddy", "DRREDDY.NS"),
    ("larsen", "LT.NS"),
    ("l&t", "LT.NS"),
    ("tech mahindra", "TECHM.NS"),
    ("mahindra", "M&M.NS"),
    ("zomato", "ETERNAL.NS"),
    ("eternal", "ETERNAL.NS"),
    ("dmart", "DMART.NS"),
    ("avenue supermarts", "DMART.NS"),
    ("adani green", "ADANIGREEN.NS"),
    ("adani ports", "ADANIPORTS.NS"),
    ("adani power", "ADANIPOWER.NS"),
    ("adani enterprises", "ADANIENT.NS"),
    ("adani", "ADANIENT.NS"),
    ("wipro", "WIPRO.NS"),
    ("hcl", "HCLTECH.NS"),
    ("titan", "TITAN.NS"),
    ("trent", "TRENT.NS"),
    ("ultratech", "ULTRACEMCO.NS"),
    ("nestle", "NESTLEIND.NS"),
    ("itc", "ITC.NS"),
    ("ntpc", "NTPC.NS"),
    ("ongc", "ONGC.NS"),
    ("coal india", "COALINDIA.NS"),
    ("jio financial", "JIOFIN.NS"),
    ("varun beverages", "VBL.NS"),
    ("vedanta", "VEDL.NS"),
    ("apollo hospitals", "APOLLOHOSP.NS"),
    ("eicher motors", "EICHERMOT.NS"),
    ("hero motocorp", "HEROMOTOCO.NS"),
    ("hindalco", "HINDALCO.NS"),
    ("jsw steel", "JSWSTEEL.NS"),
    ("britannia", "BRITANNIA.NS"),
    ("cipla", "CIPLA.NS"),
]


def _is_hinglish(query: str) -> bool:
    """Detect whether the user's message uses Hinglish/Hindi conversational cues."""
    tokens = set(re.findall(r"[a-z]+", query.lower()))
    return any(cue in tokens for cue in _HINGLISH_CUES)


def _extract_mentioned_symbols(query: str) -> list[str]:
    """Identify up to 2 NSE symbols referenced by ticker or company name."""
    matched: list[str] = []
    q_lower = query.lower()

    def _add(sym: str) -> None:
        if sym not in matched:
            matched.append(sym)

    for explicit in re.findall(r"\b([A-Za-z0-9&-]{2,15}\.(?:NS|BO))\b", query.upper()):
        _add(explicit)

    for alias, sym in _STOCK_ALIASES:
        if re.search(rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])", q_lower):
            _add(sym)

    for company, sym in NSE_STOCKS.items():
        base_sym = sym.replace(".NS", "").lower()
        if len(base_sym) >= 3 and re.search(rf"\b{re.escape(base_sym)}\b", q_lower):
            _add(sym)
        clean_co = re.sub(r"\s*\([^)]*\)", "", company).strip().lower()
        if len(clean_co) >= 4 and re.search(rf"\b{re.escape(clean_co)}\b", q_lower):
            _add(sym)

    return matched[:2]


def _format_live_stock_response(
    symbols: list[str], hinglish: bool
) -> tuple[str, str, list[dict[str, Any]]]:
    """Fetch live NSE telemetry via get_stock_analysis() and craft a persona reply."""
    scans: list[dict[str, Any]] = []
    errors: list[str] = []

    for sym in symbols:
        metrics, err = get_stock_analysis(sym)
        if metrics:
            scans.append(metrics)
        elif err:
            errors.append(f"{sym}: {err}")

    if not scans:
        err_detail = "; ".join(errors) if errors else "Ticker feed unavailable."
        if hinglish:
            return (
                f"`[BAWSAQ LIVE LINK // FEED ERROR]`\n\n"
                f"Arre boss, live data abhi intercept nahi ho paya ({err_detail}). "
                f"Thodi der baad try karo ya exact NSE ticker (`RELIANCE.NS`, `TCS.NS`) daalo!",
                "bearish",
                [],
            )
        return (
            f"`[BAWSAQ LIVE LINK // FEED ERROR]`\n\n"
            f"Runner, couldn't pull live bars right now ({err_detail}). Try a verified NSE ticker like `RELIANCE.NS` or `TCS.NS`.",
            "bearish",
            [],
        )

    lines: list[str] = []
    if hinglish:
        lines.append("`[LIVE BAWSAQ INTEL // REAL-TIME NSE SCAN]`\n")
        lines.append("Suno boss — terminal pe abhi ka **live data** lock ho gaya hai:")
    else:
        lines.append("`[LIVE BAWSAQ INTEL // REAL-TIME NSE SCAN]`\n")
        lines.append("Listen up, runner — here's the live telemetry straight off the BAWSAQ wire:")

    buy_hits = 0
    sell_hits = 0
    for m in scans:
        sig = m["signal"]
        if sig == "BUY":
            buy_hits += 1
            sig_icon = "🟢"
        elif sig == "SELL":
            sell_hits += 1
            sig_icon = "🔴"
        else:
            sig_icon = "🟡"

        sma_pos = "above 50-SMA" if m["close"] >= m["sma50"] else "below 50-SMA"
        lines.append(
            f"\n* 🎯 **{m['symbol']}** — **₹{m['close']:,.2f}** (`{m['day_change_pct']:+.2f}%`)"
            f"\n  - **RSI (14):** `{m['rsi']:.1f}` | **50-SMA:** `₹{m['sma50']:,.2f}` ({sma_pos}) | **200-SMA:** `₹{m['sma200']:,.2f}`"
            f"\n  - **Signal:** {sig_icon} **{sig}** (`{m['confidence']}%` conf) — *{m['final_reason']}*"
        )

    if hinglish:
        lines.append("\n🕶️ *Insider Take:* Always RSI aur 50-SMA support check karke hi entry lena, aur stop-loss tight rakhna!")
    else:
        lines.append("\n🕶️ *Insider Take:* Respect the 50-SMA trendline and keep risk tight on every drop.")

    if sell_hits > 0 and buy_hits == 0:
        mood = "bearish"
    elif buy_hits > 0 or all(m["close"] >= m["sma50"] and m["rsi"] < 65 for m in scans):
        mood = "bullish"
    else:
        mood = "neutral"

    return "\n".join(lines), mood, scans


def _format_for_pro_standard(text: str) -> str:
    """Cleanly adapt tutor copy to neutral corporate fintech terminology for Default Pro Standard."""
    replacements = (
        ("[CYBER-BROKER // ENCRYPTED TERMINAL ONLINE]", "**AI Financial Assistant**"),
        ("[BUNKER AI // ENCRYPTED TERMINAL ONLINE]", "**AI Financial Assistant**"),
        ("[ENCRYPTED UPLINK // ₹10,000 ALLOCATION BLUEPRINT]", "**₹10,000 Portfolio Allocation Guide**"),
        ("[ENCRYPTED BLUEPRINT // ₹10,000 SMART ALLOCATION]", "**₹10,000 Portfolio Allocation Guide**"),
        ("[HEURISTIC MATRIX // BUY & SELL RULES]", "**Rule-Based Signal Criteria (BUY & SELL)**"),
        ("[GREEN LIGHT // BUY SIGNAL PROTOCOL]", "**Rule-Based BUY Signal Criteria**"),
        ("[RED ALERT // SELL SIGNAL PROTOCOL]", "**Rule-Based SELL Signal Criteria**"),
        ("[INTEL DECRYPTED // P/E RATIO]", "**P/E Ratio Overview**"),
        ("[INTEL DECRYPTED // EPS]", "**Earnings Per Share (EPS) Overview**"),
        ("[INTEL DECRYPTED // MARKET CAP]", "**Market Capitalization Overview**"),
        ("[SCANNER LOCKED // RSI-14 TELEMETRY]", "**RSI-14 Momentum Indicator**"),
        ("[RADAR TRACE // SMA 50 vs SMA 200]", "**Moving Average Crossovers (50 vs 200 SMA)**"),
        ("LIVE BAWSAQ PULSE", "Live NSE Snapshot"),
        ("BUNKER.NET PULSE", "Live NSE Snapshot"),
        ("BAWSAQ", "NSE India"),
        ("BUNKER.NET", "NSE India"),
        ("Vice City", "NSE"),
        ("Syndicate Rule-Based Trigger Logic:", "Rule-Based Decision Logic:"),
        ("Synopsis Rule-Based SELL Signal Condition:", "Rule-Based SELL Signal Criteria:"),
        ("Synopsis Rule-Based BUY Signal Condition:", "Rule-Based BUY Signal Criteria:"),
        ("Listen up, runner — smart operators never dump the whole ₹10,000 stash on one getaway car. Split it across three tiers:", "Smart long-term investors diversify a ₹10,000 budget across three balanced tiers:"),
        ("Insider Take", "Technical Summary"),
        ("Street Read:", "Analytical Interpretation:"),
        ("Radar Zones:", "Valuation Ranges:"),
        ("Turf Tiers (SEBI / NSE):", "SEBI / NSE Classification Tiers:"),
        ("Armored giants, lower volatility", "Large established companies with lower volatility"),
        ("Fast growth, medium heat", "Higher growth potential with moderate volatility"),
        ("Wild swings — 6-star risk!", "Higher volatility and higher risk"),
        ("Possible stealth bargain — or a busted value trap.", "Potentially undervalued relative to sector peers, or a value trap."),
        ("daily street noise", "short-term price noise"),
        ("Sellers ran out of ammo — prime reversal radar.", "Oversold momentum — potential mean-reversion zone."),
        ("Engine redlining — high pullback/profit-booking risk.", "Overbought momentum — elevated pullback/profit-booking risk."),
        ("Target is oversold / coiled for bounce", "Stock is in an attractive / oversold RSI zone"),
        ("Structural support is holding strong", "Price remains above structural support"),
        ("Momentum is redlining in overbought territory", "Momentum is stretched in the overbought zone"),
        ("Support floor shattered", "Structural support has broken down"),
        ("Either tripwire triggers a **SELL** order at **82% Confidence** to protect your stash!", "Either condition triggers a **SELL** signal at **82% Confidence** to help manage downside risk."),
        ("When both tripwires align, the terminal flashes **BUY** at **88% Confidence**!", "When both conditions align, the system generates a **BUY** signal at **88% Confidence**."),
        ("getaway car", "sideways market"),
        ("protect your stash", "protect capital"),
        ("Intercepted query:", "Query:"),
        ("Boss, aapne poocha:", "Aapne poocha:"),
    )
    out = text
    for old, new in replacements:
        out = out.replace(old, new)
    return out


def _format_for_doomsday(text: str) -> str:
    """Adapt educational responses cleanly to Bunker AI / DEFCON-1 terminology without GTA VI slang."""
    replacements = (
        ("[INTEL DECRYPTED // P/E RATIO]", "[BUNKER DECRYPT // P/E RATIO]"),
        ("[INTEL DECRYPTED // EPS]", "[BUNKER DECRYPT // EPS]"),
        ("[INTEL DECRYPTED // MARKET CAP]", "[BUNKER DECRYPT // MARKET CAP]"),
        ("[SCANNER LOCKED // RSI-14 TELEMETRY]", "[DEFCON SCANNER // RSI-14 TELEMETRY]"),
        ("[RADAR TRACE // SMA 50 vs SMA 200]", "[BUNKER TRACE // SMA 50 vs SMA 200]"),
        ("[HEURISTIC MATRIX // BUY & SELL RULES]", "[DEFCON MATRIX // BUY & SELL RULES]"),
        ("[CYBER-BROKER // ENCRYPTED TERMINAL ONLINE]", "[BUNKER AI // ENCRYPTED TERMINAL ONLINE]"),
        ("[ENCRYPTED UPLINK // ₹10,000 ALLOCATION BLUEPRINT]", "[DEFCON-1 PROTOCOL // ₹10,000 SURVIVAL PORTFOLIO]"),
        ("[ENCRYPTED BLUEPRINT // ₹10,000 SMART ALLOCATION]", "[DEFCON-1 PROTOCOL // ₹10,000 SURVIVAL ALLOCATION]"),
        ("LIVE BAWSAQ PULSE", "BUNKER.NET PULSE"),
        ("BAWSAQ traders", "Bunker.Net operators"),
        ("BAWSAQ", "BUNKER.NET"),
        ("Vice City", "Shelter Sector"),
        ("Insider Take", "Bunker Command"),
        ("Syndicate Rule-Based Trigger Logic:", "Bunker Rule-Based Trigger Logic:"),
        ("Street Read:", "Bunker Read:"),
        ("Turf Tiers (SEBI / NSE):", "Sector Tiers (SEBI / NSE):"),
        ("Wild swings — 6-star risk!", "Extreme fallout swings — Tier-6 risk!"),
        ("daily street noise", "daily radiation noise"),
        ("wait on the getaway car", "hold defensive bunker posture"),
        ("protect your stash", "protect war capital"),
        ("Tripwire", "Perimeter Sensor"),
        ("Either tripwire triggers", "Either perimeter sensor triggers"),
        ("When both tripwires align, the terminal", "When both perimeter sensors align, Bunker AI"),
    )
    out = text
    for old, new in replacements:
        out = out.replace(old, new)
    return out


def adapt_tutor_text_for_edition(text: str, edition: str = "GTA VI") -> str:
    """Adapt any assistant message for the currently active portal theme at render time."""
    ed_norm = edition.strip().upper()
    if ed_norm in {"DEFAULT", "PRO", "STANDARD"}:
        return _format_for_pro_standard(text)
    if ed_norm == "DOOMSDAY":
        return _format_for_doomsday(text)
    return text


def get_curriculum_modules(edition: str = "GTA VI") -> dict[str, str]:
    """Return theme-adapted curriculum study modules for Default Pro, Doomsday, or GTA VI."""
    ed_norm = edition.strip().upper()
    if ed_norm in {"DEFAULT", "PRO", "STANDARD"}:
        pro_titles = {
            "1. BAWSAQ & NSE Fundamentals (Equities, Exchanges & Bulls/Bears)": "1. Stock Market & NSE Fundamentals (Equities, Exchanges & Regimes)",
            "2. Cyber Scanners (RSI, 50 SMA, 200 SMA & Golden Cross)": "2. Technical Indicators (RSI, 50 SMA, 200 SMA & Golden Cross)",
            "3. Syndicate Heuristics (Rules behind BUY, SELL & HOLD)": "3. Rule-Based Signal Logic (BUY, SELL & HOLD Criteria)",
            "4. Corporate Valuation Intel (P/E Ratio, Market Cap, EPS)": "4. Fundamental Valuation Metrics (P/E Ratio, Market Cap, EPS)",
            "5. Heist Survival Rules (Risk Management & Allocation)": "5. Portfolio Risk Management & Capital Allocation",
        }
        pro_body_replacements = (
            ("[FILE 01] Market Street Fundamentals", "Stock Market & Exchange Fundamentals"),
            ("[FILE 02] Technical Scanner Telemetry", "Technical Analysis & Momentum Indicators"),
            ("[FILE 03] Rule-Based Decision Matrix (BCC 351 Specs)", "Rule-Based Decision Matrix (BCC 351)"),
            ("[FILE 04] Valuation & Fundamentals Recon", "Fundamental Valuation Ratios"),
            ("[FILE 05] Risk & Stash Protection", "Risk Management & Capital Preservation"),
            ("company's turf,", "company's equity,"),
            ("Grabbing a share", "Buying a share"),
            ("(Real-World BAWSAQ & LCN)", "(Primary Indian Stock Exchanges)"),
            ("Sellers are gassed out — prime dip-buying radar.", "Indicates oversold momentum — potential value entry zone."),
            ("Engine is redlining — high risk of a sharp pullback.", "Indicates overbought conditions — heightened pullback risk."),
            ("Mid-range street trend line.", "Medium-term trend benchmark."),
            ("Heavyweight institutional support/resistance floor.", "Long-term institutional support/resistance trendline."),
            ("maximum bullish heat!", "a strong long-term bullish crossover signal."),
            ("No black boxes here, runner — pure transparent logic:", "Transparent, deterministic decision logic:"),
            ("Sideways chop — keep your powder dry.", "Consolidation phase — await clearer trend confirmation."),
            ("the street pays", "investors pay"),
            ("Diversify Your Drops:", "Diversify Holdings:"),
            ("Never dump your whole stash", "Never concentrate total capital"),
            ("You can't run tomorrow's heist if you blow the vault today.", "Preserving downside capital ensures long-term compounding."),
        )
        out: dict[str, str] = {}
        for title, body in CURRICULUM_MODULES.items():
            clean_title = pro_titles.get(title, _format_for_pro_standard(title))
            clean_body = _format_for_pro_standard(body)
            for old, new in pro_body_replacements:
                clean_body = clean_body.replace(old, new)
            out[clean_title] = clean_body
        return out

    if ed_norm == "DOOMSDAY":
        doom_titles = {
            "1. BAWSAQ & NSE Fundamentals (Equities, Exchanges & Bulls/Bears)": "1. BUNKER.NET & NSE Fundamentals (Equities & Market Regimes)",
            "2. Cyber Scanners (RSI, 50 SMA, 200 SMA & Golden Cross)": "2. Geiger Scanners (RSI, 50 SMA, 200 SMA & Golden Cross)",
            "3. Syndicate Heuristics (Rules behind BUY, SELL & HOLD)": "3. DEFCON Signal Matrix (Rules behind BUY, SELL & HOLD)",
            "4. Corporate Valuation Intel (P/E Ratio, Market Cap, EPS)": "4. Corporate Valuation Intel (P/E Ratio, Market Cap, EPS)",
            "5. Heist Survival Rules (Risk Management & Allocation)": "5. Bunker Survival Rules (Risk Management & Capital Allocation)",
        }
        doom_body_replacements = (
            ("Market Street Fundamentals", "Bunker Market Fundamentals"),
            ("(Real-World BAWSAQ & LCN)", "(BUNKER.NET & Sector Omega Feeds)"),
            ("company's turf,", "company's armored sector,"),
            ("No black boxes here, runner", "No black boxes here, Commander"),
            ("Mid-range street trend line.", "Mid-range perimeter trendline."),
            ("Risk & Stash Protection", "Risk & War Capital Protection"),
            ("whole stash", "entire war capital"),
            ("tomorrow's heist if you blow the vault today.", "tomorrow's defense if you compromise the bunker today."),
        )
        out = {}
        for title, body in CURRICULUM_MODULES.items():
            clean_title = doom_titles.get(title, _format_for_doomsday(title))
            clean_body = _format_for_doomsday(body)
            for old, new in doom_body_replacements:
                clean_body = clean_body.replace(old, new)
            out[clean_title] = clean_body
        return out

    return CURRICULUM_MODULES


def generate_tutor_turn(
    query: str,
    edition: str = "GTA VI",
) -> tuple[str, str, list[dict[str, Any]]]:
    """
    Generate a theme-aware Cyber-Broker, Bunker AI, or Pro Standard response with mood & live scans.
    Returns: (reply_text, mood ['bullish'|'bearish'|'neutral'], scanned_metrics_list)
    """
    raw_reply, raw_mood, raw_scans = _generate_tutor_turn_inner(query, edition=edition)
    ed_norm = edition.strip().upper()
    if ed_norm in {"DEFAULT", "PRO", "STANDARD"}:
        return _format_for_pro_standard(raw_reply), raw_mood, raw_scans
    if ed_norm == "DOOMSDAY":
        return _format_for_doomsday(raw_reply), raw_mood, raw_scans
    return raw_reply, raw_mood, raw_scans


def _generate_tutor_turn_inner(
    query: str,
    edition: str = "GTA VI",
) -> tuple[str, str, list[dict[str, Any]]]:
    ed_norm = edition.strip().upper()
    doomsday = ed_norm == "DOOMSDAY"
    default_pro = ed_norm in {"DEFAULT", "PRO", "STANDARD"}
    q = query.lower().strip()
    hinglish = _is_hinglish(query)

    mentioned_syms = _extract_mentioned_symbols(query)
    if mentioned_syms:
        text, mood, scans = _format_live_stock_response(mentioned_syms, hinglish)
        if doomsday:
            text = (
                text.replace("BAWSAQ", "BUNKER.NET")
                .replace("Vice City", "Shelter Sector")
                .replace("Insider Take", "Bunker Command")
            )
        elif default_pro:
            text = _format_for_pro_standard(text)
        return text, mood, scans

    if any(
        k in q
        for k in ("budget", "10000", "10,000", "5000", "50000", "invest", "recommend", "allocat", "long term")
    ):
        live_scans: list[dict[str, Any]] = []
        scanner_lines: list[str] = []
        for sym in ("SBIN.NS", "ITC.NS"):
            m, _ = get_stock_analysis(sym)
            if m:
                live_scans.append(m)
                dot = "🟢" if m["signal"] == "BUY" else ("🔴" if m["signal"] == "SELL" else "🟡")
                scanner_lines.append(f"`{m['symbol']}` {dot} ₹{m['close']:,.2f} (RSI: {m['rsi']:.1f}, {m['signal']})")

        feed_name = "BUNKER.NET PULSE" if doomsday else "LIVE BAWSAQ PULSE"
        live_strip = (
            f"\n\n📡 **{feed_name}:** {'  |  '.join(scanner_lines)}"
            if scanner_lines
            else ""
        )
        if doomsday and hinglish:
            text = (
                "`[DEFCON-1 PROTOCOL // ₹10,000 SURVIVAL ALLOCATION]`\n\n"
                "Commander — fallout market mein poora ₹10,000 war capital ek asset mein lock mat karo. 3-tier bunker split use karo:\n\n"
                "* 🛡️ **Core Bunker Armor (50–60% ~ ₹5,000 – ₹6,000):** `SBIN.NS` ya `ITC.NS` (hardened liquidity & defensive floor).\n"
                "* 🔋 **Mobile Tactical Units (30% ~ ₹3,000):** `TCS.NS` ya `INFY.NS` (resilient tech recovery).\n"
                "* ☢️ **Fallback Index Shield (10–20% ~ ₹1,000 – ₹2,000):** `NIFTYBEES` (top-50 NSE radiation hedge)."
                f"{live_strip}\n\n📌 *Bunker Directive:* Staged deployment rakho aur emergency reserve liquid rakhna!"
            )
        elif doomsday:
            text = (
                "`[DEFCON-1 PROTOCOL // ₹10,000 SURVIVAL PORTFOLIO]`\n\n"
                "Commander — smart bunker tacticians never expose all ₹10,000 war capital on a single sector. Deploy in three armored tiers:\n\n"
                "* 🛡️ **Core Bunker Stability (50–60% ~ ₹5,000 – ₹6,000):** **SBIN** or **ITC** — high-liquidity defensive perimeter.\n"
                "* 🔋 **Tactical Recovery Engine (30% ~ ₹3,000):** **TCS / Infosys** or **Tata Motors PV (`TMPV.NS`)**.\n"
                "* ☢️ **Top-50 Fallback Shield (10–20% ~ ₹1,000 – ₹2,000):** **NIFTYBEES** — instant multi-sector survival hedge."
                f"{live_strip}\n\n📌 *Bunker Directive:* Deploy in phased tranches and keep emergency reserve capital uncompromised!"
            )
        elif hinglish:
            text = (
                "`[ENCRYPTED BLUEPRINT // ₹10,000 SMART ALLOCATION]`\n\n"
                "Suno boss — ₹10,000 ka poora stash ek hi stock mein mat daalo. Yeh solid 3-tier plan follow karo:\n\n"
                "* 🏦 **Bluechip Armor (50–60% ~ ₹5,000 – ₹6,000):** `SBIN.NS` ya `ITC.NS` (high liquidity & dividend backing).\n"
                "* 🚀 **Growth Engine (30% ~ ₹3,000):** `TCS.NS` ya `INFY.NS` (long-term compounding).\n"
                "* 🛡️ **Index Safe-House (10–20% ~ ₹1,000 – ₹2,000):** `NIFTYBEES` (top 50 NSE diversification)."
                f"{live_strip}\n\n📌 *Street Rule:* SIP mode rakho aur emergency cash alag rakhna!"
            )
        else:
            text = (
                "`[ENCRYPTED UPLINK // ₹10,000 ALLOCATION BLUEPRINT]`\n\n"
                "Listen up, runner — smart operators never dump the whole ₹10,000 stash on one getaway car. Split it across three tiers:\n\n"
                "* 🏦 **Armored Bluechips (50–60% ~ ₹5,000 – ₹6,000):** **SBIN** or **ITC** — steady liquidity and low street heat.\n"
                "* 🚀 **Cyber Tech & Growth (30% ~ ₹3,000):** **TCS / Infosys** or **Tata Motors PV (`TMPV.NS`)**.\n"
                "* 🛡️ **Index Safe-House ETFs (10–20% ~ ₹1,000 – ₹2,000):** **NIFTYBEES** — instant top-50 NSE exposure."
                f"{live_strip}\n\n📌 *Disciplined Rule:* Use systematic SIP drops and never deploy rent money needed within 12 months!"
            )
        return (_format_for_pro_standard(text) if default_pro else text), "bullish", live_scans

    if "p/e" in q or "pe ratio" in q:
        text = """`[INTEL DECRYPTED // P/E RATIO]`

📊 **Price-to-Earnings (P/E) Ratio:**
- **Formula:** `Current Market Price ÷ Earnings Per Share (EPS)`
- **Street Read:** Tells us how many rupees BAWSAQ traders pay for ₹1 of annual profit.
- **Radar Zones:**
  - *< 20 (Below Sector Avg):* Possible stealth bargain — or a busted value trap.
  - *> 40 (Hot Momentum):* High growth priced in; zero margin for earnings misses."""
        return text, "neutral", []

    if "eps" in q:
        text = """`[INTEL DECRYPTED // EPS]`

💰 **EPS (Earnings Per Share):**
- **Formula:** `Net Profit ÷ Total Outstanding Shares`
- **Street Read:** Measures real profit firepower per single share. Rising YoY EPS means strong financial health."""
        return text, "bullish", []

    if "market cap" in q:
        text = """`[INTEL DECRYPTED // MARKET CAP]`

🏢 **Market Capitalization:**
- **Formula:** $\\text{Total Shares} \\times \\text{Current Share Price}$
- **Turf Tiers (SEBI / NSE):**
  - **Large Cap:** ₹20,000 Cr+ (Armored giants, lower volatility).
  - **Mid Cap:** ₹5,000 – ₹20,000 Cr (Fast growth, medium heat).
  - **Small Cap:** < ₹5,000 Cr (Wild swings — 6-star risk!)."""
        return text, "neutral", []

    if "rsi" in q:
        text = """`[SCANNER LOCKED // RSI-14 TELEMETRY]`

📈 **Relative Strength Index (RSI - 14):**
Built by J. Welles Wilder, RSI tracks momentum from 0 to 100:
- **RSI < 30–40 (Oversold Zone):** Sellers ran out of ammo — prime reversal radar.
- **RSI > 65–70 (Overbought Zone):** Engine redlining — high pullback/profit-booking risk."""
        return text, "neutral", []

    if any(k in q for k in ("golden cross", "death cross", "sma", "moving average")):
        mood = "bearish" if "death cross" in q and "golden cross" not in q else "bullish"
        text = """`[RADAR TRACE // SMA 50 vs SMA 200]`

📉 **Moving Average Crosses:**
- **SMA (Simple Moving Average):** Strips out daily street noise to highlight the true trendline.
- **🟢 Golden Cross:** 50-Day SMA slices *above* 200-Day SMA — high-conviction bullish surge!
- **🔴 Death Cross:** 50-Day SMA drops *below* 200-Day SMA — bearish warning; protect capital."""
        return text, mood, []

    has_buy = any(k in q for k in ("buy", "khareed"))
    has_sell = any(k in q for k in ("sell", "bech"))

    if has_buy and has_sell:
        text = """`[HEURISTIC MATRIX // BUY & SELL RULES]`

🎯 **Syndicate Rule-Based Trigger Logic:**
- **🟢 BUY (88% Confidence):** Triggers when **RSI < 40** AND **Close Price > 95% of 50-Day SMA**.
- **🔴 SELL (82% Confidence):** Triggers when **RSI > 65** OR **Close Price < 92% of 50-Day SMA**.
- **🟡 HOLD (65% Confidence):** Consolidation — wait on the getaway car."""
        return text, "neutral", []

    if has_sell:
        if hinglish:
            text = """`[RED ALERT // SELL SIGNAL PROTOCOL]`

🛑 **Bechne (SELL) ka Rule Trigger:**
1. **RSI > 65** (Stock overbought zone mein garam ho chuka hai).
2. **YA Close Price < 92% of 50-Day SMA** (Support floor toot gaya hai).
Dono mein se koi bhi hit ho, terminal **SELL** (`82% Confidence`) flash karta hai taaki profit safe rahe!"""
        else:
            text = """`[RED ALERT // SELL SIGNAL PROTOCOL]`

🛑 **Synopsis Rule-Based SELL Signal Condition:**
1. **RSI > 65** (Momentum is redlining in overbought territory).
2. **OR Close Price < 92% of 50-Day SMA** (Support floor shattered).
Either tripwire triggers a **SELL** order at **82% Confidence** to protect your stash!"""
        return text, "bearish", []

    if has_buy or any(k in q for k in ("signal", "logic")):
        if hinglish:
            text = """`[GREEN LIGHT // BUY SIGNAL PROTOCOL]`

🎯 **Khareedne (BUY) ka Rule Trigger:**
1. **RSI < 40** (Momentum oversold / attractive zone mein hai).
2. **Close Price > 95% of 50-Day SMA** (Price support hold kar raha hai).
Jab dono match hon, terminal **BUY** (`88% Confidence`) flash karta hai!"""
        else:
            text = """`[GREEN LIGHT // BUY SIGNAL PROTOCOL]`

🎯 **Synopsis Rule-Based BUY Signal Condition:**
Under the BCC 351 Mini Project matrix:
1. **RSI < 40** (Target is oversold / coiled for bounce).
2. **Close Price > 95% of 50-Day SMA** (Structural support is holding strong).
When both tripwires align, the terminal flashes **BUY** at **88% Confidence**!"""
        return text, "bullish", []

    if hinglish:
        header_tag = "[BUNKER AI // ENCRYPTED TERMINAL ONLINE]" if doomsday else "[CYBER-BROKER // ENCRYPTED TERMINAL ONLINE]"
        feed_lbl = "BUNKER.NET" if doomsday else "BAWSAQ"
        lead = "☢️" if doomsday else "🕶️"
        text = f"""`{header_tag}`

{lead} Boss, aapne poocha: *"{query}"*.

Kisi bhi NSE company ka **naam likho** (jaise *"Reliance ka RSI aur price batao"* ya *"TCS vs Infosys"*) — main abhi live {feed_lbl} data scan kar dunga! Ya phir poochho:
- 📊 **"BUY aur SELL signal kaise trigger hota hai?"**
- 💰 **"10,000 budget ke liye allocation batao"**
- 📉 **"P/E Ratio aur EPS kya hota hai?"**"""
    else:
        header_tag = "[BUNKER AI // ENCRYPTED TERMINAL ONLINE]" if doomsday else "[CYBER-BROKER // ENCRYPTED TERMINAL ONLINE]"
        feed_lbl = "BUNKER.NET" if doomsday else "BAWSAQ"
        lead = "☢️" if doomsday else "🕶️"
        text = f"""`{header_tag}`

{lead} Intercepted query: *"{query}"*.

Name **any NSE company** (like *"Analyze Reliance"*, *"How is TCS doing?"*, or *"Infosys RSI"*) and I'll scan live {feed_lbl} market bars on the spot — or ask:
- 📊 **"How does the BUY signal trigger?"**
- 🛑 **"How does the SELL signal work?"**
- 📈 **"Explain Golden Cross and Death Cross."**
- 💰 **"Suggest a ₹10,000 budget allocation."**"""
    return text, "neutral", []


def generate_bot_response(query: str, edition: str = "GTA VI") -> str:
    """Return a dual-world Cyber-Broker / Bunker AI response (backward-compatible string interface)."""
    reply, _, _ = generate_tutor_turn(query, edition=edition)
    return reply
