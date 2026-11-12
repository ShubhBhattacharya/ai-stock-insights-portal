"""Modern, responsive UI styling and reusable visual components."""

from __future__ import annotations

import html
import streamlit as st
import plotly.graph_objects as go


GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg-canvas: #0b1120;
    --bg-surface: rgba(17, 24, 39, 0.85);
    --bg-elevated: rgba(30, 41, 59, 0.65);
    --border-subtle: rgba(148, 163, 184, 0.16);
    --border-hover: rgba(56, 189, 248, 0.45);
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --accent-sky: #38bdf8;
    --accent-emerald: #10b981;
    --accent-rose: #ef4444;
    --accent-amber: #f59e0b;
    --radius-lg: 16px;
    --radius-md: 12px;
    --radius-sm: 8px;
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Main container responsive spacing (compatible with Streamlit 1.x & 1.5x) */
.main .block-container,
[data-testid="stMainBlockContainer"] {
    padding-top: clamp(1.25rem, 2.5vw, 2.25rem);
    padding-bottom: 3rem;
    padding-left: clamp(0.85rem, 2.5vw, 2.5rem);
    padding-right: clamp(0.85rem, 2.5vw, 2.5rem);
    max-width: 1440px;
}

/* Subtle horizontal dividers */
hr {
    border-color: var(--border-subtle) !important;
    margin: 1.25rem 0 !important;
}

/* Subtle background mesh */
.stApp {
    background:
        radial-gradient(circle at 15% 10%, rgba(56, 189, 248, 0.08), transparent 35%),
        radial-gradient(circle at 85% 15%, rgba(16, 185, 129, 0.07), transparent 32%),
        var(--bg-canvas);
}

/* Sidebar polish */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #0b1120 100%);
    border-right: 1px solid var(--border-subtle);
}

section[data-testid="stSidebar"] .stRadio > div {
    gap: 0.3rem;
}

section[data-testid="stSidebar"] .stRadio label {
    padding: 0.55rem 0.75rem;
    border-radius: 10px;
    border: 1px solid transparent;
    transition: background-color 0.18s ease, border-color 0.18s ease;
}

section[data-testid="stSidebar"] .stRadio label:hover {
    background-color: rgba(56, 189, 248, 0.08);
    border-color: rgba(56, 189, 248, 0.22);
}

/* Hero Banner */
.portal-hero {
    position: relative;
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(17, 45, 78, 0.92) 55%, rgba(6, 78, 59, 0.88) 100%);
    border: 1px solid rgba(56, 189, 248, 0.22);
    border-radius: var(--radius-lg);
    padding: clamp(1.15rem, 2.5vw, 1.75rem) clamp(1.15rem, 3vw, 2rem);
    margin-bottom: 1.4rem;
    box-shadow: 0 12px 32px -12px rgba(2, 6, 23, 0.7);
    overflow: hidden;
}

.portal-hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #7dd3fc;
    background: rgba(56, 189, 248, 0.14);
    border: 1px solid rgba(56, 189, 248, 0.3);
    padding: 0.24rem 0.65rem;
    border-radius: 999px;
    margin-bottom: 0.6rem;
}

.portal-hero h1 {
    margin: 0;
    font-size: clamp(1.35rem, 2.6vw, 2rem);
    font-weight: 800;
    line-height: 1.2;
    color: #ffffff;
    letter-spacing: -0.02em;
}

.portal-hero p {
    margin: 0.45rem 0 0 0;
    color: #cbd5e1;
    font-size: clamp(0.86rem, 1.3vw, 0.98rem);
    line-height: 1.45;
}

/* Elevated Cards & KPI Grid */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(175px, 1fr));
    gap: 0.85rem;
    margin: 0.75rem 0 1.25rem 0;
}

.kpi-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 0.95rem 1.1rem;
    backdrop-filter: blur(10px);
    transition: transform 0.18s ease, border-color 0.18s ease;
}

.kpi-card:hover {
    transform: translateY(-2px);
    border-color: var(--border-hover);
}

.kpi-label {
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-secondary);
    margin-bottom: 0.35rem;
}

.kpi-value {
    font-size: clamp(1.25rem, 2vw, 1.6rem);
    font-weight: 700;
    color: var(--text-primary);
    font-variant-numeric: tabular-nums;
    line-height: 1.2;
    word-break: break-word;
}

.kpi-delta {
    display: inline-block;
    margin-top: 0.4rem;
    font-size: 0.78rem;
    font-weight: 600;
    padding: 0.16rem 0.5rem;
    border-radius: 999px;
    font-variant-numeric: tabular-nums;
}

.tone-up {
    color: #6ee7b7;
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.3);
}

.tone-down {
    color: #fda4af;
    background: rgba(239, 68, 68, 0.15);
    border: 1px solid rgba(239, 68, 68, 0.3);
}

.tone-neutral {
    color: #cbd5e1;
    background: rgba(148, 163, 184, 0.14);
    border: 1px solid rgba(148, 163, 184, 0.25);
}

.tone-warn {
    color: #fcd34d;
    background: rgba(245, 158, 11, 0.15);
    border: 1px solid rgba(245, 158, 11, 0.3);
}

/* Signal Pill Badges */
.signal-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.3rem 0.75rem;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.03em;
}

.badge-buy {
    background: rgba(16, 185, 129, 0.18);
    color: #6ee7b7;
    border: 1px solid rgba(16, 185, 129, 0.45);
}

.badge-sell {
    background: rgba(239, 68, 68, 0.18);
    color: #fca5a5;
    border: 1px solid rgba(239, 68, 68, 0.45);
}

.badge-hold {
    background: rgba(245, 158, 11, 0.18);
    color: #fde68a;
    border: 1px solid rgba(245, 158, 11, 0.45);
}

/* Surface Panel */
.surface-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 1.1rem 1.25rem;
    margin-bottom: 1rem;
}

.sidebar-profile-card {
    background: rgba(30, 41, 59, 0.6);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 0.9rem 1rem;
    margin-bottom: 0.85rem;
}

.sidebar-profile-name {
    font-size: 1rem;
    font-weight: 700;
    color: #f8fafc;
    margin-bottom: 0.35rem;
}

.sidebar-cash-pill {
    font-size: 0.85rem;
    color: #7dd3fc;
    font-weight: 600;
    font-variant-numeric: tabular-nums;
}

.news-item-card {
    background: rgba(15, 23, 42, 0.7);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
    padding: 0.7rem 0.9rem;
    margin-bottom: 0.55rem;
    transition: border-color 0.16s ease;
}

.news-item-card:hover {
    border-color: var(--border-hover);
}

.news-item-card a {
    color: #e2e8f0;
    text-decoration: none;
    font-weight: 600;
    font-size: 0.9rem;
    line-height: 1.35;
    display: block;
}

.news-item-card a:hover {
    color: #38bdf8;
}

.news-publisher {
    color: #94a3b8;
    font-size: 0.76rem;
    margin-top: 0.25rem;
}

/* Native Streamlit Metric Refinement */
div[data-testid="stMetric"] {
    background: var(--bg-surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 0.85rem 1rem;
}

div[data-testid="stMetricValue"] {
    font-size: clamp(1.2rem, 1.8vw, 1.55rem);
    font-weight: 700;
    font-variant-numeric: tabular-nums;
}

/* Button touch targets & transitions */
.stButton > button, .stDownloadButton > button {
    border-radius: 10px;
    font-weight: 600;
    min-height: 42px;
    transition: transform 0.14s ease, box-shadow 0.14s ease;
}

.stButton > button:hover, .stDownloadButton > button:hover {
    transform: translateY(-1px);
}

/* Tabs polish */
button[data-baseweb="tab"] {
    font-weight: 600;
    border-radius: 8px 8px 0 0;
}

/* DataFrames & Tables responsive scrolling */
div[data-testid="stDataFrame"], div[data-testid="stTable"] {
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    overflow-x: auto;
}

/* Tablet & Mobile Responsive Rules */
@media (max-width: 1024px) {
    div[data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
        gap: 0.75rem !important;
    }

    div[data-testid="stHorizontalBlock"] > div[data-testid="column"],
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
        min-width: 240px !important;
        flex: 1 1 240px !important;
    }
}

@media (max-width: 640px) {
    .main .block-container,
    [data-testid="stMainBlockContainer"] {
        padding-top: 1rem;
        padding-left: 0.75rem;
        padding-right: 0.75rem;
    }

    div[data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
    }

    div[data-testid="stHorizontalBlock"] > div[data-testid="column"],
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
        width: 100% !important;
        min-width: 100% !important;
        flex: 1 1 100% !important;
    }

    .kpi-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.65rem;
    }

    .kpi-card {
        padding: 0.75rem 0.85rem;
    }
}
</style>
"""


def inject_global_styles() -> None:
    """Inject global responsive CSS into the Streamlit page."""
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def render_page_header(title: str, subtitle: str, badge: str = "NSE INDIA • LIVE ANALYTICS") -> None:
    """Render a responsive glassmorphic hero header for a page module."""
    safe_badge = html.escape(badge)
    safe_title = html.escape(title)
    safe_subtitle = html.escape(subtitle)
    st.markdown(
        f'<div class="portal-hero">'
        f'<div class="portal-hero-badge">{safe_badge}</div>'
        f"<h1>{safe_title}</h1>"
        f"<p>{safe_subtitle}</p>"
        f"</div>",
        unsafe_allow_html=True,
    )


def render_signal_badge(signal: str, confidence: int | None = None) -> str:
    """Return HTML markup for a styled BUY / SELL / HOLD pill badge."""
    sig_upper = signal.upper()
    if sig_upper == "BUY":
        cls, dot = "badge-buy", "🟢"
    elif sig_upper == "SELL":
        cls, dot = "badge-sell", "🔴"
    else:
        cls, dot = "badge-hold", "🟡"

    suffix = f" · {confidence}% Confidence" if confidence is not None else ""
    return f'<span class="signal-badge {cls}">{dot} {html.escape(sig_upper)}{html.escape(suffix)}</span>'


def render_kpi_grid(cards: list[dict[str, str]]) -> None:
    """
    Render a responsive CSS-grid row of KPI cards.
    Each card dict supports: label, value, optional delta, optional tone ('up'|'down'|'warn'|'neutral').
    """
    card_html_parts: list[str] = []
    for card in cards:
        label = html.escape(str(card.get("label", "")))
        value = html.escape(str(card.get("value", "")))
        delta = card.get("delta", "")
        tone = card.get("tone", "neutral")
        tone_class = f"tone-{tone}" if tone in {"up", "down", "warn", "neutral"} else "tone-neutral"
        delta_html = f'<div class="kpi-delta {tone_class}">{html.escape(str(delta))}</div>' if delta else ""
        card_html_parts.append(
            f'<div class="kpi-card">'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{value}</div>'
            f"{delta_html}"
            f"</div>"
        )
    st.markdown(f'<div class="kpi-grid">{"".join(card_html_parts)}</div>', unsafe_allow_html=True)


def style_plotly_figure(fig: go.Figure, height: int = 500, title: str | None = None) -> go.Figure:
    """Apply consistent dark-theme fintech styling and responsive margins to Plotly figures."""
    layout_kwargs: dict = {
        "template": "plotly_dark",
        "paper_bgcolor": "rgba(17, 24, 39, 0.55)",
        "plot_bgcolor": "rgba(15, 23, 42, 0.55)",
        "font": {"family": "Inter, sans-serif", "color": "#e2e8f0", "size": 12},
        "height": height,
        "margin": {"l": 16, "r": 16, "t": 54, "b": 28},
        "hovermode": "x unified",
        "legend": {
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
            "bgcolor": "rgba(0,0,0,0)",
        },
    }
    if title:
        layout_kwargs["title"] = {"text": title, "font": {"size": 15, "color": "#f8fafc"}}

    fig.update_layout(**layout_kwargs)
    fig.update_xaxes(gridcolor="rgba(148, 163, 184, 0.1)", zeroline=False)
    fig.update_yaxes(gridcolor="rgba(148, 163, 184, 0.1)", zeroline=False)
    return fig
