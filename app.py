import concurrent.futures
import datetime
import numpy as np
import pandas as pd
import pandas_ta as ta
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
from plotly.subplots import make_subplots
from sklearn.linear_model import LinearRegression

# ==============================================================================
# PAGE CONFIGURATION & CUSTOM STYLING
# ==============================================================================
st.set_page_config(
    page_title="AI Stock Insights Portal | NSE India",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    /* Metric Cards */
    div[data-testid="stMetricValue"] {
        font-size: 1.6rem;
        font-weight: 700;
    }
    
    /* Custom badge tags */
    .badge-buy {
        background-color: #0f5132;
        color: #75b798;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: bold;
        display: inline-block;
    }
    .badge-sell {
        background-color: #842029;
        color: #ea868f;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: bold;
        display: inline-block;
    }
    .badge-hold {
        background-color: #664d03;
        color: #ffda6a;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: bold;
        display: inline-block;
    }
    .project-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #065f46 100%);
        padding: 18px 24px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
    }
    .project-header h1 {
        margin: 0;
        font-size: 1.8rem;
        color: #ffffff;
    }
    .project-header p {
        margin: 4px 0 0 0;
        color: #cbd5e1;
        font-size: 0.95rem;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# COMPREHENSIVE LIST OF NSE EQUITIES (VERIFIED ACTIVE)
# ==============================================================================
NSE_STOCKS = {
    "Reliance Industries": "RELIANCE.NS",
    "Tata Consultancy Services (TCS)": "TCS.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "Infosys": "INFY.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "State Bank of India (SBI)": "SBIN.NS",
    "Bharti Airtel": "BHARTIARTL.NS",
    "Hindustan Unilever (HUL)": "HINDUNILVR.NS",
    "ITC Limited": "ITC.NS",
    "Larsen & Toubro (L&T)": "LT.NS",
    "Bajaj Finance": "BAJFINANCE.NS",
    "Asian Paints": "ASIANPAINT.NS",
    "Axis Bank": "AXISBANK.NS",
    "Adani Enterprises": "ADANIENT.NS",
    "Adani Ports": "ADANIPORTS.NS",
    "Apollo Hospitals": "APOLLOHOSP.NS",
    "Bajaj Auto": "BAJAJ-AUTO.NS",
    "Bajaj Finserv": "BAJAJFINSV.NS",
    "Bharat Petroleum (BPCL)": "BPCL.NS",
    "Britannia Industries": "BRITANNIA.NS",
    "Cipla": "CIPLA.NS",
    "Coal India": "COALINDIA.NS",
    "Coforge": "COFORGE.NS",
    "Divi's Laboratories": "DIVISLAB.NS",
    "Dr. Reddy's Laboratories": "DRREDDY.NS",
    "Eicher Motors": "EICHERMOT.NS",
    "Eternal (Zomato)": "ETERNAL.NS",
    "Grasim Industries": "GRASIM.NS",
    "HCL Technologies": "HCLTECH.NS",
    "HDFC Life": "HDFCLIFE.NS",
    "Hero MotoCorp": "HEROMOTOCO.NS",
    "Hindalco Industries": "HINDALCO.NS",
    "IndusInd Bank": "INDUSINDBK.NS",
    "JSW Steel": "JSWSTEEL.NS",
    "Kotak Mahindra Bank": "KOTAKBANK.NS",
    "Mahindra & Mahindra (M&M)": "M&M.NS",
    "Maruti Suzuki": "MARUTI.NS",
    "Nestle India": "NESTLEIND.NS",
    "NTPC": "NTPC.NS",
    "Oil & Natural Gas Corp (ONGC)": "ONGC.NS",
    "Persistent Systems": "PERSISTENT.NS",
    "Power Grid Corporation": "POWERGRID.NS",
    "SBI Life Insurance": "SBILIFE.NS",
    "Sun Pharma": "SUNPHARMA.NS",
    "Tata Consumer Products": "TATACONSUM.NS",
    "Tata Motors PV": "TMPV.NS",
    "Tata Power": "TATAPOWER.NS",
    "Tata Steel": "TATASTEEL.NS",
    "Tech Mahindra": "TECHM.NS",
    "Titan Company": "TITAN.NS",
    "UltraTech Cement": "ULTRACEMCO.NS",
    "UPL Limited": "UPL.NS",
    "Wipro": "WIPRO.NS",
}

# ==============================================================================
# SESSION STATE INITIALIZATION
# ==============================================================================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "username" not in st.session_state:
    st.session_state["username"] = "Guest User"
if "users" not in st.session_state:
    st.session_state["users"] = {
        "admin": "admin123",
        "shubh": "shubh123",
        "rohit": "rohit123",
        "utkarsh": "utkarsh123",
    }
if "cash_balance" not in st.session_state:
    st.session_state["cash_balance"] = 100000.0  # ₹1 Lakh Virtual Starting Capital
if "portfolio" not in st.session_state:
    st.session_state["portfolio"] = {}
if "trade_history" not in st.session_state:
    st.session_state["trade_history"] = []
if "alerts" not in st.session_state:
    st.session_state["alerts"] = []

# ==============================================================================
# DATA ACCESS & CACHING LAYER
# ==============================================================================
@st.cache_data(ttl=300, show_spinner=False)
def fetch_stock_dataframe(ticker_symbol):
    """
    Downloads 1 year of historical OHLCV data from Yahoo Finance.
    Cleans multi-index headers, validates min 50 rows, handles fallback extensions.
    """
    ticker_clean = ticker_symbol.strip().upper()
    
    # Format symbol for Indian equities if no suffix specified
    candidates = []
    if "." in ticker_clean:
        candidates.append(ticker_clean)
    else:
        candidates.append(ticker_clean + ".NS")
        candidates.append(ticker_clean + ".BO")
        candidates.append(ticker_clean)

    for sym in candidates:
        try:
            df = yf.download(
                sym,
                period="1y",
                interval="1d",
                auto_adjust=False,
                progress=False,
            )
            if df is not None and not df.empty and len(df) >= 30:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                # Drop rows where Close is NaN
                df = df.dropna(subset=["Close"])
                return df, sym
        except Exception:
            continue

    # Fallback to Ticker object history
    for sym in candidates:
        try:
            t = yf.Ticker(sym)
            df = t.history(period="1y")
            if df is not None and not df.empty and len(df) >= 30:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                df = df.dropna(subset=["Close"])
                return df, sym
        except Exception:
            continue

    return pd.DataFrame(), ticker_clean


# ==============================================================================
# ANALYTICS & DECISION LAYER (RULE-BASED SIGNAL ENGINE - SYNOPSIS COMPLIANT)
# ==============================================================================
@st.cache_data(ttl=300, show_spinner=False)
def get_stock_analysis(ticker_symbol):
    """
    Computes technical indicators and rule-based decision logic matching the
    project synopsis:
    - RSI(14)
    - SMA(50)
    - SMA(200)
    
    Rules:
      * BUY (Confidence: 88%): RSI < 40 and Close > 95% of SMA_50
        "Oversold condition near moving-average support"
      * SELL (Confidence: 82%): RSI > 65 OR Close < 92% of SMA_50
        "Overbought condition or notable break below SMA support"
      * HOLD (Confidence: 65%): All other cases
        "Consolidation or no strong trigger"
    """
    try:
        df, formatted_ticker = fetch_stock_dataframe(ticker_symbol)
        if df.empty or len(df) < 30:
            return None, f"Insufficient or unavailable market data for '{ticker_symbol}'."

        close_series = df["Close"].astype(float)

        # Technical Indicators via pandas_ta
        rsi_series = ta.rsi(close_series, length=14)
        sma50_series = ta.sma(close_series, length=min(50, len(df) - 1))
        sma200_series = ta.sma(close_series, length=min(200, len(df) - 1))
        bbands = ta.bbands(close_series, length=20, std=2)

        df["RSI"] = rsi_series
        df["SMA_50"] = sma50_series
        df["SMA_200"] = sma200_series
        if bbands is not None and not bbands.empty:
            df["BBL"] = bbands.iloc[:, 0]
            df["BBM"] = bbands.iloc[:, 1]
            df["BBU"] = bbands.iloc[:, 2]

        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest

        close = float(latest["Close"])
        prev_close = float(prev["Close"])
        day_change = close - prev_close
        day_change_pct = (day_change / prev_close) * 100 if prev_close else 0.0

        rsi = float(latest["RSI"]) if not pd.isna(latest["RSI"]) else 50.0
        sma50 = float(latest["SMA_50"]) if not pd.isna(latest["SMA_50"]) else close
        sma200 = float(latest["SMA_200"]) if not pd.isna(latest["SMA_200"]) else close
        volume = float(latest["Volume"])
        high_52w = float(df["High"].max())
        low_52w = float(df["Low"].min())

        reasons = []
        # RSI Analysis
        if rsi < 35:
            reasons.append(
                f"🟢 **RSI Oversold ({rsi:.1f}):** Momentum indicates potential undervaluation and buying interest."
            )
        elif rsi > 70:
            reasons.append(
                f"🔴 **RSI Overbought ({rsi:.1f}):** Momentum is stretched near upper levels; risk of profit-taking."
            )
        else:
            reasons.append(
                f"🟡 **Neutral RSI ({rsi:.1f}):** Price momentum is within normal bounds (35-70)."
            )

        # 50-day SMA Support/Resistance
        sma50_ratio = (close / sma50) * 100
        if close >= sma50:
            reasons.append(
                f"🟢 **Above 50-Day SMA (₹{sma50:.2f}):** Trading at {sma50_ratio:.1f}% of SMA50, signaling positive short-term trend."
            )
        else:
            reasons.append(
                f"🔴 **Below 50-Day SMA (₹{sma50:.2f}):** Trading at {sma50_ratio:.1f}% of SMA50, exhibiting short-term technical resistance."
            )

        # Golden Cross / Long-term Trend
        if sma50 > sma200:
            reasons.append(
                f"🟢 **Bullish Alignment:** 50-Day SMA (₹{sma50:.2f}) is above 200-Day SMA (₹{sma200:.2f})."
            )
        else:
            reasons.append(
                f"🔴 **Bearish Alignment:** 50-Day SMA (₹{sma50:.2f}) remains below 200-Day SMA (₹{sma200:.2f})."
            )

        # Rule-Based Decision Logic as specified in Synopsis:
        if rsi < 40 and close > (sma50 * 0.95):
            signal = "BUY"
            confidence = 88
            final_reason = "Oversold condition near moving-average support. Attractive accumulation opportunity."
        elif rsi > 65 or close < (sma50 * 0.92):
            signal = "SELL"
            confidence = 82
            final_reason = "Overbought condition or notable break below 50-day SMA support. Risk mitigation recommended."
        else:
            signal = "HOLD"
            confidence = 65
            final_reason = "Consolidation or no strong directional trigger. Maintain current exposure."

        return {
            "symbol": formatted_ticker,
            "close": round(close, 2),
            "prev_close": round(prev_close, 2),
            "day_change": round(day_change, 2),
            "day_change_pct": round(day_change_pct, 2),
            "volume": int(volume),
            "high_52w": round(high_52w, 2),
            "low_52w": round(low_52w, 2),
            "rsi": round(rsi, 2),
            "sma50": round(sma50, 2),
            "sma200": round(sma200, 2),
            "signal": signal,
            "confidence": confidence,
            "reasons": reasons,
            "final_reason": final_reason,
            "df": df,
        }, None
    except Exception as e:
        return None, str(e)


# ==============================================================================
# MACHINE LEARNING PRICE FORECAST ENGINE
# ==============================================================================
def predict_stock_prices(df, days=30):
    """
    Fits a Scikit-Learn Linear Regression model over historical day indices
    to project future price trends for the specified horizon (7, 15, or 30 days).
    """
    df_clean = df.dropna(subset=["Close"]).copy()
    if len(df_clean) < 15:
        return pd.DataFrame(), 0.0

    X = np.arange(len(df_clean)).reshape(-1, 1)
    y = df_clean["Close"].values.astype(float)

    model = LinearRegression()
    model.fit(X, y)
    r2_score = model.score(X, y)

    future_X = np.arange(len(df_clean), len(df_clean) + days).reshape(-1, 1)
    predictions = model.predict(future_X).flatten()

    last_date = df_clean.index[-1]
    future_dates = [
        last_date + datetime.timedelta(days=i) for i in range(1, days + 1)
    ]

    pred_df = pd.DataFrame(
        {"Date": future_dates, "Predicted_Close": np.round(predictions, 2)}
    )
    pred_df.set_index("Date", inplace=True)
    return pred_df, round(r2_score, 3)


# ==============================================================================
# MARKET NEWS SENTIMENT ANALYZER (COMPATIBLE WITH YFINANCE >= 0.2.50)
# ==============================================================================
@st.cache_data(ttl=600, show_spinner=False)
def fetch_news_sentiment(ticker_symbol):
    """
    Fetches latest news feeds for the given ticker, extracts titles and URLs,
    and calculates rule-based market sentiment.
    """
    try:
        t = yf.Ticker(ticker_symbol)
        raw_news = t.news[:6] if t.news else []
        if not raw_news:
            return "Neutral 🟡", "No recent news feed available for this ticker.", []

        news_items = []
        for n in raw_news:
            title = n.get("title")
            url = n.get("link")
            publisher = n.get("publisher", "")
            
            # Check nested structure in recent yfinance updates
            content = n.get("content")
            if isinstance(content, dict):
                title = title or content.get("title")
                url = url or (content.get("canonicalUrl") or {}).get("url")
                provider = content.get("provider")
                if isinstance(provider, dict):
                    publisher = publisher or provider.get("displayName", "")

            if title:
                news_items.append({
                    "title": title,
                    "url": url or "#",
                    "publisher": publisher or "Market Wire",
                })

        if not news_items:
            return "Neutral 🟡", "News items had no parseable titles.", []

        positive_keywords = [
            "growth", "profit", "surge", "rise", "record", "gain", "buy", "bullish",
            "expansion", "beat", "rally", "upgrade", "dividend", "revenue", "order",
            "contracts", "milestone", "positive", "high"
        ]
        negative_keywords = [
            "fall", "loss", "drop", "decline", "slash", "risk", "bearish", "sell",
            "lawsuit", "penalty", "cut", "probe", "investigation", "downgrade",
            "crash", "plunge", "concern", "miss", "weak"
        ]

        pos_count = 0
        neg_count = 0
        for item in news_items:
            text = item["title"].lower()
            pos_count += sum(1 for w in positive_keywords if w in text)
            neg_count += sum(1 for w in negative_keywords if w in text)

        if pos_count > neg_count:
            sentiment = "Bullish / Positive 🟢"
        elif neg_count > pos_count:
            sentiment = "Bearish / Negative 🔴"
        else:
            sentiment = "Neutral / Balanced 🟡"

        summary = f"Scanned {len(news_items)} recent headlines (Positive cues: {pos_count}, Negative cues: {neg_count})."
        return sentiment, summary, news_items
    except Exception as e:
        return "Neutral 🟡", f"News feed unavailable: {str(e)}", []


# ==============================================================================
# EXECUTIVE TECHNICAL REPORT GENERATOR (.TXT)
# ==============================================================================
def generate_text_report(m):
    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = f"""================================================================================
AI STOCK INSIGHTS PORTAL - EXECUTIVE TECHNICAL REPORT
Academic Project: BCC 351 (Mini Project) | Dronacharya Group of Institutions
================================================================================
Ticker Symbol       : {m['symbol']}
Generated At        : {timestamp_str}
Current Market Price: INR {m['close']:,.2f}
Day Change          : INR {m['day_change']:+.2f} ({m['day_change_pct']:+.2f}%)
52-Week Range       : INR {m['low_52w']:,.2f} - INR {m['high_52w']:,.2f}
Trading Volume      : {m['volume']:,}

--------------------------------------------------------------------------------
1. TECHNICAL INDICATORS OVERVIEW
--------------------------------------------------------------------------------
- RSI (14 Periods)  : {m['rsi']}
- 50-Day SMA        : INR {m['sma50']:,.2f}
- 200-Day SMA       : INR {m['sma200']:,.2f}

--------------------------------------------------------------------------------
2. AI RULE-BASED DECISION & CONFIDENCE
--------------------------------------------------------------------------------
Final Signal        : {m['signal']}
Confidence Level    : {m['confidence']}%
Executive Rationale : {m['final_reason']}

--------------------------------------------------------------------------------
3. EXPLAINABLE TECHNICAL BREAKDOWN
--------------------------------------------------------------------------------
"""
    for r in m["reasons"]:
        cleaned = r.replace("🟢", "").replace("🔴", "").replace("🟡", "").replace("**", "")
        report += f"  * {cleaned}\n"

    report += f"""
================================================================================
DISCLAIMER:
This report is generated strictly for academic and educational purposes under
B.Tech Mini Project BCC 351 and must NOT be considered financial or investment advice.
================================================================================
"""
    return report


# ==============================================================================
# FAST PARALLEL BATCH FETCHER FOR MARKET OVERVIEW
# ==============================================================================
def fetch_batch_overview(stock_items):
    """
    Downloads stock data concurrently using ThreadPoolExecutor for lightning speed.
    """
    results = []
    
    def fetch_single(item):
        name, sym = item
        m, err = get_stock_analysis(sym)
        if m:
            return {
                "Company Name": name,
                "Symbol": sym.replace(".NS", "").replace(".BO", ""),
                "Price": m["close"],
                "Change %": m["day_change_pct"],
                "RSI": m["rsi"],
                "SMA 50": m["sma50"],
                "Signal": m["signal"],
                "Confidence": f"{m['confidence']}%",
                "Raw_Signal": m["signal"],
                "Raw_Change": m["day_change_pct"],
            }
        return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(fetch_single, item) for item in stock_items]
        for f in concurrent.futures.as_completed(futures):
            res = f.result()
            if res:
                results.append(res)

    return sorted(results, key=lambda x: x["Company Name"])


# ==============================================================================
# AI STOCK TUTOR CHATBOT ENGINE
# ==============================================================================
def generate_bot_response(query):
    q = query.lower()

    if any(k in q for k in ["budget", "10000", "5000", "50000", "invest", "recommend"]):
        return """💡 **Educational Portfolio Allocation Framework (e.g. ₹10,000 Budget):**

Risk diversification prevents catastrophic drawdowns. Here is a balanced asset allocation model:

* 🏦 **Large-Cap Bluechips (50-60% ~ ₹5,000 - ₹6,000):**
  - **State Bank of India (SBIN)** or **ITC Limited** (Consistent dividend stability and high liquidity).
* 🚀 **Growth & Technology Leaders (30% ~ ₹3,000):**
  - **Infosys / TCS** or **Tata Motors PV** (Long-term multi-year structural tailwinds).
* 🛡️ **Index ETFs (10-20% ~ ₹1,000 - ₹2,000):**
  - **NIFTYBEES** (Broad equity exposure across top 50 Indian companies).

📌 *Disciplined Rule:* Use systematic investment plans (SIPs) and never invest money you will need in the next 12 months!"""

    elif "p/e" in q or "pe ratio" in q:
        return """📊 **P/E Ratio (Price-to-Earnings):**
- **Formula:** Current Market Price ÷ Earnings Per Share (EPS).
- **Interpretation:** Indicates how much investors are willing to pay for ₹1 of annual earnings.
- **Benchmark:**
  - *Below Sector Average (< 20):* Potential undervaluation or value trap.
  - *Above Sector Average (> 40):* High growth expectations or overvalued."""

    elif "rsi" in q:
        return """📈 **RSI (Relative Strength Index - 14 Periods):**
- Developed by J. Welles Wilder, RSI measures the magnitude of recent price changes (0 to 100).
- **RSI < 30-40 (Oversold):** Sellers may be exhausted; watch for bullish reversals.
- **RSI > 65-70 (Overbought):** Buyers may be stretched; risk of profit-taking consolidation."""

    elif "golden cross" in q or "death cross" in q or "sma" in q or "moving average" in q:
        return """📉 **Moving Average Crosses (SMA 50 vs SMA 200):**
- **SMA (Simple Moving Average):** Smoothes out day-to-day noise to highlight the underlying trend.
- **🟢 Golden Cross:** Occurs when the 50-Day SMA crosses *above* the 200-Day SMA. Strong long-term bullish signal.
- **🔴 Death Cross:** Occurs when the 50-Day SMA crosses *below* the 200-Day SMA. Long-term bearish warning."""

    elif "buy" in q or "signal" in q or "logic" in q:
        return """🎯 **Synopsis Rule-Based BUY Signal Condition:**
Under the BCC 351 Mini Project rules:
1. **RSI < 40** (Stock is in oversold/attractive momentum territory).
2. **Close Price > 95% of 50-Day SMA** (Price is maintaining structural moving average support).
When both align, the portal emits a **BUY** signal with **88% Confidence**!"""

    elif "sell" in q:
        return """🛑 **Synopsis Rule-Based SELL Signal Condition:**
1. **RSI > 65** (Momentum overbought).
2. **OR Close Price < 92% of 50-Day SMA** (Severe breakdown below support).
When either triggers, the portal emits a **SELL** signal with **82% Confidence** to protect capital."""

    else:
        return f"""🤖 **AI Stock Tutor Response:**

You asked about: *"{query}"*.

I can help clarify technical concepts used in this project:
- 📊 **"What is RSI and how does the Buy signal trigger?"**
- 📈 **"Explain Golden Cross and Death Cross."**
- 💰 **"Suggest a ₹10,000 budget allocation for beginners."**
- 📉 **"What is the difference between 50 SMA and 200 SMA?"**"""


# ==============================================================================
# AUTHENTICATION PAGE
# ==============================================================================
def login_page():
    st.markdown("""
    <div class="project-header">
        <h1>📈 AI Stock Insights Portal</h1>
        <p>A Web-Based Technical-Analysis Dashboard for Indian Equity Markets | Mini Project BCC 351</p>
    </div>
    """, unsafe_allow_html=True)

    col_center = st.columns([1, 2, 1])[1]
    with col_center:
        st.subheader("🔐 User Portal Sign-In")
        
        # 1-Click Guest / Evaluator Button
        if st.button("⚡ 1-Click Guest / Evaluator Access (Demo Mode)", type="primary", use_container_width=True):
            st.session_state["authenticated"] = True
            st.session_state["username"] = "Academic Evaluator"
            st.rerun()

        st.markdown("<p style='text-align:center; color:gray;'>— OR SIGN IN WITH ACCOUNT —</p>", unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["Sign In", "Create Account"])

        with tab_login:
            email = st.text_input("Username", value="admin", key="login_username")
            password = st.text_input("Password", type="password", value="admin123", key="login_password")
            
            if st.button("Sign In to Portal", use_container_width=True):
                valid_pass = st.session_state["users"].get(email.strip().lower())
                if valid_pass and valid_pass == password:
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = email.capitalize()
                    st.rerun()
                else:
                    st.error("Invalid credentials. Try username: 'admin' and password: 'admin123' or use 1-Click Demo!")

        with tab_register:
            new_user = st.text_input("Choose Username", key="reg_username")
            new_pass = st.text_input("Choose Password", type="password", key="reg_password")
            confirm_pass = st.text_input("Confirm Password", type="password", key="reg_confirm")
            
            if st.button("Register New User", use_container_width=True):
                if not new_user or not new_pass:
                    st.error("All fields are required.")
                elif new_pass != confirm_pass:
                    st.error("Passwords do not match.")
                elif new_user.lower() in st.session_state["users"]:
                    st.error("Username already taken.")
                else:
                    st.session_state["users"][new_user.lower()] = new_pass
                    st.success(f"User '{new_user}' created successfully! You can now Sign In.")

        st.markdown("---")
        st.caption("🎓 **B.Tech Mini Project BCC 351** | Dronacharya Group of Institutions (AKTU) | Session 2025-26")


# ==============================================================================
# MAIN APPLICATION INTERFACE
# ==============================================================================
def main_dashboard():
    # Sidebar
    st.sidebar.markdown(f"### 👤 {st.session_state['username']}")
    st.sidebar.markdown(f"💰 Virtual Cash: **₹{st.session_state['cash_balance']:,.2f}**")
    
    # Portfolio Quick Status
    num_holdings = len(st.session_state["portfolio"])
    st.sidebar.caption(f"📁 Holdings: **{num_holdings} Active Stocks**")
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state["authenticated"] = False
        st.rerun()

    st.sidebar.markdown("---")
    
    app_mode = st.sidebar.radio(
        "Navigation",
        [
            "📊 Market Overview",
            "🤖 Single Stock AI & ML Prediction",
            "⚖️ Two-Stock Comparison",
            "💼 Virtual Paper Trading",
            "🎯 Portfolio Risk Optimizer",
            "🚨 Price Alerts",
            "🎓 AI Stock Tutor & Chatbot",
            "📜 Project Synopsis & Credits",
        ],
        index=0,
    )

    st.sidebar.markdown("---")
    st.sidebar.info("""
    **Project Info:**
    - Mini Project: BCC 351
    - Tech: Streamlit, yfinance, Plotly, pandas-ta
    - Market: NSE India
    """)

    # --------------------------------------------------------------------------
    # MODULE 1: MARKET OVERVIEW
    # --------------------------------------------------------------------------
    if app_mode == "📊 Market Overview":
        st.markdown("""
        <div class="project-header">
            <h1>📊 Indian Equities - Real-Time Market Overview</h1>
            <p>Live snapshot of major NSE stocks, technical indicators, and AI decision signals</p>
        </div>
        """, unsafe_allow_html=True)

        col_ctrl1, col_ctrl2 = st.columns([3, 1])
        with col_ctrl1:
            stock_count = st.slider("Select number of stocks to scan:", min_value=5, max_value=30, value=15, step=5)
        with col_ctrl2:
            st.write("")
            refresh = st.button("🔄 Refresh Data", type="primary", use_container_width=True)

        selected_items = list(NSE_STOCKS.items())[:stock_count]

        with st.spinner(f"Analyzing {stock_count} NSE Equities via concurrent threads..."):
            overview_data = fetch_batch_overview(selected_items)

        if overview_data:
            df_ov = pd.DataFrame(overview_data)
            
            # Summary Metrics Row
            total_scanned = len(df_ov)
            buy_signals = sum(1 for item in overview_data if item["Raw_Signal"] == "BUY")
            sell_signals = sum(1 for item in overview_data if item["Raw_Signal"] == "SELL")
            hold_signals = sum(1 for item in overview_data if item["Raw_Signal"] == "HOLD")

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Scanned", total_scanned)
            c2.metric("🟢 BUY Signals", buy_signals, delta=f"{(buy_signals/total_scanned)*100:.0f}%")
            c3.metric("🔴 SELL Signals", sell_signals, delta=f"-{(sell_signals/total_scanned)*100:.0f}%", delta_color="inverse")
            c4.metric("🟡 HOLD Signals", hold_signals, delta=f"{(hold_signals/total_scanned)*100:.0f}%", delta_color="off")

            st.markdown("---")

            # Filter Tab
            filter_choice = st.radio("Filter by Signal:", ["All", "BUY Only", "SELL Only", "HOLD Only"], horizontal=True)
            if filter_choice == "BUY Only":
                df_filtered = df_ov[df_ov["Raw_Signal"] == "BUY"]
            elif filter_choice == "SELL Only":
                df_filtered = df_ov[df_ov["Raw_Signal"] == "SELL"]
            elif filter_choice == "HOLD Only":
                df_filtered = df_ov[df_ov["Raw_Signal"] == "HOLD"]
            else:
                df_filtered = df_ov

            display_df = df_filtered.drop(columns=["Raw_Signal", "Raw_Change"])
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Price": st.column_config.NumberColumn(format="₹%.2f"),
                    "Change %": st.column_config.NumberColumn(format="%.2f%%"),
                    "RSI": st.column_config.NumberColumn(format="%.2f"),
                    "SMA 50": st.column_config.NumberColumn(format="₹%.2f"),
                }
            )

    # --------------------------------------------------------------------------
    # MODULE 2: SINGLE STOCK AI & ML PREDICTION
    # --------------------------------------------------------------------------
    elif app_mode == "🤖 Single Stock AI & ML Prediction":
        st.markdown("""
        <div class="project-header">
            <h1>🤖 Single Stock AI Analysis & ML Price Forecast</h1>
            <p>Comprehensive technical breakdown, rule-based decision logic, news sentiment, and linear projection</p>
        </div>
        """, unsafe_allow_html=True)

        col_s1, col_s2, col_s3 = st.columns([2, 1, 1])
        with col_s1:
            selected_name = st.selectbox("Select NSE Stock from List:", list(NSE_STOCKS.keys()), index=0)
            default_sym = NSE_STOCKS[selected_name]
        with col_s2:
            custom_sym = st.text_input("Or Enter Custom Symbol:", value=default_sym).upper().strip()
        with col_s3:
            forecast_days = st.selectbox("Forecast Horizon:", [7, 15, 30], index=2)

        metrics, error = get_stock_analysis(custom_sym)

        if error:
            st.error(f"❌ {error}")
            st.info("Tip: Ensure the symbol is a valid NSE/BSE ticker, e.g., 'RELIANCE.NS', 'TCS.NS', 'INFY.NS'.")
        elif metrics:
            df = metrics["df"]

            # Key Metrics Cards
            st.markdown("### 📌 Live Market Snapshot")
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Live Close", f"₹{metrics['close']:,.2f}", delta=f"{metrics['day_change']:+.2f} ({metrics['day_change_pct']:+.2f}%)")
            m2.metric("RSI (14)", f"{metrics['rsi']:.1f}")
            m3.metric("50-Day SMA", f"₹{metrics['sma50']:,.2f}")
            m4.metric("200-Day SMA", f"₹{metrics['sma200']:,.2f}")
            
            signal_color = "#0f5132" if metrics["signal"] == "BUY" else ("#842029" if metrics["signal"] == "SELL" else "#664d03")
            m5.metric("AI Signal", metrics["signal"], delta=f"{metrics['confidence']}% Confidence")

            st.markdown("---")

            # AI Decision Explanation Card
            col_dec1, col_dec2 = st.columns([3, 2])
            with col_dec1:
                st.subheader(f"🧠 Rule-Based Decision: {metrics['signal']} ({metrics['confidence']}% Confidence)")
                if metrics["signal"] == "BUY":
                    st.success(f"**Strategic Rationale:** {metrics['final_reason']}")
                elif metrics["signal"] == "SELL":
                    st.error(f"**Strategic Rationale:** {metrics['final_reason']}")
                else:
                    st.warning(f"**Strategic Rationale:** {metrics['final_reason']}")

                st.markdown("**Explainable Technical Triggers:**")
                for r in metrics["reasons"]:
                    st.markdown(f"- {r}")

            with col_dec2:
                st.subheader("📰 Market News Sentiment")
                sentiment, msg, news_items = fetch_news_sentiment(metrics["symbol"])
                st.markdown(f"**Sentiment Verdict:** {sentiment}")
                st.caption(msg)
                if news_items:
                    for item in news_items[:3]:
                        st.markdown(f"• [{item['title']}]({item['url']}) *({item['publisher']})*")

            # Report and Data Download Buttons
            st.markdown("---")
            dcol1, dcol2 = st.columns([1, 1])
            with dcol1:
                st.download_button(
                    label="📥 Download Executive Technical Report (.txt)",
                    data=generate_text_report(metrics),
                    file_name=f"{metrics['symbol']}_Technical_Report.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
            with dcol2:
                csv_data = df.to_csv().encode('utf-8')
                st.download_button(
                    label="📊 Export Historical Data & Indicators (.csv)",
                    data=csv_data,
                    file_name=f"{metrics['symbol']}_1Y_Data.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

            st.markdown("---")

            # ML Price Forecast & Plotly Visualizations
            st.subheader(f"📈 Interactive Technical Chart & {forecast_days}-Day ML Price Forecast")
            
            pred_df, r2_score = predict_stock_prices(df, days=forecast_days)
            st.caption(f"Machine Learning Model: Linear Trend Regression ($R^2$ Fit = {r2_score:.2f})")

            # Multi-panel Plotly Chart
            fig = make_subplots(
                rows=3,
                cols=1,
                shared_xaxes=True,
                vertical_spacing=0.04,
                subplot_titles=(
                    f"{metrics['symbol']} Price Candlesticks, SMAs & {forecast_days}-Day Forecast",
                    "Trading Volume",
                    "RSI (14-Period Oscillator)",
                ),
                row_heights=[0.6, 0.2, 0.2],
            )

            # Candlestick
            fig.add_trace(
                go.Candlestick(
                    x=df.index,
                    open=df["Open"],
                    high=df["High"],
                    low=df["Low"],
                    close=df["Close"],
                    name="OHLC Price",
                ),
                row=1, col=1,
            )

            # 50-Day SMA
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df["SMA_50"],
                    mode="lines",
                    name="50 SMA",
                    line=dict(color="#f59e0b", width=1.8),
                ),
                row=1, col=1,
            )

            # 200-Day SMA
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df["SMA_200"],
                    mode="lines",
                    name="200 SMA",
                    line=dict(color="#3b82f6", width=1.8),
                ),
                row=1, col=1,
            )

            # ML Forecast
            if not pred_df.empty:
                fig.add_trace(
                    go.Scatter(
                        x=pred_df.index,
                        y=pred_df["Predicted_Close"],
                        mode="lines+markers",
                        name=f"{forecast_days}-Day ML Forecast",
                        line=dict(color="#ec4899", width=2.2, dash="dash"),
                        marker=dict(size=4),
                    ),
                    row=1, col=1,
                )

            # Volume
            vol_colors = [
                "#10b981" if c >= o else "#ef4444"
                for c, o in zip(df["Close"], df["Open"])
            ]
            fig.add_trace(
                go.Bar(
                    x=df.index,
                    y=df["Volume"],
                    name="Volume",
                    marker_color=vol_colors,
                ),
                row=2, col=1,
            )

            # RSI Oscillator
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df["RSI"],
                    mode="lines",
                    name="RSI (14)",
                    line=dict(color="#8b5cf6", width=1.5),
                ),
                row=3, col=1,
            )

            # RSI threshold lines (70 overbought, 30 oversold)
            fig.add_hline(y=70, line_dash="dot", line_color="#ef4444", row=3, col=1)
            fig.add_hline(y=30, line_dash="dot", line_color="#10b981", row=3, col=1)

            fig.update_layout(
                template="plotly_dark",
                xaxis_rangeslider_visible=False,
                height=750,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=40, r=40, t=60, b=40),
            )
            st.plotly_chart(fig, use_container_width=True)

    # --------------------------------------------------------------------------
    # MODULE 3: TWO-STOCK COMPARISON ENGINE
    # --------------------------------------------------------------------------
    elif app_mode == "⚖️ Two-Stock Comparison":
        st.markdown("""
        <div class="project-header">
            <h1>⚖️ Two-Stock Technical Comparison Engine</h1>
            <p>Direct head-to-head comparison of indicators, signals, and normalized price performance</p>
        </div>
        """, unsafe_allow_html=True)

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            s1_name = st.selectbox("Select First Stock:", list(NSE_STOCKS.keys()), index=0)
            s1_sym = NSE_STOCKS[s1_name]
        with col_c2:
            s2_name = st.selectbox("Select Second Stock:", list(NSE_STOCKS.keys()), index=1)
            s2_sym = NSE_STOCKS[s2_name]

        if st.button("Run Head-to-Head Comparison", type="primary", use_container_width=True):
            with st.spinner("Fetching and comparing market data..."):
                m1, e1 = get_stock_analysis(s1_sym)
                m2, e2 = get_stock_analysis(s2_sym)

            if e1 or e2:
                st.error(f"Error fetching data: {e1 or e2}")
            elif m1 and m2:
                comp_table = {
                    "Metric": [
                        "Current Price",
                        "Day Change (%)",
                        "52-Week High",
                        "52-Week Low",
                        "RSI (14)",
                        "50-Day SMA",
                        "200-Day SMA",
                        "AI Signal",
                        "Confidence Score",
                    ],
                    s1_name: [
                        f"₹{m1['close']:,.2f}",
                        f"{m1['day_change_pct']:+.2f}%",
                        f"₹{m1['high_52w']:,.2f}",
                        f"₹{m1['low_52w']:,.2f}",
                        f"{m1['rsi']:.1f}",
                        f"₹{m1['sma50']:,.2f}",
                        f"₹{m1['sma200']:,.2f}",
                        m1["signal"],
                        f"{m1['confidence']}%",
                    ],
                    s2_name: [
                        f"₹{m2['close']:,.2f}",
                        f"{m2['day_change_pct']:+.2f}%",
                        f"₹{m2['high_52w']:,.2f}",
                        f"₹{m2['low_52w']:,.2f}",
                        f"{m2['rsi']:.1f}",
                        f"₹{m2['sma50']:,.2f}",
                        f"₹{m2['sma200']:,.2f}",
                        m2["signal"],
                        f"{m2['confidence']}%",
                    ],
                }

                st.subheader("📋 Comparative Metrics Table")
                st.table(pd.DataFrame(comp_table))

                # Normalized % Performance Chart
                st.subheader("📈 1-Year Normalized Percentage Return Comparison")
                df1 = m1["df"]["Close"]
                df2 = m2["df"]["Close"]

                norm1 = ((df1 / df1.iloc[0]) - 1) * 100
                norm2 = ((df2 / df2.iloc[0]) - 1) * 100

                fig_comp = go.Figure()
                fig_comp.add_trace(go.Scatter(x=norm1.index, y=norm1, mode="lines", name=f"{s1_name} (% Return)", line=dict(color="#3b82f6", width=2)))
                fig_comp.add_trace(go.Scatter(x=norm2.index, y=norm2, mode="lines", name=f"{s2_name} (% Return)", line=dict(color="#10b981", width=2)))

                fig_comp.update_layout(
                    template="plotly_dark",
                    title="Cumulative Return Comparison (%)",
                    yaxis_title="Return (%)",
                    height=450,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig_comp, use_container_width=True)

    # --------------------------------------------------------------------------
    # MODULE 4: VIRTUAL PAPER TRADING SIMULATOR
    # --------------------------------------------------------------------------
    elif app_mode == "💼 Virtual Paper Trading":
        st.markdown("""
        <div class="project-header">
            <h1>💼 Virtual Paper Trading Simulator</h1>
            <p>Practice trading live NSE equities with ₹1,00,000 risk-free virtual balance</p>
        </div>
        """, unsafe_allow_html=True)

        col_w1, col_w2, col_w3 = st.columns(3)
        col_w1.metric("Available Cash", f"₹{st.session_state['cash_balance']:,.2f}")
        
        # Calculate current total holdings value
        holdings_value = 0.0
        for sym, d in st.session_state["portfolio"].items():
            m, _ = get_stock_analysis(sym)
            curr = m["close"] if m else d["buy_price"]
            holdings_value += curr * d["qty"]

        total_net_worth = st.session_state["cash_balance"] + holdings_value
        total_pnl = total_net_worth - 100000.0
        total_pnl_pct = (total_pnl / 100000.0) * 100

        col_w2.metric("Portfolio Holdings Value", f"₹{holdings_value:,.2f}")
        col_w3.metric("Total Net Worth", f"₹{total_net_worth:,.2f}", delta=f"{total_pnl:+.2f} ({total_pnl_pct:+.2f}%)")

        st.markdown("---")

        # Order Execution Form
        st.subheader("🛒 Execute New Order")
        trade_name = st.selectbox("Select Stock to Trade:", list(NSE_STOCKS.keys()))
        trade_sym = NSE_STOCKS[trade_name]

        trade_metric, trade_err = get_stock_analysis(trade_sym)
        if trade_metric:
            live_price = trade_metric["close"]
            st.info(f"Live Price for **{trade_name} ({trade_sym})**: **₹{live_price:,.2f}** | Signal: **{trade_metric['signal']}**")

            col_o1, col_o2, col_o3 = st.columns([1, 1, 2])
            order_qty = col_o1.number_input("Shares Quantity", min_value=1, value=10, step=1)
            order_val = order_qty * live_price
            col_o3.write(f"**Total Transaction Value:** ₹{order_val:,.2f}")

            with col_o1:
                if st.button("🟢 BUY Shares", use_container_width=True):
                    if st.session_state["cash_balance"] >= order_val:
                        st.session_state["cash_balance"] -= order_val
                        if trade_sym in st.session_state["portfolio"]:
                            curr_q = st.session_state["portfolio"][trade_sym]["qty"]
                            curr_avg = st.session_state["portfolio"][trade_sym]["buy_price"]
                            new_q = curr_q + order_qty
                            new_avg = ((curr_q * curr_avg) + order_val) / new_q
                            st.session_state["portfolio"][trade_sym] = {"name": trade_name, "qty": new_q, "buy_price": new_avg}
                        else:
                            st.session_state["portfolio"][trade_sym] = {"name": trade_name, "qty": order_qty, "buy_price": live_price}
                        
                        st.session_state["trade_history"].append({
                            "Time": datetime.datetime.now().strftime("%H:%M:%S"),
                            "Action": "BUY",
                            "Stock": trade_name,
                            "Quantity": order_qty,
                            "Price": f"₹{live_price:,.2f}",
                            "Total": f"₹{order_val:,.2f}",
                        })
                        st.success(f"Bought {order_qty} shares of {trade_name} at ₹{live_price:,.2f}!")
                        st.rerun()
                    else:
                        st.error("Insufficient cash balance!")

            with col_o2:
                if st.button("🔴 SELL Shares", use_container_width=True):
                    if trade_sym in st.session_state["portfolio"] and st.session_state["portfolio"][trade_sym]["qty"] >= order_qty:
                        st.session_state["cash_balance"] += order_val
                        st.session_state["portfolio"][trade_sym]["qty"] -= order_qty
                        if st.session_state["portfolio"][trade_sym]["qty"] == 0:
                            del st.session_state["portfolio"][trade_sym]
                        
                        st.session_state["trade_history"].append({
                            "Time": datetime.datetime.now().strftime("%H:%M:%S"),
                            "Action": "SELL",
                            "Stock": trade_name,
                            "Quantity": order_qty,
                            "Price": f"₹{live_price:,.2f}",
                            "Total": f"₹{order_val:,.2f}",
                        })
                        st.success(f"Sold {order_qty} shares of {trade_name} at ₹{live_price:,.2f}!")
                        st.rerun()
                    else:
                        st.error("You do not hold enough shares of this stock to sell!")

        st.markdown("---")

        # Current Holdings Table
        st.subheader("📁 Current Portfolio Holdings")
        if st.session_state["portfolio"]:
            port_records = []
            for s_sym, data in st.session_state["portfolio"].items():
                m_info, _ = get_stock_analysis(s_sym)
                c_price = m_info["close"] if m_info else data["buy_price"]
                cur_val = c_price * data["qty"]
                pnl = (c_price - data["buy_price"]) * data["qty"]
                pnl_pct = ((c_price - data["buy_price"]) / data["buy_price"]) * 100

                port_records.append({
                    "Stock": data.get("name", s_sym),
                    "Symbol": s_sym.replace(".NS", ""),
                    "Quantity": data["qty"],
                    "Avg Buy Price": f"₹{data['buy_price']:,.2f}",
                    "Live Price": f"₹{c_price:,.2f}",
                    "Position Value": f"₹{cur_val:,.2f}",
                    "Unrealized P&L": f"₹{pnl:+,.2f} ({pnl_pct:+.2f}%)",
                })
            st.dataframe(pd.DataFrame(port_records), use_container_width=True, hide_index=True)
        else:
            st.info("No active holdings. Execute a BUY order above to start building your portfolio.")

        # Trade History Log
        if st.session_state["trade_history"]:
            with st.expander("📜 Order Execution Log"):
                st.dataframe(pd.DataFrame(st.session_state["trade_history"]), use_container_width=True, hide_index=True)

        if st.button("🔄 Reset Portfolio to ₹1,00,000 Starting Cash"):
            st.session_state["cash_balance"] = 100000.0
            st.session_state["portfolio"] = {}
            st.session_state["trade_history"] = []
            st.success("Portfolio reset successfully!")
            st.rerun()

    # --------------------------------------------------------------------------
    # MODULE 5: PORTFOLIO RISK OPTIMIZER
    # --------------------------------------------------------------------------
    elif app_mode == "🎯 Portfolio Risk Optimizer":
        st.markdown("""
        <div class="project-header">
            <h1>🎯 Dynamic Portfolio Risk & Correlation Analyzer</h1>
            <p>Analyze multi-stock annualized volatility, Sharpe ratio, and asset correlations</p>
        </div>
        """, unsafe_allow_html=True)

        selected_stocks = st.multiselect(
            "Select Basket of Equities to Analyze:",
            list(NSE_STOCKS.keys()),
            default=["Reliance Industries", "Tata Consultancy Services (TCS)", "HDFC Bank", "Infosys"],
        )

        if len(selected_stocks) < 2:
            st.warning("Please select at least 2 stocks to compute portfolio risk and correlation.")
        else:
            if st.button("Calculate Portfolio Risk Profile", type="primary"):
                with st.spinner("Analyzing returns and covariance matrix..."):
                    returns_dict = {}
                    for name in selected_stocks:
                        sym = NSE_STOCKS[name]
                        df_s, _ = fetch_stock_dataframe(sym)
                        if not df_s.empty:
                            returns_dict[name] = df_s["Close"].pct_change().dropna()

                    if len(returns_dict) >= 2:
                        returns_df = pd.DataFrame(returns_dict).dropna()
                        
                        # Annualized volatility for equal-weighted portfolio
                        num_assets = len(returns_df.columns)
                        weights = np.ones(num_assets) / num_assets
                        cov_matrix = returns_df.cov() * 252
                        port_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
                        port_volatility = np.sqrt(port_variance) * 100

                        # Mean annualized return
                        annual_returns = (returns_df.mean() * 252) * 100
                        port_return = float(np.dot(weights, annual_returns))
                        risk_free_rate = 6.5  # RBI repo rate proxy
                        sharpe_ratio = (port_return - risk_free_rate) / port_volatility if port_volatility > 0 else 0.0

                        c_r1, c_r2, c_r3 = st.columns(3)
                        c_r1.metric("Annualized Portfolio Volatility", f"{port_volatility:.2f}%")
                        c_r2.metric("Expected Annualized Return", f"{port_return:.2f}%")
                        c_r3.metric("Estimated Sharpe Ratio", f"{sharpe_ratio:.2f}")

                        st.markdown("---")
                        if port_volatility < 18:
                            st.success("🟢 **Conservative Risk Profile:** Low volatility, ideal for capital preservation.")
                        elif port_volatility < 28:
                            st.warning("🟡 **Moderate Risk Profile:** Balanced risk-reward structure.")
                        else:
                            st.error("🔴 **Aggressive Risk Profile:** High volatility basket; prone to sharp drawdowns.")

                        # Correlation Matrix Heatmap
                        st.subheader("🔥 Asset Correlation Heatmap")
                        corr_df = returns_df.corr()
                        fig_corr = px.imshow(
                            corr_df,
                            text_auto=".2f",
                            aspect="auto",
                            color_continuous_scale="RdBu_r",
                            title="Cross-Asset Return Correlation",
                        )
                        fig_corr.update_layout(template="plotly_dark", height=450)
                        st.plotly_chart(fig_corr, use_container_width=True)

    # --------------------------------------------------------------------------
    # MODULE 6: PRICE ALERTS
    # --------------------------------------------------------------------------
    elif app_mode == "🚨 Price Alerts":
        st.markdown("""
        <div class="project-header">
            <h1>🚨 Real-Time Price Alerts & Trigger System</h1>
            <p>Set threshold price targets with live trigger status indicators</p>
        </div>
        """, unsafe_allow_html=True)

        col_a1, col_a2, col_a3 = st.columns([2, 1, 1])
        with col_a1:
            alert_name = st.selectbox("Select Target Stock:", list(NSE_STOCKS.keys()))
            alert_sym = NSE_STOCKS[alert_name]
        with col_a2:
            direction = st.selectbox("Condition:", ["Crosses Above", "Falls Below"])
        with col_a3:
            target = st.number_input("Target Price (INR):", min_value=1.0, value=1500.0, step=10.0)

        if st.button("Set New Price Alert", type="primary"):
            st.session_state["alerts"].append({
                "name": alert_name,
                "symbol": alert_sym,
                "condition": direction,
                "target": target,
                "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            })
            st.success(f"Alert set: When {alert_name} {direction.lower()} ₹{target:,.2f}")

        st.markdown("---")
        st.subheader("🔔 Active Alerts Monitor")
        if st.session_state["alerts"]:
            for idx, a in enumerate(st.session_state["alerts"]):
                m, _ = get_stock_analysis(a["symbol"])
                if m:
                    live_p = m["close"]
                    triggered = (live_p >= a["target"]) if a["condition"] == "Crosses Above" else (live_p <= a["target"])
                    status_badge = "🚨 TRIGGERED!" if triggered else "⏳ Monitoring..."

                    col_card, col_del = st.columns([5, 1])
                    with col_card:
                        if triggered:
                            st.error(f"**{a['name']} ({a['symbol']})** — Target: ₹{a['target']:,.2f} | Live: ₹{live_p:,.2f} ➔ **{status_badge}**")
                        else:
                            st.info(f"**{a['name']} ({a['symbol']})** — Target: ₹{a['target']:,.2f} | Live: ₹{live_p:,.2f} ➔ **{status_badge}**")
                    with col_del:
                        if st.button("Delete", key=f"del_{idx}"):
                            st.session_state["alerts"].pop(idx)
                            st.rerun()
        else:
            st.info("No active alerts. Configure one above to receive price alerts.")

    # --------------------------------------------------------------------------
    # MODULE 7: AI STOCK TUTOR & CHATBOT
    # --------------------------------------------------------------------------
    elif app_mode == "🎓 AI Stock Tutor & Chatbot":
        st.markdown("""
        <div class="project-header">
            <h1>🎓 AI Stock Tutor & Learning Assistant</h1>
            <p>Learn financial concepts, technical indicators, and ask investment strategy questions</p>
        </div>
        """, unsafe_allow_html=True)

        tab_course, tab_assistant = st.tabs(["📚 Interactive Learning Modules", "🤖 Ask AI Tutor"])

        with tab_course:
            st.subheader("📖 Curated Financial Curriculum")
            topic = st.selectbox(
                "Choose Concept to Explore:",
                [
                    "1. Stock Market Fundamentals (Equities, Exchanges & Bulls/Bears)",
                    "2. Technical Indicators (RSI, 50 SMA, 200 SMA & Golden Cross)",
                    "3. Decision Framework (Rules behind BUY, SELL & HOLD)",
                    "4. Valuation & Fundamentals (P/E Ratio, Market Cap, EPS)",
                    "5. Risk Management & Portfolio Allocation Rules",
                ],
            )

            st.markdown("---")
            if "1. Stock Market Fundamentals" in topic:
                st.markdown("""
                ### 🏢 Module 1: Stock Market Fundamentals
                - **Shares & Equities:** Buying a share gives you fractional ownership in that company's assets and future cash flows.
                - **NSE & BSE:** India's primary national exchanges regulated by SEBI.
                - **Market Trends:**
                  - 🟢 **Bull Market:** A sustained period of rising asset prices driven by economic optimism.
                  - 🔴 **Bear Market:** A prolonged decline in asset prices typically exceeding a 20% drop from recent peaks.
                """)
            elif "2. Technical Indicators" in topic:
                st.markdown("""
                ### 📈 Module 2: Core Technical Indicators
                - **Relative Strength Index (RSI - 14):** A momentum oscillator bounded between 0 and 100.
                  - *Oversold (< 35):* Potential bullish exhaustion of sellers.
                  - *Overbought (> 70):* Elevated risk of profit-taking.
                - **50-Day & 200-Day Simple Moving Averages (SMA):**
                  - **50 SMA:** Intermediate price trend indicator.
                  - **200 SMA:** Long-term institutional trend benchmark.
                  - **Golden Cross:** 50 SMA crossing above 200 SMA indicates strong bullish momentum.
                """)
            elif "3. Decision Framework" in topic:
                st.markdown("""
                ### 🎯 Module 3: Rule-Based Signal Framework (Synopsis Specification)
                The AI Stock Insights Portal uses transparent heuristics:
                - **BUY (88% Confidence):** Triggered when `RSI < 40` AND `Close > 95% of SMA_50`.
                - **SELL (82% Confidence):** Triggered when `RSI > 65` OR `Close < 92% of SMA_50`.
                - **HOLD (65% Confidence):** All other conditions (range-bound consolidation).
                """)
            elif "4. Valuation" in topic:
                st.markdown("""
                ### 📊 Module 4: Valuation & Company Fundamentals
                - **P/E (Price-to-Earnings):** Market Price per share divided by EPS. Shows what investors pay per rupee of profit.
                - **Market Capitalization:** Total outstanding shares multiplied by share price (Large-cap > ₹20,000 Cr).
                - **EPS (Earnings Per Share):** Net profit divided by common shares outstanding.
                """)
            elif "5. Risk Management" in topic:
                st.markdown("""
                ### 🛡️ Module 5: Risk Management & Allocation
                - **Diversification:** Never invest all capital in one stock or single sector.
                - **Stop-Loss Discipline:** Define max risk per trade (e.g. 5-8% drawdown threshold).
                - **Capital Preservation:** Compounding only works if you protect against major drawdowns.
                """)

        with tab_assistant:
            st.subheader("💬 Ask Your AI Financial Tutor")
            
            if "messages" not in st.session_state:
                st.session_state.messages = [
                    {"role": "assistant", "content": "Hello! I am your AI Stock Tutor. Ask me any question about technical indicators, financial metrics, or how the Buy/Sell rules work!"}
                ]

            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            if prompt := st.chat_input("E.g., How does the BUY signal trigger? Or: Recommend strategy for ₹10,000 budget..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                reply = generate_bot_response(prompt)
                with st.chat_message("assistant"):
                    st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})

    # --------------------------------------------------------------------------
    # MODULE 8: PROJECT SYNOPSIS & CREDITS
    # --------------------------------------------------------------------------
    elif app_mode == "📜 Project Synopsis & Credits":
        st.markdown("""
        <div class="project-header">
            <h1>📜 Academic Project Synopsis & Architecture</h1>
            <p>B.Tech. II Year III Semester Mini Project (BCC 351) | Dronacharya Group of Institutions</p>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("🎓 Project Credentials")
        st.markdown("""
        - **Course:** BCC 351 (Internship / Mini Project)
        - **Institution:** Dronacharya Group of Institutions, Greater Noida
        - **Affiliation:** Dr. A.P.J. Abdul Kalam Technical University (AKTU), Lucknow
        - **Academic Session:** 2025–2026
        """)

        st.subheader("👥 Project Team Members")
        st.markdown("""
        | Name | University Roll Number | Role |
        | :--- | :--- | :--- |
        | **Rohit** | `2502301530051` | Data Pipeline & Indicator Engine |
        | **Shubh** | `2502301530059` | Machine Learning Models & Visualizations |
        | **Utkarsh** | `2502301530069` | Web Dashboard Architecture & Integration |
        """)

        st.markdown("---")
        st.subheader("🏛️ Software Architecture (5-Layer Design)")
        st.markdown("""
        1. **Presentation Layer:** Built with Streamlit with responsive tabs, forms, metrics, Plotly figures, and multi-mode navigation.
        2. **Data-Access Layer:** Integrated with `yfinance` to retrieve historical daily OHLCV equity bars with caching (`@st.cache_data`).
        3. **Analytics Layer:** Utilizes `pandas-ta` to calculate 14-period RSI, 50-day SMA, 200-day SMA, and Bollinger Bands.
        4. **Decision Layer:** Executes rule-based heuristic logic to generate transparent BUY, SELL, or HOLD decisions with confidence scores.
        5. **Visualisation Layer:** Employs `plotly.graph_objects` to generate interactive multi-panel candlestick, volume, and RSI charts.
        """)

        st.markdown("---")
        st.info("⚠️ **Academic Disclaimer:** This software dashboard is created solely for educational and academic project purposes. Market data is obtained from public web APIs.")


# ==============================================================================
# ENTRY POINT ROUTING
# ==============================================================================
if st.session_state["authenticated"]:
    main_dashboard()
else:
    login_page()