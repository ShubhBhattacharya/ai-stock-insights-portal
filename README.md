# AI Stock Insights Portal 📈
### An Academic Technical-Analysis & Predictive Intelligence Dashboard for Indian Equity Markets
**B.Tech. II Year III Semester Mini Project (Course Code: BCC 351)**  
*Dronacharya Group of Institutions, Greater Noida | Affiliated to Dr. A.P.J. Abdul Kalam Technical University (AKTU), Lucknow*  
*Academic Session: 2025–2026*

---

## 👥 Project Team Members
| Name | University Roll Number | Primary Module Responsibility |
| :--- | :--- | :--- |
| **Rohit** | `2502301530051` | Data Pipeline, Technical Indicator Calculations & Confluence Engine |
| **Shubh** | `2502301530059` | Machine Learning Forecasting, Holdout Validation & Visualizations |
| **Utkarsh** | `2502301530069` | Dashboard Architecture, Dual Database Layer & Security Integration |

---

## 🚀 Executive Summary & Academic Objectives
The **AI Stock Insights Portal** is an end-to-end technical analysis and predictive intelligence web platform engineered in Python and Streamlit. Built for Indian equity markets (NSE tickers), it combines real-time financial data pipelines, industry-standard mathematical indicators, dynamic multi-factor signal confluence, machine learning price forecasting with rigorous chronological validation, paper trading with transactional persistence, and an interactive financial curriculum.

### Core Objectives
1. **Real-Time Market Data Pipeline:** Fetch reliable daily OHLCV market feeds for 30+ NSE equities with multi-threaded concurrent fetching (`concurrent.futures.ThreadPoolExecutor`) and resilient `@st.cache_data` caching.
2. **Technical Indicator Engine:** Formulate 14-period Relative Strength Index (RSI), 50-day and 200-day Simple Moving Averages (SMA), and Bollinger Bands ($\pm 2\sigma$, 20-period) using vectorized Pandas algorithms.
3. **Dynamic Confluence Scoring:** Replaced static percentages with a 5-factor technical confluence algorithm (0–100%) evaluating RSI, short/long-term trend alignment, Bollinger Band position, and volume pulse.
4. **Machine Learning Trend Forecasting:** 7, 15, and 30-day price trend projection using Scikit-Learn with **rigorous chronological 80/20 train/test holdout validation**, out-of-sample MAE/RMSE/MAPE metrics, directional accuracy, and Naive Persistence baseline comparisons.
5. **Interactive Plotly Visualizations:** Multi-panel subplots featuring Candlestick bars, 50/200-SMA overlays, Bollinger Band envelopes, volume bars, and RSI oscillators with overbought/oversold boundaries.
6. **Dual-Backend Persistence:** Seamless support for cloud PostgreSQL via `DATABASE_URL` (with automatic fallback to SQLite WAL mode) delivering atomic portfolio accounting, trade ledgers, and deduplicated price alerts.
7. **Virtual Paper Trading Simulator:** Risk-free portfolio execution initialized with ₹1,00,000 virtual capital, weighted-average price tracking, and persistent trade history.
8. **Modern Portfolio Risk Optimizer:** Annualized volatility, Sharpe Ratio (benchmarked against 6.5% sovereign risk-free rate), and dynamic asset return correlation matrix heatmaps.
9. **Interactive Financial Tutor:** Natural language query resolution with explicit NSE ticker extraction, Hinglish conversational handling, and fallback offline rule-based reasoning.
10. **Three Immersion Themes:** High-contrast Default Pro Standard, 80s Synthwave Vice City Edition, and Post-Apocalyptic Doomsday Bunker Edition.

---

## 🧠 Decision & Signal Engine (Dynamic Confluence Architecture)

The portal evaluates market conditions using transparent technical indicators combined with a dynamic 5-factor Confluence Score:

| Indicator / Condition | Rule Logic | Confluence Contribution |
| :--- | :--- | :--- |
| **RSI Momentum** | $\text{RSI} < 35$ (Oversold Accumulation) or $\text{RSI} > 65$ (Overbought Exhaustion) | +25 pts |
| **50-Day Trend** | Price position relative to 50-day SMA ($Close > 0.95 \times \text{SMA}_{50}$) | +25 pts |
| **200-Day Macro Trend** | Long-term institutional regime ($Close > \text{SMA}_{200}$) | +20 pts |
| **Bollinger Volatility** | Compression near Lower Band (Value) or Upper Band (Stretched) | +15 pts |
| **Volume Confirmation** | Current volume exceeding 20-day moving average volume | +15 pts |

*Confluence scores range from 50% (baseline consolidation) up to 95%+ (high-conviction multi-indicator confluence).*

---

## 🔬 Machine Learning Evaluation Methodology

Unlike simple curve fitting, the portal enforces academic rigor in price forecasting:
- **Zero Future-Data Leakage:** Data is partitioned strictly chronologically (first 80% train bars, final 20% holdout test bars).
- **Out-of-Sample Metrics:** Holdout Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), Mean Absolute Percentage Error (MAPE), and Directional Accuracy are computed solely on unseen data.
- **Benchmark Comparison:** All ML predictions are benchmarked against a **Naive Persistence (Random Walk)** baseline ($Price_t = Price_{t-1}$).
- **Non-Negative Guardrails:** Predictions are bounded by $\max(P, 0.01)$ to prevent non-physical negative price projections.
- **Data Thresholds:** Requires at least 25 historical trading bars; returns an honest insufficient data status if historical data is limited.

---

## 🏗️ Architectural Topology

```mermaid
flowchart TD
    A["User Presentation Layer<br/>(Streamlit, Responsive Glassmorphism Cards, Dark/Vice/Doomsday Themes)"]
    B["Authentication & Security Gate<br/>(Argon2/PBKDF2 Hashing, 12+ Char Policy, Role Sanitization)"]
    C["Data-Access & Fetching Engine<br/>(yfinance API, ThreadPoolExecutor, Resilient Cache)"]
    D["Quantitative Analytics Layer<br/>(RSI-14, SMA-50, SMA-200, Bollinger Bands, Dynamic Confluence)"]
    E["Machine Learning & Holdout Engine<br/>(Scikit-Learn Linear Regression, 80/20 Chronological Split, Naive Baseline)"]
    F["Dual-Engine Persistence Layer<br/>(PostgreSQL via DATABASE_URL / SQLite WAL Mode, Atomic Transactions)"]
    G["Visualization Engine<br/>(Plotly Subplots: Candlestick, Overlays, Volume, RSI Oscillators)"]

    A --> B
    B --> C
    C --> D
    D --> E
    D --> G
    A --> F
```

---

## 💻 Installation & Setup

### Prerequisites
- Python 3.10, 3.11, or 3.12 installed on your system.

### 1. Clone the Repository
```bash
git clone https://github.com/ShubhBhattacharya/ai-stock-insights-portal.git
cd ai-stock-insights-portal
```

### 2. Install Required Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Database (Optional Cloud Persistence)
- By default, the application runs using **SQLite with WAL mode enabled** at `data/portal.db` (zero setup required).
- For cloud PostgreSQL persistence, set the `DATABASE_URL` environment variable or Streamlit secret:
  ```bash
  export DATABASE_URL="postgresql://username:password@hostname:5432/dbname"
  ```

### 4. Run the Streamlit Application
```bash
streamlit run app.py
```
Access the application in your browser at `http://localhost:8501`.

---

## 🧪 Comprehensive Test Suite (Quality Assurance)

The project includes 42 automated unit and integration tests covering security, database transactions, financial math, machine learning, and natural language parsing.

Run all tests:
```bash
python -m pytest tests/ -v
```

### Test Coverage Highlights:
- **Authentication & Security (`tests/test_auth.py`):** PBKDF2/Argon2 hashing, constant-time comparisons, 12+ character complexity enforcement, unauthorized admin role sanitization, and non-bypass authentication integrity.
- **Database Transactions (`tests/test_db.py`):** Atomic buy/sell portfolio balance adjustments, weighted average cost accounting, insufficient funds rejection, unowned share sale protection, alert deduplication, and inline trigger edits.
- **Financial Math (`tests/test_financial_calculations.py`):** Annualized Sharpe Ratio, zero-volatility safeguards, and correlation matrix symmetry.
- **ML Forecasting (`tests/test_forecasting.py`):** Chronological holdout validation, out-of-sample error tracking, naive persistence comparisons, non-negative price bounds, and insufficient data handling.
- **Market Data (`tests/test_market_data.py`):** NSE ticker sanitization, OHLCV normalization, technical indicator bounds, and confluence scoring.
- **AI Tutor (`tests/test_tutor.py`):** Natural language entity extraction, Hinglish translation, speech sanitization, and educational disclaimers.

---

## 🔐 Authentication & Seeded Demo Accounts

Security policies strictly require 12+ character complex credentials. Pre-seeded demo accounts are provided for academic evaluation:

| Username | Clearance Password | Assigned Role | Purpose |
| :--- | :--- | :--- | :--- |
| **`evaluator`** | `EvaluatorDemo#2026!` | `evaluator` | Academic examination & demo evaluation |
| **`shubh`** | `ShubhPortfolio#2026!` | `user` | Team member workspace |
| **`rohit`** | `RohitIndicator#2026!` | `user` | Team member workspace |
| **`utkarsh`** | `UtkarshArchitect#2026!` | `user` | Team member workspace |

*Self-registration is available on the Sign-In tab; all public registrations are assigned the `user` role with isolated portfolio records.*

---

## 📂 Project Directory Structure

```
ai-stock-insights-portal/
├── .streamlit/
│   └── config.toml                     # Streamlit theme configuration & telemetry settings
├── app.py                              # Central application router & navigation orchestration
├── requirements.txt                    # Pinned production dependencies
├── README.md                           # Master project documentation
├── AI stocks prediction app (2).pdf    # Official AKTU BCC 351 Mini Project Synopsis
├── data/
│   └── portal.db                       # SQLite WAL database (auto-generated in local mode)
├── tests/                              # Automated pytest suite (42 tests)
│   ├── test_auth.py
│   ├── test_db.py
│   ├── test_financial_calculations.py
│   ├── test_forecasting.py
│   ├── test_market_data.py
│   └── test_tutor.py
└── src/
    ├── constants.py                    # NSE universe, seeded credentials & team metadata
    ├── state.py                        # Streamlit session state initializer
    ├── styles.py                       # Modern CSS styling, Vice City theme, responsive cards
    ├── services/
    │   ├── db.py                       # Dual-backend database engine (PostgreSQL / SQLite WAL)
    │   ├── market_data.py              # yfinance OHLCV, indicator math & confluence engine
    │   ├── forecasting.py              # Scikit-Learn regression & chronological validation
    │   ├── reporting.py                # Executive technical analysis text report generator
    │   ├── tutor.py                    # NLP entity parsing & educational response engine
    │   └── voice_service.py            # Speech recognition & Whisper voice controls
    └── views/
        ├── auth.py                     # Secure login, registration & evaluator access
        ├── single_stock.py             # Candlestick charts, indicators & ML holdout display
        ├── market_overview.py          # Parallel multi-stock scanner & signal table
        ├── comparison.py               # Head-to-head two-stock normalized performance
        ├── paper_trading.py            # Virtual portfolio management & order execution
        ├── risk_optimizer.py           # Volatility, Sharpe ratio & correlation heatmaps
        ├── price_alerts.py             # Price threshold triggers & inline editor
        ├── ai_tutor.py                 # Interactive financial learning chatbot
        └── synopsis.py                 # Academic syllabus, course codes & credits
```

---

## ⚖️ Regulatory & Academic Disclaimer
*This software dashboard is developed strictly for educational, research, and academic evaluation purposes in partial fulfillment of the B.Tech Degree (Course Code: BCC 351) at Dronacharya Group of Institutions. The platform does NOT provide certified investment advisory services, SEBI-registered portfolio management, or guaranteed stock price predictions. Equity investments are subject to market risks.*
