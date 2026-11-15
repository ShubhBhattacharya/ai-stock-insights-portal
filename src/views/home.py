"""Reference Executive Landing Dashboard (Vice City Synthwave Edition).

Implements the pixel-perfect reference dashboard layout:
1. Collegiate Top Bar (Dronacharya Group of Institutions | BCCI 351 | Vice City Special Events)
2. Synthwave Retro Sunset Skyline Hero Banner with glowing title, badges, cursive neon script & pill search
3. Four Sleek Glassmorphism Quick Action Cards
4. Main 3-Column Dashboard Grid:
   - Market Overview (Nifty tabs, large metric 25,666.40, smooth green area chart, timeframe pills)
   - Stock Performance (interactive candlestick chart with clean timestamps)
   - AI Insights (Bullish Outlook card, checkmarked points, View All link)
5. Clean Footer Bar with college branding and quote
"""

from __future__ import annotations

import html
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.constants import NSE_STOCKS
from src.state import get_portal_theme, is_default_theme, is_doomsday


def _render_hero_skyline_svg() -> str:
    """Generate inline SVG for the Synthwave Sunset Skyline with palms, retro sun, and city silhouette."""
    return """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 320" preserveAspectRatio="none" style="width:100%; height:100%; position:absolute; top:0; left:0; pointer-events:none; border-radius:18px;">
      <defs>
        <linearGradient id="skyGrad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#0c041f" />
          <stop offset="45%" stop-color="#1f093d" />
          <stop offset="75%" stop-color="#400b4d" />
          <stop offset="100%" stop-color="#18042b" />
        </linearGradient>
        <linearGradient id="sunGrad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#fee440" />
          <stop offset="30%" stop-color="#ff7a00" />
          <stop offset="70%" stop-color="#ff2a85" />
          <stop offset="100%" stop-color="#7928ca" />
        </linearGradient>
        <linearGradient id="gridGrad" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="rgba(0, 245, 212, 0.45)" />
          <stop offset="100%" stop-color="rgba(255, 42, 133, 0.05)" />
        </linearGradient>
        <filter id="neonGlow" x="-30%" y="-30%" width="160%" height="160%">
          <feGaussianBlur stdDeviation="8" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      <!-- Background Sky -->
      <rect width="1200" height="320" fill="url(#skyGrad)" />

      <!-- Synthwave Striped Sun -->
      <g transform="translate(850, 150)" filter="url(#neonGlow)">
        <circle cx="0" cy="0" r="92" fill="url(#sunGrad)" />
        <!-- Horizontal Retro Slats across Sun -->
        <rect x="-92" y="8" width="184" height="4" fill="#18042b" />
        <rect x="-92" y="20" width="184" height="6" fill="#18042b" />
        <rect x="-92" y="34" width="184" height="8" fill="#18042b" />
        <rect x="-92" y="50" width="184" height="10" fill="#18042b" />
        <rect x="-92" y="68" width="184" height="12" fill="#18042b" />
      </g>

      <!-- Distant City Skyline Silhouettes -->
      <g fill="#0b0319" opacity="0.95">
        <rect x="680" y="160" width="35" height="160" />
        <rect x="720" y="140" width="28" height="180" />
        <rect x="752" y="120" width="42" height="200" />
        <polygon points="773,95 765,120 781,120" />
        <rect x="798" y="150" width="32" height="170" />
        <rect x="834" y="130" width="46" height="190" />
        <polygon points="857,105 848,130 866,130" />
        <rect x="884" y="155" width="28" height="165" />
        <rect x="916" y="135" width="36" height="185" />
        <rect x="956" y="110" width="44" height="210" />
        <polygon points="978,85 970,110 986,110" />
        <rect x="1004" y="145" width="32" height="175" />
        <rect x="1040" y="165" width="40" height="155" />
        <rect x="1084" y="138" width="30" height="182" />
        <rect x="1118" y="152" width="48" height="168" />
      </g>

      <!-- Distant Glowing Windows -->
      <g fill="#00f5d4" opacity="0.6">
        <circle cx="760" cy="135" r="1.5" /><circle cx="775" cy="145" r="1.5" />
        <circle cx="845" cy="140" r="1.5" /><circle cx="855" cy="155" r="1.5" />
        <circle cx="965" cy="120" r="1.5" /><circle cx="980" cy="130" r="1.5" />
        <circle cx="1090" cy="150" r="1.5" />
      </g>
      <g fill="#ff2a85" opacity="0.6">
        <circle cx="765" cy="165" r="1.5" /><circle cx="780" cy="175" r="1.5" />
        <circle cx="860" cy="170" r="1.5" /><circle cx="975" cy="160" r="1.5" />
        <circle cx="1050" cy="180" r="1.5" />
      </g>

      <!-- Wet Neon Reflective Road Horizon -->
      <rect x="0" y="275" width="1200" height="45" fill="#090214" />
      <line x1="0" y1="275" x2="1200" y2="275" stroke="#ff2a85" stroke-width="2.5" opacity="0.75" filter="url(#neonGlow)" />

      <!-- Palm Tree Silhouette (Right) -->
      <g fill="#070212" opacity="0.95" transform="translate(1000, 100) scale(0.9)">
        <path d="M110,220 C105,160 95,110 80,70 C88,110 96,160 100,220 Z" />
        <path d="M80,72 C105,55 130,60 145,80 C122,72 100,72 82,78 Z" />
        <path d="M78,70 C98,38 122,25 140,32 C118,38 98,52 82,72 Z" />
        <path d="M76,68 C78,32 92,10 108,4 C94,22 86,45 80,68 Z" />
        <path d="M74,70 C58,38 36,25 12,30 C36,38 58,52 72,72 Z" />
        <path d="M73,76 C44,62 18,70 2,88 C26,78 50,78 74,82 Z" />
      </g>

      <!-- Retro Sports Car Silhouette (Right Ground) -->
      <g fill="#05010a" transform="translate(900, 245) scale(0.68)">
        <!-- Car Body -->
        <path d="M20,38 L65,36 L115,18 L195,18 L245,34 L295,36 L305,44 L300,54 L20,54 Z" />
        <!-- Cabin Windows -->
        <path d="M120,20 L190,20 L235,33 L120,33 Z" fill="#ff2a85" opacity="0.35" />
        <!-- Wheels -->
        <circle cx="75" cy="54" r="16" fill="#020005" stroke="#00f5d4" stroke-width="2.5" />
        <circle cx="250" cy="54" r="16" fill="#020005" stroke="#ff2a85" stroke-width="2.5" />
        <!-- Rear Light Bar Glow -->
        <line x1="288" y1="38" x2="305" y2="40" stroke="#ff2a6d" stroke-width="3.5" filter="url(#neonGlow)" />
        <!-- Headlight Beam -->
        <polygon points="20,44 -50,60 -40,38" fill="url(#gridGrad)" opacity="0.45" />
      </g>
    </svg>
    """


def render_collegiate_top_bar() -> None:
    """Render the clean collegiate top bar with DGI branding, BCC 351, theme indicator & profile."""
    username = html.escape(str(st.session_state.get("username", "SHUBH")).upper())
    portal_theme = str(st.session_state.get("portal_theme", "GTA VI (Vice City)"))

    st.markdown(
        f"""
        <div class="ref-top-bar">
          <div class="ref-top-left">
            <span class="ref-top-crest">🏛️</span>
            <div>
              <div class="ref-top-title">★ Dronacharya Group of Institutions ★</div>
              <div class="ref-top-sub">BCCI 351 &nbsp;|&nbsp; Vice City Special Events</div>
            </div>
          </div>
          <div class="ref-top-right">
            <div class="ref-theme-toggle-pill" title="Active Theme: {portal_theme}">
              <span class="ref-sun-icon">☀️</span>
              <span class="ref-moon-icon">🌙</span>
            </div>
            <div class="ref-profile-pill">
              <span style="font-size:0.95rem;">👤</span>
              <span style="font-weight:700; letter-spacing:0.04em;">{username}</span>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero_banner(on_search_callback=None) -> None:
    """Render the synthwave retro sunset skyline hero banner, cursive lettering, and centered pill search bar."""
    svg_bg = _render_hero_skyline_svg()

    st.markdown(
        f"""
        <div class="ref-hero-banner">
          {svg_bg}
          <div class="ref-hero-content">
            <div class="ref-hero-left">
              <h1 class="ref-hero-title">
                <span class="glow-cyan">AI Stock Insights</span>
                <span class="glow-magenta">Portal</span>
              </h1>
              <div class="ref-hero-subtitle">Analyze • Predict • Invest Smarter</div>
              <div class="ref-hero-badges-pill">
                <span>⚡ Real-Time Analysis</span>
                <span class="pill-divider">|</span>
                <span>🤖 AI-Powered Insights</span>
                <span class="pill-divider">|</span>
                <span>📊 Professional Charts</span>
              </div>
            </div>
            <div class="ref-hero-right">
              <div class="ref-cursive-script">
                Invest Smart<br>Trade Better
              </div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Centered Pill Search Container
    st.markdown('<div class="ref-search-wrapper">', unsafe_allow_html=True)
    c_search, c_btn = st.columns([4, 1.2], gap="small")
    with c_search:
        search_query = st.text_input(
            "Search Ticker",
            placeholder="🔍 Enter Stock Ticker (e.g. RELIANCE, TCS, INFY)...",
            label_visibility="collapsed",
            key="home_hero_search_input",
        ).strip().upper()

    with c_btn:
        analyze_clicked = st.button(
            "Analyze Stock ➔",
            key="home_hero_analyze_btn",
            use_container_width=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    if analyze_clicked or (search_query and st.session_state.get("last_hero_query") != search_query):
        target_sym = search_query if search_query else "RELIANCE"
        if not target_sym.endswith(".NS") and not target_sym.endswith(".BO") and not target_sym.startswith("^"):
            target_sym = f"{target_sym}.NS"

        st.session_state["single_stock_symbol"] = target_sym
        st.session_state["single_stock_select"] = next(
            (k for k, v in NSE_STOCKS.items() if v == target_sym),
            "Reliance Industries",
        )
        st.session_state["last_hero_query"] = search_query
        if on_search_callback:
            on_search_callback(target_sym)


def render_four_quick_action_cards(on_navigate_callback=None) -> None:
    """Render exactly 4 sleek glassmorphism cards with smooth neon glowing borders."""
    cards_data = [
        {
            "icon": "📈",
            "variant": "cyan",
            "title": "Advanced Analysis",
            "subtitle": "Deep technical & fundamental analysis",
            "target": "📈 Stock Analysis",
            "btn_key": "btn_quick_act_1",
        },
        {
            "icon": "🧠",
            "variant": "magenta",
            "title": "AI Predictions",
            "subtitle": "Smart predictions with cutting-edge AI",
            "target": "📈 Stock Analysis",
            "btn_key": "btn_quick_act_2",
        },
        {
            "icon": "📊",
            "variant": "blue",
            "title": "Market Trends",
            "subtitle": "Real-time market trends & insights",
            "target": "🌐 Market Overview",
            "btn_key": "btn_quick_act_3",
        },
        {
            "icon": "⚡",
            "variant": "gold",
            "title": "Investment Ideas",
            "subtitle": "Expert-backed opportunities",
            "target": "🎯 Portfolio Risk Optimizer",
            "btn_key": "btn_quick_act_4",
        },
    ]

    cols = st.columns(4, gap="medium")
    for i, col in enumerate(cols):
        item = cards_data[i]
        with col:
            st.markdown(
                f"""
                <div class="ref-action-card ref-card-{item['variant']}">
                  <div class="ref-action-icon-box ref-icon-{item['variant']}">
                    <span>{item['icon']}</span>
                  </div>
                  <div class="ref-action-text-box">
                    <div class="ref-action-card-title">{item['title']}</div>
                    <div class="ref-action-card-sub">{item['subtitle']}</div>
                  </div>
                  <div class="ref-action-card-arrow">➔</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(
                f"Open {item['title']} ➔",
                key=item["btn_key"],
                use_container_width=True,
            ):
                if on_navigate_callback:
                    on_navigate_callback(item["target"])


def _generate_smooth_market_chart() -> go.Figure:
    """Generate high-fidelity smooth green area chart matching the Market Overview card in reference."""
    # 26 timepoints simulating bullish session from 09:15 to 15:30
    x_times = [
        "09:15", "09:30", "09:45", "10:00", "10:15", "10:30", "10:45", "11:00",
        "11:15", "11:30", "11:45", "12:00", "12:15", "12:30", "12:45", "13:00",
        "13:15", "13:30", "13:45", "14:00", "14:15", "14:30", "14:45", "15:00",
        "15:15", "15:30",
    ]
    # Smooth upward trajectory climbing to 25,666.40
    y_vals = [
        25530.0, 25545.0, 25528.0, 25555.0, 25580.0, 25565.0, 25590.0, 25610.0,
        25600.0, 25625.0, 25615.0, 25630.0, 25642.0, 25635.0, 25650.0, 25640.0,
        25655.0, 25648.0, 25660.0, 25652.0, 25668.0, 25660.0, 25672.0, 25665.0,
        25662.0, 25666.40,
    ]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x_times,
            y=y_vals,
            mode="lines",
            line=dict(color="#00f5d4", width=2.8, shape="spline", smoothing=1.1),
            fill="tozeroy",
            fillcolor="rgba(0, 245, 212, 0.12)",
            hoverinfo="x+y",
            hovertemplate="<b>%{x}</b><br>NIFTY: %{y:,.2f}<extra></extra>",
        )
    )
    fig.update_layout(
        height=190,
        margin=dict(l=0, r=0, t=6, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        xaxis=dict(
            visible=False,
            showgrid=False,
        ),
        yaxis=dict(
            visible=False,
            showgrid=False,
            range=[25480, 25700],
        ),
    )
    return fig


def _generate_candlestick_chart() -> go.Figure:
    """Generate high-fidelity interactive Candlestick chart matching the Stock Performance card in reference."""
    timestamps = ["09:15", "10:30", "11:45", "13:00", "14:15", "15:30"]
    detailed_times = [
        "09:15", "09:35", "09:55", "10:15", "10:35", "10:55",
        "11:15", "11:35", "11:55", "12:15", "12:35", "12:55",
        "13:15", "13:35", "13:55", "14:15", "14:35", "14:55",
        "15:15", "15:30",
    ]
    opens = [
        25240, 25260, 25290, 25310, 25350, 25330,
        25380, 25420, 25400, 25440, 25470, 25450,
        25490, 25520, 25550, 25570, 25610, 25590,
        25640, 25655,
    ]
    highs = [
        25270, 25300, 25325, 25365, 25375, 25390,
        25430, 25450, 25445, 25480, 25505, 25495,
        25535, 25560, 25585, 25625, 25640, 25650,
        25675, 25685,
    ]
    lows = [
        25220, 25245, 25270, 25295, 25320, 25310,
        25365, 25395, 25380, 25420, 25435, 25430,
        25470, 25500, 25530, 25550, 25580, 25570,
        25615, 25640,
    ]
    closes = [
        25260, 25290, 25305, 25355, 25335, 25375,
        25415, 25405, 25435, 25475, 25455, 25490,
        25525, 25555, 25575, 25615, 25595, 25645,
        25660, 25666.40,
    ]

    fig = go.Figure()
    fig.add_trace(
        go.Candlestick(
            x=detailed_times,
            open=opens,
            high=highs,
            low=lows,
            close=closes,
            increasing_line_color="#00f5d4",
            increasing_fillcolor="rgba(0, 245, 212, 0.85)",
            decreasing_line_color="#ff2a6d",
            decreasing_fillcolor="rgba(255, 42, 109, 0.85)",
            name="OHLC",
        )
    )
    fig.update_layout(
        height=210,
        margin=dict(l=5, r=42, t=8, b=24),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_rangeslider_visible=False,
        showlegend=False,
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.05)",
            tickmode="array",
            tickvals=["09:15", "10:35", "11:55", "13:15", "14:35", "15:30"],
            ticktext=["09:15", "10:30", "11:45", "13:00", "14:15", "15:30"],
            tickfont=dict(size=10, color="#94a3b8", family="'Share Tech Mono', monospace"),
            linecolor="rgba(255, 255, 255, 0.1)",
        ),
        yaxis=dict(
            side="right",
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.05)",
            tickmode="array",
            tickvals=[25200, 25400, 25600],
            ticktext=["25,200", "25,400", "25,600"],
            tickfont=dict(size=10, color="#94a3b8", family="'Share Tech Mono', monospace"),
            linecolor="rgba(255, 255, 255, 0.1)",
        ),
    )
    return fig


def render_main_three_column_grid(on_navigate_callback=None) -> None:
    """Render the Main 3-Column Dashboard Grid: Market Overview, Stock Performance, AI Insights."""
    col_left, col_mid, col_right = st.columns([1.15, 1.35, 1.1], gap="medium")

    # ==================== CARD 1: MARKET OVERVIEW ====================
    with col_left:
        st.markdown(
            """
            <div class="ref-grid-card">
              <div class="ref-card-header">
                <div class="ref-card-title-group">
                  <span class="ref-card-icon cyan">📈</span>
                  <span class="ref-card-title">Market Overview</span>
                </div>
                <div class="ref-live-badge">
                  <span class="ref-live-dot"></span>
                  <span>Live</span>
                </div>
              </div>
              <div class="ref-tabs-row">
                <span class="ref-tab-item active">NIFTY 50</span>
                <span class="ref-tab-item">SENSEX</span>
                <span class="ref-tab-item">BANKNIFTY</span>
              </div>
              <div class="ref-metric-block">
                <div class="ref-metric-val">25,666.40</div>
                <div class="ref-metric-delta">▲ +138.70 (+0.54%)</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        area_fig = _generate_smooth_market_chart()
        st.plotly_chart(
            area_fig,
            use_container_width=True,
            config={"displayModeBar": False, "staticPlot": False},
            key="ref_market_area_chart",
        )

        st.markdown(
            """
            <div class="ref-timeframe-pills">
              <span class="ref-tf-pill active">1D</span>
              <span class="ref-tf-pill">1W</span>
              <span class="ref-tf-pill">1M</span>
              <span class="ref-tf-pill">3M</span>
              <span class="ref-tf-pill">1Y</span>
              <span class="ref-tf-pill">ALL</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Open Live Market Overview ➔", key="btn_open_market_overview", use_container_width=True):
            if on_navigate_callback:
                on_navigate_callback("🌐 Market Overview")

    # ==================== CARD 2: STOCK PERFORMANCE ====================
    with col_mid:
        st.markdown(
            """
            <div class="ref-grid-card">
              <div class="ref-card-header">
                <div class="ref-card-title-group">
                  <span class="ref-card-icon blue">📊</span>
                  <span class="ref-card-title">Stock Performance</span>
                </div>
                <div class="ref-select-pill">
                  <span>1D</span>
                  <span style="font-size:0.7rem; margin-left:0.25rem;">▼</span>
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        candle_fig = _generate_candlestick_chart()
        st.plotly_chart(
            candle_fig,
            use_container_width=True,
            config={"displayModeBar": False, "staticPlot": False},
            key="ref_candle_chart",
        )
        if st.button("Analyze Technicals & ML ➔", key="btn_open_stock_perf", use_container_width=True):
            if on_navigate_callback:
                on_navigate_callback("📈 Stock Analysis")

    # ==================== CARD 3: AI INSIGHTS ====================
    with col_right:
        st.markdown(
            """
            <div class="ref-grid-card">
              <div class="ref-card-header">
                <div class="ref-card-title-group">
                  <span class="ref-card-icon magenta">✨</span>
                  <span class="ref-card-title">AI Insights</span>
                </div>
                <div class="ref-view-all-link">
                  <span>View All ➔</span>
                </div>
              </div>
              <div class="ref-outlook-box">
                <div class="ref-outlook-top">
                  <div class="ref-outlook-icon">💡</div>
                  <div class="ref-outlook-title">Bullish Outlook</div>
                  <div class="ref-outlook-graph">📶</div>
                </div>
                <div class="ref-outlook-desc">
                  Market shows strong momentum with positive global cues.
                </div>
              </div>
              <div class="ref-bullets-list">
                <div class="ref-bullet-item">
                  <span class="ref-check-icon">✔</span>
                  <span class="ref-bullet-text">Nifty above 25,600</span>
                </div>
                <div class="ref-bullet-item">
                  <span class="ref-check-icon">✔</span>
                  <span class="ref-bullet-text">Bank Nifty hits new high</span>
                </div>
                <div class="ref-bullet-item">
                  <span class="ref-check-icon">✔</span>
                  <span class="ref-bullet-text">IT stocks showing strength</span>
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Open AI Chatbot & Insights ➔", key="btn_open_ai_insights", use_container_width=True):
            if on_navigate_callback:
                on_navigate_callback("✨ AI Insights")


def render_footer_bar() -> None:
    """Render the sleek collegiate footer bar."""
    st.markdown(
        """
        <div class="ref-footer-bar">
          <div class="ref-footer-quote">
            <span class="ref-footer-icon">📈</span>
            <em>"Smarter Analysis. Greater Opportunities."</em>
          </div>
          <div class="ref-footer-college">
            <span>🏛️ Dronacharya Group of Institutions &nbsp;|&nbsp; BCC 351</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_home_dashboard(on_navigate=None) -> None:
    """Orchestrate the full Reference Executive Dashboard matching the reference screenshot pixel-for-pixel."""
    render_collegiate_top_bar()
    st.markdown('<div style="height: 0.6rem;"></div>', unsafe_allow_html=True)

    def _handle_search(ticker: str) -> None:
        if on_navigate:
            on_navigate("📈 Stock Analysis")

    render_hero_banner(on_search_callback=_handle_search)
    st.markdown('<div style="height: 0.8rem;"></div>', unsafe_allow_html=True)

    render_four_quick_action_cards(on_navigate_callback=on_navigate)
    st.markdown('<div style="height: 0.85rem;"></div>', unsafe_allow_html=True)

    render_main_three_column_grid(on_navigate_callback=on_navigate)
    st.markdown('<div style="height: 1.2rem;"></div>', unsafe_allow_html=True)

    render_footer_bar()
