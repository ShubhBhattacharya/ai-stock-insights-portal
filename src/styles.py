"""GTA VI / Vice City (Leonida Edition) Synthwave Neon UI Styling & HUD Components."""

from __future__ import annotations

import base64
import html
from pathlib import Path
import sys

_ROOT_DIR = str(Path(__file__).resolve().parents[1])
if _ROOT_DIR not in sys.path:
    sys.path.insert(0, _ROOT_DIR)

import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

from src.state import get_portal_theme, is_default_theme, is_doomsday, switch_world_edition

_ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets"


def _load_gta_transition_video_uri() -> str:
    """Video transitions removed in favor of instant CSS fade animations."""
    return ""


@st.cache_data(show_spinner=False)
def _cached_load_gta_video_uri(path_str: str, mtime: float) -> str:
    return ""

_PALM_LEFT_SVG = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 260 220'%3E"
    "%3Cg fill='%2305020f' opacity='0.9'%3E"
    "%3Cpath d='M36,220 C42,165 56,118 76,82 C70,118 58,166 52,220 Z'/%3E"
    "%3Cpath d='M74,84 C45,68 18,74 4,94 C26,86 50,86 72,92 Z'/%3E"
    "%3Cpath d='M75,82 C54,50 28,36 8,42 C32,48 55,62 72,82 Z'/%3E"
    "%3Cpath d='M77,80 C74,42 58,18 42,8 C58,28 68,54 74,80 Z'/%3E"
    "%3Cpath d='M79,82 C94,46 118,32 142,36 C118,44 96,60 82,84 Z'/%3E"
    "%3Cpath d='M80,86 C112,72 138,80 156,100 C130,90 104,88 80,92 Z'/%3E"
    "%3C/g%3E%3C/svg%3E"
)

_PALM_RIGHT_SVG = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 260 220'%3E"
    "%3Cg fill='%2305020f' opacity='0.9'%3E"
    "%3Cpath d='M224,220 C216,160 198,112 178,76 C186,114 202,162 208,220 Z'/%3E"
    "%3Cpath d='M180,78 C210,62 238,68 254,88 C230,80 206,80 182,86 Z'/%3E"
    "%3Cpath d='M178,76 C202,44 228,30 248,38 C224,44 200,58 182,78 Z'/%3E"
    "%3Cpath d='M176,74 C180,36 196,14 214,6 C198,26 188,50 180,76 Z'/%3E"
    "%3Cpath d='M174,76 C156,42 132,28 106,34 C132,42 156,56 172,78 Z'/%3E"
    "%3Cpath d='M173,82 C142,68 114,76 96,96 C122,86 148,84 174,88 Z'/%3E"
    "%3C/g%3E%3C/svg%3E"
)

_RUINED_LEFT_SVG = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 280 220'%3E"
    "%3Cg fill='%23080403' opacity='0.94'%3E"
    "%3Cpath d='M0,220 L0,96 L18,90 L28,118 L42,64 L64,52 L72,88 L88,78 L98,132 L116,120 L132,160 L158,150 L176,184 L210,220 Z'/%3E"
    "%3Crect x='46' y='88' width='8' height='12' fill='%23ff4500' opacity='0.55'/%3E"
    "%3Crect x='58' y='112' width='8' height='10' fill='%2339ff14' opacity='0.35'/%3E"
    "%3C/g%3E%3C/svg%3E"
)

_RUINED_RIGHT_SVG = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 280 220'%3E"
    "%3Cg fill='%23080403' opacity='0.94'%3E"
    "%3Cpath d='M280,220 L280,82 L254,74 L240,104 L224,48 L196,62 L188,96 L168,86 L154,142 L134,132 L116,168 L92,160 L70,192 L48,220 Z'/%3E"
    "%3Crect x='212' y='82' width='8' height='12' fill='%23ff4500' opacity='0.55'/%3E"
    "%3Crect x='194' y='110' width='8' height='10' fill='%23ffb703' opacity='0.45'/%3E"
    "%3C/g%3E%3C/svg%3E"
)

GLOBAL_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;800;900&family=Rajdhani:wght@500;600;700&family=Share+Tech+Mono&family=Yellowtail&family=Inter:wght@400;500;600;700&display=swap');

:root {{
    --bg-primary: #070B1A;
    --bg-secondary: #0D1226;
    --bg-card: rgba(16, 26, 50, 0.72);
    --bg-card-solid: #101A32;
    --accent-cyan: #00E5FF;
    --accent-magenta: #FF35C8;
    --accent-violet: #8B5CF6;
    --text-primary: #F4F7FF;
    --text-secondary: #94A3B8;
    --market-green: #00D68F;
    --market-red: #FF4D6D;
    --border-cyan: rgba(0, 229, 255, 0.28);
    --border-magenta: rgba(255, 53, 200, 0.35);
    --radius-lg: 16px;
    --radius-md: 12px;
    --radius-sm: 8px;
}}

/* Base Streamlit Layout & Typography */
html, body, [data-testid="stAppViewContainer"], .stApp {{
    background-color: #070B1A !important;
    color: #F4F7FF !important;
    font-family: 'Rajdhani', 'Inter', -apple-system, sans-serif !important;
}}

[data-testid="stAppViewContainer"] {{
    background: radial-gradient(circle at 50% 0%, #101835 0%, #070B1A 75%) !important;
}}

.main .block-container {{
    max-width: 1440px !important;
    padding-top: 1.2rem !important;
    padding-bottom: 2.5rem !important;
    padding-left: 1.8rem !important;
    padding-right: 1.8rem !important;
}}

/* Custom Neon Scrollbars */
::-webkit-scrollbar {{
    width: 8px;
    height: 8px;
}}
::-webkit-scrollbar-track {{
    background: #070B1A;
}}
::-webkit-scrollbar-thumb {{
    background: linear-gradient(180deg, #00E5FF 0%, #FF35C8 100%);
    border-radius: 4px;
}}

/* Top Fast CSS Neon Glow Progress Line */
.gta-neon-glow-line {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 2.5px;
    background: linear-gradient(90deg, #00E5FF 0%, #8B5CF6 50%, #FF35C8 100%);
    box-shadow: 0 0 12px rgba(0, 229, 255, 0.8), 0 0 20px rgba(255, 53, 200, 0.6);
    z-index: 999999;
    animation: neonLinePulse 2.5s ease-in-out infinite;
}}

@keyframes neonLinePulse {{
    0%, 100% {{ opacity: 0.85; filter: drop-shadow(0 0 6px #00E5FF); }}
    50% {{ opacity: 1; filter: drop-shadow(0 0 14px #FF35C8); }}
}}

/* Sidebar - Deep Obsidian Navy with Cyan Accent Divider */
[data-testid="stSidebar"] {{
    background-color: #0D1226 !important;
    border-right: 1px solid rgba(0, 229, 255, 0.16) !important;
    box-shadow: 4px 0 24px rgba(0, 0, 0, 0.45) !important;
}}

[data-testid="stSidebar"] .block-container {{
    padding-top: 1.2rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}}

/* Clean Fixed Sidebar Brand Logo */
.ref-sidebar-logo-container {{
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.4rem 0.4rem 1rem 0.4rem;
    border-bottom: 1px solid rgba(0, 229, 255, 0.16);
    margin-bottom: 0.9rem;
}}

.ref-sidebar-logo-icon {{
    font-size: 2.1rem;
    filter: drop-shadow(0 0 10px rgba(0, 229, 255, 0.65));
}}

.ref-sidebar-logo-text {{
    display: flex;
    flex-direction: column;
}}

.ref-logo-title {{
    font-family: 'Orbitron', sans-serif;
    font-size: 1.15rem;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: 0.04em;
    line-height: 1.15;
}}

.ref-logo-sub {{
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.85rem;
    font-weight: 700;
    color: #FF35C8;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}}

/* Sidebar Navigation Radio - Sleek Pills */
[data-testid="stSidebar"] div[data-testid="stRadio"] label[data-testid="stWidgetLabel"] {{
    display: none !important;
}}

[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] {{
    display: flex !important;
    flex-direction: column !important;
    gap: 0.35rem !important;
}}

[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label {{
    display: flex !important;
    align-items: center !important;
    padding: 0.58rem 0.95rem !important;
    border-radius: 12px !important;
    background: transparent !important;
    border: 1px solid transparent !important;
    color: #94A3B8 !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.94rem !important;
    letter-spacing: 0.02em !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    margin: 0 !important;
}}

[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {{
    background: rgba(0, 229, 255, 0.08) !important;
    color: #F4F7FF !important;
    border-color: rgba(0, 229, 255, 0.25) !important;
    transform: translateX(2px) !important;
}}

[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked),
[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] {{
    background: linear-gradient(90deg, rgba(255, 53, 200, 0.28) 0%, rgba(139, 92, 246, 0.38) 100%) !important;
    border: 1px solid rgba(255, 53, 200, 0.75) !important;
    color: #FFFFFF !important;
    box-shadow: 0 0 16px rgba(255, 53, 200, 0.35) !important;
}}

[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] input[type="radio"] {{
    display: none !important;
}}

[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] div[data-testid="stMarkdownContainer"] p {{
    margin: 0 !important;
    color: inherit !important;
    font-size: inherit !important;
    font-weight: inherit !important;
}}

/* Sidebar Powered by AI Badge Card */
.ref-sidebar-powered-card {{
    background: rgba(16, 26, 50, 0.85);
    border: 1px solid rgba(255, 53, 200, 0.35);
    border-radius: 14px;
    padding: 0.85rem 1rem;
    margin-top: 1.4rem;
    box-shadow: 0 4px 18px rgba(0, 0, 0, 0.5);
}}

.ref-powered-top {{
    display: flex;
    align-items: center;
    gap: 0.45rem;
    font-family: 'Orbitron', sans-serif;
    font-size: 0.82rem;
    font-weight: 700;
    color: #FF35C8;
}}

.ref-powered-desc {{
    font-size: 0.75rem;
    color: #94A3B8;
    margin-top: 0.35rem;
    line-height: 1.35;
}}

.ref-powered-chart {{
    margin-top: 0.45rem;
    font-size: 1.1rem;
}}

/* Top Collegiate Header Bar */
.ref-top-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(16, 26, 50, 0.75);
    border: 1px solid rgba(0, 229, 255, 0.22);
    border-radius: 14px;
    padding: 0.6rem 1.15rem;
    margin-bottom: 0.6rem;
}}

.ref-top-left {{
    display: flex;
    align-items: center;
    gap: 0.75rem;
}}

.ref-top-crest {{
    font-size: 1.4rem;
    filter: drop-shadow(0 0 8px rgba(0, 229, 255, 0.5));
}}

.ref-top-title {{
    font-family: 'Rajdhani', sans-serif;
    font-weight: 700;
    font-size: 0.95rem;
    color: #F4F7FF;
    letter-spacing: 0.03em;
}}

.ref-top-sub {{
    font-size: 0.75rem;
    color: #94A3B8;
    letter-spacing: 0.04em;
}}

.ref-top-right {{
    display: flex;
    align-items: center;
    gap: 0.75rem;
}}

.ref-theme-toggle-pill {{
    display: flex;
    align-items: center;
    gap: 0.45rem;
    background: rgba(7, 11, 26, 0.85);
    border: 1px solid rgba(0, 229, 255, 0.3);
    border-radius: 20px;
    padding: 0.25rem 0.65rem;
    font-size: 0.85rem;
}}

.ref-profile-pill {{
    display: flex;
    align-items: center;
    gap: 0.45rem;
    background: linear-gradient(90deg, #FF35C8 0%, #8B5CF6 100%);
    border-radius: 20px;
    padding: 0.35rem 0.95rem;
    color: #FFFFFF;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.03em;
    box-shadow: 0 0 12px rgba(255, 53, 200, 0.4);
}}

/* Synthwave Sunset Skyline Hero Banner */
.ref-hero-banner {{
    position: relative;
    border-radius: 18px;
    min-height: 255px;
    padding: 2rem 2.4rem;
    background: linear-gradient(135deg, rgba(7, 11, 26, 0.95) 0%, rgba(16, 26, 50, 0.95) 55%, rgba(24, 9, 43, 0.95) 100%);
    border: 1.5px solid rgba(255, 53, 200, 0.38);
    box-shadow: 0 8px 36px rgba(0, 0, 0, 0.7), inset 0 0 24px rgba(255, 53, 200, 0.12);
    overflow: hidden;
}}

.ref-hero-content {{
    position: relative;
    z-index: 2;
    display: flex;
    justify-content: space-between;
    align-items: center;
}}

.ref-hero-left {{
    max-width: 65%;
}}

.ref-hero-title {{
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.85rem;
    font-weight: 800;
    line-height: 1.1;
    margin: 0;
    letter-spacing: 0.02em;
}}

.glow-cyan {{
    color: #FFFFFF;
    text-shadow: 0 0 16px rgba(0, 229, 255, 0.85), 0 0 32px rgba(0, 229, 255, 0.4);
}}

.glow-magenta {{
    color: #FF35C8;
    text-shadow: 0 0 18px rgba(255, 53, 200, 0.85), 0 0 36px rgba(255, 53, 200, 0.45);
    margin-left: 0.35rem;
}}

.ref-hero-subtitle {{
    font-size: 1.08rem;
    font-weight: 600;
    color: #CBD5E1;
    letter-spacing: 0.08em;
    margin-top: 0.45rem;
}}

.ref-hero-badges-pill {{
    display: inline-flex;
    align-items: center;
    gap: 0.65rem;
    background: rgba(7, 11, 26, 0.88);
    border: 1px solid rgba(255, 53, 200, 0.38);
    border-radius: 30px;
    padding: 0.38rem 1.15rem;
    margin-top: 1rem;
    font-size: 0.78rem;
    color: #F4F7FF;
    box-shadow: 0 0 14px rgba(255, 53, 200, 0.25);
}}

.pill-divider {{
    color: rgba(255, 255, 255, 0.25);
}}

.ref-hero-right {{
    text-align: right;
    padding-right: 0.5rem;
}}

.ref-cursive-script {{
    font-family: 'Yellowtail', cursive;
    font-size: 2.35rem;
    color: #FF35C8;
    text-shadow: 0 0 16px rgba(255, 53, 200, 0.9), 0 0 30px rgba(255, 53, 200, 0.5);
    line-height: 1.15;
    transform: rotate(-3deg);
}}

/* Centered Search Bar Pill */
.ref-search-wrapper {{
    margin-top: -1.45rem;
    position: relative;
    z-index: 10;
    padding: 0 1.5rem;
}}

.ref-search-wrapper div[data-testid="stTextInput"] input {{
    background: rgba(16, 26, 50, 0.96) !important;
    border: 1.5px solid rgba(0, 229, 255, 0.55) !important;
    border-radius: 30px !important;
    color: #FFFFFF !important;
    padding: 0.65rem 1.45rem !important;
    font-size: 0.92rem !important;
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.6), inset 0 0 16px rgba(0, 229, 255, 0.12) !important;
}}

.ref-search-wrapper div[data-testid="stTextInput"] input:focus {{
    border-color: #00E5FF !important;
    box-shadow: 0 0 20px rgba(0, 229, 255, 0.55) !important;
}}

.ref-search-wrapper div[data-testid="stButton"] button {{
    background: linear-gradient(90deg, #00E5FF 0%, #8B5CF6 50%, #FF35C8 100%) !important;
    border: none !important;
    border-radius: 30px !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    font-size: 0.92rem !important;
    padding: 0.62rem 1.4rem !important;
    box-shadow: 0 0 20px rgba(255, 53, 200, 0.6) !important;
    transition: all 0.22s ease !important;
}}

.ref-search-wrapper div[data-testid="stButton"] button:hover {{
    transform: scale(1.02) !important;
    box-shadow: 0 0 28px rgba(0, 229, 255, 0.8) !important;
}}

/* 4 Quick Action Cards */
.ref-action-card {{
    display: flex;
    align-items: center;
    gap: 0.85rem;
    padding: 0.95rem 1.1rem;
    border-radius: 14px;
    background: rgba(16, 26, 50, 0.75);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.45), inset 0 0 14px rgba(0, 229, 255, 0.06);
    transition: all 0.22s ease;
    min-height: 86px;
    border: 1.5px solid rgba(0, 229, 255, 0.28);
    margin-bottom: 0.45rem;
}}

.ref-action-card:hover {{
    transform: translateY(-4px);
}}

.ref-card-cyan {{
    border-color: rgba(0, 229, 255, 0.45);
    box-shadow: 0 4px 18px rgba(0, 229, 255, 0.2);
}}
.ref-card-cyan:hover {{
    border-color: #00E5FF;
    box-shadow: 0 0 22px rgba(0, 229, 255, 0.45);
}}

.ref-card-magenta {{
    border-color: rgba(255, 53, 200, 0.45);
    box-shadow: 0 4px 18px rgba(255, 53, 200, 0.2);
}}
.ref-card-magenta:hover {{
    border-color: #FF35C8;
    box-shadow: 0 0 22px rgba(255, 53, 200, 0.45);
}}

.ref-card-blue {{
    border-color: rgba(139, 92, 246, 0.45);
    box-shadow: 0 4px 18px rgba(139, 92, 246, 0.2);
}}
.ref-card-blue:hover {{
    border-color: #8B5CF6;
    box-shadow: 0 0 22px rgba(139, 92, 246, 0.45);
}}

.ref-card-gold {{
    border-color: rgba(254, 228, 64, 0.45);
    box-shadow: 0 4px 18px rgba(254, 228, 64, 0.2);
}}
.ref-card-gold:hover {{
    border-color: #fee440;
    box-shadow: 0 0 22px rgba(254, 228, 64, 0.45);
}}

.ref-action-icon-box {{
    width: 38px;
    height: 38px;
    border-radius: 9px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.15rem;
    flex-shrink: 0;
}}

.ref-icon-cyan {{
    background: rgba(0, 229, 255, 0.15);
    border: 1px solid #00E5FF;
    box-shadow: 0 0 10px rgba(0, 229, 255, 0.35);
}}

.ref-icon-magenta {{
    background: rgba(255, 53, 200, 0.15);
    border: 1px solid #FF35C8;
    box-shadow: 0 0 10px rgba(255, 53, 200, 0.35);
}}

.ref-icon-blue {{
    background: rgba(139, 92, 246, 0.15);
    border: 1px solid #8B5CF6;
    box-shadow: 0 0 10px rgba(139, 92, 246, 0.35);
}}

.ref-icon-gold {{
    background: rgba(254, 228, 64, 0.15);
    border: 1px solid #fee440;
    box-shadow: 0 0 10px rgba(254, 228, 64, 0.35);
}}

.ref-action-text-box {{
    flex: 1;
    min-width: 0;
}}

.ref-action-card-title {{
    font-size: 0.94rem;
    font-weight: 700;
    color: #FFFFFF;
    letter-spacing: 0.02em;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}

.ref-action-card-sub {{
    font-size: 0.73rem;
    color: #94A3B8;
    margin-top: 0.15rem;
    line-height: 1.3;
}}

.ref-action-card-arrow {{
    color: #94A3B8;
    font-size: 0.95rem;
    margin-left: auto;
    flex-shrink: 0;
    transition: transform 0.2s ease;
}}

.ref-action-card:hover .ref-action-card-arrow {{
    transform: translateX(3px);
    color: #FFFFFF;
}}

/* Main 3-Column Dashboard Grid Cards */
.ref-grid-card {{
    background: rgba(16, 26, 50, 0.75);
    border: 1.5px solid rgba(0, 229, 255, 0.25);
    border-radius: 16px;
    padding: 1.15rem 1.3rem;
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.5), inset 0 0 16px rgba(0, 229, 255, 0.06);
    margin-bottom: 0.5rem;
}}

.ref-card-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.65rem;
}}

.ref-card-title-group {{
    display: flex;
    align-items: center;
    gap: 0.45rem;
}}

.ref-card-title {{
    font-size: 1.05rem;
    font-weight: 700;
    color: #FFFFFF;
    letter-spacing: 0.02em;
}}

.ref-live-badge {{
    background: rgba(0, 214, 143, 0.14);
    border: 1px solid #00D68F;
    border-radius: 16px;
    padding: 0.2rem 0.65rem;
    color: #00D68F;
    font-size: 0.74rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 0.35rem;
}}

.ref-live-dot {{
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #00D68F;
    box-shadow: 0 0 8px #00D68F;
    animation: badge-float 1.8s infinite ease-in-out;
}}

.ref-tabs-row {{
    display: flex;
    gap: 0.5rem;
    margin-bottom: 0.85rem;
}}

.ref-tab-item {{
    font-size: 0.78rem;
    font-weight: 700;
    padding: 0.25rem 0.75rem;
    border-radius: 8px;
    color: #94A3B8;
    background: rgba(7, 11, 26, 0.6);
    border: 1px solid rgba(0, 229, 255, 0.14);
    cursor: pointer;
}}

.ref-tab-item.active {{
    color: #FFFFFF;
    background: linear-gradient(90deg, rgba(255, 53, 200, 0.25), rgba(139, 92, 246, 0.35));
    border-color: #FF35C8;
    box-shadow: 0 0 10px rgba(255, 53, 200, 0.3);
}}

.ref-metric-block {{
    margin-bottom: 0.65rem;
}}

.ref-metric-val {{
    font-family: 'Share Tech Mono', monospace;
    font-size: 1.95rem;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: 0.03em;
}}

.ref-metric-delta {{
    font-size: 0.88rem;
    font-weight: 700;
    color: #00D68F;
    margin-top: 0.15rem;
}}

.ref-timeframe-pills {{
    display: flex;
    gap: 0.4rem;
    justify-content: flex-start;
    margin-top: 0.6rem;
}}

.ref-tf-pill {{
    font-size: 0.72rem;
    font-weight: 700;
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    color: #94A3B8;
    background: rgba(7, 11, 26, 0.6);
    border: 1px solid rgba(0, 229, 255, 0.14);
    cursor: pointer;
}}

.ref-tf-pill.active {{
    color: #00E5FF;
    border-color: #00E5FF;
    background: rgba(0, 229, 255, 0.12);
    box-shadow: 0 0 8px rgba(0, 229, 255, 0.25);
}}

.ref-select-pill {{
    background: rgba(7, 11, 26, 0.7);
    border: 1px solid rgba(0, 229, 255, 0.25);
    border-radius: 8px;
    padding: 0.25rem 0.65rem;
    font-size: 0.78rem;
    font-weight: 700;
    color: #00E5FF;
    display: flex;
    align-items: center;
}}

.ref-view-all-link {{
    font-size: 0.8rem;
    font-weight: 700;
    color: #FF35C8;
    cursor: pointer;
}}

.ref-outlook-box {{
    background: rgba(7, 11, 26, 0.8);
    border: 1px solid rgba(0, 214, 143, 0.35);
    border-radius: 12px;
    padding: 0.85rem 1rem;
    margin-bottom: 0.95rem;
    box-shadow: inset 0 0 12px rgba(0, 214, 143, 0.08);
}}

.ref-outlook-top {{
    display: flex;
    align-items: center;
    gap: 0.45rem;
}}

.ref-outlook-icon {{
    font-size: 1.15rem;
}}

.ref-outlook-title {{
    font-size: 0.92rem;
    font-weight: 700;
    color: #00D68F;
}}

.ref-outlook-graph {{
    margin-left: auto;
    font-size: 1.1rem;
}}

.ref-outlook-desc {{
    font-size: 0.76rem;
    color: #CBD5E1;
    margin-top: 0.35rem;
    line-height: 1.35;
}}

.ref-bullets-list {{
    display: flex;
    flex-direction: column;
    gap: 0.55rem;
}}

.ref-bullet-item {{
    display: flex;
    align-items: center;
    gap: 0.55rem;
    font-size: 0.82rem;
    color: #F4F7FF;
}}

.ref-check-icon {{
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: rgba(0, 214, 143, 0.2);
    border: 1px solid #00D68F;
    color: #00D68F;
    font-size: 0.68rem;
    font-weight: 900;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}}

/* Collegiate Footer Bar */
.ref-footer-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 1px solid rgba(0, 229, 255, 0.16);
    padding: 0.95rem 0.5rem 0.5rem 0.5rem;
    margin-top: 1.2rem;
    font-size: 0.82rem;
    color: #94A3B8;
}}

.ref-footer-quote {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #F4F7FF;
    font-style: italic;
}}

.ref-footer-college {{
    color: #94A3B8;
    letter-spacing: 0.03em;
}}

/* Clean Subpage Header (Used across Single Stock, Market Overview, AI Tutor, etc.) */
.ref-subpage-header {{
    background: rgba(16, 26, 50, 0.75);
    border: 1.5px solid rgba(0, 229, 255, 0.25);
    border-radius: 16px;
    padding: 1.25rem 1.6rem;
    margin-bottom: 1rem;
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.5);
}}

.ref-subpage-badge {{
    display: inline-block;
    font-size: 0.74rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    color: #00E5FF;
    text-transform: uppercase;
    margin-bottom: 0.35rem;
}}

.ref-subpage-title {{
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.1rem;
    font-weight: 800;
    color: #FFFFFF;
    text-shadow: 0 0 16px rgba(0, 229, 255, 0.4);
    margin: 0;
    line-height: 1.15;
}}

.ref-subpage-sub {{
    font-size: 0.88rem;
    color: #94A3B8;
    margin: 0.35rem 0 0 0;
}}

/* Global Streamlit Widgets Styling for GTA VI Mode */
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input,
div[data-testid="stSelectbox"] select,
div[data-testid="stSelectbox"] > div > div {{
    background-color: #101A32 !important;
    border: 1px solid rgba(0, 229, 255, 0.28) !important;
    color: #F4F7FF !important;
    border-radius: 10px !important;
}}

div[data-testid="stButton"] button {{
    background: linear-gradient(90deg, #00E5FF 0%, #8B5CF6 50%, #FF35C8 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    padding: 0.55rem 1.2rem !important;
    box-shadow: 0 4px 16px rgba(255, 53, 200, 0.35) !important;
    transition: all 0.2s ease !important;
}}

div[data-testid="stButton"] button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 22px rgba(0, 229, 255, 0.55) !important;
}}

/* Surface & KPI Card Styling Across Submodules */
.surface-card, .tactical-card, .kpi-card, .vice-card, .stock-stat-box {{
    background: rgba(16, 26, 50, 0.75) !important;
    border: 1px solid rgba(0, 229, 255, 0.22) !important;
    border-radius: 14px !important;
    padding: 1.1rem 1.25rem !important;
    box-shadow: 0 4px 18px rgba(0, 0, 0, 0.4) !important;
    color: #F4F7FF !important;
}}

.kpi-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 0.85rem;
    margin: 0.95rem 0;
}}

.kpi-label {{
    font-size: 0.78rem;
    font-weight: 700;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}

.kpi-value {{
    font-family: 'Share Tech Mono', monospace;
    font-size: 1.65rem;
    font-weight: 800;
    color: #FFFFFF;
    margin: 0.25rem 0;
}}

.kpi-delta.tone-up {{ color: #00D68F !important; font-weight: 700; }}
.kpi-delta.tone-down {{ color: #FF4D6D !important; font-weight: 700; }}
.kpi-delta.tone-warn {{ color: #FEE440 !important; font-weight: 700; }}
.kpi-delta.tone-neutral {{ color: #94A3B8 !important; }}

/* Signal Badges */
.signal-badge {{
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.3rem 0.75rem;
    border-radius: 20px;
    font-weight: 800;
    font-size: 0.82rem;
    letter-spacing: 0.04em;
}}

.badge-buy {{
    background: rgba(0, 214, 143, 0.16);
    border: 1px solid #00D68F;
    color: #00D68F;
}}

.badge-sell {{
    background: rgba(255, 77, 109, 0.16);
    border: 1px solid #FF4D6D;
    color: #FF4D6D;
}}

.badge-hold {{
    background: rgba(254, 228, 64, 0.16);
    border: 1px solid #FEE440;
    color: #FEE440;
}}

/* Neuter and Suppress Old Legacy Artifacts completely */
.vice-hud-top,
.wanted-rack,
.weazel-flash-bar,
.tactical-hazard-strip,
.rivet-dot,
.graffiti-vi {{
    display: none !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    opacity: 0 !important;
}}

.steel-rivet-card {{
    background: rgba(16, 26, 50, 0.75) !important;
    border: 1.5px solid rgba(0, 229, 255, 0.25) !important;
    border-radius: 16px !important;
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.5) !important;
}}

@keyframes fadeInModal {{
    from {{ opacity: 0; transform: translateY(6px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

@keyframes badge-float {{
    0%, 100% {{ transform: translateY(0px); }}
    50% {{ transform: translateY(-2px); }}
}}
</style>
"""

DOOMSDAY_OVERRIDE_CSS = f"""
<style>
:root {{
    --bg-canvas: #0c0604;
    --bg-violet: #240c06;
    --bg-surface: rgba(20, 14, 12, 0.93);
    --bg-steel: linear-gradient(160deg, rgba(44, 42, 40, 0.96) 0%, rgba(20, 16, 15, 0.98) 58%, rgba(34, 22, 16, 0.96) 100%);
    --neon-pink: #ff4500;
    --neon-orange: #ff7a00;
    --neon-yellow: #ffb703;
    --neon-cyan: #39ff14;
    --neon-green: #39ff14;
    --neon-crimson: #ff2a00;
    --border-neon: rgba(57, 255, 20, 0.56);
    --border-magenta: rgba(255, 69, 0, 0.68);
}}

/* Cyber-Apocalypse Fiery Ruined Skyline + Tactical Amber Grid */
.stApp {{
    background-color: #0b0504;
    background-image:
        url("{_RUINED_LEFT_SVG}"),
        url("{_RUINED_RIGHT_SVG}"),
        linear-gradient(90deg, rgba(57, 255, 20, 0.08) 1px, transparent 1px),
        linear-gradient(0deg, rgba(255, 69, 0, 0.10) 1px, transparent 1px),
        radial-gradient(circle at 20% 24%, rgba(255, 69, 0, 0.36), transparent 44%),
        radial-gradient(circle at 80% 18%, rgba(255, 183, 3, 0.24), transparent 42%),
        radial-gradient(circle at 50% 82%, rgba(255, 42, 0, 0.28), transparent 52%),
        linear-gradient(180deg, #160603 0%, #3d1205 46%, #260a04 78%, #090504 100%) !important;
    background-position: left bottom, right bottom, center center, center center, center center, center center, center center, center center !important;
    background-size: 245px auto, 245px auto, 48px 48px, 48px 48px, 100% 100%, 100% 100%, 100% 100%, 100% 100% !important;
    border-top: 2px solid #ff4500 !important;
    border-bottom: 2px solid #39ff14 !important;
}}

/* Tactical Doomsday Command Board Overrides */
.tactical-card {{
    background: rgba(16, 12, 10, 0.96) !important;
}}
.tactical-card-cyan {{
    border: 2px solid #39ff14 !important;
    box-shadow: 0 0 14px rgba(57, 255, 20, 0.28) !important;
}}
.tactical-card-magenta {{
    border: 2px solid #ff4500 !important;
    box-shadow: 0 0 14px rgba(255, 69, 0, 0.28) !important;
}}
.tactical-hazard-strip {{
    background: linear-gradient(90deg, #39ff14 0%, #ff4500 100%) !important;
}}
.tactical-center-shell {{
    background: rgba(14, 12, 10, 0.96) !important;
    border: 2px solid #39ff14 !important;
    box-shadow: 0 0 14px rgba(57, 255, 20, 0.22) !important;
}}
.tactical-status-card {{
    background: rgba(18, 14, 11, 0.96) !important;
    border-color: rgba(57, 255, 20, 0.5) !important;
}}
.tactical-status-wanted {{
    border-color: #ff4500 !important;
    background: linear-gradient(145deg, rgba(44, 16, 10, 0.96), rgba(16, 12, 10, 0.98)) !important;
}}

/* Armored Blast-Shelter Sidebar HUD */
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, rgba(20, 16, 14, 0.99) 0%, rgba(30, 16, 11, 0.98) 62%, rgba(12, 9, 8, 0.99) 100%) !important;
    border-right: 3px solid #ff4500 !important;
    box-shadow: 4px 0 26px rgba(255, 69, 0, 0.34), inset -2px 0 14px rgba(57, 255, 20, 0.22) !important;
}}

section[data-testid="stSidebar"] .stRadio label {{
    border: 1px solid rgba(57, 255, 20, 0.28) !important;
    background: rgba(18, 14, 12, 0.85) !important;
}}

section[data-testid="stSidebar"] .stRadio label:hover {{
    background: linear-gradient(90deg, rgba(255, 69, 0, 0.28), rgba(57, 255, 20, 0.18)) !important;
    border-color: #39ff14 !important;
    box-shadow: 0 0 14px rgba(57, 255, 20, 0.42) !important;
}}

/* Armored Top Banner & Edition Toggle */
div[data-testid="stVerticalBlock"]:has(> div.element-container span.edition-toggle-marker),
div[data-testid="stVerticalBlockBorderWrapper"]:has(span.edition-toggle-marker) {{
    background: linear-gradient(160deg, rgba(38, 34, 32, 0.97), rgba(16, 13, 12, 0.98)) !important;
    border: 2px solid #ffb703 !important;
    box-shadow: 0 0 22px rgba(255, 69, 0, 0.45), inset 0 0 14px rgba(57, 255, 20, 0.16) !important;
}}

.vice-hud-top {{
    background: linear-gradient(90deg, rgba(28, 22, 20, 0.97), rgba(52, 20, 10, 0.96), rgba(28, 22, 20, 0.97)) !important;
    border: 2px solid #ff4500 !important;
    box-shadow: 0 0 20px rgba(255, 69, 0, 0.45), inset 0 0 12px rgba(57, 255, 20, 0.18) !important;
}}

.wing-pill {{
    background: linear-gradient(90deg, rgba(255, 69, 0, 0.36), rgba(57, 255, 20, 0.22)) !important;
    border: 1.5px solid #39ff14 !important;
    text-shadow: 0 0 8px rgba(57, 255, 20, 0.85) !important;
}}

.vice-sub-ribbon {{
    font-family: 'Orbitron', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.09em !important;
    color: #ffb703 !important;
    text-shadow: 0 0 10px rgba(255, 69, 0, 0.9) !important;
}}

.wanted-rack {{
    border: 1.5px solid #ff2a00 !important;
    background: rgba(24, 8, 6, 0.92) !important;
    box-shadow: 0 0 14px rgba(255, 42, 0, 0.55) !important;
}}

.portal-hero {{
    background:
        url("{_RUINED_LEFT_SVG}"),
        url("{_RUINED_RIGHT_SVG}"),
        repeating-linear-gradient(-45deg, rgba(255, 183, 3, 0.06) 0 12px, transparent 12px 24px),
        linear-gradient(135deg, rgba(26, 15, 12, 0.96) 0%, rgba(58, 20, 8, 0.94) 52%, rgba(18, 22, 16, 0.96) 100%) !important;
    background-position: left bottom, right bottom, center center, center center !important;
    background-size: 165px auto, 165px auto, 100% 100%, 100% 100% !important;
    background-repeat: no-repeat, no-repeat, no-repeat, no-repeat !important;
    border: 2px solid #39ff14 !important;
    box-shadow: 0 0 26px rgba(57, 255, 20, 0.32), 0 0 38px rgba(255, 69, 0, 0.34) !important;
}}

.portal-hero::before {{
    content: "DEFCON-1 BUNKERNET // RADIATION LEVEL CRIT // SYS.ARMED" !important;
    color: #ffb703 !important;
}}

.portal-hero h1,
.portal-hero h1.vice-calligraphy {{
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 900 !important;
    letter-spacing: 0.04em !important;
    background: linear-gradient(180deg, #ff7a00 0%, #ffb703 45%, #39ff14 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    filter: drop-shadow(0 0 12px rgba(57, 255, 20, 0.72)) !important;
}}

.sidebar-profile-card,
.safehouse-card,
.street-race-board {{
    background: linear-gradient(155deg, rgba(28, 22, 20, 0.97), rgba(14, 11, 10, 0.98)) !important;
    border: 2px solid #ff4500 !important;
    box-shadow: 0 0 20px rgba(255, 69, 0, 0.32), inset 0 0 14px rgba(57, 255, 20, 0.14) !important;
}}

.race-fill-cyan {{
    background: repeating-linear-gradient(-55deg, #39ff14 0px, #39ff14 10px, #15803d 10px, #15803d 16px) !important;
    box-shadow: 0 0 12px rgba(57, 255, 20, 0.78) !important;
}}

.race-fill-pink {{
    background: repeating-linear-gradient(-55deg, #ff4500 0px, #ff4500 10px, #9a3412 10px, #9a3412 16px) !important;
    box-shadow: 0 0 12px rgba(255, 69, 0, 0.78) !important;
}}

.weazel-flash-bar {{
    background: linear-gradient(90deg, rgba(14, 24, 12, 0.97), rgba(34, 14, 8, 0.97)) !important;
    border: 2px solid #ffb703 !important;
    border-left: 6px solid #39ff14 !important;
    box-shadow: 0 0 20px rgba(255, 69, 0, 0.42) !important;
}}

.weazel-tag {{
    background: linear-gradient(90deg, #39ff14, #ffb703) !important;
}}

.stButton > button[kind="primary"],
button[data-testid="stBaseButton-primary"],
button[data-testid="baseButton-primary"] {{
    color: #fff7ed !important;
    background: linear-gradient(90deg, #9a1b00 0%, #ff4500 50%, #ffb703 100%) !important;
    border: 2px solid #ffb703 !important;
    text-shadow: 0 1px 4px rgba(0, 0, 0, 0.85);
}}

div[data-testid="stForm"] {{
    background: rgba(18, 13, 12, 0.94) !important;
    border: 2px solid #ff4500 !important;
    box-shadow: 0 0 22px rgba(255, 69, 0, 0.28), inset 0 0 14px rgba(57, 255, 20, 0.14) !important;
}}

div[data-testid="stVerticalBlock"]:has(> div.element-container span.ifruit-anchor),
div[data-testid="stVerticalBlockBorderWrapper"]:has(span.ifruit-anchor) {{
    background: linear-gradient(165deg, rgba(24, 22, 20, 0.98), rgba(14, 18, 14, 0.98)) !important;
    border: 2px solid #39ff14 !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.9), 0 0 22px rgba(57, 255, 20, 0.4) !important;
}}
</style>
"""




DEFAULT_PRO_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');

:root {
    --pro-canvas: #0b1120;
    --pro-surface: #111827;
    --pro-surface-elevated: #162032;
    --pro-emerald: #10b981;
    --pro-blue: #3b82f6;
    --pro-border: rgba(255, 255, 255, 0.08);
    --pro-border-strong: rgba(255, 255, 255, 0.14);
    --pro-text: #f8fafc;
    --pro-muted: #94a3b8;
    --radius-lg: 14px;
    --radius-md: 10px;
    --radius-sm: 8px;
}

@keyframes pro-progress-fill {
    0% { width: 10%; }
    55% { width: 72%; }
    100% { width: 100%; }
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    color: var(--pro-text);
}

html, body, [data-testid="stAppViewContainer"], .stApp {
    overflow-x: hidden !important;
}

.stApp {
    background-color: var(--pro-canvas) !important;
    background-image:
        radial-gradient(circle at 15% 8%, rgba(59, 130, 246, 0.08), transparent 40%),
        radial-gradient(circle at 88% 12%, rgba(16, 185, 129, 0.07), transparent 36%) !important;
    border-top: none !important;
    border-bottom: none !important;
}

/* Hide Default Streamlit Header Chrome & Keep Sidebar Toggle Clickable */
header[data-testid="stHeader"] {
    background: transparent !important;
    height: 0px !important;
    min-height: 0px !important;
    border: none !important;
    overflow: visible !important;
}

[data-testid="stToolbar"],
[data-testid="stDecoration"] {
    display: none !important;
}

#MainMenu,
footer {
    visibility: hidden !important;
}

[data-testid="stSidebarCollapsedControl"],
[data-testid="stExpandSidebarButton"] {
    visibility: visible !important;
    display: flex !important;
    position: fixed !important;
    top: 10px !important;
    left: 10px !important;
    z-index: 999999 !important;
}

.main .block-container,
.block-container,
[data-testid="stMainBlockContainer"] {
    padding-top: 0.75rem !important;
    padding-bottom: 3.25rem;
    padding-left: clamp(0.9rem, 2.5vw, 2.25rem);
    padding-right: clamp(0.9rem, 2.5vw, 2.25rem);
    max-width: 1440px;
}

hr {
    border: none !important;
    height: 1px !important;
    background: var(--pro-border) !important;
    margin: 1.1rem 0 !important;
}

/* Top Edition Switcher Console in Default Mode */
div[data-testid="stVerticalBlock"]:has(> div.element-container span.edition-toggle-marker),
div[data-testid="stVerticalBlockBorderWrapper"]:has(span.edition-toggle-marker) {
    max-width: 820px !important;
    margin: 0 auto 0.85rem auto !important;
    background: var(--pro-surface) !important;
    border: 1px solid var(--pro-border) !important;
    border-radius: var(--radius-md) !important;
    padding: 0.55rem 0.85rem 0.7rem 0.85rem !important;
    box-shadow: 0 4px 18px rgba(0, 0, 0, 0.28) !important;
}

.edition-toggle-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.45rem;
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    color: var(--pro-muted);
    margin-bottom: 0.45rem;
}

/* Corporate Fintech Sidebar */
section[data-testid="stSidebar"] {
    background: #0f172a !important;
    border-right: 1px solid var(--pro-border) !important;
    box-shadow: none !important;
}

section[data-testid="stSidebar"] .stRadio > div {
    gap: 0.28rem;
}

section[data-testid="stSidebar"] .stRadio label {
    font-size: 0.85rem;
    font-weight: 500;
    padding: 0.52rem 0.75rem;
    border-radius: var(--radius-sm);
    border: 1px solid transparent;
    background: transparent;
    transition: background-color 0.15s ease, border-color 0.15s ease;
}

section[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(59, 130, 246, 0.12);
    border-color: rgba(59, 130, 246, 0.28);
}

.sidebar-profile-card {
    background: var(--pro-surface);
    border: 1px solid var(--pro-border);
    border-radius: var(--radius-md);
    padding: 0.9rem 1rem;
    margin-bottom: 0.75rem;
}

.sidebar-profile-name {
    font-size: 0.92rem;
    font-weight: 700;
    color: var(--pro-text);
    margin-bottom: 0.22rem;
}

.sidebar-cash-pill {
    font-size: 0.9rem;
    font-weight: 700;
    color: var(--pro-emerald);
    font-variant-numeric: tabular-nums;
}

/* Pro Corporate Page Header */
.pro-page-header {
    background: var(--pro-surface);
    border: 1px solid var(--pro-border);
    border-radius: var(--radius-lg);
    padding: clamp(1.1rem, 2.2vw, 1.55rem) clamp(1.2rem, 2.6vw, 1.85rem);
    margin-bottom: 1.15rem;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.22);
}

.pro-header-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--pro-emerald);
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.28);
    padding: 0.22rem 0.68rem;
    border-radius: 999px;
    margin-bottom: 0.55rem;
}

.pro-page-header h1 {
    margin: 0;
    font-size: clamp(1.4rem, 2.5vw, 1.95rem);
    font-weight: 800;
    color: var(--pro-text);
    letter-spacing: -0.02em;
    line-height: 1.22;
}

.pro-page-header p {
    margin: 0.35rem 0 0 0;
    font-size: 0.92rem;
    color: var(--pro-muted);
    line-height: 1.45;
}

/* Corporate Surface Cards (Overrides Steel Rivet Card Cleanly With Zero Hazard Stripes) */
.steel-rivet-card,
.surface-card {
    background: var(--pro-surface);
    border: 1px solid var(--pro-border);
    border-radius: var(--radius-md);
    padding: 1.1rem 1.25rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.rivet-dot {
    display: none;
}

.graffiti-vi {
    font-weight: 800;
    font-size: 1.85rem;
    color: var(--pro-blue);
    letter-spacing: -0.04em;
}

.console-hud-ruler {
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 0.76rem;
    font-weight: 600;
    color: var(--pro-muted);
    padding: 0.45rem 0;
    margin: 0.35rem 0 0.65rem 0;
    border-top: 1px solid var(--pro-border);
    border-bottom: 1px solid var(--pro-border);
}

/* Clean KPI Grid */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(195px, 1fr));
    gap: 0.85rem;
    margin: 0.75rem 0 1.25rem 0;
}

.kpi-card {
    background: var(--pro-surface);
    border: 1px solid var(--pro-border);
    border-radius: var(--radius-md);
    padding: 0.95rem 1.15rem;
    transition: border-color 0.15s ease, transform 0.15s ease;
}

.kpi-card:hover {
    border-color: rgba(59, 130, 246, 0.45);
    transform: translateY(-1px);
}

.kpi-label {
    font-size: 0.74rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--pro-muted);
    margin-bottom: 0.32rem;
}

.kpi-value {
    font-size: clamp(1.28rem, 2vw, 1.6rem);
    font-weight: 700;
    color: var(--pro-text);
    font-variant-numeric: tabular-nums;
    line-height: 1.22;
}

.kpi-delta {
    display: inline-block;
    margin-top: 0.4rem;
    font-size: 0.76rem;
    font-weight: 600;
    padding: 0.16rem 0.52rem;
    border-radius: 999px;
    font-variant-numeric: tabular-nums;
}

.tone-up { color: #34d399; background: rgba(16, 185, 129, 0.14); border: 1px solid rgba(16, 185, 129, 0.28); }
.tone-down { color: #f87171; background: rgba(239, 68, 68, 0.14); border: 1px solid rgba(239, 68, 68, 0.28); }
.tone-neutral { color: #93c5fd; background: rgba(59, 130, 246, 0.12); border: 1px solid rgba(59, 130, 246, 0.28); }
.tone-warn { color: #fbbf24; background: rgba(245, 158, 11, 0.14); border: 1px solid rgba(245, 158, 11, 0.28); }

/* Signal Badges */
.signal-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.38rem;
    padding: 0.28rem 0.78rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.03em;
}

.badge-buy { color: #34d399; background: rgba(16, 185, 129, 0.14); border: 1px solid rgba(16, 185, 129, 0.35); }
.badge-sell { color: #f87171; background: rgba(239, 68, 68, 0.14); border: 1px solid rgba(239, 68, 68, 0.35); }
.badge-hold { color: #fbbf24; background: rgba(245, 158, 11, 0.14); border: 1px solid rgba(245, 158, 11, 0.35); }

/* Clean Triggered Price Alert Banner */
.wanted-alert-flash {
    background: var(--pro-surface);
    border: 1px solid rgba(16, 185, 129, 0.42);
    border-left: 4px solid var(--pro-emerald);
    border-radius: var(--radius-md);
    padding: 0.9rem 1.15rem;
    margin-bottom: 0.65rem;
}

/* News Card */
.news-item-card {
    background: var(--pro-surface);
    border: 1px solid var(--pro-border);
    border-radius: var(--radius-sm);
    padding: 0.72rem 0.9rem;
    margin-bottom: 0.55rem;
    transition: border-color 0.15s ease;
}

.news-item-card:hover {
    border-color: rgba(59, 130, 246, 0.45);
}

.news-item-card a {
    color: var(--pro-text);
    text-decoration: none;
    font-weight: 600;
    font-size: 0.9rem;
    line-height: 1.38;
    display: block;
}

.news-item-card a:hover {
    color: var(--pro-blue);
}

.news-publisher {
    color: var(--pro-muted);
    font-size: 0.74rem;
    margin-top: 0.25rem;
}

/* Comparison Benchmark Card */
.street-race-board {
    background: var(--pro-surface);
    border: 1px solid var(--pro-border);
    border-radius: var(--radius-md);
    padding: 1.1rem 1.25rem;
    margin: 0.8rem 0 1.15rem 0;
}

.race-winner-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    font-size: 0.8rem;
    font-weight: 700;
    color: #064e3b;
    background: var(--pro-emerald);
    padding: 0.28rem 0.82rem;
    border-radius: 999px;
}

.race-metric-block {
    margin-bottom: 0.82rem;
}

.race-track {
    width: 100%;
    height: 10px;
    border-radius: 999px;
    background: rgba(15, 23, 42, 0.9);
    border: 1px solid var(--pro-border);
    overflow: hidden;
    margin: 0.22rem 0;
}

.race-fill-cyan {
    height: 100%;
    border-radius: 999px;
    background: var(--pro-emerald);
}

.race-fill-pink {
    height: 100%;
    border-radius: 999px;
    background: var(--pro-blue);
}

/* Fintech 1.5s Transition Card */
.pro-transition-shell {
    max-width: 680px;
    margin: 3rem auto;
    background: var(--pro-surface);
    border: 1px solid var(--pro-border);
    border-radius: var(--radius-lg);
    padding: 2rem 1.75rem;
    text-align: center;
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.42);
}

.pro-progress-track {
    width: 100%;
    height: 8px;
    border-radius: 999px;
    background: #1e293b;
    overflow: hidden;
    margin: 1.15rem 0;
}

.pro-progress-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, var(--pro-blue), var(--pro-emerald));
    animation: pro-progress-fill 1.4s ease-out forwards;
}

/* Clean Buttons, Forms, Inputs, Expanders, Chat */
.stButton > button[kind="primary"],
button[data-testid="stBaseButton-primary"],
button[data-testid="baseButton-primary"] {
    font-weight: 600 !important;
    color: #ffffff !important;
    background: linear-gradient(90deg, #2563eb 0%, #10b981 100%) !important;
    border: 1px solid rgba(255, 255, 255, 0.14) !important;
    border-radius: var(--radius-sm) !important;
    min-height: 42px !important;
    transition: opacity 0.15s ease, transform 0.15s ease !important;
}

.stButton > button[kind="primary"]:hover,
button[data-testid="stBaseButton-primary"]:hover,
button[data-testid="baseButton-primary"]:hover {
    opacity: 0.94;
    transform: translateY(-1px);
}

.stButton > button, .stDownloadButton > button {
    font-size: 0.84rem;
    font-weight: 600;
    border-radius: var(--radius-sm);
    min-height: 40px;
    border: 1px solid var(--pro-border-strong);
    background: var(--pro-surface-elevated);
    color: var(--pro-text);
    transition: border-color 0.15s ease, background-color 0.15s ease;
}

.stButton > button:hover, .stDownloadButton > button:hover {
    border-color: var(--pro-blue);
}

div[data-testid="stForm"] {
    background: var(--pro-surface);
    border: 1px solid var(--pro-border);
    border-radius: var(--radius-md);
    padding: 1.05rem 1.15rem;
}

div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div {
    background-color: #0f172a !important;
    border: 1px solid var(--pro-border-strong) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--pro-text) !important;
}

div[data-baseweb="input"] > div:focus-within,
div[data-baseweb="select"] > div:focus-within {
    border-color: var(--pro-blue) !important;
}

div[data-testid="stExpander"] {
    background: var(--pro-surface) !important;
    border: 1px solid var(--pro-border) !important;
    border-radius: var(--radius-md) !important;
}

div[data-testid="stAlert"] {
    background: var(--pro-surface) !important;
    border: 1px solid var(--pro-border) !important;
    border-radius: var(--radius-sm) !important;
}

div[data-testid="stChatMessage"] {
    background: var(--pro-surface) !important;
    border: 1px solid var(--pro-border) !important;
    border-radius: var(--radius-md) !important;
    padding: 0.75rem 1rem !important;
    margin-bottom: 0.55rem !important;
}

div[data-testid="stChatInput"] > div {
    background: var(--pro-surface) !important;
    border: 1px solid var(--pro-border-strong) !important;
    border-radius: var(--radius-md) !important;
}

button[data-baseweb="tab"] {
    font-size: 0.84rem !important;
    font-weight: 600 !important;
    border-radius: 8px 8px 0 0;
    background: var(--pro-surface) !important;
    border: 1px solid var(--pro-border) !important;
    margin-right: 0.25rem;
}

div[data-testid="stMetric"] {
    background: var(--pro-surface);
    border: 1px solid var(--pro-border);
    border-radius: var(--radius-md);
    padding: 0.85rem 1rem;
}

div[data-testid="stDataFrame"], div[data-testid="stTable"] {
    border: 1px solid var(--pro-border);
    border-radius: var(--radius-md);
    overflow-x: auto;
}

@media (min-width: 769px) and (max-width: 1366px) {
    .main .block-container,
    [data-testid="stMainBlockContainer"] {
        padding-left: 1.15rem;
        padding-right: 1.15rem;
    }
    .kpi-grid {
        grid-template-columns: repeat(auto-fit, minmax(155px, 1fr));
    }
    .stButton > button, .stDownloadButton > button {
        font-size: 0.8rem;
        padding-left: 0.65rem;
        padding-right: 0.65rem;
    }
}

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

@media (max-width: 768px) {
    .main .block-container,
    [data-testid="stMainBlockContainer"] {
        padding-top: 0.75rem;
        padding-bottom: 2rem;
        padding-left: 0.65rem;
        padding-right: 0.65rem;
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
        gap: 0.6rem;
    }
}
</style>
"""






def inject_global_styles() -> None:
    """Inject active portal theme CSS cleanly with zero bleed between modes."""
    theme = get_portal_theme()
    if theme == "DEFAULT":
        st.markdown(DEFAULT_PRO_CSS, unsafe_allow_html=True)
    elif theme == "DOOMSDAY":
        st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
        st.markdown(DOOMSDAY_OVERRIDE_CSS, unsafe_allow_html=True)
    else:
        st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def render_edition_toggle(in_sidebar: bool = False) -> None:
    """Render Portal Theme / Edition Switcher."""
    theme = get_portal_theme()
    if theme == "DEFAULT":
        active_badge = "💼 ACTIVE: DEFAULT (PRO STANDARD)"
        badge_color = "#10b981"
    elif theme == "DOOMSDAY":
        active_badge = "☣️ ACTIVE: DOOMSDAY (DEFCON-1)"
        badge_color = "#39ff14"
    else:
        active_badge = "🌴 ACTIVE: GTA VI (VICE CITY)"
        badge_color = "#00E5FF"

    target = st.sidebar if in_sidebar else st

    if in_sidebar:
        st.sidebar.markdown(
            f'<div style="font-size:0.72rem; font-weight:700; letter-spacing:0.06em; color:#94a3b8; margin-bottom:0.35rem;">'
            f'PORTAL THEME // EDITION<br/>'
            f'<span style="color:{badge_color};">{active_badge}</span>'
            f"</div>",
            unsafe_allow_html=True,
        )
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.sidebar.button(
                "💼 Default Pro",
                key="edition_btn_default",
                type="primary" if theme == "DEFAULT" else "secondary",
                use_container_width=True,
            ):
                if theme != "DEFAULT":
                    switch_world_edition("DEFAULT")
                    st.rerun()
        with col2:
            if st.sidebar.button(
                "🌴 GTA VI",
                key="edition_btn_gta",
                type="primary" if theme == "GTA VI" else "secondary",
                use_container_width=True,
            ):
                if theme != "GTA VI":
                    switch_world_edition("GTA VI")
                    st.rerun()
        if st.sidebar.button(
            "🌋 Doomsday (Apocalypse)",
            key="edition_btn_doomsday",
            type="primary" if theme == "DOOMSDAY" else "secondary",
            use_container_width=True,
        ):
            if theme != "DOOMSDAY":
                switch_world_edition("DOOMSDAY")
                st.rerun()
        return

    with target.container():
        st.markdown(
            f'<div style="background:rgba(16,26,50,0.85); border:1px solid rgba(0,229,255,0.25); border-radius:12px; padding:0.6rem 1rem; margin-bottom:0.8rem; display:flex; justify-content:space-between; align-items:center;">'
            f'<span style="font-size:0.82rem; font-weight:700; color:#00E5FF;">PORTAL THEME // EDITION SWITCHER</span>'
            f'<span style="font-size:0.78rem; font-weight:700; color:{badge_color};">{active_badge}</span>'
            f"</div>",
            unsafe_allow_html=True,
        )
        col_def, col_gta, col_doom = st.columns(3, gap="small")
        with col_def:
            if st.button("💼 Default Pro", key="edition_btn_top_def", use_container_width=True):
                if theme != "DEFAULT":
                    switch_world_edition("DEFAULT")
                    st.rerun()
        with col_gta:
            if st.button("🌴 GTA VI", key="edition_btn_top_gta", use_container_width=True):
                if theme != "GTA VI":
                    switch_world_edition("GTA VI")
                    st.rerun()
        with col_doom:
            if st.button("🌋 Doomsday", key="edition_btn_top_doom", use_container_width=True):
                if theme != "DOOMSDAY":
                    switch_world_edition("DOOMSDAY")
                    st.rerun()


def render_wanted_stars_html(active_stars: int = 6, total_stars: int = 6) -> str:
    """Wanted stars removed in GTA VI Vice City Edition (kept only for Doomsday)."""
    if not is_doomsday():
        return ""
    clamped = max(0, min(active_stars, total_stars))
    stars_on = "".join('<span class="wanted-star-on">★</span>' for _ in range(clamped))
    stars_off = "".join('<span class="wanted-star-off">☆</span>' for _ in range(total_stars - clamped))
    return (
        f'<div class="wanted-rack" style="display:flex !important; opacity:1 !important;">'
        f'<span class="wanted-label">WANTED</span>'
        f"{stars_on}{stars_off}"
        f"</div>"
    )


def render_vice_hud_banner(wanted_stars: int = 6, telemetry: str = "BAWSAQ // LCN LIVE LINK") -> None:
    """Top eagle wing & wanted banner removed in GTA VI (kept only for Doomsday)."""
    if not is_doomsday():
        return
    stars_html = render_wanted_stars_html(active_stars=wanted_stars, total_stars=6)
    safe_telemetry = html.escape("SECURITY LEVEL: DEFCON-1 · RADIOACTIVITY ALERT")
    wing_text = "☣️ ★ DRONACHARYA GROUP OF INSTITUTIONS • AKTU ★ ☣️"
    sub_ribbon = "⚠️ DEFCON-1 BUNKER PROTOCOL • APOCALYPSE TERMINAL ⚠️"
    title_grad = "linear-gradient(90deg,#ffb703,#ff4500,#39ff14)"

    st.markdown(
        f'<div class="vice-hud-top" style="display:flex !important; opacity:1 !important;">'
        f'<div class="vice-telemetry-tag">▸▸ {safe_telemetry}<br/>'
        f'<span style="font-family:\'Orbitron\',sans-serif; font-weight:900; font-size:0.78rem; '
        f'background:{title_grad}; -webkit-background-clip:text; '
        f'-webkit-text-fill-color:transparent; filter:drop-shadow(0 0 6px rgba(57,255,20,0.45));">'
        f'AI STOCK INSIGHTS PORTAL · BCC 351</span></div>'
        f'<div class="vice-wing-emblem">'
        f'<div class="vice-wing-row">'
        f'<span class="wing-chevron"></span>'
        f'<span class="wing-pill">{wing_text}</span>'
        f'<span class="wing-chevron right"></span>'
        f'</div>'
        f'<div class="vice-sub-ribbon">{sub_ribbon}</div>'
        f'</div>'
        f'{stars_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_page_header(
    title: str,
    subtitle: str,
    badge: str = "NSE INDIA • AI INSIGHTS",
    use_calligraphy: bool = False,
    wanted_stars: int = 0,
) -> None:
    """Render clean collegiate header (Default Pro) or sleek modern Vice City card (GTA VI)."""
    safe_badge = html.escape(badge)
    safe_title = html.escape(title)
    safe_subtitle = html.escape(subtitle)

    if is_default_theme():
        st.markdown(
            f'<div class="pro-page-header">'
            f'<div class="pro-header-badge">● {safe_badge}</div>'
            f"<h1>{safe_title}</h1>"
            f"<p>{safe_subtitle}</p>"
            f"</div>",
            unsafe_allow_html=True,
        )
        return

    if is_doomsday():
        render_vice_hud_banner(wanted_stars=wanted_stars)
        st.markdown(
            f'<div class="portal-hero">'
            f'<div class="portal-hero-badge">☣️ {safe_badge}</div>'
            f'<div class="portal-hero-row">'
            f"<div style='flex:1; min-width:260px;'>"
            f"<h1>{safe_title}</h1>"
            f"<p>▸▸ {safe_subtitle}</p>"
            f"</div>"
            f'<div class="pixel-arrow-pill">☢️ 📉🔥 DEFCON-1 INDEX ▾▾</div>'
            f"</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        return

    # GTA VI (Vice City) Clean Reference Header Card
    st.markdown(
        f'<div class="ref-subpage-header">'
        f'<div class="ref-subpage-badge">⚡ {safe_badge}</div>'
        f'<h1 class="ref-subpage-title">{safe_title}</h1>'
        f'<p class="ref-subpage-sub">▸▸ {safe_subtitle}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _clean_html(html_str: str) -> str:
    """Strip leading/trailing whitespace on every line so Markdown never treats HTML as an indented code block."""
    return "\n".join(line.strip() for line in html_str.splitlines() if line.strip())


def render_doomsday_reboot_overlay() -> None:
    """Render fallback reboot overlay for Doomsday edition."""
    st.markdown(
        _clean_html("""
        <div class="leonida-transition-shell">
            <div class="steel-rivet-card doomsday-glitch-stage" style="text-align:center; padding:1.8rem 1.4rem;">
                <div class="doomsday-scan-beam"></div>
                <div style="font-family:'Orbitron',sans-serif; color:#ffb703; font-size:0.85rem; letter-spacing:0.14em;">
                    ⚠️ FALLBACK / EMERGENCY REBOOT INITIATED
                </div>
                <div class="cyber-uplink-crest" style="border-color:#ff4500;">
                    <div class="cyber-uplink-ring" style="border-color:#39ff14;"></div>
                    <div style="font-size:3.2rem; filter:drop-shadow(0 0 14px #39ff14);">☣️</div>
                </div>
                <div class="neon-progress-track" style="border-color:#39ff14;">
                    <div class="neon-progress-fill" style="background:linear-gradient(90deg,#9a1b00,#ff4500,#ffb703,#39ff14);"></div>
                </div>
                <div class="glitch-seq-line seq-1" style="color:#ff4500;">▸ ALERT: REDIRECTING TO bunker.net CLIENT...</div>
                <div class="glitch-seq-line seq-3" style="color:#39ff14;">▸ DEFCON-1 STATUS ACTIVE // BUNKER ONLINE</div>
            </div>
        </div>
        """),
        unsafe_allow_html=True,
    )


def render_login_transition_overlay(username: str) -> None:
    """Render clean theme-aware login loading transition."""
    safe_user = html.escape(username)
    if is_default_theme():
        st.markdown(
            _clean_html(f"""
            <div class="pro-transition-shell">
                <div style="font-size:0.75rem; font-weight:700; letter-spacing:0.08em; color:#10b981; text-transform:uppercase;">
                    AI STOCK INSIGHTS PORTAL • PRO STANDARD
                </div>
                <h2 style="margin:0.45rem 0 0.25rem 0; font-size:1.45rem; font-weight:800; color:#f8fafc;">
                    Authenticating Live NSE Market Feed...
                </h2>
                <p style="margin:0; color:#94a3b8; font-size:0.9rem;">
                    Initializing equity analytics, ML price regression, and paper portfolio for <strong>{safe_user}</strong>
                </p>
                <div class="pro-progress-track">
                    <div class="pro-progress-fill"></div>
                </div>
            </div>
            """),
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        _clean_html(f"""
        <div style="display:flex; justify-content:center; align-items:center; min-height:240px;">
            <div style="background:rgba(16,26,50,0.92); border:1.5px solid rgba(0,229,255,0.45); border-radius:16px; padding:2rem 2.5rem; text-align:center; box-shadow:0 8px 32px rgba(0,0,0,0.6);">
                <div style="font-size:2.2rem; margin-bottom:0.6rem;">🌴🏙️</div>
                <div style="font-family:'Orbitron',sans-serif; font-size:1.15rem; font-weight:800; color:#00E5FF; margin-bottom:0.35rem;">
                    WELCOME, {safe_user.upper()}
                </div>
                <div style="font-size:0.85rem; color:#94a3b8; margin-bottom:1.2rem;">
                    Loading AI Stock Insights & Live NSE Analytics...
                </div>
                <div style="width:260px; height:4px; background:rgba(0,229,255,0.15); border-radius:4px; overflow:hidden; margin:0 auto;">
                    <div style="width:100%; height:100%; background:linear-gradient(90deg, #00E5FF, #FF35C8); animation: neonLinePulse 1.5s infinite;"></div>
                </div>
            </div>
        </div>
        """),
        unsafe_allow_html=True,
    )


def build_gta_chase_transition_html(wanted_stars: int = 2) -> str:
    """Fast CSS neon glow transition line (video transition removed)."""
    return '<div class="gta-neon-glow-line"></div>'


def render_gta_chase_transition(wanted_stars: int = 2) -> None:
    """Render fast CSS neon glow transition line without blocking or video."""
    st.markdown('<div class="gta-neon-glow-line"></div>', unsafe_allow_html=True)


def render_weazel_flash_ticker(headlines: list[str]) -> None:
    """Ticker removed in GTA VI Vice City Edition (kept only for Doomsday)."""
    if not is_doomsday():
        return
    joined = "   ✦   ".join(html.escape(h) for h in headlines if h)
    if not joined:
        joined = "CRITICAL EMERGENCY MONITORING ACTIVE — BUNKER.NET NSE SURVEILLANCE LOCKED"
    tag_text = "☣️ DISASTER BROADCAST NETWORK"
    st.markdown(
        f'<div class="weazel-flash-bar" style="display:flex !important; opacity:1 !important;">'
        f'<div class="weazel-tag">{tag_text}</div>'
        f'<div class="weazel-marquee-wrap">'
        f'<div class="weazel-marquee-track">{joined} &nbsp;&nbsp;&nbsp;✦&nbsp;&nbsp;&nbsp; {joined}</div>'
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )


def render_signal_badge(signal: str, confidence: int | None = None) -> str:
    """Return HTML markup for a BUY / SELL / HOLD pill badge."""
    sig_upper = signal.upper()
    if sig_upper == "BUY":
        cls, dot = "badge-buy", "🟢"
    elif sig_upper == "SELL":
        cls, dot = "badge-sell", "🔴"
    else:
        cls, dot = "badge-hold", "🟡"

    suffix = f" · {confidence}% CONF" if confidence is not None else ""
    return f'<span class="signal-badge {cls}">{dot} {html.escape(sig_upper)}{html.escape(suffix)}</span>'


def render_kpi_grid(cards: list[dict[str, str]]) -> None:
    """Render a responsive KPI card grid."""
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
    """Apply active portal theme styling to Plotly figures cleanly across all 3 editions."""
    if is_default_theme():
        layout_kwargs: dict = {
            "template": "plotly_dark",
            "paper_bgcolor": "#111827",
            "plot_bgcolor": "#0f172a",
            "font": {"family": "Plus Jakarta Sans, Inter, sans-serif", "color": "#e2e8f0", "size": 12},
            "height": height,
            "margin": {"l": 16, "r": 16, "t": 54, "b": 28},
            "hovermode": "x unified",
            "legend": {
                "orientation": "h",
                "yanchor": "bottom",
                "y": 1.02,
                "xanchor": "right",
                "x": 1,
                "bgcolor": "rgba(17, 24, 39, 0.85)",
                "bordercolor": "rgba(255, 255, 255, 0.08)",
                "borderwidth": 1,
            },
        }
        if title:
            layout_kwargs["title"] = {
                "text": title,
                "font": {"family": "Plus Jakarta Sans, Inter, sans-serif", "size": 15, "color": "#f8fafc"},
            }
        fig.update_layout(**layout_kwargs)
        fig.update_xaxes(
            gridcolor="rgba(255, 255, 255, 0.06)",
            linecolor="rgba(255, 255, 255, 0.14)",
            zeroline=False,
        )
        fig.update_yaxes(
            gridcolor="rgba(255, 255, 255, 0.06)",
            linecolor="rgba(255, 255, 255, 0.14)",
            zeroline=False,
        )
        return fig

    doomsday = is_doomsday()
    paper_bg = "rgba(16, 11, 9, 0.94)" if doomsday else "#070B1A"
    plot_bg = "rgba(24, 15, 11, 0.92)" if doomsday else "#101A32"
    accent_primary = "#39ff14" if doomsday else "#00E5FF"
    grid_x = "rgba(255, 69, 0, 0.18)" if doomsday else "rgba(255, 255, 255, 0.06)"
    grid_y = "rgba(57, 255, 20, 0.14)" if doomsday else "rgba(255, 255, 255, 0.06)"

    layout_kwargs = {
        "template": "plotly_dark",
        "paper_bgcolor": paper_bg,
        "plot_bgcolor": plot_bg,
        "font": {"family": "Share Tech Mono, Rajdhani, sans-serif", "color": "#f8fafc", "size": 12},
        "height": height,
        "margin": {"l": 16, "r": 16, "t": 58, "b": 28},
        "hovermode": "x unified",
        "legend": {
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
            "bgcolor": "rgba(16, 10, 8, 0.78)" if doomsday else "rgba(16, 26, 50, 0.8)",
            "bordercolor": "rgba(57, 255, 20, 0.42)" if doomsday else "rgba(0, 229, 255, 0.25)",
            "borderwidth": 1,
        },
    }
    if title:
        layout_kwargs["title"] = {
            "text": title,
            "font": {"family": "Rajdhani, Orbitron, sans-serif", "size": 15, "color": accent_primary},
        }

    fig.update_layout(**layout_kwargs)
    fig.update_xaxes(
        gridcolor=grid_x,
        linecolor=accent_primary,
        zeroline=False,
    )
    fig.update_yaxes(
        gridcolor=grid_y,
        linecolor="#ff4500" if doomsday else "rgba(255, 53, 200, 0.35)",
        zeroline=False,
    )
    return fig


__all__ = [
    "build_gta_chase_transition_html",
    "inject_global_styles",
    "render_doomsday_reboot_overlay",
    "render_edition_toggle",
    "render_gta_chase_transition",
    "render_kpi_grid",
    "render_login_transition_overlay",
    "render_page_header",
    "render_signal_badge",
    "render_wanted_stars_html",
    "render_weazel_flash_ticker",
    "style_plotly_figure",
]
