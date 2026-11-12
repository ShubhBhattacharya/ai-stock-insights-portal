"""Application-wide constants, stock universe, and configuration values."""

INITIAL_VIRTUAL_CAPITAL: float = 100_000.0
RISK_FREE_RATE_PCT: float = 6.5
MIN_HISTORY_ROWS: int = 30

DEFAULT_USERS: dict[str, str] = {
    "admin": "admin123",
    "shubh": "shubh123",
    "rohit": "rohit123",
    "utkarsh": "utkarsh123",
}

NAV_ITEMS: list[str] = [
    "📊 Market Overview",
    "🤖 Single Stock AI & ML Prediction",
    "⚖️ Two-Stock Comparison",
    "💼 Virtual Paper Trading",
    "🎯 Portfolio Risk Optimizer",
    "🚨 Price Alerts",
    "🎓 AI Stock Tutor & Chatbot",
    "📜 Project Synopsis & Credits",
]

# Comprehensive list of verified active NSE equities
NSE_STOCKS: dict[str, str] = {
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

TEAM_MEMBERS: list[dict[str, str]] = [
    {
        "Name": "Rohit",
        "Roll Number": "2502301530051",
        "Role": "Data Pipeline & Technical Indicator Engine",
    },
    {
        "Name": "Shubh",
        "Roll Number": "2502301530059",
        "Role": "Machine Learning Models & Visualizations",
    },
    {
        "Name": "Utkarsh",
        "Roll Number": "2502301530069",
        "Role": "Web Dashboard Architecture & Integration",
    },
]
