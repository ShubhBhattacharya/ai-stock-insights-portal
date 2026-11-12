"""AI Stock Tutor educational curriculum and rule-based Q&A assistant."""

from __future__ import annotations

CURRICULUM_MODULES: dict[str, str] = {
    "1. Stock Market Fundamentals (Equities, Exchanges & Bulls/Bears)": """
### 🏢 Module 1: Stock Market Fundamentals
- **Shares & Equities:** Buying a share gives you fractional ownership in that company's assets and future cash flows.
- **NSE & BSE:** India's primary national exchanges regulated by SEBI.
- **Market Trends:**
  - 🟢 **Bull Market:** A sustained period of rising asset prices driven by economic optimism.
  - 🔴 **Bear Market:** A prolonged decline in asset prices typically exceeding a 20% drop from recent peaks.
""",
    "2. Technical Indicators (RSI, 50 SMA, 200 SMA & Golden Cross)": """
### 📈 Module 2: Core Technical Indicators
- **Relative Strength Index (RSI - 14):** A momentum oscillator bounded between 0 and 100.
  - *Oversold (< 35):* Potential bullish exhaustion of sellers.
  - *Overbought (> 70):* Elevated risk of profit-taking.
- **50-Day & 200-Day Simple Moving Averages (SMA):**
  - **50 SMA:** Intermediate price trend indicator.
  - **200 SMA:** Long-term institutional trend benchmark.
  - **Golden Cross:** 50 SMA crossing above 200 SMA indicates strong bullish momentum.
""",
    "3. Decision Framework (Rules behind BUY, SELL & HOLD)": """
### 🎯 Module 3: Rule-Based Signal Framework (Synopsis Specification)
The AI Stock Insights Portal uses transparent heuristics:
- **BUY (88% Confidence):** Triggered when `RSI < 40` AND `Close > 95% of SMA_50`.
- **SELL (82% Confidence):** Triggered when `RSI > 65` OR `Close < 92% of SMA_50`.
- **HOLD (65% Confidence):** All other conditions (range-bound consolidation).
""",
    "4. Valuation & Fundamentals (P/E Ratio, Market Cap, EPS)": """
### 📊 Module 4: Valuation & Company Fundamentals
- **P/E (Price-to-Earnings):** Market Price per share divided by EPS. Shows what investors pay per rupee of profit.
- **Market Capitalization:** Total outstanding shares multiplied by share price (Large-cap > ₹20,000 Cr).
- **EPS (Earnings Per Share):** Net profit divided by common shares outstanding.
""",
    "5. Risk Management & Portfolio Allocation Rules": """
### 🛡️ Module 5: Risk Management & Allocation
- **Diversification:** Never invest all capital in one stock or single sector.
- **Stop-Loss Discipline:** Define max risk per trade (e.g. 5–8% drawdown threshold).
- **Capital Preservation:** Compounding only works if you protect against major drawdowns.
""",
}

QUICK_PROMPTS: list[str] = [
    "How does the BUY signal trigger?",
    "Explain Golden Cross and Death Cross",
    "What is P/E Ratio and EPS?",
    "Suggest a ₹10,000 budget allocation",
]


def generate_bot_response(query: str) -> str:
    """Return an educational tutor response tailored to the user's question."""
    q = query.lower()

    if any(
        k in q
        for k in ("budget", "10000", "10,000", "5000", "50000", "invest", "recommend", "allocat", "long term")
    ):
        return """💡 **Educational Portfolio Allocation Framework (e.g. ₹10,000 Budget):**

Risk diversification prevents catastrophic drawdowns. Here is a balanced asset allocation model:

* 🏦 **Large-Cap Bluechips (50–60% ~ ₹5,000 – ₹6,000):**
  - **State Bank of India (SBIN)** or **ITC Limited** (Consistent dividend stability and high liquidity).
* 🚀 **Growth & Technology Leaders (30% ~ ₹3,000):**
  - **Infosys / TCS** or **Tata Motors PV** (Long-term multi-year structural tailwinds).
* 🛡️ **Index ETFs (10–20% ~ ₹1,000 – ₹2,000):**
  - **NIFTYBEES** (Broad equity exposure across top 50 Indian companies).

📌 *Disciplined Rule:* Use systematic investment plans (SIPs) and never invest money you will need in the next 12 months!"""

    if "p/e" in q or "pe ratio" in q:
        return """📊 **P/E Ratio (Price-to-Earnings):**
- **Formula:** Current Market Price ÷ Earnings Per Share (EPS).
- **Interpretation:** Indicates how much investors are willing to pay for ₹1 of annual earnings.
- **Benchmark:**
  - *Below Sector Average (< 20):* Potential undervaluation or value trap.
  - *Above Sector Average (> 40):* High growth expectations or overvalued."""

    if "eps" in q:
        return """💰 **EPS (Earnings Per Share):**
- **Formula:** Net Profit ÷ Total Outstanding Shares.
- **Interpretation:** Measures how much profit a company earns for each individual share. Consistent YoY EPS growth signals strong financial health."""

    if "market cap" in q:
        return """🏢 **Market Capitalization:**
- **Formula:** $\\text{Total Shares} \\times \\text{Current Share Price}$.
- **Categories (SEBI / Indian Market):**
  - **Large Cap:** ₹20,000 Cr+ (High stability, lower volatility).
  - **Mid Cap:** ₹5,000 – ₹20,000 Cr (Balanced growth & risk).
  - **Small Cap:** < ₹5,000 Cr (Higher volatility & risk/reward)."""

    if "rsi" in q:
        return """📈 **RSI (Relative Strength Index - 14 Periods):**
- Developed by J. Welles Wilder, RSI measures the magnitude of recent price changes (0 to 100).
- **RSI < 30–40 (Oversold):** Sellers may be exhausted; watch for bullish reversals.
- **RSI > 65–70 (Overbought):** Buyers may be stretched; risk of profit-taking consolidation."""

    if any(k in q for k in ("golden cross", "death cross", "sma", "moving average")):
        return """📉 **Moving Average Crosses (SMA 50 vs SMA 200):**
- **SMA (Simple Moving Average):** Smoothes out day-to-day noise to highlight the underlying trend.
- **🟢 Golden Cross:** Occurs when the 50-Day SMA crosses *above* the 200-Day SMA. Strong long-term bullish signal.
- **🔴 Death Cross:** Occurs when the 50-Day SMA crosses *below* the 200-Day SMA. Long-term bearish warning."""

    has_buy = any(k in q for k in ("buy", "khareed"))
    has_sell = any(k in q for k in ("sell", "bech"))

    if has_buy and has_sell:
        return """🎯 **Synopsis Rule-Based BUY & SELL Signal Conditions:**
- **🟢 BUY (88% Confidence):** Triggered when **RSI < 40** AND **Close Price > 95% of 50-Day SMA**.
- **🔴 SELL (82% Confidence):** Triggered when **RSI > 65** OR **Close Price < 92% of 50-Day SMA**.
- **🟡 HOLD (65% Confidence):** All other range-bound market conditions."""

    if has_sell:
        return """🛑 **Synopsis Rule-Based SELL Signal Condition:**
1. **RSI > 65** (Momentum overbought).
2. **OR Close Price < 92% of 50-Day SMA** (Severe breakdown below support).
When either triggers, the portal emits a **SELL** signal with **82% Confidence** to protect capital."""

    if has_buy or any(k in q for k in ("signal", "logic")):
        return """🎯 **Synopsis Rule-Based BUY Signal Condition:**
Under the BCC 351 Mini Project rules:
1. **RSI < 40** (Stock is in oversold/attractive momentum territory).
2. **Close Price > 95% of 50-Day SMA** (Price is maintaining structural moving average support).
When both align, the portal emits a **BUY** signal with **88% Confidence**!"""

    return f"""🤖 **AI Stock Tutor Response:**

You asked about: *"{query}"*.

I can help clarify technical concepts used in this project:
- 📊 **"What is RSI and how does the Buy signal trigger?"**
- 📈 **"Explain Golden Cross and Death Cross."**
- 💰 **"Suggest a ₹10,000 budget allocation for beginners."**
- 📉 **"What is P/E Ratio and EPS?"**"""
