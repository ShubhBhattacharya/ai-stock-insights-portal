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
    """Load assets/gta_transition_3s.mp4 once and cache as a base64 data URI based on file mtime."""
    video_path = _ASSETS_DIR / "gta_transition_3s.mp4"
    if not video_path.is_file():
        return ""
    mtime = video_path.stat().st_mtime
    return _cached_load_gta_video_uri(str(video_path), mtime)


@st.cache_data(show_spinner=False)
def _cached_load_gta_video_uri(path_str: str, mtime: float) -> str:
    b64 = base64.b64encode(Path(path_str).read_bytes()).decode("ascii")
    return f"data:video/mp4;base64,{b64}"

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
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;800;900&family=Rajdhani:wght@500;600;700&family=Share+Tech+Mono&family=Yellowtail&display=swap');

:root {{
    --bg-canvas: #070312;
    --bg-violet: #170631;
    --bg-surface: rgba(13, 6, 34, 0.9);
    --bg-steel: linear-gradient(160deg, rgba(35, 41, 66, 0.95) 0%, rgba(16, 12, 38, 0.97) 55%, rgba(28, 15, 48, 0.96) 100%);
    --neon-pink: #ff2a85;
    --neon-orange: #ff7a00;
    --neon-yellow: #fee440;
    --neon-cyan: #00f5d4;
    --neon-green: #39ff14;
    --neon-crimson: #ff2a6d;
    --border-neon: rgba(0, 245, 212, 0.45);
    --border-magenta: rgba(255, 42, 133, 0.58);
    --text-primary: #f8fafc;
    --text-secondary: #cbd5e1;
    --radius-lg: 16px;
    --radius-md: 12px;
    --radius-sm: 8px;
}}

@keyframes vice-pulse {{
    0%, 100% {{
        box-shadow: 0 0 12px rgba(0, 245, 212, 0.7), 0 0 26px rgba(255, 42, 133, 0.45), inset 0 0 12px rgba(254, 228, 64, 0.25);
    }}
    50% {{
        box-shadow: 0 0 24px rgba(0, 245, 212, 0.98), 0 0 40px rgba(254, 228, 64, 0.65), inset 0 0 18px rgba(0, 245, 212, 0.45);
    }}
}}

@keyframes neon-flicker {{
    0%, 19%, 21%, 23%, 25%, 54%, 56%, 100% {{ opacity: 1; }}
    20%, 24%, 55% {{ opacity: 0.85; }}
}}

@keyframes badge-float {{
    0%, 100% {{ transform: translateY(0px); }}
    50% {{ transform: translateY(-2px); }}
}}

@keyframes hazard-flash {{
    0%, 100% {{
        border-color: #ff2a6d;
        box-shadow: 0 0 14px rgba(255, 42, 109, 0.72), inset 0 0 12px rgba(255, 42, 109, 0.24);
    }}
    50% {{
        border-color: #00f5d4;
        box-shadow: 0 0 22px rgba(0, 245, 212, 0.82), inset 0 0 14px rgba(0, 245, 212, 0.26);
    }}
}}

@keyframes spin-radar {{
    from {{ transform: rotate(0deg); }}
    to {{ transform: rotate(360deg); }}
}}

@keyframes progress-sweep {{
    0% {{ width: 8%; }}
    45% {{ width: 64%; }}
    85% {{ width: 96%; }}
    100% {{ width: 100%; }}
}}

@keyframes transition-zoom-in {{
    0% {{ opacity: 0; transform: scale(1.04); }}
    25% {{ opacity: 1; transform: scale(1); }}
    100% {{ opacity: 1; transform: scale(1); }}
}}

@keyframes ticker-scroll {{
    0% {{ transform: translateX(12%); }}
    100% {{ transform: translateX(-18%); }}
}}

@keyframes weazel-scroll {{
    0% {{ transform: translateX(6%); }}
    100% {{ transform: translateX(-52%); }}
}}

@keyframes race-bar-sweep {{
    0% {{ transform: scaleX(0.18); }}
    100% {{ transform: scaleX(1); }}
}}

@keyframes phase-seq-1 {{
    0%, 34% {{ opacity: 1; }}
    36%, 100% {{ opacity: 0.28; }}
}}

@keyframes phase-seq-2 {{
    0%, 33% {{ opacity: 0.28; }}
    35%, 68% {{ opacity: 1; }}
    70%, 100% {{ opacity: 0.28; }}
}}

@keyframes phase-seq-3 {{
    0%, 67% {{ opacity: 0.28; }}
    70%, 100% {{ opacity: 1; }}
}}

@keyframes glitch-scan-sweep {{
    0% {{ top: -8%; opacity: 0.9; }}
    50% {{ top: 52%; opacity: 0.75; }}
    100% {{ top: 105%; opacity: 0.9; }}
}}

/* Global Edition Toggle Armored Console */
div[data-testid="stVerticalBlock"]:has(> div.element-container span.edition-toggle-marker),
div[data-testid="stVerticalBlockBorderWrapper"]:has(span.edition-toggle-marker) {{
    max-width: 780px !important;
    margin: 0 auto 0.65rem auto !important;
    background: linear-gradient(155deg, rgba(22, 26, 38, 0.94), rgba(10, 8, 22, 0.96)) !important;
    border: 2px solid rgba(0, 245, 212, 0.52) !important;
    border-radius: 14px !important;
    padding: 0.45rem 0.75rem 0.6rem 0.75rem !important;
    box-shadow: 0 0 18px rgba(0, 245, 212, 0.22), inset 0 0 14px rgba(255, 42, 133, 0.14) !important;
}}

.edition-toggle-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.4rem;
    font-family: 'Orbitron', sans-serif;
    font-size: 0.74rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    color: #fee440;
    margin-bottom: 0.35rem;
}}

.doomsday-glitch-stage {{
    position: relative;
    overflow: hidden;
}}

.doomsday-scan-beam {{
    position: absolute;
    left: 0;
    right: 0;
    height: 10px;
    background: linear-gradient(180deg, transparent, rgba(57, 255, 20, 0.75), rgba(255, 69, 0, 0.55), transparent);
    box-shadow: 0 0 22px rgba(57, 255, 20, 0.85);
    animation: glitch-scan-sweep 1.25s linear infinite;
    pointer-events: none;
}}

html, body, [class*="css"] {{
    font-family: 'Rajdhani', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    color: var(--text-primary);
}}

html, body, [data-testid="stAppViewContainer"], .stApp {{
    overflow-x: hidden !important;
}}

/* Leonida Synthwave Dusk Sky + Neon Horizon Grid + Dual Palm Shadows */
.stApp {{
    background-color: var(--bg-canvas);
    background-image:
        url("{_PALM_LEFT_SVG}"),
        url("{_PALM_RIGHT_SVG}"),
        linear-gradient(90deg, rgba(255, 42, 133, 0.14) 1px, transparent 1px),
        linear-gradient(0deg, rgba(0, 245, 212, 0.11) 1px, transparent 1px),
        radial-gradient(circle at 18% 12%, rgba(255, 42, 133, 0.28), transparent 36%),
        radial-gradient(circle at 82% 14%, rgba(0, 245, 212, 0.24), transparent 36%),
        radial-gradient(circle at 50% 85%, rgba(255, 122, 0, 0.16), transparent 45%),
        linear-gradient(180deg, #070312 0%, #15052e 48%, #210738 82%, #090418 100%);
    background-position: left bottom, right bottom, center center, center center, center center, center center, center center, center center;
    background-size: 230px auto, 230px auto, 56px 56px, 56px 56px, 100% 100%, 100% 100%, 100% 100%, 100% 100%;
    background-repeat: no-repeat, no-repeat, repeat, repeat, no-repeat, no-repeat, no-repeat, no-repeat;
    border-top: 2px solid rgba(255, 42, 133, 0.52);
    border-bottom: 2px solid rgba(0, 245, 212, 0.42);
}}

/* Hide Default Streamlit Header Chrome & Keep Sidebar Toggle Clickable */
header[data-testid="stHeader"] {{
    background: transparent !important;
    height: 0px !important;
    min-height: 0px !important;
    border: none !important;
    overflow: visible !important;
}}

[data-testid="stToolbar"],
[data-testid="stDecoration"] {{
    display: none !important;
}}

#MainMenu,
footer {{
    visibility: hidden !important;
}}

[data-testid="stSidebarCollapsedControl"],
[data-testid="stExpandSidebarButton"] {{
    visibility: visible !important;
    display: flex !important;
    position: fixed !important;
    top: 10px !important;
    left: 10px !important;
    z-index: 999999 !important;
}}

/* Main Container Spacing */
.main .block-container,
.block-container,
[data-testid="stMainBlockContainer"] {{
    padding-top: 0.75rem !important;
    padding-bottom: 5.5rem;
    padding-left: clamp(0.85rem, 2.4vw, 2.25rem);
    padding-right: clamp(0.85rem, 2.4vw, 2.25rem);
    max-width: 1460px;
}}

/* Calibration Neon Divider */
hr {{
    border: none !important;
    height: 2px !important;
    background: linear-gradient(90deg, transparent 0%, var(--neon-pink) 20%, var(--neon-cyan) 50%, var(--neon-yellow) 80%, transparent 100%) !important;
    box-shadow: 0 0 10px rgba(0, 245, 212, 0.5);
    margin: 1.15rem 0 !important;
}}

/* Sidebar Cyber HUD */
section[data-testid="stSidebar"] {{
    background:
        linear-gradient(180deg, rgba(13, 5, 34, 0.98) 0%, rgba(23, 6, 48, 0.97) 60%, rgba(8, 3, 22, 0.99) 100%);
    border-right: 2px solid var(--neon-pink);
    box-shadow: 4px 0 26px rgba(255, 42, 133, 0.3), inset -1px 0 14px rgba(0, 245, 212, 0.22);
}}

section[data-testid="stSidebar"] .stRadio > div {{
    gap: 0.32rem;
}}

section[data-testid="stSidebar"] .stRadio label {{
    font-family: 'Orbitron', sans-serif;
    font-size: 0.78rem;
    letter-spacing: 0.03em;
    padding: 0.54rem 0.72rem;
    border-radius: 8px;
    border: 1px solid rgba(0, 245, 212, 0.2);
    background: rgba(14, 6, 36, 0.75);
    transition: all 0.18s ease;
}}

section[data-testid="stSidebar"] .stRadio label:hover {{
    background: linear-gradient(90deg, rgba(255, 42, 133, 0.24), rgba(0, 245, 212, 0.16));
    border-color: var(--neon-cyan);
    box-shadow: 0 0 14px rgba(0, 245, 212, 0.38);
    transform: translateX(3px);
}}

/* Top GTA Wing Emblem + 6-Star Wanted Rack */
.vice-hud-top {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
    flex-wrap: wrap;
    padding: 0.5rem 0.9rem;
    margin-bottom: 0.75rem;
    border-radius: 12px;
    background: linear-gradient(90deg, rgba(14, 5, 34, 0.94), rgba(34, 8, 60, 0.94), rgba(14, 5, 34, 0.94));
    border: 1.5px solid var(--neon-pink);
    box-shadow: 0 0 18px rgba(255, 42, 133, 0.4), inset 0 0 14px rgba(0, 245, 212, 0.16);
}}

.vice-telemetry-tag {{
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    color: var(--neon-cyan);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    text-shadow: 0 0 8px rgba(0, 245, 212, 0.7);
}}

.vice-wing-emblem {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.18rem;
    margin: 0 auto;
    text-align: center;
}}

.vice-wing-row {{
    display: inline-flex;
    align-items: center;
    gap: 0.55rem;
}}

.wing-chevron {{
    display: inline-block;
    width: 34px;
    height: 10px;
    background: linear-gradient(90deg, var(--neon-pink), var(--neon-cyan));
    clip-path: polygon(0 50%, 28% 0, 100% 30%, 82% 50%, 100% 70%, 28% 100%);
    filter: drop-shadow(0 0 6px rgba(0, 245, 212, 0.85));
}}

.wing-chevron.right {{
    transform: scaleX(-1);
}}

.wing-pill {{
    font-family: 'Orbitron', sans-serif;
    font-size: clamp(0.65rem, 1.12vw, 0.82rem);
    font-weight: 800;
    letter-spacing: 0.09em;
    color: #ffffff;
    background: linear-gradient(90deg, rgba(255, 42, 133, 0.38), rgba(0, 245, 212, 0.25));
    border: 1px solid var(--neon-cyan);
    border-radius: 999px;
    padding: 0.22rem 0.85rem;
    text-shadow: 0 0 8px rgba(0, 245, 212, 0.8);
    box-shadow: 0 0 12px rgba(255, 42, 133, 0.45);
}}

.vice-sub-ribbon {{
    font-family: 'Yellowtail', cursive;
    font-size: 1.08rem;
    color: #ff6ec7;
    letter-spacing: 0.04em;
    text-shadow: 0 0 8px rgba(255, 42, 133, 0.9), 0 0 16px rgba(0, 245, 212, 0.7);
}}

.wanted-rack {{
    display: inline-flex;
    align-items: center;
    gap: 0.22rem;
    padding: 0.28rem 0.65rem;
    border-radius: 8px;
    background: rgba(7, 3, 18, 0.86);
    border: 1px solid rgba(254, 228, 64, 0.55);
    box-shadow: 0 0 14px rgba(254, 228, 64, 0.3);
}}

.wanted-label {{
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    color: #cbd5e1;
    margin-right: 0.25rem;
    letter-spacing: 0.08em;
}}

.wanted-star-on {{
    color: var(--neon-yellow);
    font-size: 1.05rem;
    text-shadow: 0 0 8px rgba(254, 228, 64, 0.95), 0 0 16px rgba(255, 122, 0, 0.85);
    animation: neon-flicker 4s infinite;
}}

.wanted-star-off {{
    color: rgba(148, 163, 184, 0.28);
    font-size: 1.05rem;
}}

/* Hero Banner */
.portal-hero {{
    position: relative;
    background:
        url("{_PALM_LEFT_SVG}"),
        url("{_PALM_RIGHT_SVG}"),
        linear-gradient(90deg, rgba(255, 42, 133, 0.14) 1px, transparent 1px),
        linear-gradient(0deg, rgba(0, 245, 212, 0.1) 1px, transparent 1px),
        linear-gradient(135deg, rgba(16, 6, 40, 0.96) 0%, rgba(44, 11, 78, 0.93) 48%, rgba(12, 34, 68, 0.95) 100%);
    background-position: left bottom, right bottom, center bottom, center bottom, center center;
    background-size: 165px auto, 165px auto, 32px 32px, 32px 32px, 100% 100%;
    background-repeat: no-repeat, no-repeat, repeat, repeat, no-repeat;
    border: 2px solid var(--neon-cyan);
    border-radius: var(--radius-lg);
    padding: clamp(1.1rem, 2.5vw, 1.75rem) clamp(1.15rem, 3vw, 2rem);
    margin-bottom: 1.25rem;
    box-shadow:
        0 0 24px rgba(0, 245, 212, 0.36),
        0 0 42px rgba(255, 42, 133, 0.26),
        inset 0 0 24px rgba(255, 42, 133, 0.16);
    overflow: hidden;
}}

.portal-hero::before {{
    content: "LEONIDA CALIBRATION // 00 -- 25 -- 50 -- 75 -- 100 // SYS.OK";
    position: absolute;
    top: 6px;
    right: 14px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.64rem;
    letter-spacing: 0.1em;
    color: rgba(0, 245, 212, 0.68);
}}

.portal-hero-badge {{
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    font-family: 'Orbitron', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    color: var(--neon-yellow);
    background: rgba(255, 42, 133, 0.24);
    border: 1px solid var(--neon-pink);
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    margin-bottom: 0.55rem;
    box-shadow: 0 0 12px rgba(255, 42, 133, 0.48);
}}

.portal-hero-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    flex-wrap: wrap;
}}

.portal-hero h1 {{
    margin: 0;
    font-family: 'Orbitron', sans-serif;
    font-size: clamp(1.4rem, 2.8vw, 2.2rem);
    font-weight: 900;
    line-height: 1.18;
    letter-spacing: 0.02em;
    background: linear-gradient(90deg, #ff2a85 0%, #ff7a00 50%, #fee440 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 0 10px rgba(0, 245, 212, 0.8));
}}

.portal-hero h1.vice-calligraphy {{
    font-family: 'Yellowtail', cursive !important;
    font-size: clamp(2.15rem, 4.4vw, 3.45rem) !important;
    font-weight: 400 !important;
    letter-spacing: 0.02em;
    padding-right: 0.4rem;
    background: linear-gradient(180deg, #ff4da6 0%, #ff7a00 58%, #fee440 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(2px 3px 0px #00f5d4) drop-shadow(0 0 14px rgba(0, 245, 212, 0.88));
}}

.portal-hero p {{
    margin: 0.45rem 0 0 0;
    font-family: 'Share Tech Mono', monospace;
    color: #e2e8f0;
    font-size: clamp(0.84rem, 1.25vw, 0.98rem);
    line-height: 1.45;
    text-shadow: 0 1px 6px rgba(0, 0, 0, 0.85);
}}

.pixel-arrow-pill {{
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.25rem 0.65rem;
    border-radius: 6px;
    background: rgba(7, 3, 18, 0.82);
    border: 1px solid var(--neon-green);
    color: var(--neon-green);
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.8rem;
    box-shadow: 0 0 12px rgba(57, 255, 20, 0.38);
    animation: badge-float 2.8s ease-in-out infinite;
}}

/* Steel Panel + 4 Corner Rivets + Hazard Stripes */
.steel-rivet-card {{
    position: relative;
    background: var(--bg-steel);
    border: 2px solid #64748b;
    border-radius: 14px;
    padding: 1.35rem 1.45rem;
    margin-bottom: 1rem;
    overflow: hidden;
    box-shadow:
        0 0 24px rgba(0, 245, 212, 0.32),
        0 14px 32px rgba(0, 0, 0, 0.78),
        inset 0 0 0 1px rgba(255, 255, 255, 0.12);
}}

.steel-rivet-card::before,
.steel-rivet-card::after {{
    content: "";
    position: absolute;
    left: 0;
    right: 0;
    height: 9px;
    background: repeating-linear-gradient(
        -45deg,
        #fee440 0px,
        #fee440 10px,
        #0f172a 10px,
        #0f172a 20px
    );
    opacity: 0.94;
}}

.steel-rivet-card::before {{ top: 0; border-bottom: 1px solid #000; }}
.steel-rivet-card::after {{ bottom: 0; border-top: 1px solid #000; }}

.rivet-dot {{
    position: absolute;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: radial-gradient(circle at 35% 35%, #f8fafc, #64748b 60%, #1e293b 100%);
    box-shadow: 0 0 5px rgba(0, 245, 212, 0.55);
    z-index: 2;
}}
.rivet-tl {{ top: 14px; left: 10px; }}
.rivet-tr {{ top: 14px; right: 10px; }}
.rivet-bl {{ bottom: 14px; left: 10px; }}
.rivet-br {{ bottom: 14px; right: 10px; }}

.graffiti-vi {{
    font-family: 'Orbitron', sans-serif;
    font-weight: 900;
    font-size: 2.65rem;
    line-height: 1;
    letter-spacing: -0.06em;
    background: linear-gradient(135deg, #00f5d4 0%, #c084fc 45%, #ff2a85 75%, #fee440 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(2px 2px 0px #090314) drop-shadow(0 0 12px rgba(255, 42, 133, 0.9));
    user-select: none;
}}

/* Cinematic 2-Second Login Transition Sequence */
.leonida-transition-shell {{
    animation: transition-zoom-in 0.55s ease-out;
    max-width: 820px;
    margin: 1.5rem auto;
}}

.cyber-uplink-crest {{
    position: relative;
    width: 156px;
    height: 156px;
    margin: 0.75rem auto 1rem auto;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 2.5px solid var(--neon-cyan);
    background: radial-gradient(circle, rgba(255, 42, 133, 0.22) 0%, rgba(10, 4, 28, 0.94) 72%);
    box-shadow: 0 0 28px rgba(0, 245, 212, 0.55), inset 0 0 22px rgba(255, 42, 133, 0.35);
    animation: vice-pulse 1.5s infinite;
}}

.cyber-uplink-ring {{
    position: absolute;
    inset: 9px;
    border-radius: 50%;
    border: 2px dashed rgba(254, 228, 64, 0.68);
    animation: spin-radar 3.2s linear infinite;
}}

.neon-progress-track {{
    width: 100%;
    height: 18px;
    border-radius: 999px;
    background: rgba(7, 3, 18, 0.9);
    border: 1.5px solid var(--neon-cyan);
    padding: 2px;
    overflow: hidden;
    box-shadow: 0 0 16px rgba(0, 245, 212, 0.4);
}}

.neon-progress-fill {{
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #ff2a85 0%, #ff7a00 45%, #fee440 75%, #00f5d4 100%);
    box-shadow: 0 0 16px rgba(255, 42, 133, 0.85);
    animation: progress-sweep 1.85s ease-out forwards;
}}

.holo-ticker-strip {{
    overflow: hidden;
    white-space: nowrap;
    margin: 0.8rem 0;
    padding: 0.35rem 0.6rem;
    border-top: 1px dashed rgba(0, 245, 212, 0.45);
    border-bottom: 1px dashed rgba(255, 42, 133, 0.45);
    background: rgba(7, 3, 18, 0.72);
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.8rem;
    color: var(--neon-cyan);
}}

.holo-ticker-inner {{
    display: inline-block;
    animation: ticker-scroll 3.8s linear infinite;
}}

.glitch-seq-line {{
    font-family: 'Orbitron', sans-serif;
    font-size: clamp(0.82rem, 1.5vw, 1rem);
    font-weight: 800;
    letter-spacing: 0.08em;
    text-align: center;
    margin: 0.25rem 0;
}}

.seq-1 {{ color: var(--neon-pink); text-shadow: 0 0 10px rgba(255, 42, 133, 0.85); animation: phase-seq-1 1.9s linear forwards; }}
.seq-2 {{ color: var(--neon-yellow); text-shadow: 0 0 10px rgba(254, 228, 64, 0.85); animation: phase-seq-2 1.9s linear forwards; }}
.seq-3 {{ color: var(--neon-green); text-shadow: 0 0 12px rgba(57, 255, 20, 0.9); animation: phase-seq-3 1.9s linear forwards; }}

/* Wanted Flashing Triggered Alert Card */
.wanted-alert-flash {{
    position: relative;
    background: linear-gradient(135deg, rgba(45, 7, 28, 0.94), rgba(14, 7, 36, 0.96));
    border: 2px solid #ff2a6d;
    border-radius: 12px;
    padding: 0.9rem 1.2rem;
    margin-bottom: 0.65rem;
    animation: hazard-flash 1.4s ease-in-out infinite;
}}

/* Calibration HUD Ruler */
.console-hud-ruler {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.68rem;
    color: var(--neon-cyan);
    border-top: 1px dashed rgba(0, 245, 212, 0.45);
    border-bottom: 1px dashed rgba(255, 42, 133, 0.45);
    padding: 0.25rem 0.5rem;
    margin: 0.35rem 0 0.65rem 0;
    background: rgba(7, 3, 18, 0.72);
    letter-spacing: 0.08em;
}}

/* KPI Cards Grid */
.kpi-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(185px, 1fr));
    gap: 0.85rem;
    margin: 0.75rem 0 1.25rem 0;
}}

.kpi-card {{
    position: relative;
    background: rgba(14, 7, 36, 0.94);
    border: 1.5px solid var(--border-neon);
    border-radius: var(--radius-md);
    padding: 0.95rem 1.1rem;
    box-shadow: 0 0 12px rgba(0, 245, 212, 0.16);
    will-change: transform;
    transition: transform 0.18s ease, border-color 0.18s ease;
}}

.kpi-card:hover {{
    transform: translateY(-2px);
    border-color: var(--neon-pink);
}}

.kpi-label {{
    font-family: 'Orbitron', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--neon-cyan);
    margin-bottom: 0.35rem;
}}

.kpi-value {{
    font-family: 'Share Tech Mono', monospace;
    font-size: clamp(1.3rem, 2vw, 1.65rem);
    font-weight: 700;
    color: var(--text-primary);
    font-variant-numeric: tabular-nums;
    line-height: 1.2;
    word-break: break-word;
    text-shadow: 0 0 10px rgba(0, 245, 212, 0.34);
}}

.kpi-delta {{
    display: inline-block;
    margin-top: 0.42rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.76rem;
    font-weight: 700;
    padding: 0.18rem 0.55rem;
    border-radius: 999px;
    font-variant-numeric: tabular-nums;
}}

.tone-up {{ color: #39ff14; background: rgba(57, 255, 20, 0.12); border: 1px solid rgba(57, 255, 20, 0.45); }}
.tone-down {{ color: #ff4d8d; background: rgba(255, 42, 109, 0.16); border: 1px solid rgba(255, 42, 109, 0.5); }}
.tone-neutral {{ color: #7dd3fc; background: rgba(0, 245, 212, 0.12); border: 1px solid rgba(0, 245, 212, 0.38); }}
.tone-warn {{ color: #fee440; background: rgba(254, 228, 64, 0.13); border: 1px solid rgba(254, 228, 64, 0.48); }}

/* Signal Badges */
.signal-badge {{
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-family: 'Orbitron', sans-serif;
    padding: 0.32rem 0.85rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 800;
    letter-spacing: 0.06em;
}}

.badge-buy {{ background: rgba(57, 255, 20, 0.14); color: #39ff14; border: 1.5px solid #39ff14; box-shadow: 0 0 14px rgba(57, 255, 20, 0.4); }}
.badge-sell {{ background: rgba(255, 42, 109, 0.18); color: #ff4d8d; border: 1.5px solid #ff2a6d; box-shadow: 0 0 14px rgba(255, 42, 109, 0.45); }}
.badge-hold {{ background: rgba(254, 228, 64, 0.14); color: #fee440; border: 1.5px solid #fee440; box-shadow: 0 0 14px rgba(254, 228, 64, 0.38); }}

/* WEAZEL NEWS // LEONIDA MARKET FLASH Lower-Third Ticker */
.weazel-flash-bar {{
    display: flex;
    align-items: center;
    gap: 0.75rem;
    background: linear-gradient(90deg, rgba(28, 6, 36, 0.96), rgba(14, 7, 36, 0.96));
    border: 2px solid #ff2a6d;
    border-left: 6px solid #fee440;
    border-radius: 10px;
    padding: 0.5rem 0.85rem;
    margin: 0.95rem 0 0.45rem 0;
    box-shadow: 0 0 20px rgba(255, 42, 109, 0.36);
    overflow: hidden;
}}

.weazel-tag {{
    flex-shrink: 0;
    font-family: 'Orbitron', sans-serif;
    font-weight: 900;
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    color: #070312;
    background: linear-gradient(90deg, #ff2a6d, #fee440);
    padding: 0.28rem 0.65rem;
    border-radius: 6px;
    text-transform: uppercase;
}}

.weazel-marquee-wrap {{
    flex: 1;
    overflow: hidden;
    white-space: nowrap;
}}

.weazel-marquee-track {{
    display: inline-block;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.84rem;
    color: #f8fafc;
    animation: weazel-scroll 18s linear infinite;
}}

/* Safehouse Empire Tier Card & XP Bar */
.safehouse-card {{
    position: relative;
    background: linear-gradient(155deg, rgba(16, 7, 42, 0.96), rgba(32, 9, 54, 0.96));
    border: 2px solid var(--neon-pink);
    border-radius: 14px;
    padding: 1.05rem 1.2rem;
    margin-bottom: 1rem;
    box-shadow: 0 0 22px rgba(255, 42, 133, 0.28), inset 0 0 18px rgba(0, 245, 212, 0.16);
    overflow: hidden;
}}

.safehouse-tier-badge {{
    display: inline-block;
    font-family: 'Orbitron', sans-serif;
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    color: #070312;
    background: linear-gradient(90deg, #00f5d4, #fee440);
    padding: 0.22rem 0.68rem;
    border-radius: 999px;
}}

.xp-bar-track {{
    width: 100%;
    height: 16px;
    border-radius: 999px;
    background: rgba(7, 3, 18, 0.92);
    border: 1.5px solid rgba(254, 228, 64, 0.65);
    padding: 2px;
    overflow: hidden;
    margin-top: 0.38rem;
}}

.xp-bar-fill {{
    height: 100%;
    border-radius: 999px;
    background: repeating-linear-gradient(
        -55deg,
        #fee440 0px,
        #fee440 10px,
        #00f5d4 10px,
        #00f5d4 18px
    );
    box-shadow: 0 0 14px rgba(0, 245, 212, 0.7);
    transition: width 0.6s ease-out;
}}

/* Head-to-Head Street Race Segmented Racing Bars */
.street-race-board {{
    position: relative;
    background: linear-gradient(160deg, rgba(16, 8, 40, 0.96), rgba(10, 5, 28, 0.97));
    border: 2px solid var(--neon-cyan);
    border-radius: 14px;
    padding: 1.1rem 1.25rem;
    margin: 0.8rem 0 1.15rem 0;
    box-shadow: 0 0 24px rgba(0, 245, 212, 0.24), inset 0 0 18px rgba(255, 42, 133, 0.14);
}}

.race-winner-pill {{
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-family: 'Orbitron', sans-serif;
    font-weight: 900;
    font-size: 0.84rem;
    letter-spacing: 0.06em;
    color: #070312;
    background: linear-gradient(90deg, #fee440, #39ff14);
    padding: 0.3rem 0.9rem;
    border-radius: 999px;
    box-shadow: 0 0 18px rgba(254, 228, 64, 0.75);
}}

.race-metric-block {{
    margin-bottom: 0.85rem;
}}

.race-track {{
    width: 100%;
    height: 14px;
    border-radius: 999px;
    background: rgba(6, 2, 16, 0.94);
    border: 1px solid rgba(148, 163, 184, 0.35);
    overflow: hidden;
    padding: 2px;
    margin: 0.22rem 0;
}}

.race-fill-cyan {{
    height: 100%;
    border-radius: 999px;
    transform-origin: left center;
    animation: race-bar-sweep 0.9s ease-out forwards;
    background: repeating-linear-gradient(-55deg, #00f5d4 0px, #00f5d4 10px, #0284c7 10px, #0284c7 16px);
    box-shadow: 0 0 12px rgba(0, 245, 212, 0.78);
}}

.race-fill-pink {{
    height: 100%;
    border-radius: 999px;
    transform-origin: left center;
    animation: race-bar-sweep 0.9s ease-out forwards;
    background: repeating-linear-gradient(-55deg, #ff2a85 0px, #ff2a85 10px, #9333ea 10px, #9333ea 16px);
    box-shadow: 0 0 12px rgba(255, 42, 133, 0.78);
}}

/* Collapsible iFruit Market Phone Floating Right-Edge Dock */
div[data-testid="stVerticalBlock"]:has(> div.element-container span.ifruit-anchor),
div[data-testid="stVerticalBlockBorderWrapper"]:has(span.ifruit-anchor) {{
    position: fixed !important;
    right: 1rem !important;
    bottom: 3.4rem !important;
    width: 295px !important;
    max-width: calc(100vw - 2rem) !important;
    max-height: 70vh !important;
    overflow-y: auto !important;
    z-index: 950 !important;
    background: linear-gradient(165deg, rgba(10, 5, 28, 0.97), rgba(24, 9, 48, 0.98)) !important;
    border: 2px solid #00f5d4 !important;
    border-radius: 18px !important;
    padding: 0.55rem 0.7rem !important;
    box-shadow: 0 8px 22px rgba(0, 0, 0, 0.78) !important;
    will-change: transform;
}}

@media (max-width: 768px) {{
    div[data-testid="stVerticalBlock"]:has(> div.element-container span.ifruit-anchor),
    div[data-testid="stVerticalBlockBorderWrapper"]:has(span.ifruit-anchor) {{
        position: static !important;
        width: 100% !important;
        max-width: 100% !important;
        margin-top: 1rem !important;
    }}
}}

/* Surface & Sidebar Profile Cards */
.surface-card {{
    background: var(--bg-surface);
    border: 1.5px solid var(--border-neon);
    border-radius: var(--radius-md);
    padding: 1.05rem 1.2rem;
    margin-bottom: 1rem;
    box-shadow: 0 0 16px rgba(0, 245, 212, 0.16);
}}

.sidebar-profile-card {{
    position: relative;
    background: linear-gradient(145deg, rgba(22, 8, 48, 0.96), rgba(10, 5, 28, 0.98));
    border: 2px solid var(--neon-cyan);
    border-radius: var(--radius-md);
    padding: 1.05rem 1rem 0.95rem 1rem;
    margin-bottom: 0.85rem;
    overflow: hidden;
    box-shadow: 0 0 16px rgba(0, 245, 212, 0.28), inset 0 0 12px rgba(255, 42, 133, 0.16);
}}

.sidebar-profile-card::before {{
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 6px;
    background: repeating-linear-gradient(-45deg, #fee440 0 8px, #0b0422 8px 16px);
}}

.sidebar-profile-name {{
    font-family: 'Orbitron', sans-serif;
    font-size: 0.92rem;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 0.25rem;
    text-shadow: 0 0 8px rgba(0, 245, 212, 0.55);
}}

.sidebar-cash-pill {{
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.88rem;
    color: var(--neon-green);
    font-weight: 700;
    font-variant-numeric: tabular-nums;
}}

.news-item-card {{
    background: rgba(14, 6, 36, 0.88);
    border: 1px solid rgba(255, 42, 133, 0.38);
    border-radius: var(--radius-sm);
    padding: 0.72rem 0.9rem;
    margin-bottom: 0.55rem;
    transition: all 0.18s ease;
}}

.news-item-card:hover {{
    border-color: var(--neon-cyan);
    box-shadow: 0 0 14px rgba(0, 245, 212, 0.28);
}}

.news-item-card a {{
    color: #f1f5f9;
    text-decoration: none;
    font-weight: 600;
    font-size: 0.92rem;
    line-height: 1.35;
    display: block;
}}

.news-item-card a:hover {{
    color: var(--neon-cyan);
}}

.news-publisher {{
    font-family: 'Share Tech Mono', monospace;
    color: var(--neon-pink);
    font-size: 0.74rem;
    margin-top: 0.25rem;
}}

/* Primary Arcade Buttons */
.stButton > button[kind="primary"],
button[data-testid="stBaseButton-primary"],
button[data-testid="baseButton-primary"] {{
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 800 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase;
    color: #070312 !important;
    background: linear-gradient(90deg, #00f5d4 0%, #39ff14 48%, #fee440 100%) !important;
    border: 2px solid #fee440 !important;
    border-radius: 10px !important;
    min-height: 46px !important;
    box-shadow: 0 0 14px rgba(0, 245, 212, 0.45);
    will-change: transform;
    transition: transform 0.15s ease, filter 0.15s ease !important;
}}

/* Tactical Command Board Ticker Cards & Bottom Status Strip */
.tactical-card {{
    position: relative;
    background: rgba(11, 5, 30, 0.94);
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 0.85rem;
    will-change: transform;
    transition: transform 0.16s ease;
}}
.tactical-card:hover {{
    transform: translateY(-2px);
}}
.tactical-card-cyan {{
    border: 2px solid #00f5d4;
    box-shadow: 0 0 14px rgba(0, 245, 212, 0.28);
}}
.tactical-card-magenta {{
    border: 2px solid #ff2a85;
    box-shadow: 0 0 14px rgba(255, 42, 133, 0.28);
}}
.tactical-hazard-strip {{
    height: 7px;
    width: 100%;
    background: repeating-linear-gradient(
        -55deg,
        #fee440 0px,
        #fee440 8px,
        #0b0714 8px,
        #0b0714 16px
    );
}}
.tactical-card-inner {{
    padding: 0.65rem 0.85rem;
}}
.tactical-grid-head,
.tactical-grid-row {{
    display: grid;
    grid-template-columns: 1.35fr 1fr 0.9fr;
    gap: 0.35rem;
    align-items: center;
    font-family: 'Share Tech Mono', monospace;
}}
.tactical-grid-head {{
    font-family: 'Orbitron', sans-serif;
    font-size: 0.65rem;
    font-weight: 800;
    color: #94a3b8;
    letter-spacing: 0.08em;
    border-bottom: 1px solid rgba(255, 255, 255, 0.14);
    padding-bottom: 0.32rem;
    margin-bottom: 0.32rem;
}}
.tactical-grid-row {{
    font-size: 0.84rem;
    padding: 0.3rem 0;
    border-bottom: 1px dashed rgba(255, 255, 255, 0.08);
    font-variant-numeric: tabular-nums;
}}
.tactical-grid-row:last-child {{
    border-bottom: none;
    padding-bottom: 0.1rem;
}}
.tactical-sym {{
    color: #f8fafc;
    font-weight: 700;
    letter-spacing: 0.03em;
}}
.tactical-pos {{ color: #39ff14; font-weight: 700; text-align: right; }}
.tactical-neg {{ color: #ff4d6d; font-weight: 700; text-align: right; }}
.tactical-rng {{ color: #cbd5e1; font-weight: 600; text-align: right; }}

.tactical-center-shell {{
    background: rgba(11, 5, 30, 0.95);
    border: 2px solid #00f5d4;
    border-radius: 12px;
    padding: 0.55rem 0.75rem 0.25rem 0.75rem;
    box-shadow: 0 0 16px rgba(0, 245, 212, 0.24);
}}

.tactical-status-strip {{
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.75rem;
    margin: 0.65rem 0 1.05rem 0;
}}
.tactical-status-card {{
    background: rgba(12, 6, 32, 0.94);
    border: 1.5px solid rgba(0, 245, 212, 0.52);
    border-radius: 10px;
    padding: 0.7rem 0.9rem;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    gap: 0.25rem;
}}
.tactical-status-wanted {{
    border-color: #fee440;
    background: linear-gradient(145deg, rgba(28, 12, 48, 0.95), rgba(14, 7, 32, 0.97));
    animation: vice-pulse 2.2s ease-in-out infinite;
    will-change: transform, opacity;
}}
@media (max-width: 900px) {{
    .tactical-status-strip {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }}
}}
@media (max-width: 560px) {{
    .tactical-status-strip {{
        grid-template-columns: 1fr;
    }}
}}

.stButton > button[kind="primary"]:hover,
button[data-testid="stBaseButton-primary"]:hover,
button[data-testid="baseButton-primary"]:hover {{
    transform: translateY(-2px) scale(1.01) !important;
    filter: brightness(1.08);
}}

.stButton > button, .stDownloadButton > button {{
    font-family: 'Orbitron', sans-serif;
    font-size: 0.82rem;
    letter-spacing: 0.04em;
    border-radius: 10px;
    font-weight: 700;
    min-height: 42px;
    border: 1.5px solid rgba(0, 245, 212, 0.48);
    background: rgba(16, 7, 38, 0.88);
    color: #f8fafc;
    transition: all 0.15s ease;
}}

.stButton > button:hover, .stDownloadButton > button:hover {{
    transform: translateY(-1px);
    border-color: var(--neon-pink);
    box-shadow: 0 0 14px rgba(255, 42, 133, 0.45);
}}

/* Zero Standard White/Grey Boxes: Forms, Inputs, Expanders, Alerts, Chat Bubbles */
div[data-testid="stForm"] {{
    background: rgba(11, 5, 28, 0.9);
    border: 1.5px solid var(--neon-pink);
    border-radius: 12px;
    padding: 1rem 1.1rem;
    box-shadow: 0 0 20px rgba(255, 42, 133, 0.24), inset 0 0 14px rgba(0, 245, 212, 0.14);
}}

div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div {{
    background-color: rgba(9, 4, 24, 0.94) !important;
    border: 1px solid rgba(0, 245, 212, 0.48) !important;
    border-radius: 8px !important;
    font-family: 'Share Tech Mono', monospace !important;
    color: #f8fafc !important;
}}

div[data-baseweb="input"] > div:focus-within,
div[data-baseweb="select"] > div:focus-within {{
    border-color: var(--neon-pink) !important;
    box-shadow: 0 0 12px rgba(255, 42, 133, 0.55) !important;
}}

div[data-testid="stExpander"] {{
    background: rgba(12, 5, 32, 0.9) !important;
    border: 1.5px solid rgba(0, 245, 212, 0.42) !important;
    border-radius: 12px !important;
}}

div[data-testid="stAlert"] {{
    background: rgba(14, 6, 36, 0.92) !important;
    border: 1.5px solid rgba(0, 245, 212, 0.45) !important;
    border-radius: 10px !important;
}}

div[data-testid="stChatMessage"] {{
    background: rgba(13, 6, 36, 0.92) !important;
    border: 1.5px solid rgba(0, 245, 212, 0.48) !important;
    border-radius: 12px !important;
    padding: 0.75rem 1rem !important;
    margin-bottom: 0.6rem !important;
    box-shadow: 0 0 14px rgba(0, 245, 212, 0.16);
}}

div[data-testid="stChatInput"] > div {{
    background: rgba(11, 4, 28, 0.95) !important;
    border: 1.5px solid var(--neon-pink) !important;
    border-radius: 12px !important;
    box-shadow: 0 0 16px rgba(255, 42, 133, 0.28);
}}

/* Tabs */
button[data-baseweb="tab"] {{
    font-family: 'Orbitron', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em;
    border-radius: 8px 8px 0 0;
    background: rgba(15, 6, 38, 0.72) !important;
    border: 1px solid rgba(0, 245, 212, 0.25) !important;
    margin-right: 0.25rem;
}}

/* Native Metrics & DataFrames */
div[data-testid="stMetric"] {{
    background: var(--bg-surface);
    border: 1.5px solid var(--border-neon);
    border-radius: var(--radius-md);
    padding: 0.85rem 1rem;
}}

div[data-testid="stMetricValue"] {{
    font-family: 'Share Tech Mono', monospace;
    font-size: clamp(1.2rem, 1.8vw, 1.55rem);
    font-weight: 700;
    font-variant-numeric: tabular-nums;
}}

div[data-testid="stDataFrame"], div[data-testid="stTable"] {{
    border: 1.5px solid var(--border-magenta);
    border-radius: var(--radius-md);
    overflow-x: auto;
    box-shadow: 0 0 18px rgba(255, 42, 133, 0.2);
}}

/* Medium Laptop Responsive Polish (769px - 1366px) */
@media (min-width: 769px) and (max-width: 1366px) {{
    .main .block-container,
    [data-testid="stMainBlockContainer"] {{
        padding-left: 1.1rem;
        padding-right: 1.1rem;
    }}
    .tactical-card-inner {{
        padding: 0.45rem 0.65rem 0.55rem 0.65rem;
    }}
    .tactical-grid-row {{
        font-size: 0.78rem;
        gap: 0.25rem;
    }}
    .tactical-card-bottom {{
        font-size: 0.72rem;
    }}
    .kpi-grid {{
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    }}
    .stButton > button, .stDownloadButton > button {{
        font-size: 0.78rem;
        padding-left: 0.6rem;
        padding-right: 0.6rem;
    }}
}}

/* Tablet & Mobile Responsive Breakpoints */
@media (max-width: 1024px) {{
    div[data-testid="stHorizontalBlock"] {{
        flex-wrap: wrap !important;
        gap: 0.75rem !important;
    }}
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"],
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {{
        min-width: 240px !important;
        flex: 1 1 240px !important;
    }}
}}

@media (max-width: 768px) {{
    .main .block-container,
    [data-testid="stMainBlockContainer"] {{
        padding-top: 0.75rem;
        padding-bottom: 2.5rem;
        padding-left: 0.65rem;
        padding-right: 0.65rem;
    }}
    div[data-testid="stHorizontalBlock"] {{
        flex-direction: column !important;
    }}
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"],
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {{
        width: 100% !important;
        min-width: 100% !important;
        flex: 1 1 100% !important;
    }}
    button[data-baseweb="tab"] {{
        font-size: 0.7rem !important;
        padding: 0.45rem 0.55rem !important;
    }}
    .console-hud-ruler {{
        justify-content: center;
        text-align: center;
        font-size: 0.64rem;
    }}
    .console-hud-ruler span:first-child,
    .console-hud-ruler span:last-child {{
        display: none;
    }}
    .weazel-flash-bar {{
        flex-direction: column;
        align-items: flex-start;
        gap: 0.35rem;
    }}
    .kpi-grid {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.6rem;
    }}
    .kpi-card {{
        padding: 0.75rem 0.8rem;
    }}
    .wing-chevron {{
        display: none;
    }}
    .stApp {{
        background-size: 120px auto, 120px auto, 44px 44px, 44px 44px, 100% 100%, 100% 100%, 100% 100%, 100% 100%;
    }}
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
    background: repeating-linear-gradient(
        -55deg,
        #ffb703 0px,
        #ffb703 8px,
        #18120e 8px,
        #18120e 16px
    ) !important;
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
    """Inject ONLY the active portal theme CSS so zero styles bleed between modes."""
    theme = get_portal_theme()
    if theme == "DEFAULT":
        st.markdown(DEFAULT_PRO_CSS, unsafe_allow_html=True)
    elif theme == "DOOMSDAY":
        st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
        st.markdown(DOOMSDAY_OVERRIDE_CSS, unsafe_allow_html=True)
    else:
        st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def render_edition_toggle(in_sidebar: bool = False) -> None:
    """Render the 3-option Portal Theme / Edition Switcher (Default Pro | GTA VI | Doomsday)."""
    theme = get_portal_theme()
    if theme == "DEFAULT":
        active_badge = "💼 ACTIVE: DEFAULT (PRO STANDARD)"
        badge_color = "#10b981"
    elif theme == "DOOMSDAY":
        active_badge = "☣️ ACTIVE: DOOMSDAY (DEFCON-1)"
        badge_color = "#39ff14"
    else:
        active_badge = "🌴 ACTIVE: GTA VI (VICE CITY)"
        badge_color = "#00f5d4"

    target = st.sidebar if in_sidebar else st

    if in_sidebar:
        st.sidebar.markdown(
            f'<div style="font-size:0.72rem; font-weight:700; letter-spacing:0.06em; color:#94a3b8; margin-bottom:0.35rem;">'
            f'PORTAL THEME // EDITION<br/>'
            f'<span style="color:{badge_color};">{active_badge}</span>'
            f"</div>",
            unsafe_allow_html=True,
        )
        if st.sidebar.button(
            "💼 Default (Pro Standard)",
            key="edition_btn_default",
            type="primary" if theme == "DEFAULT" else "secondary",
            width="stretch",
        ):
            if theme != "DEFAULT":
                switch_world_edition("DEFAULT")
                st.rerun()
        if st.sidebar.button(
            "🌴 GTA VI (Vice City)",
            key="edition_btn_gta",
            type="primary" if theme == "GTA VI" else "secondary",
            width="stretch",
        ):
            if theme != "GTA VI":
                switch_world_edition("GTA VI")
                st.rerun()
        if st.sidebar.button(
            "🌋 Doomsday (Apocalypse)",
            key="edition_btn_doomsday",
            type="primary" if theme == "DOOMSDAY" else "secondary",
            width="stretch",
        ):
            if theme != "DOOMSDAY":
                switch_world_edition("DOOMSDAY")
                st.rerun()
        return

    with target.container():
        st.markdown('<span class="edition-toggle-marker"></span>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="edition-toggle-header">'
            f'<span>⚡ PORTAL THEME // EDITION SWITCHER</span>'
            f'<span style="color:{badge_color};">{active_badge}</span>'
            f"</div>",
            unsafe_allow_html=True,
        )
        col_def, col_gta, col_doom = st.columns(3, gap="small")
        with col_def:
            if st.button(
                "💼 Default (Pro Standard)",
                key="edition_btn_default",
                type="primary" if theme == "DEFAULT" else "secondary",
                width="stretch",
            ):
                if theme != "DEFAULT":
                    switch_world_edition("DEFAULT")
                    st.rerun()
        with col_gta:
            if st.button(
                "🌴 GTA VI (Vice City)",
                key="edition_btn_gta",
                type="primary" if theme == "GTA VI" else "secondary",
                width="stretch",
            ):
                if theme != "GTA VI":
                    switch_world_edition("GTA VI")
                    st.rerun()
        with col_doom:
            if st.button(
                "🌋 Doomsday (Apocalypse)",
                key="edition_btn_doomsday",
                type="primary" if theme == "DOOMSDAY" else "secondary",
                width="stretch",
            ):
                if theme != "DOOMSDAY":
                    switch_world_edition("DOOMSDAY")
                    st.rerun()


def render_wanted_stars_html(active_stars: int = 6, total_stars: int = 6) -> str:
    """Return HTML markup for Wanted stars (GTA VI), Alert System (Doomsday), or empty string in Default."""
    if is_default_theme():
        return ""
    clamped = max(0, min(active_stars, total_stars))
    if is_doomsday():
        on_icons = "".join('<span class="wanted-star-on" style="color:#ffb703;">⚠️</span>' for _ in range(clamped))
        off_icons = "".join('<span class="wanted-star-off">△</span>' for _ in range(total_stars - clamped))
        return (
            f'<div class="wanted-rack">'
            f'<span class="wanted-label" style="color:#ff4500; font-weight:700;">🚨 APOCALYPSE ALERT SYSTEM (TIER {clamped})</span>'
            f"{on_icons}{off_icons}"
            f"</div>"
        )
    stars_on = "".join('<span class="wanted-star-on">★</span>' for _ in range(clamped))
    stars_off = "".join('<span class="wanted-star-off">☆</span>' for _ in range(total_stars - clamped))
    return (
        f'<div class="wanted-rack">'
        f'<span class="wanted-label">WANTED</span>'
        f"{stars_on}{stars_off}"
        f"</div>"
    )


def render_vice_hud_banner(wanted_stars: int = 6, telemetry: str = "BAWSAQ // LCN LIVE LINK") -> None:
    """Render top armored wing emblem (GTA/Doomsday only; hidden in Default Pro Standard)."""
    if is_default_theme():
        return
    doomsday = is_doomsday()
    stars_html = render_wanted_stars_html(active_stars=wanted_stars, total_stars=6)
    safe_telemetry = html.escape(
        "SECURITY LEVEL: DEFCON-1 · RADIOACTIVITY ALERT" if (doomsday and telemetry == "BAWSAQ // LCN LIVE LINK") else telemetry
    )
    wing_text = (
        "☣️ ★ DRONACHARYA GROUP OF INSTITUTIONS • AKTU ★ ☣️"
        if doomsday
        else "🦅 ★ DRONACHARYA GROUP OF INSTITUTIONS • AKTU ★ 🦅"
    )
    sub_ribbon = (
        "⚠️ DEFCON-1 BUNKER PROTOCOL • APOCALYPSE TERMINAL ⚠️"
        if doomsday
        else "★ ★ ★ Vice City Special Events • Leonida Terminal ★ ★ ★"
    )
    title_grad = (
        "linear-gradient(90deg,#ffb703,#ff4500,#39ff14)"
        if doomsday
        else "linear-gradient(90deg,#ff2a85,#ff7a00,#fee440)"
    )

    st.markdown(
        f'<div class="vice-hud-top">'
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
        f"</div>"
        f'<div class="vice-sub-ribbon">{sub_ribbon}</div>'
        f"</div>"
        f"{stars_html}"
        f"</div>",
        unsafe_allow_html=True,
    )


def render_page_header(
    title: str,
    subtitle: str,
    badge: str = "NSE INDIA • BAWSAQ LIVE",
    use_calligraphy: bool = False,
    wanted_stars: int = 6,
) -> None:
    """Render clean corporate header (Default) or synthwave/apocalypse hero banner."""
    if is_default_theme():
        safe_badge = html.escape(badge)
        safe_title = html.escape(title)
        safe_subtitle = html.escape(subtitle)
        st.markdown(
            f'<div class="pro-page-header">'
            f'<div class="pro-header-badge">● {safe_badge}</div>'
            f"<h1>{safe_title}</h1>"
            f"<p>{safe_subtitle}</p>"
            f"</div>",
            unsafe_allow_html=True,
        )
        return

    doomsday = is_doomsday()
    render_vice_hud_banner(wanted_stars=wanted_stars)
    safe_badge = html.escape(badge)
    safe_title = html.escape(title)
    safe_subtitle = html.escape(subtitle)
    title_cls = ' class="vice-calligraphy"' if (use_calligraphy and not doomsday) else ""
    badge_icon = "☣️" if doomsday else "🌴"
    right_pill = "☢️ 📉🔥 DEFCON-1 INDEX ▾▾" if doomsday else "🌅 📈🌴 BAWSAQ INDEX ▲▲"

    st.markdown(
        f'<div class="portal-hero">'
        f'<div class="portal-hero-badge">{badge_icon} {safe_badge}</div>'
        f'<div class="portal-hero-row">'
        f"<div style='flex:1; min-width:260px;'>"
        f"<h1{title_cls}>{safe_title}</h1>"
        f"<p>▸▸ {safe_subtitle}</p>"
        f"</div>"
        f'<div class="pixel-arrow-pill">{right_pill}</div>'
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )


def render_doomsday_reboot_overlay() -> None:
    """Render full-screen Fallback / Emergency Reboot transition when switching into Doomsday."""
    render_vice_hud_banner(wanted_stars=6, telemetry="EMERGENCY REBOOT // BUNKER.NET")
    st.markdown(
        """
        <div class="leonida-transition-shell">
            <div class="steel-rivet-card doomsday-glitch-stage" style="text-align:center; padding:1.75rem 1.5rem;">
                <div class="doomsday-scan-beam"></div>
                <span class="rivet-dot rivet-tl"></span>
                <span class="rivet-dot rivet-tr"></span>
                <span class="rivet-dot rivet-bl"></span>
                <span class="rivet-dot rivet-br"></span>
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
                <div class="holo-ticker-strip" style="color:#39ff14; border-color:rgba(255,69,0,0.55);">
                    <div class="holo-ticker-inner">
                        DEFCON-1 ACTIVE // BUNKER.NET ENCRYPTED LINK &nbsp;//&nbsp; NSE FEED ROUTED TO SHELTER NODES
                        &nbsp;//&nbsp; RADIATION SHIELDS: ENGAGED
                    </div>
                </div>
                <div class="glitch-seq-line seq-1" style="color:#ff4500;">▸ ALERT: REDIRECTING TO bunker.net CLIENT...</div>
                <div class="glitch-seq-line seq-2" style="color:#ffb703;">▸ BYPASSING GLOBAL SECURITY RADARS...</div>
                <div class="glitch-seq-line seq-3" style="color:#39ff14;">▸ DEFCON-1 STATUS ACTIVE // BUNKER ONLINE</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_login_transition_overlay(username: str) -> None:
    """Render theme-aware login loading transition (1.5s fintech bar in Default, 2s in GTA/Doomsday)."""
    safe_user = html.escape(username)
    if is_default_theme():
        st.markdown(
            f"""
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
                <div style="font-size:0.78rem; color:#64748b;">
                    Dronacharya Group of Institutions · B.Tech Mini Project BCC 351
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    doomsday = is_doomsday()
    if doomsday:
        render_vice_hud_banner(wanted_stars=6, telemetry="BUNKER.NET ENTRY PROTOCOL")
        st.markdown(
            f"""
            <div class="leonida-transition-shell">
                <div class="steel-rivet-card doomsday-glitch-stage" style="text-align:center; padding:1.75rem 1.5rem;">
                    <div class="doomsday-scan-beam"></div>
                    <span class="rivet-dot rivet-tl"></span>
                    <span class="rivet-dot rivet-tr"></span>
                    <span class="rivet-dot rivet-bl"></span>
                    <span class="rivet-dot rivet-br"></span>
                    <div style="font-family:'Orbitron',sans-serif; color:#39ff14; font-size:0.82rem; letter-spacing:0.14em;">
                        SURVIVOR CLEARANCE // {safe_user.upper()}
                    </div>
                    <div class="cyber-uplink-crest" style="border-color:#ff4500;">
                        <div class="cyber-uplink-ring" style="border-color:#39ff14;"></div>
                        <div style="font-size:3.1rem; filter:drop-shadow(0 0 14px #39ff14);">☣️</div>
                    </div>
                    <div class="neon-progress-track" style="border-color:#39ff14;">
                        <div class="neon-progress-fill" style="background:linear-gradient(90deg,#9a1b00,#ff4500,#ffb703,#39ff14);"></div>
                    </div>
                    <div class="holo-ticker-strip" style="color:#39ff14; border-color:rgba(255,69,0,0.55);">
                        <div class="holo-ticker-inner">
                            BUNKER.NET UPLINK LOCKED &nbsp;//&nbsp; RELIANCE.NS &nbsp;//&nbsp; TCS.NS &nbsp;//&nbsp; SBIN.NS &nbsp;//&nbsp; WAR CAPITAL READY
                        </div>
                    </div>
                    <div class="glitch-seq-line seq-1" style="color:#ff4500;">▸ ALERT: CONNECTING TO BUNKER.NET...</div>
                    <div class="glitch-seq-line seq-2" style="color:#ffb703;">▸ BYPASSING GLOBAL SECURITY RADARS...</div>
                    <div class="glitch-seq-line seq-3" style="color:#39ff14;">▸ DEFCON-1 STATUS ACTIVE // ACCESS GRANTED</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    render_vice_hud_banner(wanted_stars=6, telemetry="LEONIDA ENTRY PROTOCOL")
    st.markdown(
        f"""
        <div class="leonida-transition-shell">
            <div class="steel-rivet-card" style="text-align:center; padding:1.75rem 1.5rem;">
                <span class="rivet-dot rivet-tl"></span>
                <span class="rivet-dot rivet-tr"></span>
                <span class="rivet-dot rivet-bl"></span>
                <span class="rivet-dot rivet-br"></span>
                <div style="font-family:'Orbitron',sans-serif; color:#00f5d4; font-size:0.82rem; letter-spacing:0.14em;">
                    OPERATOR VERIFIED // {safe_user.upper()}
                </div>
                <div class="cyber-uplink-crest">
                    <div class="cyber-uplink-ring"></div>
                    <div class="graffiti-vi" style="font-size:3.1rem;">VI</div>
                </div>
                <div class="neon-progress-track">
                    <div class="neon-progress-fill"></div>
                </div>
                <div class="holo-ticker-strip">
                    <div class="holo-ticker-inner">
                        RELIANCE.NS ▲ +1.84% &nbsp;//&nbsp; TCS.NS ▲ +0.92% &nbsp;//&nbsp; HDFCBANK.NS ▲ +1.15%
                        &nbsp;//&nbsp; INFY.NS ▼ -0.38% &nbsp;//&nbsp; SBIN.NS ▲ +2.07% &nbsp;//&nbsp; ADANIENT.NS ▲ +1.02%
                    </div>
                </div>
                <div class="glitch-seq-line seq-1">▸ INITIALIZING BAWSAQ / NSE FEED...</div>
                <div class="glitch-seq-line seq-2">▸ BYPASSING SECURITY...</div>
                <div class="glitch-seq-line seq-3">▸ ACCESS GRANTED // WELCOME TO LEONIDA</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_gta_chase_transition_html(wanted_stars: int = 2) -> str:
    """Build the 3.5-second GTA VI Video Transition Modal (LOADING... + Purple-Blue Progress Bar)."""
    video_uri = _load_gta_transition_video_uri()
    source_tags = ""
    if video_uri:
        source_tags += f'<source src="{video_uri}" type="video/mp4">\n'
    source_tags += '<source src="app/static/gta_transition_3s.mp4" type="video/mp4">\n'
    source_tags += '<source src="static/gta_transition_3s.mp4" type="video/mp4">\n'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<style>
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}
html, body {{
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: transparent;
}}
@keyframes loadProgress {{
    0%   {{ width: 0%; }}
    100% {{ width: 100%; }}
}}
@keyframes modalDismiss {{
    0%, 92% {{ opacity: 1; pointer-events: auto; }}
    99%     {{ opacity: 0; pointer-events: none; }}
    100%    {{ opacity: 0; pointer-events: none; display: none; }}
}}
#gta-transition-root {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.85);
    z-index: 999999;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    animation: modalDismiss 3.5s ease-in forwards;
}}
</style>
</head>
<body>
<div id="gta-transition-root">
    <div style="width:min(860px, 92vw); border-radius:18px; border:2px solid #ff2a85; box-shadow:0 0 40px rgba(255,42,133,0.6); overflow:hidden; background:#000;">
        <video autoplay muted playsinline style="width:100%; height:auto; display:block; object-fit:cover;">
            {source_tags}
        </video>
        <div style="padding:15px; text-align:center; background:linear-gradient(180deg, #111, #000);">
            <p style="color:#fff; font-family:monospace; font-size:18px; letter-spacing:2px; margin-bottom:8px;">LOADING...</p>
            <div style="width:100%; height:6px; background:#222; border-radius:3px; overflow:hidden;">
                <div style="width:100%; height:100%; background:linear-gradient(90deg, #ff2a85, #8b5cf6, #00f5d4); animation: loadProgress 3.5s linear forwards;"></div>
            </div>
        </div>
    </div>
</div>
<script>
setTimeout(function() {{
    var el = document.getElementById('gta-transition-root');
    if (el) {{
        el.style.transition = 'opacity 0.25s ease';
        el.style.opacity = '0';
        el.style.pointerEvents = 'none';
        setTimeout(function() {{
            el.style.display = 'none';
            try {{
                if (window.frameElement) {{
                    window.frameElement.style.display = 'none';
                    window.frameElement.style.height = '0px';
                }}
            }} catch(e) {{}}
        }}, 200);
    }}
}}, 3450);
</script>
</body>
</html>
"""


def render_gta_chase_transition(wanted_stars: int = 2) -> None:
    """Render the 3.5s GTA VI video transition overlay inside streamlit.components.v1.html(..., height=520)."""
    html_content = build_gta_chase_transition_html(wanted_stars=wanted_stars)
    components.html(html_content, height=520, scrolling=False)


def render_weazel_flash_ticker(headlines: list[str]) -> None:
    """Render lower-third breaking ticker (hidden in Default Pro Standard)."""
    if is_default_theme():
        return
    doomsday = is_doomsday()
    joined = "   ✦   ".join(html.escape(h) for h in headlines if h)
    if not joined:
        joined = (
            "CRITICAL EMERGENCY MONITORING ACTIVE — BUNKER.NET NSE SURVEILLANCE LOCKED"
            if doomsday
            else "BAWSAQ / LCN EQUITIES MONITORING ACTIVE — NO EXTREME SIGNAL ALERTS TRIGGERED"
        )
    tag_text = "☣️ DISASTER BROADCAST NETWORK" if doomsday else "WEAZEL NEWS // LEONIDA MARKET FLASH"
    st.markdown(
        f'<div class="weazel-flash-bar">'
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
    paper_bg = "rgba(16, 11, 9, 0.94)" if doomsday else "rgba(11, 5, 36, 0.92)"
    plot_bg = "rgba(24, 15, 11, 0.92)" if doomsday else "rgba(16, 7, 46, 0.90)"
    accent_primary = "#39ff14" if doomsday else "#00f5d4"
    grid_x = "rgba(255, 69, 0, 0.18)" if doomsday else "rgba(255, 42, 133, 0.16)"
    grid_y = "rgba(57, 255, 20, 0.14)" if doomsday else "rgba(0, 245, 212, 0.12)"

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
            "bgcolor": "rgba(10, 4, 28, 0.65)" if not doomsday else "rgba(16, 10, 8, 0.78)",
            "bordercolor": "rgba(57, 255, 20, 0.42)" if doomsday else "rgba(0, 245, 212, 0.35)",
            "borderwidth": 1,
        },
    }
    if title:
        layout_kwargs["title"] = {
            "text": title,
            "font": {"family": "Orbitron, sans-serif", "size": 15, "color": accent_primary},
        }

    fig.update_layout(**layout_kwargs)
    fig.update_xaxes(
        gridcolor=grid_x,
        linecolor=accent_primary,
        zeroline=False,
    )
    fig.update_yaxes(
        gridcolor=grid_y,
        linecolor="#ff4500" if doomsday else "rgba(255, 42, 133, 0.35)",
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
