"""GTA VI / Vice City Synthwave Neon UI Styling and Reusable HUD Components."""

from __future__ import annotations

import html
import plotly.graph_objects as go
import streamlit as st

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

GLOBAL_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;800;900&family=Rajdhani:wght@500;600;700&family=Share+Tech+Mono&family=Yellowtail&display=swap');

:root {{
    --bg-canvas: #070312;
    --bg-violet: #170631;
    --bg-surface: rgba(14, 7, 34, 0.86);
    --bg-steel: linear-gradient(160deg, rgba(35, 41, 66, 0.94) 0%, rgba(16, 13, 36, 0.96) 55%, rgba(28, 17, 48, 0.95) 100%);
    --neon-pink: #ff2a85;
    --neon-orange: #ff7a00;
    --neon-yellow: #ffe600;
    --neon-cyan: #00f0ff;
    --neon-green: #39ff14;
    --neon-crimson: #ff2a6d;
    --border-neon: rgba(0, 240, 255, 0.42);
    --border-magenta: rgba(255, 42, 133, 0.55);
    --text-primary: #f8fafc;
    --text-secondary: #cbd5e1;
    --radius-lg: 16px;
    --radius-md: 12px;
    --radius-sm: 8px;
}}

@keyframes vice-pulse {{
    0%, 100% {{
        box-shadow: 0 0 12px rgba(0, 240, 255, 0.65), 0 0 26px rgba(255, 42, 133, 0.45), inset 0 0 12px rgba(255, 230, 0, 0.25);
    }}
    50% {{
        box-shadow: 0 0 22px rgba(0, 240, 255, 0.95), 0 0 38px rgba(255, 230, 0, 0.65), inset 0 0 18px rgba(0, 240, 255, 0.4);
    }}
}}

@keyframes neon-flicker {{
    0%, 19%, 21%, 23%, 25%, 54%, 56%, 100% {{
        opacity: 1;
    }}
    20%, 24%, 55% {{
        opacity: 0.88;
    }}
}}

@keyframes badge-float {{
    0%, 100% {{ transform: translateY(0px); }}
    50% {{ transform: translateY(-2px); }}
}}

html, body, [class*="css"] {{
    font-family: 'Rajdhani', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}}

/* Synthwave Dusk Sky + Neon Horizon Grid + Dual Palm Shadows */
.stApp {{
    background-color: var(--bg-canvas);
    background-image:
        url("{_PALM_LEFT_SVG}"),
        url("{_PALM_RIGHT_SVG}"),
        linear-gradient(90deg, rgba(255, 42, 133, 0.14) 1px, transparent 1px),
        linear-gradient(0deg, rgba(0, 240, 255, 0.11) 1px, transparent 1px),
        radial-gradient(circle at 18% 12%, rgba(255, 42, 133, 0.26), transparent 36%),
        radial-gradient(circle at 82% 14%, rgba(0, 240, 255, 0.22), transparent 36%),
        radial-gradient(circle at 50% 85%, rgba(255, 122, 0, 0.16), transparent 45%),
        linear-gradient(180deg, #070312 0%, #15052e 48%, #210738 82%, #090418 100%);
    background-position: left bottom, right bottom, center center, center center, center center, center center, center center, center center;
    background-size: 230px auto, 230px auto, 56px 56px, 56px 56px, 100% 100%, 100% 100%, 100% 100%, 100% 100%;
    background-repeat: no-repeat, no-repeat, repeat, repeat, no-repeat, no-repeat, no-repeat, no-repeat;
    background-attachment: fixed;
    box-shadow: inset 0 0 0 2px rgba(255, 42, 133, 0.48), inset 0 0 28px rgba(0, 240, 255, 0.24);
}}

/* CRT Digital Scanline Overlay (Non-interactive) */
.stApp::after {{
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 999;
    background: repeating-linear-gradient(
        0deg,
        rgba(255, 255, 255, 0.025) 0px,
        rgba(255, 255, 255, 0.025) 1px,
        transparent 1px,
        transparent 3px
    );
}}

/* Main Container Multi-Layer Neon HUD Frame */
.main .block-container,
[data-testid="stMainBlockContainer"] {{
    padding-top: clamp(0.85rem, 2vw, 1.5rem);
    padding-bottom: 3rem;
    padding-left: clamp(0.85rem, 2.4vw, 2.25rem);
    padding-right: clamp(0.85rem, 2.4vw, 2.25rem);
    max-width: 1460px;
}}

/* Calibration Markings Divider */
hr {{
    border: none !important;
    height: 2px !important;
    background: linear-gradient(90deg, transparent 0%, var(--neon-pink) 20%, var(--neon-cyan) 50%, var(--neon-yellow) 80%, transparent 100%) !important;
    box-shadow: 0 0 10px rgba(0, 240, 255, 0.45);
    margin: 1.15rem 0 !important;
}}

/* Sidebar Cyber Console */
section[data-testid="stSidebar"] {{
    background:
        linear-gradient(180deg, rgba(13, 5, 34, 0.97) 0%, rgba(23, 6, 48, 0.96) 60%, rgba(8, 3, 22, 0.98) 100%);
    border-right: 2px solid var(--neon-pink);
    box-shadow: 4px 0 24px rgba(255, 42, 133, 0.28), inset -1px 0 12px rgba(0, 240, 255, 0.2);
}}

section[data-testid="stSidebar"] .stRadio > div {{
    gap: 0.32rem;
}}

section[data-testid="stSidebar"] .stRadio label {{
    font-family: 'Orbitron', sans-serif;
    font-size: 0.8rem;
    letter-spacing: 0.03em;
    padding: 0.55rem 0.72rem;
    border-radius: 8px;
    border: 1px solid rgba(0, 240, 255, 0.16);
    background: rgba(15, 7, 36, 0.65);
    transition: all 0.18s ease;
}}

section[data-testid="stSidebar"] .stRadio label:hover {{
    background: linear-gradient(90deg, rgba(255, 42, 133, 0.22), rgba(0, 240, 255, 0.14));
    border-color: var(--neon-cyan);
    box-shadow: 0 0 12px rgba(0, 240, 255, 0.35);
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
    background: linear-gradient(90deg, rgba(14, 5, 34, 0.92), rgba(34, 8, 60, 0.92), rgba(14, 5, 34, 0.92));
    border: 1.5px solid var(--neon-pink);
    box-shadow: 0 0 18px rgba(255, 42, 133, 0.38), inset 0 0 14px rgba(0, 240, 255, 0.16);
}}

.vice-telemetry-tag {{
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    color: var(--neon-cyan);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    text-shadow: 0 0 8px rgba(0, 240, 255, 0.65);
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
    filter: drop-shadow(0 0 6px rgba(0, 240, 255, 0.8));
}}

.wing-chevron.right {{
    transform: scaleX(-1);
}}

.wing-pill {{
    font-family: 'Orbitron', sans-serif;
    font-size: clamp(0.66rem, 1.15vw, 0.82rem);
    font-weight: 800;
    letter-spacing: 0.09em;
    color: #ffffff;
    background: linear-gradient(90deg, rgba(255, 42, 133, 0.35), rgba(0, 240, 255, 0.25));
    border: 1px solid var(--neon-cyan);
    border-radius: 999px;
    padding: 0.22rem 0.85rem;
    text-shadow: 0 0 8px rgba(0, 240, 255, 0.75);
    box-shadow: 0 0 12px rgba(255, 42, 133, 0.45);
}}

.vice-sub-ribbon {{
    font-family: 'Yellowtail', cursive;
    font-size: 1.08rem;
    color: #ff6ec7;
    letter-spacing: 0.04em;
    text-shadow: 0 0 8px rgba(255, 42, 133, 0.9), 0 0 16px rgba(0, 240, 255, 0.65);
}}

.wanted-rack {{
    display: inline-flex;
    align-items: center;
    gap: 0.22rem;
    padding: 0.28rem 0.65rem;
    border-radius: 8px;
    background: rgba(7, 3, 18, 0.82);
    border: 1px solid rgba(255, 230, 0, 0.45);
    box-shadow: 0 0 12px rgba(255, 230, 0, 0.25);
}}

.wanted-label {{
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    color: #94a3b8;
    margin-right: 0.25rem;
    letter-spacing: 0.08em;
}}

.wanted-star-on {{
    color: var(--neon-yellow);
    font-size: 1.05rem;
    text-shadow: 0 0 8px rgba(255, 230, 0, 0.95), 0 0 16px rgba(255, 122, 0, 0.8);
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
        linear-gradient(0deg, rgba(0, 240, 255, 0.1) 1px, transparent 1px),
        linear-gradient(135deg, rgba(16, 6, 40, 0.96) 0%, rgba(44, 11, 78, 0.92) 48%, rgba(12, 34, 68, 0.94) 100%);
    background-position: left bottom, right bottom, center bottom, center bottom, center center;
    background-size: 165px auto, 165px auto, 32px 32px, 32px 32px, 100% 100%;
    background-repeat: no-repeat, no-repeat, repeat, repeat, no-repeat;
    border: 2px solid var(--neon-cyan);
    border-radius: var(--radius-lg);
    padding: clamp(1.1rem, 2.5vw, 1.75rem) clamp(1.15rem, 3vw, 2rem);
    margin-bottom: 1.25rem;
    box-shadow:
        0 0 24px rgba(0, 240, 255, 0.35),
        0 0 42px rgba(255, 42, 133, 0.25),
        inset 0 0 24px rgba(255, 42, 133, 0.15);
    overflow: hidden;
}}

.portal-hero::before {{
    content: "CALIBRATION // 00 -- 25 -- 50 -- 75 -- 100 // SYS.OK";
    position: absolute;
    top: 6px;
    right: 14px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.64rem;
    letter-spacing: 0.1em;
    color: rgba(0, 240, 255, 0.62);
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
    background: rgba(255, 42, 133, 0.22);
    border: 1px solid var(--neon-pink);
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    margin-bottom: 0.55rem;
    box-shadow: 0 0 12px rgba(255, 42, 133, 0.45);
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
    background: linear-gradient(90deg, #ff2a85 0%, #ff7a00 50%, #ffe600 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 0 10px rgba(0, 240, 255, 0.75));
}}

.portal-hero h1.vice-calligraphy {{
    font-family: 'Yellowtail', cursive !important;
    font-size: clamp(2.15rem, 4.4vw, 3.45rem) !important;
    font-weight: 400 !important;
    letter-spacing: 0.02em;
    padding-right: 0.4rem;
    background: linear-gradient(180deg, #ff4da6 0%, #ff7a00 58%, #ffe600 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(2px 3px 0px #00f0ff) drop-shadow(0 0 14px rgba(0, 240, 255, 0.85));
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
    background: rgba(7, 3, 18, 0.78);
    border: 1px solid var(--neon-green);
    color: var(--neon-green);
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.8rem;
    box-shadow: 0 0 12px rgba(57, 255, 20, 0.35);
    animation: badge-float 2.8s ease-in-out infinite;
}}

/* Steel Panel + 4 Corner Rivets + Hazard Stripes + Graffiti VI */
.steel-rivet-card {{
    position: relative;
    background: var(--bg-steel);
    border: 2px solid #64748b;
    border-radius: 14px;
    padding: 1.35rem 1.45rem;
    margin-bottom: 1rem;
    overflow: hidden;
    box-shadow:
        0 0 24px rgba(0, 240, 255, 0.32),
        0 14px 32px rgba(0, 0, 0, 0.75),
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
        #ffe600 0px,
        #ffe600 10px,
        #0f172a 10px,
        #0f172a 20px
    );
    opacity: 0.92;
}}

.steel-rivet-card::before {{ top: 0; border-bottom: 1px solid #000; }}
.steel-rivet-card::after {{ bottom: 0; border-top: 1px solid #000; }}

.rivet-dot {{
    position: absolute;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: radial-gradient(circle at 35% 35%, #f8fafc, #64748b 60%, #1e293b 100%);
    box-shadow: 0 0 4px rgba(0, 240, 255, 0.5);
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
    background: linear-gradient(135deg, #00f0ff 0%, #c084fc 45%, #ff2a85 75%, #ffe600 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(2px 2px 0px #090314) drop-shadow(0 0 12px rgba(255, 42, 133, 0.9));
    user-select: none;
}}

/* Calibration HUD Box around Console Forms */
.console-hud-ruler {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.68rem;
    color: var(--neon-cyan);
    border-top: 1px dashed rgba(0, 240, 255, 0.45);
    border-bottom: 1px dashed rgba(255, 42, 133, 0.45);
    padding: 0.25rem 0.5rem;
    margin: 0.35rem 0 0.65rem 0;
    background: rgba(7, 3, 18, 0.65);
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
    background: var(--bg-surface);
    border: 1.5px solid var(--border-neon);
    border-radius: var(--radius-md);
    padding: 0.95rem 1.1rem;
    backdrop-filter: blur(10px);
    box-shadow: 0 0 16px rgba(0, 240, 255, 0.14), inset 0 0 12px rgba(255, 42, 133, 0.08);
    transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
}}

.kpi-card:hover {{
    transform: translateY(-2px);
    border-color: var(--neon-pink);
    box-shadow: 0 0 22px rgba(255, 42, 133, 0.35), 0 0 12px rgba(0, 240, 255, 0.28);
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
    text-shadow: 0 0 10px rgba(0, 240, 255, 0.32);
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

.tone-up {{
    color: #39ff14;
    background: rgba(57, 255, 20, 0.12);
    border: 1px solid rgba(57, 255, 20, 0.45);
}}

.tone-down {{
    color: #ff4d8d;
    background: rgba(255, 42, 109, 0.16);
    border: 1px solid rgba(255, 42, 109, 0.5);
}}

.tone-neutral {{
    color: #7dd3fc;
    background: rgba(0, 240, 255, 0.12);
    border: 1px solid rgba(0, 240, 255, 0.35);
}}

.tone-warn {{
    color: #ffe600;
    background: rgba(255, 230, 0, 0.13);
    border: 1px solid rgba(255, 230, 0, 0.45);
}}

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

.badge-buy {{
    background: rgba(57, 255, 20, 0.14);
    color: #39ff14;
    border: 1.5px solid #39ff14;
    box-shadow: 0 0 14px rgba(57, 255, 20, 0.4);
}}

.badge-sell {{
    background: rgba(255, 42, 109, 0.18);
    color: #ff4d8d;
    border: 1.5px solid #ff2a6d;
    box-shadow: 0 0 14px rgba(255, 42, 109, 0.45);
}}

.badge-hold {{
    background: rgba(255, 230, 0, 0.14);
    color: #ffe600;
    border: 1.5px solid #ffe600;
    box-shadow: 0 0 14px rgba(255, 230, 0, 0.38);
}}

/* Surface & Sidebar Profile Cards */
.surface-card {{
    background: var(--bg-surface);
    border: 1.5px solid var(--border-neon);
    border-radius: var(--radius-md);
    padding: 1.05rem 1.2rem;
    margin-bottom: 1rem;
    box-shadow: 0 0 16px rgba(0, 240, 255, 0.14);
}}

.sidebar-profile-card {{
    background: linear-gradient(145deg, rgba(22, 8, 48, 0.94), rgba(10, 5, 28, 0.96));
    border: 1.5px solid var(--neon-cyan);
    border-radius: var(--radius-md);
    padding: 0.9rem 1rem;
    margin-bottom: 0.85rem;
    box-shadow: 0 0 16px rgba(0, 240, 255, 0.25), inset 0 0 12px rgba(255, 42, 133, 0.15);
}}

.sidebar-profile-name {{
    font-family: 'Orbitron', sans-serif;
    font-size: 0.95rem;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 0.25rem;
    text-shadow: 0 0 8px rgba(0, 240, 255, 0.5);
}}

.sidebar-cash-pill {{
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.88rem;
    color: var(--neon-green);
    font-weight: 700;
    font-variant-numeric: tabular-nums;
}}

.news-item-card {{
    background: rgba(14, 6, 36, 0.86);
    border: 1px solid rgba(255, 42, 133, 0.35);
    border-radius: var(--radius-sm);
    padding: 0.72rem 0.9rem;
    margin-bottom: 0.55rem;
    transition: all 0.18s ease;
}}

.news-item-card:hover {{
    border-color: var(--neon-cyan);
    box-shadow: 0 0 14px rgba(0, 240, 255, 0.25);
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

/* Hazard / VIP Access Primary Buttons & Arcade Controls */
.stButton > button[kind="primary"],
button[data-testid="stBaseButton-primary"],
button[data-testid="baseButton-primary"] {{
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 800 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase;
    color: #070312 !important;
    background: linear-gradient(90deg, #00f0ff 0%, #39ff14 48%, #ffe600 100%) !important;
    border: 2px solid #ffe600 !important;
    border-radius: 10px !important;
    min-height: 46px !important;
    animation: vice-pulse 2.4s infinite;
    transition: transform 0.15s ease, filter 0.15s ease !important;
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
    border: 1.5px solid rgba(0, 240, 255, 0.45);
    background: rgba(16, 7, 38, 0.85);
    color: #f8fafc;
    transition: all 0.15s ease;
}}

.stButton > button:hover, .stDownloadButton > button:hover {{
    transform: translateY(-1px);
    border-color: var(--neon-pink);
    box-shadow: 0 0 14px rgba(255, 42, 133, 0.45);
}}

/* Arcade Inputs, Forms & Selectors */
div[data-testid="stForm"] {{
    background: rgba(11, 5, 28, 0.85);
    border: 1.5px solid var(--neon-pink);
    border-radius: 12px;
    padding: 1rem 1.1rem;
    box-shadow: 0 0 20px rgba(255, 42, 133, 0.22), inset 0 0 14px rgba(0, 240, 255, 0.12);
}}

div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div {{
    background-color: rgba(9, 4, 24, 0.92) !important;
    border: 1px solid rgba(0, 240, 255, 0.45) !important;
    border-radius: 8px !important;
    font-family: 'Share Tech Mono', monospace !important;
}}

div[data-baseweb="input"] > div:focus-within,
div[data-baseweb="select"] > div:focus-within {{
    border-color: var(--neon-pink) !important;
    box-shadow: 0 0 12px rgba(255, 42, 133, 0.55) !important;
}}

/* Tabs */
button[data-baseweb="tab"] {{
    font-family: 'Orbitron', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em;
    border-radius: 8px 8px 0 0;
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
    box-shadow: 0 0 18px rgba(255, 42, 133, 0.18);
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

@media (max-width: 640px) {{
    .main .block-container,
    [data-testid="stMainBlockContainer"] {{
        padding-top: 0.75rem;
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


def inject_global_styles() -> None:
    """Inject GTA VI / Vice City synthwave CSS into the Streamlit page."""
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def render_wanted_stars_html(active_stars: int = 5, total_stars: int = 6) -> str:
    """Return HTML markup for a retro 6-star GTA Wanted Level bar."""
    clamped = max(0, min(active_stars, total_stars))
    stars_on = "".join('<span class="wanted-star-on">★</span>' for _ in range(clamped))
    stars_off = "".join('<span class="wanted-star-off">☆</span>' for _ in range(total_stars - clamped))
    return (
        f'<div class="wanted-rack">'
        f'<span class="wanted-label">WANTED</span>'
        f"{stars_on}{stars_off}"
        f"</div>"
    )


def render_vice_hud_banner(wanted_stars: int = 5, telemetry: str = "BAWSAQ // LCN LIVE LINK") -> None:
    """Render top GTA-style neon wing emblem banner and 6-star wanted level rack."""
    stars_html = render_wanted_stars_html(active_stars=wanted_stars, total_stars=6)
    safe_telemetry = html.escape(telemetry)
    st.markdown(
        f'<div class="vice-hud-top">'
        f'<div class="vice-telemetry-tag">▸▸ {safe_telemetry}</div>'
        f'<div class="vice-wing-emblem">'
        f'<div class="vice-wing-row">'
        f'<span class="wing-chevron"></span>'
        f'<span class="wing-pill">🦅 ★ DRONACHARYA GROUP OF INSTITUTIONS • AKTU ★ 🦅</span>'
        f'<span class="wing-chevron right"></span>'
        f"</div>"
        f'<div class="vice-sub-ribbon">★ ★ ★ Vice City Special Events • BAWSAQ Terminal ★ ★ ★</div>'
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
    wanted_stars: int = 5,
) -> None:
    """Render the GTA VI neon wing HUD bar and Vice City synthwave hero banner."""
    render_vice_hud_banner(wanted_stars=wanted_stars)
    safe_badge = html.escape(badge)
    safe_title = html.escape(title)
    safe_subtitle = html.escape(subtitle)
    title_cls = ' class="vice-calligraphy"' if use_calligraphy else ""
    st.markdown(
        f'<div class="portal-hero">'
        f'<div class="portal-hero-badge">🌴 {safe_badge}</div>'
        f'<div class="portal-hero-row">'
        f"<div style='flex:1; min-width:260px;'>"
        f"<h1{title_cls}>{safe_title}</h1>"
        f"<p>▸▸ {safe_subtitle}</p>"
        f"</div>"
        f'<div class="pixel-arrow-pill">🌅 📈🌴 BAWSAQ INDEX ▲▲</div>'
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )


def render_signal_badge(signal: str, confidence: int | None = None) -> str:
    """Return HTML markup for a neon BUY / SELL / HOLD pill badge."""
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
    """Render a responsive neon HUD CSS-grid row of KPI cards."""
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
    """Apply retro Vice City synthwave styling and responsive margins to Plotly figures."""
    layout_kwargs: dict = {
        "template": "plotly_dark",
        "paper_bgcolor": "rgba(10, 4, 28, 0.88)",
        "plot_bgcolor": "rgba(18, 7, 42, 0.85)",
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
            "bgcolor": "rgba(10, 4, 28, 0.55)",
            "bordercolor": "rgba(0, 240, 255, 0.3)",
            "borderwidth": 1,
        },
    }
    if title:
        layout_kwargs["title"] = {
            "text": title,
            "font": {"family": "Orbitron, sans-serif", "size": 15, "color": "#00f0ff"},
        }

    fig.update_layout(**layout_kwargs)
    fig.update_xaxes(
        gridcolor="rgba(255, 42, 133, 0.16)",
        linecolor="rgba(0, 240, 255, 0.35)",
        zeroline=False,
    )
    fig.update_yaxes(
        gridcolor="rgba(0, 240, 255, 0.12)",
        linecolor="rgba(255, 42, 133, 0.35)",
        zeroline=False,
    )
    return fig
