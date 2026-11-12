"""Lester's Cyber Uplink — Educational Curriculum & Underground Hacker AI Tutor."""

from __future__ import annotations

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
    "How does the BUY signal trigger?",
    "Explain Golden Cross and Death Cross",
    "What is P/E Ratio and EPS?",
    "Suggest a ₹10,000 budget allocation",
]


def generate_bot_response(query: str) -> str:
    """Return an underground cyber-hacker ('Lester') educational tutor response."""
    q = query.lower()

    if any(
        k in q
        for k in ("budget", "10000", "10,000", "5000", "50000", "invest", "recommend", "allocat", "long term")
    ):
        return """`[ENCRYPTED UPLINK // LESTER'S ALLOCATION BLUEPRINT]`

Listen up, runner — smart operators never put the whole ₹10,000 stash on one getaway car. Split the risk across three tiers:

* 🏦 **Heavy Armored Bluechips (50–60% ~ ₹5,000 – ₹6,000):**
  - **SBIN** or **ITC** — high liquidity, dividend armor, low street heat.
* 🚀 **Cyber Tech & Growth (30% ~ ₹3,000):**
  - **TCS / Infosys** or **Tata Motors PV** — long-horizon compounding engines.
* 🛡️ **Index Safe-House ETFs (10–20% ~ ₹1,000 – ₹2,000):**
  - **NIFTYBEES** — instant exposure to the top 50 NSE heavyweights.

📌 *Street Rule:* Run automated SIP drops and never gamble rent money you need within 12 months!"""

    if "p/e" in q or "pe ratio" in q:
        return """`[INTEL DECRYPTED // P/E RATIO]`

📊 **Price-to-Earnings (P/E) Ratio:**
- **Formula:** `Current Market Price ÷ Earnings Per Share (EPS)`
- **Street Read:** Tells us how much the BAWSAQ crowd is overpaying for ₹1 of actual profit.
- **Radar Zones:**
  - *< 20 (Below Sector Avg):* Possible stealth bargain — or a busted value trap.
  - *> 40 (Hot Momentum):* High growth baked in; zero room for earnings misses."""

    if "eps" in q:
        return """`[INTEL DECRYPTED // EPS]`

💰 **EPS (Earnings Per Share):**
- **Formula:** `Net Profit ÷ Total Outstanding Shares`
- **Street Read:** Measures real cash firepower per single share. Rising YoY EPS means the syndicate is printing steady profit."""

    if "market cap" in q:
        return """`[INTEL DECRYPTED // MARKET CAP]`

🏢 **Market Capitalization:**
- **Formula:** $\\text{Total Shares} \\times \\text{Current Share Price}$
- **Turf Tiers (SEBI / NSE):**
  - **Large Cap:** ₹20,000 Cr+ (Armored giants, lower volatility).
  - **Mid Cap:** ₹5,000 – ₹20,000 Cr (Fast growth, medium heat).
  - **Small Cap:** < ₹5,000 Cr (Wild swings — 6-star risk!)."""

    if "rsi" in q:
        return """`[SCANNER LOCKED // RSI-14 TELEMETRY]`

📈 **Relative Strength Index (RSI - 14):**
Built by J. Welles Wilder, this gauge tracks price speed from 0 to 100:
- **RSI < 30–40 (Oversold Zone):** Sellers ran out of ammo — watch for a bounce play.
- **RSI > 65–70 (Overbought Zone):** Too much heat on the wire — ripe for profit-taking pullbacks."""

    if any(k in q for k in ("golden cross", "death cross", "sma", "moving average")):
        return """`[RADAR TRACE // SMA 50 vs SMA 200]`

📉 **Moving Average Crosses:**
- **SMA (Simple Moving Average):** Strips out daily street noise to reveal the true trendline.
- **🟢 Golden Cross:** 50-Day SMA breaks *above* 200-Day SMA — full green light bullish surge!
- **🔴 Death Cross:** 50-Day SMA drops *below* 200-Day SMA — bail out, bearish warning."""

    has_buy = any(k in q for k in ("buy", "khareed"))
    has_sell = any(k in q for k in ("sell", "bech"))

    if has_buy and has_sell:
        return """`[HEURISTIC MATRIX // BUY & SELL RULES]`

🎯 **Syndicate Rule-Based Trigger Logic:**
- **🟢 BUY (88% Confidence):** Triggers when **RSI < 40** AND **Close Price > 95% of 50-Day SMA**.
- **🔴 SELL (82% Confidence):** Triggers when **RSI > 65** OR **Close Price < 92% of 50-Day SMA**.
- **🟡 HOLD (65% Confidence):** Everything in between — wait on the getaway car."""

    if has_sell:
        return """`[RED ALERT // SELL SIGNAL PROTOCOL]`

🛑 **Synopsis Rule-Based SELL Signal Condition:**
1. **RSI > 65** (Momentum is redlining in overbought territory).
2. **OR Close Price < 92% of 50-Day SMA** (Support floor shattered).
Either tripwire triggers a **SELL** order at **82% Confidence** to protect your stash!"""

    if has_buy or any(k in q for k in ("signal", "logic")):
        return """`[GREEN LIGHT // BUY SIGNAL PROTOCOL]`

🎯 **Synopsis Rule-Based BUY Signal Condition:**
Under the BCC 351 Mini Project matrix:
1. **RSI < 40** (Target is oversold / coiled for bounce).
2. **Close Price > 95% of 50-Day SMA** (Structural support is holding strong).
When both tripwires align, the terminal flashes **BUY** at **88% Confidence**!"""

    return f"""`[LESTER // ENCRYPTED TERMINAL ONLINE]`

🕶️ Intercepted query: *"{query}"*.

Run one of these intel lookups on the terminal:
- 📊 **"What is RSI and how does the BUY signal trigger?"**
- 🛑 **"How does the SELL signal work?"**
- 📈 **"Explain Golden Cross and Death Cross."**
- 💰 **"Suggest a ₹10,000 budget allocation."**
- 📉 **"What is P/E Ratio and EPS?"**"""
