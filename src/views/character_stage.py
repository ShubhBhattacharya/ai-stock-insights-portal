"""Full-Body Animated GTA VI / Vice City Cyber-Broker Character Stage."""

from __future__ import annotations

import html
import json
import streamlit as st


def render_character_stage(
    mood: str = "neutral",
    is_speaking: bool = False,
    turn_id: int = 0,
    operator_name: str = "SHUBH",
    edition: str = "GTA VI",
) -> None:
    """
    Render an interactive full-body SVG Cyber-Broker (GTA VI) or Bunker Tactician (Doomsday)
    character inside a self-contained HTML component supporting idle, speaking (3.8s auto-revert),
    and bullish/bearish state-driven expressions & backlight shifts.
    """
    doomsday = edition.strip().upper() == "DOOMSDAY"
    safe_mood = mood if mood in {"bullish", "bearish", "neutral"} else "neutral"
    safe_name = html.escape(operator_name.upper()[:14])

    if doomsday:
        if safe_mood == "bullish":
            aura_primary, aura_secondary, border_color = "#39ff14", "#ffb703", "#39ff14"
            mood_label, mood_color = "🛡️ SECTOR SECURED", "#39ff14"
        elif safe_mood == "bearish":
            aura_primary, aura_secondary, border_color = "#ff2a00", "#ff4500", "#ff2a00"
            mood_label, mood_color = "☢️ FALLOUT ALERT", "#ff4500"
        else:
            aura_primary, aura_secondary, border_color = "#39ff14", "#ff4500", "#39ff14"
            mood_label, mood_color = "☢️ DEFCON-1 STANDBY", "#39ff14"
        stage_bg = "radial-gradient(circle at 50% 42%, rgba(92, 26, 8, 0.94) 0%, #0d0504 85%)"
        tag_color = "#39ff14"
        tag_border = "rgba(57, 255, 20, 0.72)"
        hud_tag_text = f"☢️ BUNKER AI • {safe_name}"
        initial_status = "📡 TRANSMITTING BUNKER INTEL..." if is_speaking else mood_label
    else:
        if safe_mood == "bullish":
            aura_primary, aura_secondary, border_color = "#00f5d4", "#39ff14", "#00f5d4"
            mood_label, mood_color = "📈 BULLISH STANCE", "#39ff14"
        elif safe_mood == "bearish":
            aura_primary, aura_secondary, border_color = "#ff2a6d", "#ff2a85", "#ff2a85"
            mood_label, mood_color = "🚨 RISK ALERT", "#ff4d8d"
        else:
            aura_primary, aura_secondary, border_color = "#00f5d4", "#ff2a85", "#ff2a85"
            mood_label, mood_color = "🕶️ STANDBY IDLE", "#00f5d4"
        stage_bg = "radial-gradient(circle at 50% 42%, rgba(44, 11, 78, 0.92) 0%, #090318 82%)"
        tag_color = "#00f5d4"
        tag_border = "rgba(0, 245, 212, 0.65)"
        hud_tag_text = f"🤖 AI TUTOR • {safe_name}"
        initial_status = "🔊 TRANSMITTING INTEL..." if is_speaking else mood_label

    speaking_cls = "is-speaking" if is_speaking else ""

    brow_alert_svg = (
        '<line x1="160" y1="88" x2="175" y2="92" stroke="#1e1b4b" stroke-width="2.5" stroke-linecap="round" />'
        '<line x1="200" y1="88" x2="185" y2="92" stroke="#1e1b4b" stroke-width="2.5" stroke-linecap="round" />'
        if safe_mood == "bearish"
        else ""
    )
    if safe_mood == "bullish":
        static_mouth_svg = '<path class="mouth-static" d="M168,124 Q180,134 193,123" stroke="#3b0764" stroke-width="2.6" fill="none" stroke-linecap="round" />'
    elif safe_mood == "bearish":
        static_mouth_svg = '<line class="mouth-static" x1="170" y1="126" x2="190" y2="126" stroke="#450a0a" stroke-width="2.6" stroke-linecap="round" />'
    else:
        static_mouth_svg = '<path class="mouth-static" d="M170,125 Q180,131 191,124" stroke="#3b0764" stroke-width="2.4" fill="none" stroke-linecap="round" />'

    if doomsday:
        bullish_thumb_svg = (
            '<path d="M8,4 L12,-10 Q16,-12 18,-6 L15,6 Z" fill="#c88d65" stroke="#39ff14" stroke-width="1.4" />'
            if safe_mood == "bullish"
            else ""
        )
        bearish_pointer_svg = (
            '<line x1="16" y1="8" x2="26" y2="2" stroke="#ff2a00" stroke-width="2.2" stroke-linecap="round" />'
            if safe_mood == "bearish"
            else ""
        )
        character_svg = f"""
      <svg viewBox="0 0 360 545" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="bunkerSkyGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#140602" />
            <stop offset="46%" stop-color="#5e1d08" />
            <stop offset="76%" stop-color="#a83408" />
            <stop offset="100%" stop-color="#0d0504" />
          </linearGradient>
          <radialGradient id="explosionGlow" cx="55%" cy="48%" r="46%">
            <stop offset="0%" stop-color="#ffb703" stop-opacity="0.72" />
            <stop offset="48%" stop-color="#ff4500" stop-opacity="0.34" />
            <stop offset="100%" stop-color="#140602" stop-opacity="0" />
          </radialGradient>
          <linearGradient id="armorGrad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#222629" />
            <stop offset="50%" stop-color="#181b1e" />
            <stop offset="100%" stop-color="#111315" />
          </linearGradient>
          <linearGradient id="visorGreenGrad" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stop-color="#39ff14" />
            <stop offset="50%" stop-color="#10b981" />
            <stop offset="100%" stop-color="#84cc16" />
          </linearGradient>
          <radialGradient id="bunkerAuraGrad" cx="50%" cy="48%" r="50%">
            <stop offset="0%" stop-color="{aura_primary}" stop-opacity="0.45" />
            <stop offset="60%" stop-color="{aura_secondary}" stop-opacity="0.18" />
            <stop offset="100%" stop-color="#0d0504" stop-opacity="0" />
          </radialGradient>
          <filter id="greenNeonGlow" x="-25%" y="-25%" width="150%" height="150%">
            <feGaussianBlur stdDeviation="3.0" result="blur" />
            <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
          </filter>
        </defs>

        <!-- Fiery Fallout Sky -->
        <rect x="0" y="0" width="360" height="545" fill="url(#bunkerSkyGrad)" />
        <ellipse cx="200" cy="245" rx="145" ry="118" fill="url(#explosionGlow)" />

        <!-- Crumbled Ruined Skyscrapers Silhouette -->
        <g fill="#120705" opacity="0.95">
          <polygon points="8,415 8,196 22,190 36,214 40,415" />
          <polygon points="44,415 44,162 60,174 74,158 78,415" />
          <polygon points="82,415 82,248 96,236 106,264 106,415" />
          <polygon points="246,415 246,232 262,216 274,242 274,415" />
          <polygon points="278,415 278,166 298,176 312,156 318,415" />
          <polygon points="322,415 322,208 340,224 352,202 354,415" />
        </g>

        <!-- Glowing Fire Ember Windows -->
        <g fill="#ffb703" opacity="0.55">
          <rect x="52" y="186" width="4" height="10" />
          <rect x="62" y="196" width="4" height="12" fill="#ff4500" />
          <rect x="288" y="188" width="5" height="12" fill="#ff4500" />
          <rect x="300" y="182" width="5" height="14" />
        </g>

        <!-- Top-Left Circular Biohazard Radar Seal -->
        <g transform="translate(46, 86)">
          <circle cx="0" cy="0" r="24" fill="rgba(10,16,10,0.88)" stroke="#39ff14" stroke-width="2" filter="url(#greenNeonGlow)" />
          <circle cx="0" cy="0" r="19" fill="none" stroke="#ff4500" stroke-width="1" stroke-dasharray="4 3" />
          <path d="M0,-12 A11,11 0 0,1 10,6 L4,2 A5,5 0 0,0 0,-5 Z" fill="#39ff14" />
          <path d="M10,6 A11,11 0 0,1 -10,6 L-4,2 A5,5 0 0,0 4,2 Z" fill="#39ff14" />
          <path d="M-10,6 A11,11 0 0,1 0,-12 L0,-5 A5,5 0 0,0 -4,2 Z" fill="#39ff14" />
          <circle cx="0" cy="0" r="3.2" fill="#0d0504" stroke="#39ff14" stroke-width="1.2" />
        </g>

        <!-- Bunker Mood Aura -->
        <ellipse class="aura-ring" cx="180" cy="295" rx="135" ry="190" fill="url(#bunkerAuraGrad)" />

        <!-- Toxic Green Neon Perspective Grid Floor -->
        <g stroke="#39ff14" stroke-width="1.35" opacity="0.9" filter="url(#greenNeonGlow)">
          <polygon points="88,468 272,468 338,532 22,532" fill="rgba(8,16,8,0.85)" stroke-width="2" />
          <line x1="118" y1="468" x2="72" y2="532" />
          <line x1="149" y1="468" x2="126" y2="532" />
          <line x1="180" y1="468" x2="180" y2="532" />
          <line x1="211" y1="468" x2="234" y2="532" />
          <line x1="242" y1="468" x2="288" y2="532" />
          <line x1="72" y1="482" x2="288" y2="482" />
          <line x1="56" y1="497" x2="304" y2="497" />
          <line x1="39" y1="514" x2="321" y2="514" />
        </g>

        <!-- Ground Shadow -->
        <ellipse cx="180" cy="494" rx="58" ry="11" fill="#000000" opacity="0.65" />

        <!-- ================= FULL-BODY DOOMSDAY BUNKER TACTICIAN ================= -->

        <!-- TACTICAL CARGO LEGS & LACED COMBAT BOOTS -->
        <g class="legs-anim">
          <path d="M146,298 L177,302 L166,462 L137,460 Z" fill="#2d3328" stroke="#39ff14" stroke-width="1.4" />
          <path d="M180,302 L212,298 L222,460 L192,462 Z" fill="#282e24" stroke="#39ff14" stroke-width="1.4" />
          <!-- Thigh Utility Straps & Knee Armor Pads -->
          <rect x="142" y="336" width="30" height="7" rx="2" fill="#181b1e" stroke="#ffb703" stroke-width="1" />
          <rect x="187" y="336" width="30" height="7" rx="2" fill="#181b1e" stroke="#ffb703" stroke-width="1" />
          <rect x="140" y="376" width="28" height="18" rx="4" fill="#17191c" stroke="#39ff14" stroke-width="1.3" />
          <rect x="190" y="376" width="28" height="18" rx="4" fill="#17191c" stroke="#39ff14" stroke-width="1.3" />

          <!-- Left Heavy Combat Boot -->
          <g>
            <path d="M134,452 L166,452 L168,488 L118,492 Q115,478 128,468 Z" fill="#261c17" stroke="#ffb703" stroke-width="1.6" />
            <path d="M118,488 L168,486 L168,494 L118,495 Z" fill="#39ff14" filter="url(#greenNeonGlow)" />
            <line x1="138" y1="460" x2="152" y2="460" stroke="#9ca3af" stroke-width="1.8" />
            <line x1="136" y1="468" x2="151" y2="468" stroke="#9ca3af" stroke-width="1.8" />
          </g>

          <!-- Right Heavy Combat Boot -->
          <g>
            <path d="M192,452 L224,452 L242,468 Q252,478 248,492 L192,488 Z" fill="#261c17" stroke="#ffb703" stroke-width="1.6" />
            <path d="M192,486 L248,488 L248,495 L192,494 Z" fill="#39ff14" filter="url(#greenNeonGlow)" />
            <line x1="208" y1="460" x2="222" y2="460" stroke="#9ca3af" stroke-width="1.8" />
            <line x1="210" y1="468" x2="225" y2="468" stroke="#9ca3af" stroke-width="1.8" />
          </g>
        </g>

        <!-- LEFT ARMOR ARM -->
        <g>
          <path d="M138,162 Q114,198 117,248 L129,285 L144,282 L138,244 L148,195 Z"
                fill="url(#armorGrad)" stroke="#39ff14" stroke-width="1.8" />
          <path d="M126,184 L123,238" stroke="#ffb703" stroke-width="1.8" fill="none" />
          <!-- Tactical Glove -->
          <path d="M127,280 Q122,298 131,304 Q141,304 143,292 L141,278 Z"
                fill="#1f2937" stroke="#39ff14" stroke-width="1.3" />
        </g>

        <!-- TORSO & ARMORED TACTICAL JACKET WITH GREEN/AMBER TRIMS -->
        <g class="torso-anim">
          <rect x="147" y="289" width="64" height="13" rx="3" fill="#141618" stroke="#ffb703" stroke-width="1.3" />
          <rect x="172" y="290" width="16" height="11" rx="2" fill="#39ff14" />

          <!-- Inner Armor Vest -->
          <path d="M155,154 L205,154 L207,290 L151,290 Z" fill="#161a1d" />
          <!-- Chest Tactical Circuit Lines -->
          <path d="M164,174 L176,188 L176,258" stroke="#39ff14" stroke-width="1.8" fill="none" filter="url(#greenNeonGlow)" />
          <path d="M196,174 L184,188 L184,258" stroke="#ff4500" stroke-width="1.8" fill="none" />

          <!-- Left & Right Armored Jacket Panels -->
          <path d="M136,158 L164,154 L164,293 L135,288 L137,204 Z"
                fill="url(#armorGrad)" stroke="#39ff14" stroke-width="2" />
          <path d="M194,154 L222,158 L222,204 L223,288 L194,293 Z"
                fill="url(#armorGrad)" stroke="#39ff14" stroke-width="2" />

          <!-- Shoulder Armor Plates -->
          <path d="M132,162 Q146,148 162,158 L156,178 L132,174 Z" fill="#272b30" stroke="#ffb703" stroke-width="1.5" />
          <path d="M226,162 Q212,148 196,158 L202,178 L226,174 Z" fill="#272b30" stroke="#ffb703" stroke-width="1.5" />
        </g>

        <!-- RIGHT ARM (Gesturing toward Bunker AI Chat Terminal) -->
        <g class="arm-right-anim">
          <path d="M218,162 Q244,190 258,214 L286,184 L296,194 L264,234 Q252,240 242,226 L214,190 Z"
                fill="url(#armorGrad)" stroke="#39ff14" stroke-width="2" />
          <rect x="278" y="182" width="14" height="6" rx="2" transform="rotate(42 285 185)" fill="#ff4500" />
          <g transform="translate(290, 168)">
            <path d="M0,16 Q8,2 14,0 Q18,0 16,12 L24,12 Q28,14 26,20 L25,26 Q22,30 10,28 L0,24 Z"
                  fill="#1f2937" stroke="#39ff14" stroke-width="1.3" />
            {bullish_thumb_svg}
            {bearish_pointer_svg}
          </g>
        </g>

        <!-- HEAD, TACTICAL GREEN VISOR & STUBBLE -->
        <g class="head-anim">
          <rect x="169" y="130" width="22" height="24" rx="6" fill="#be7c54" />
          <ellipse cx="150" cy="108" rx="5" ry="9" fill="#be7c54" />
          <ellipse cx="210" cy="108" rx="5" ry="9" fill="#be7c54" />
          <path d="M152,82 Q152,64 180,64 Q208,64 208,82 L207,114 Q206,136 180,140 Q154,136 153,114 Z"
                fill="#d39670" stroke="#39ff14" stroke-width="1.2" />
          <!-- Stubble Beard Shadow -->
          <path d="M154,112 Q156,134 180,139 Q204,134 206,112 Q200,126 180,129 Q160,126 154,112 Z"
                fill="rgba(24,20,18,0.38)" />
          <!-- Hair -->
          <path d="M148,96 Q146,60 174,50 Q196,42 214,62 Q216,78 210,96 Q204,76 184,74 Q160,72 152,96 Z"
                fill="#141110" stroke="#ffb703" stroke-width="1.4" />
          {brow_alert_svg}
          <!-- Glowing Green Tactical Visor Shades -->
          <g class="shades-lens">
            <rect x="154" y="90" width="52" height="16" rx="4" fill="rgba(16, 24, 16, 0.9)" stroke="#39ff14" stroke-width="1.8" />
            <rect x="157" y="92" width="21" height="12" rx="3" fill="url(#visorGreenGrad)" opacity="0.88" />
            <rect x="182" y="92" width="21" height="12" rx="3" fill="url(#visorGreenGrad)" opacity="0.88" />
            <line x1="162" y1="95" x2="170" y2="102" stroke="#ffffff" stroke-width="1.8" opacity="0.82" />
            <line x1="187" y1="95" x2="195" y2="102" stroke="#ffffff" stroke-width="1.8" opacity="0.82" />
          </g>
          <path d="M180,105 L178,116 L183,117" stroke="#9e5e3b" stroke-width="1.6" fill="none" stroke-linecap="round" />
          <g>
            {static_mouth_svg}
            <ellipse class="mouth-talking" cx="180" cy="126" rx="7.5" ry="4" fill="#140805" stroke="#39ff14" stroke-width="1.3" />
          </g>
        </g>
      </svg>"""
    else:
        bullish_thumb_svg = (
            '<path d="M8,4 L12,-10 Q16,-12 18,-6 L15,6 Z" fill="#d6956c" stroke="#39ff14" stroke-width="1.4" />'
            if safe_mood == "bullish"
            else ""
        )
        bearish_pointer_svg = (
            '<line x1="16" y1="8" x2="26" y2="2" stroke="#ff2a85" stroke-width="2.2" stroke-linecap="round" />'
            if safe_mood == "bearish"
            else ""
        )
        character_svg = f"""
      <svg viewBox="0 0 360 545" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="skyGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#0b0320" />
            <stop offset="48%" stop-color="#28094e" />
            <stop offset="78%" stop-color="#6b1463" />
            <stop offset="100%" stop-color="#0a041a" />
          </linearGradient>

          <linearGradient id="sunGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#fee440" />
            <stop offset="52%" stop-color="#ff7a00" />
            <stop offset="100%" stop-color="#ff2a85" />
          </linearGradient>

          <linearGradient id="jacketGrad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#1e1147" />
            <stop offset="50%" stop-color="#31105c" />
            <stop offset="100%" stop-color="#140c36" />
          </linearGradient>

          <linearGradient id="shadesGrad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stop-color="#00f5d4" />
            <stop offset="50%" stop-color="#8b5cf6" />
            <stop offset="100%" stop-color="#ff2a85" />
          </linearGradient>

          <radialGradient id="auraGrad" cx="50%" cy="48%" r="50%">
            <stop offset="0%" stop-color="{aura_primary}" stop-opacity="0.52" />
            <stop offset="55%" stop-color="{aura_secondary}" stop-opacity="0.22" />
            <stop offset="100%" stop-color="#070312" stop-opacity="0" />
          </radialGradient>

          <filter id="neonGlow" x="-25%" y="-25%" width="150%" height="150%">
            <feGaussianBlur stdDeviation="3.2" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        <!-- Synthwave Sky -->
        <rect x="0" y="0" width="360" height="545" fill="url(#skyGrad)" />

        <!-- Retro Vice Sun with Horizon Cuts -->
        <circle cx="195" cy="245" r="88" fill="url(#sunGrad)" opacity="0.88" />
        <rect x="102" y="255" width="186" height="5" fill="#28094e" opacity="0.82" />
        <rect x="102" y="270" width="186" height="7" fill="#28094e" opacity="0.85" />
        <rect x="102" y="288" width="186" height="9" fill="#28094e" opacity="0.9" />
        <rect x="102" y="308" width="186" height="12" fill="#28094e" opacity="0.95" />

        <!-- Distant Skyline Silhouettes -->
        <g fill="#0c0524" opacity="0.92">
          <rect x="12" y="210" width="26" height="190" />
          <rect x="42" y="175" width="30" height="225" />
          <rect x="76" y="235" width="24" height="165" />
          <rect x="256" y="220" width="26" height="180" />
          <rect x="286" y="168" width="32" height="232" />
          <rect x="322" y="205" width="28" height="195" />
        </g>

        <!-- Neon City Window Highlights -->
        <g fill="#00f5d4" opacity="0.45">
          <rect x="48" y="188" width="4" height="14" />
          <rect x="58" y="188" width="4" height="14" />
          <rect x="294" y="182" width="5" height="18" fill="#ff2a85" />
          <rect x="305" y="182" width="5" height="18" fill="#ff2a85" />
        </g>

        <!-- Palm Silhouettes -->
        <g fill="#070316" opacity="0.92">
          <path d="M36,410 Q46,320 62,250 Q52,325 46,410 Z" />
          <path d="M62,252 Q28,236 8,256 Q34,248 62,258 Z" />
          <path d="M62,250 Q38,216 14,220 Q42,226 60,252 Z" />
          <path d="M63,248 Q74,212 98,212 Q78,224 64,252 Z" />
          <path d="M64,254 Q94,240 112,262 Q88,250 64,258 Z" />

          <path d="M322,415 Q310,335 294,268 Q304,335 312,415 Z" />
          <path d="M294,270 Q264,254 244,274 Q268,266 294,276 Z" />
          <path d="M295,268 Q278,232 256,236 Q280,242 294,270 Z" />
          <path d="M296,266 Q312,230 338,234 Q316,244 297,270 Z" />
          <path d="M296,272 Q328,260 348,282 Q324,272 296,276 Z" />
        </g>

        <!-- Glowing Mood Aura Behind Character -->
        <ellipse class="aura-ring" cx="180" cy="295" rx="135" ry="190" fill="url(#auraGrad)" />

        <!-- Neon Perspective Grid Floor -->
        <g stroke="{aura_primary}" stroke-width="1.35" opacity="0.88" filter="url(#neonGlow)">
          <polygon points="88,468 272,468 338,532 22,532" fill="rgba(7,3,18,0.82)" stroke-width="2" />
          <line x1="118" y1="468" x2="72" y2="532" />
          <line x1="149" y1="468" x2="126" y2="532" />
          <line x1="180" y1="468" x2="180" y2="532" />
          <line x1="211" y1="468" x2="234" y2="532" />
          <line x1="242" y1="468" x2="288" y2="532" />
          <line x1="72" y1="482" x2="288" y2="482" />
          <line x1="56" y1="497" x2="304" y2="497" />
          <line x1="39" y1="514" x2="321" y2="514" />
        </g>

        <!-- Ground Shadow -->
        <ellipse cx="180" cy="494" rx="56" ry="11" fill="#000000" opacity="0.6" />

        <!-- ================= FULL-BODY VICE CITY CHARACTER ================= -->

        <!-- LEGS & HIGH-TOP SNEAKERS -->
        <g class="legs-anim">
          <path d="M148,298 L176,302 L166,464 L138,462 Z" fill="#131629" stroke="#00f5d4" stroke-width="1.4" />
          <path d="M180,302 L210,298 L220,462 L192,464 Z" fill="#16182e" stroke="#ff2a85" stroke-width="1.4" />
          <path d="M145,382 Q154,378 164,382" stroke="#38bdf8" stroke-width="1.2" fill="none" opacity="0.65" />
          <path d="M193,382 Q203,378 213,382" stroke="#ff2a85" stroke-width="1.2" fill="none" opacity="0.65" />

          <g>
            <path d="M135,456 L166,456 L168,488 L118,492 Q115,480 128,472 Z" fill="#1e1b4b" stroke="#00f5d4" stroke-width="1.8" />
            <path d="M118,488 L168,486 L168,494 L118,495 Z" fill="#00f5d4" filter="url(#neonGlow)" />
            <line x1="138" y1="464" x2="152" y2="464" stroke="#ffffff" stroke-width="2" />
            <line x1="135" y1="471" x2="150" y2="471" stroke="#ff2a85" stroke-width="2" />
          </g>

          <g>
            <path d="M192,456 L223,456 L240,472 Q250,480 246,492 L192,488 Z" fill="#1e1b4b" stroke="#ff2a85" stroke-width="1.8" />
            <path d="M192,486 L246,488 L246,495 L192,494 Z" fill="#ff2a85" filter="url(#neonGlow)" />
            <line x1="208" y1="464" x2="222" y2="464" stroke="#ffffff" stroke-width="2" />
            <line x1="210" y1="471" x2="225" y2="471" stroke="#00f5d4" stroke-width="2" />
          </g>
        </g>

        <!-- LEFT ARM -->
        <g>
          <path d="M138,162 Q115,198 118,248 L130,285 L144,282 L138,244 L148,195 Z"
                fill="url(#jacketGrad)" stroke="#00f5d4" stroke-width="1.8" />
          <rect x="128" y="254" width="14" height="6" rx="2" fill="#ff2a85" />
          <path d="M128,282 Q123,298 131,304 Q141,304 143,292 L141,280 Z"
                fill="#d6956c" stroke="#1e1b4b" stroke-width="1.2" />
        </g>

        <!-- TORSO & NEON PALM-PRINT VICE JACKET -->
        <g class="torso-anim">
          <rect x="148" y="290" width="62" height="12" rx="3" fill="#090318" stroke="#fee440" stroke-width="1.2" />
          <rect x="173" y="291" width="12" height="10" rx="2" fill="#fee440" />
          <path d="M156,154 L204,154 L206,292 L152,292 Z" fill="#0b081a" />
          <path d="M168,158 Q180,178 192,158" stroke="#fee440" stroke-width="1.8" fill="none" />
          <path d="M138,158 L164,154 L164,295 L136,290 L138,205 Z"
                fill="url(#jacketGrad)" stroke="#00f5d4" stroke-width="2" />
          <path d="M194,154 L220,158 L220,205 L222,290 L194,295 Z"
                fill="url(#jacketGrad)" stroke="#ff2a85" stroke-width="2" />
          <polygon points="164,154 152,188 164,225" fill="none" stroke="#ff2a85" stroke-width="2" filter="url(#neonGlow)" />
          <polygon points="194,154 206,188 194,225" fill="none" stroke="#00f5d4" stroke-width="2" filter="url(#neonGlow)" />
          <g stroke="#ff2a85" stroke-width="1.3" fill="none" opacity="0.8">
            <path d="M148,246 Q142,232 138,225" />
            <path d="M148,246 Q152,231 158,226" />
            <path d="M210,248 Q204,234 198,228" stroke="#00f5d4" />
            <path d="M210,248 Q214,233 219,229" stroke="#00f5d4" />
          </g>
        </g>

        <!-- RIGHT ARM -->
        <g class="arm-right-anim">
          <path d="M218,162 Q244,190 258,214 L286,184 L296,194 L264,234 Q252,240 242,226 L214,190 Z"
                fill="url(#jacketGrad)" stroke="#ff2a85" stroke-width="2" />
          <rect x="278" y="182" width="14" height="6" rx="2" transform="rotate(42 285 185)" fill="#00f5d4" />
          <g transform="translate(290, 168)">
            <path d="M0,16 Q8,2 14,0 Q18,0 16,12 L24,12 Q28,14 26,20 L25,26 Q22,30 10,28 L0,24 Z"
                  fill="#d6956c" stroke="#1e1b4b" stroke-width="1.2" />
            {bullish_thumb_svg}
            {bearish_pointer_svg}
          </g>
        </g>

        <!-- HEAD, HAIR, SUNGLASSES & FACIAL EXPRESSIONS -->
        <g class="head-anim">
          <rect x="169" y="130" width="22" height="24" rx="6" fill="#c68259" />
          <ellipse cx="150" cy="108" rx="5" ry="9" fill="#c68259" />
          <ellipse cx="210" cy="108" rx="5" ry="9" fill="#c68259" />
          <path d="M152,82 Q152,64 180,64 Q208,64 208,82 L207,114 Q206,136 180,140 Q154,136 153,114 Z"
                fill="#dba079" stroke="#ff2a85" stroke-width="1.2" />
          <path d="M148,96 Q146,62 174,50 Q196,42 214,62 Q216,78 210,96 Q204,76 184,74 Q160,72 152,96 Z"
                fill="#110b29" stroke="#00f5d4" stroke-width="1.5" />
          {brow_alert_svg}
          <g class="shades-lens">
            <rect x="155" y="92" width="22" height="14" rx="4" fill="url(#shadesGrad)" stroke="#00f5d4" stroke-width="1.8" />
            <rect x="183" y="92" width="22" height="14" rx="4" fill="url(#shadesGrad)" stroke="#ff2a85" stroke-width="1.8" />
            <line x1="177" y1="97" x2="183" y2="97" stroke="#fee440" stroke-width="2.2" />
            <line x1="160" y1="95" x2="168" y2="103" stroke="#ffffff" stroke-width="1.8" opacity="0.8" />
            <line x1="188" y1="95" x2="196" y2="103" stroke="#ffffff" stroke-width="1.8" opacity="0.8" />
          </g>
          <path d="M180,104 L178,116 L183,117" stroke="#b36d47" stroke-width="1.6" fill="none" stroke-linecap="round" />
          <g>
            {static_mouth_svg}
            <ellipse class="mouth-talking" cx="180" cy="126" rx="7.5" ry="4" fill="#3b0764" stroke="#ff2a85" stroke-width="1.3" />
          </g>
        </g>
      </svg>"""

    stage_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<style>
  @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Share+Tech+Mono&display=swap');

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  html, body {{
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: transparent;
    font-family: 'Orbitron', sans-serif;
  }}

  .stage-frame {{
    position: relative;
    width: 100%;
    height: 100%;
    border-radius: 14px;
    border: 2px solid {border_color};
    background: {stage_bg};
    box-shadow: inset 0 0 28px {aura_primary}44, 0 0 18px {aura_secondary}55;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}

  .stage-hud-top {{
    position: absolute;
    top: 10px;
    left: 10px;
    right: 10px;
    z-index: 4;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 6px;
    pointer-events: none;
  }}

  .hud-tag {{
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.06em;
    color: {tag_color};
    background: rgba(7, 3, 18, 0.88);
    border: 1px solid {tag_border};
    padding: 4px 8px;
    border-radius: 6px;
    box-shadow: 0 0 10px {aura_primary}44;
  }}

  .hud-status {{
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    font-weight: 700;
    color: {mood_color};
    background: rgba(7, 3, 18, 0.88);
    border: 1px solid {mood_color};
    padding: 4px 8px;
    border-radius: 6px;
    box-shadow: 0 0 10px {mood_color}55;
  }}

  .svg-wrap {{
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
  }}

  svg {{
    width: 100%;
    height: 100%;
    max-height: 100%;
    display: block;
  }}

  @keyframes chestBreathe {{
    0%, 100% {{ transform: translateY(0px) scaleY(1); }}
    50% {{ transform: translateY(-2.2px) scaleY(1.012); }}
  }}

  @keyframes legShift {{
    0%, 100% {{ transform: translateX(0px); }}
    50% {{ transform: translateX(1.5px); }}
  }}

  @keyframes headIdle {{
    0%, 100% {{ transform: translateY(0px) rotate(0deg); }}
    50% {{ transform: translateY(-2px) rotate(0.6deg); }}
  }}

  @keyframes headNod {{
    0%, 100% {{ transform: translateY(0px) rotate(0deg); }}
    25% {{ transform: translateY(-3px) rotate(2.2deg); }}
    50% {{ transform: translateY(1px) rotate(-1.5deg); }}
    75% {{ transform: translateY(-2px) rotate(1.8deg); }}
  }}

  @keyframes armIdle {{
    0%, 100% {{ transform: rotate(0deg); }}
    50% {{ transform: rotate(-2.5deg); }}
  }}

  @keyframes armExplain {{
    0%, 100% {{ transform: rotate(0deg) translateY(0px); }}
    30% {{ transform: rotate(-14deg) translateY(-4px); }}
    60% {{ transform: rotate(-4deg) translateY(1px); }}
    85% {{ transform: rotate(-16deg) translateY(-3px); }}
  }}

  @keyframes shadesGlow {{
    0%, 88%, 100% {{ opacity: 0.92; filter: drop-shadow(0 0 3px {aura_primary}); }}
    92% {{ opacity: 0.35; filter: drop-shadow(0 0 8px #fee440); }}
    96% {{ opacity: 1; filter: drop-shadow(0 0 8px {aura_secondary}); }}
  }}

  @keyframes mouthTalk {{
    0%, 100% {{ ry: 1.8px; opacity: 0.95; }}
    25% {{ ry: 5.2px; opacity: 1; }}
    50% {{ ry: 2.2px; opacity: 0.95; }}
    75% {{ ry: 6.0px; opacity: 1; }}
  }}

  @keyframes auraPulse {{
    0%, 100% {{ opacity: 0.55; transform: scale(1); }}
    50% {{ opacity: 0.85; transform: scale(1.04); }}
  }}

  .aura-ring {{
    transform-origin: 180px 290px;
    animation: auraPulse 3.2s ease-in-out infinite;
  }}

  .torso-anim {{
    transform-origin: 180px 260px;
    animation: chestBreathe 3.4s ease-in-out infinite;
  }}

  .legs-anim {{
    transform-origin: 180px 480px;
    animation: legShift 4.5s ease-in-out infinite;
  }}

  .head-anim {{
    transform-origin: 180px 132px;
    animation: headIdle 3.8s ease-in-out infinite;
  }}

  .arm-right-anim {{
    transform-origin: 214px 168px;
    animation: armIdle 3.8s ease-in-out infinite;
  }}

  .shades-lens {{
    animation: shadesGlow 4.2s ease-in-out infinite;
  }}

  .is-speaking .head-anim {{
    animation: headNod 0.72s ease-in-out infinite;
  }}

  .is-speaking .arm-right-anim {{
    animation: armExplain 0.85s ease-in-out infinite;
  }}

  .mouth-static {{ display: block; }}
  .mouth-talking {{ display: none; }}

  .is-speaking .mouth-static {{ display: none; }}
  .is-speaking .mouth-talking {{
    display: block;
    animation: mouthTalk 0.34s ease-in-out infinite;
  }}
</style>
</head>
<body>
  <div id="stageRoot" class="stage-frame {speaking_cls}" data-turn="{turn_id}">
    <div class="stage-hud-top">
      <div class="hud-tag">{hud_tag_text}</div>
      <div id="hudStatusPill" class="hud-status">{initial_status}</div>
    </div>

    <div class="svg-wrap">
      {character_svg}
    </div>
  </div>

  <script>
    (function() {{
      const root = document.getElementById("stageRoot");
      const pill = document.getElementById("hudStatusPill");
      if (root && root.classList.contains("is-speaking")) {{
        setTimeout(function() {{
          root.classList.remove("is-speaking");
          if (pill) {{
            pill.textContent = {json.dumps(mood_label)};
          }}
        }}, 3800);
      }}
    }})();
  </script>
</body>
</html>
"""
    st.iframe(stage_html, width="stretch", height=565)
