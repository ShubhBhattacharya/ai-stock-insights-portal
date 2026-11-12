"""Interactive 3D Holographic Character Portrait Stage for AI Stock Tutor."""

from __future__ import annotations

import base64
import html
import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

_ASSETS_DIR = Path(__file__).resolve().parents[2] / "assets"


@st.cache_data(show_spinner=False)
def _load_character_data_uri(doomsday: bool) -> str:
    """Load the GTA VI Jason or Doctor Doom portrait once and cache as a base64 data URI."""
    filename = "doom_character.jpg" if doomsday else "gta_character.jpg"
    asset_path = _ASSETS_DIR / filename
    if not asset_path.is_file():
        return ""
    raw_bytes = asset_path.read_bytes()
    b64 = base64.b64encode(raw_bytes).decode("ascii")
    return f"data:image/jpeg;base64,{b64}"


def _build_speech_driver_js(
    portal_theme: str,
    latest_bot_reply: str,
    reply_id: str,
    voice_enabled: bool,
    listen_label: str,
    dictating_label: str,
) -> str:
    """Build synchronized Web Speech API + Web Audio resonance driver JS shared across editions."""
    template = r"""
      const PORTAL_THEME = __PORTAL_THEME__;
      const VOICE_ENABLED = __VOICE_ENABLED__;
      const RAW_REPLY = __LATEST_BOT_REPLY__;
      const REPLY_ID = __REPLY_ID__;
      const STAND_BY_TEXT = __LISTEN_LABEL__;
      const DICTATING_TEXT = __DICTATING_LABEL__;

      const cardEl = document.getElementById("holoCard") || document.getElementById("voiceCard");
      const statusEl = document.getElementById("speakStatus");
      let activeSpeech = false;
      let doomNodes = null;
      let voiceWaitTimer = null;

      function safeGetStorage(k) {
        try { return window.localStorage ? window.localStorage.getItem(k) : null; } catch (_) { return null; }
      }
      function safeSetStorage(k, v) {
        try { if (window.localStorage) window.localStorage.setItem(k, v); } catch (_) {}
      }

      function sanitizeSpeechText(raw) {
        if (!raw) return "";
        return String(raw)
          .replace(/\[([^\]]+)\]\([^\)]+\)/g, "$1")
          .replace(/₹/g, "Rupees ")
          .replace(/[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u200D\uFE0F]/gu, " ")
          .replace(/[`*_~]+/g, "")
          .replace(/^\s{0,3}#{1,6}\s*/gm, "")
          .replace(/^\s*[-•>]+\s+/gm, "")
          .replace(/\/\/|\||\[|\]/g, ", ")
          .replace(/\s+/g, " ")
          .trim();
      }

      function setDictatingUI(speaking) {
        activeSpeech = Boolean(speaking);
        if (window.__setActiveSpeechState) {
          window.__setActiveSpeechState(activeSpeech);
        }
        if (cardEl) {
          cardEl.classList.toggle("is-speaking", activeSpeech);
        }
        if (statusEl) {
          statusEl.textContent = activeSpeech ? DICTATING_TEXT : STAND_BY_TEXT;
        }
      }

      function startDoomResonance() {
        stopDoomResonance();
        if (PORTAL_THEME !== "DOOMSDAY") return;
        try {
          const AudioCtx = window.AudioContext || window.webkitAudioContext;
          if (!AudioCtx) return;
          const actx = new AudioCtx();
          if (actx.state === "suspended") {
            actx.resume().catch(function() {});
          }
          const osc55 = actx.createOscillator();
          const osc82 = actx.createOscillator();
          osc55.type = "sawtooth";
          osc55.frequency.value = 55;
          osc82.type = "triangle";
          osc82.frequency.value = 82;

          const bandpass = actx.createBiquadFilter();
          bandpass.type = "bandpass";
          bandpass.frequency.value = 92;
          bandpass.Q.value = 3.2;

          const gain = actx.createGain();
          const now = actx.currentTime;
          gain.gain.setValueAtTime(0.0001, now);
          gain.gain.exponentialRampToValueAtTime(0.045, now + 0.18);

          osc55.connect(bandpass);
          osc82.connect(bandpass);
          bandpass.connect(gain);
          gain.connect(actx.destination);

          osc55.start();
          osc82.start();
          doomNodes = { actx: actx, osc55: osc55, osc82: osc82, gain: gain };
        } catch (_) {
          doomNodes = null;
        }
      }

      function stopDoomResonance() {
        if (!doomNodes) return;
        const nodes = doomNodes;
        doomNodes = null;
        try {
          const now = nodes.actx.currentTime;
          nodes.gain.gain.cancelScheduledValues(now);
          nodes.gain.gain.setValueAtTime(Math.max(0.0001, nodes.gain.gain.value || 0.02), now);
          nodes.gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.08);
          setTimeout(function() {
            try { nodes.osc55.stop(); } catch (_) {}
            try { nodes.osc82.stop(); } catch (_) {}
            try { nodes.actx.close(); } catch (_) {}
          }, 95);
        } catch (_) {
          try { nodes.osc55.stop(); } catch (_) {}
          try { nodes.osc82.stop(); } catch (_) {}
          try { nodes.actx.close(); } catch (_) {}
        }
      }

      function cancelAllSpeech() {
        if (voiceWaitTimer) {
          clearTimeout(voiceWaitTimer);
          voiceWaitTimer = null;
        }
        try {
          if (window.speechSynthesis) window.speechSynthesis.cancel();
        } catch (_) {}
        try {
          if (window.parent && window.parent.speechSynthesis && window.parent !== window) {
            window.parent.speechSynthesis.cancel();
          }
        } catch (_) {}
        stopDoomResonance();
        setDictatingUI(false);
      }

      function pickVoice(theme) {
        if (!window.speechSynthesis) return null;
        const voices = window.speechSynthesis.getVoices() || [];
        if (!voices.length) return null;
        const enVoices = voices.filter(function(v) { return /^en/i.test(v.lang || ""); });
        const pool = enVoices.length ? enVoices : voices;

        if (theme === "GTA VI" || theme === "DOOMSDAY") {
          const patterns = [
            /microsoft david/i,
            /\bdaniel\b/i,
            /google uk english male/i,
            /microsoft mark|microsoft george|arthur|ryan|guy|christopher|eric|alex|fred|aaron|\bmale\b/i
          ];
          for (let i = 0; i < patterns.length; i++) {
            const match = pool.find(function(v) { return patterns[i].test(v.name || ""); });
            if (match) return match;
          }
          return pool[0];
        }

        const neutralPatterns = [
          /google us english/i,
          /microsoft aria|microsoft jenny|samantha|karen|natural/i
        ];
        for (let i = 0; i < neutralPatterns.length; i++) {
          const match = pool.find(function(v) { return neutralPatterns[i].test(v.name || ""); });
          if (match) return match;
        }
        return pool[0];
      }

      function speakReply(rawText) {
        const cleanText = sanitizeSpeechText(rawText);
        if (!cleanText || typeof window.speechSynthesis === "undefined" || typeof SpeechSynthesisUtterance === "undefined") {
          setDictatingUI(false);
          return;
        }

        cancelAllSpeech();

        let dispatched = false;
        function dispatchUtterance() {
          if (dispatched) return;
          dispatched = true;
          if (voiceWaitTimer) {
            clearTimeout(voiceWaitTimer);
            voiceWaitTimer = null;
          }

          const utterance = new SpeechSynthesisUtterance(cleanText);
          const chosenVoice = pickVoice(PORTAL_THEME);
          if (chosenVoice) {
            utterance.voice = chosenVoice;
            utterance.lang = chosenVoice.lang || "en-IN";
          } else {
            utterance.lang = "en-IN";
          }

          if (PORTAL_THEME === "DOOMSDAY") {
            utterance.pitch = 0.35;
            utterance.rate = 0.84;
          } else if (PORTAL_THEME === "GTA VI") {
            utterance.pitch = 0.78;
            utterance.rate = 0.96;
          } else {
            utterance.pitch = 1.0;
            utterance.rate = 1.02;
          }
          utterance.volume = 1.0;

          utterance.onstart = function() {
            setDictatingUI(true);
            if (PORTAL_THEME === "DOOMSDAY") {
              startDoomResonance();
            }
          };
          utterance.onend = function() {
            stopDoomResonance();
            setDictatingUI(false);
          };
          utterance.onerror = function() {
            stopDoomResonance();
            setDictatingUI(false);
          };

          // Prevent Chromium GC from dropping onend mid-utterance
          window._agyActiveUtterance = utterance;
          try {
            window.speechSynthesis.speak(utterance);
          } catch (_) {
            stopDoomResonance();
            setDictatingUI(false);
          }
        }

        const existingVoices = window.speechSynthesis.getVoices ? window.speechSynthesis.getVoices() : [];
        if (existingVoices && existingVoices.length > 0) {
          dispatchUtterance();
        } else {
          const onVoices = function() {
            try { window.speechSynthesis.removeEventListener("voiceschanged", onVoices); } catch (_) {}
            dispatchUtterance();
          };
          try {
            window.speechSynthesis.addEventListener("voiceschanged", onVoices);
          } catch (_) {}
          voiceWaitTimer = setTimeout(function() {
            try { window.speechSynthesis.removeEventListener("voiceschanged", onVoices); } catch (_) {}
            dispatchUtterance();
          }, 220);
        }
      }

      window.addEventListener("pagehide", cancelAllSpeech);
      window.addEventListener("beforeunload", cancelAllSpeech);

      const prevTheme = safeGetStorage("last_spoken_portal_theme");
      if (prevTheme && prevTheme !== PORTAL_THEME) {
        cancelAllSpeech();
      }
      safeSetStorage("last_spoken_portal_theme", PORTAL_THEME);

      if (!VOICE_ENABLED) {
        cancelAllSpeech();
      } else if (REPLY_ID && RAW_REPLY) {
        const lastSpokenId = safeGetStorage("last_spoken_reply_id");
        if (lastSpokenId !== REPLY_ID) {
          safeSetStorage("last_spoken_reply_id", REPLY_ID);
          speakReply(RAW_REPLY);
        }
      }
    """
    return (
        template.replace("__PORTAL_THEME__", json.dumps(portal_theme))
        .replace("__VOICE_ENABLED__", json.dumps(bool(voice_enabled)))
        .replace("__LATEST_BOT_REPLY__", json.dumps(str(latest_bot_reply or "")))
        .replace("__REPLY_ID__", json.dumps(str(reply_id or "")))
        .replace("__LISTEN_LABEL__", json.dumps(listen_label))
        .replace("__DICTATING_LABEL__", json.dumps(dictating_label))
    )


def _render_pro_voice_bar(
    latest_bot_reply: str,
    reply_id: str,
    voice_enabled: bool,
) -> None:
    """Render a minimal institutional speech status bar and Web Speech driver for Default Pro."""
    eq_bars_html = "".join(
        f'<span class="eq-bar" style="--i:{idx}; --d:{0.42 + (idx % 6) * 0.08:.2f}s;"></span>'
        for idx in range(18)
    )
    standby_lbl = "🔇 VOICE MUTED" if not voice_enabled else "🎧 STANDBY IDLE"
    dictating_lbl = "🎙️ DICTATING LIVE"
    speech_js = _build_speech_driver_js(
        portal_theme="DEFAULT",
        latest_bot_reply=latest_bot_reply,
        reply_id=reply_id,
        voice_enabled=voice_enabled,
        listen_label=standby_lbl,
        dictating_label=dictating_lbl,
    )
    pro_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{ width: 100%; background: transparent; font-family: 'Inter', 'Segoe UI', sans-serif; }}
  .voice-bar {{
    display: flex; align-items: center; justify-content: space-between; gap: 12px;
    padding: 10px 14px; border-radius: 10px;
    background: #111827; border: 1px solid rgba(148, 163, 184, 0.24);
  }}
  .voice-bar.is-speaking {{
    border-color: rgba(16, 185, 129, 0.7);
    box-shadow: 0 0 14px rgba(16, 185, 129, 0.18);
  }}
  #speakStatus {{
    font-size: 12px; font-weight: 700; letter-spacing: 0.05em; color: #94a3b8; white-space: nowrap;
  }}
  .voice-bar.is-speaking #speakStatus {{ color: #10b981; }}
  .eq-bars {{
    display: flex; align-items: flex-end; gap: 3px; height: 18px; width: 140px;
  }}
  .eq-bar {{
    flex: 1; height: 22%; border-radius: 2px; background: linear-gradient(180deg, #10b981, #3b82f6);
    transform-origin: bottom center; opacity: 0.4;
  }}
  .voice-bar.is-speaking .eq-bar {{
    height: 92%; opacity: 1;
    animation: eqSpeak var(--d) ease-in-out infinite alternate;
    animation-delay: calc(var(--i) * -0.05s);
  }}
  @keyframes eqSpeak {{
    0% {{ transform: scaleY(0.2); opacity: 0.65; }}
    100% {{ transform: scaleY(1.0); opacity: 1.0; }}
  }}
</style>
</head>
<body>
  <div class="voice-bar" id="voiceCard">
    <span id="speakStatus">{html.escape(standby_lbl)}</span>
    <div class="eq-bars" aria-hidden="true">{eq_bars_html}</div>
  </div>
  <script>
    (function() {{
      {speech_js}
    }})();
  </script>
</body>
</html>"""
    components.html(pro_html, height=58, scrolling=False)


def render_character_stage(
    mood: str = "neutral",
    is_speaking: bool = False,
    turn_id: int = 0,
    operator_name: str = "SHUBH",
    edition: str = "GTA VI",
    latest_bot_reply: str = "",
    reply_id: str = "",
    voice_enabled: bool = True,
) -> None:
    """
    Render a 60fps 3D perspective holographic character stage (GTA VI / Doomsday) or
    clean voice status bar (Default Pro) with Web Speech API + Web Audio API dictation.
    """
    ed_norm = edition.strip().upper()
    if ed_norm in {"DEFAULT", "PRO", "STANDARD"}:
        _render_pro_voice_bar(
            latest_bot_reply=latest_bot_reply,
            reply_id=reply_id,
            voice_enabled=voice_enabled,
        )
        return

    doomsday = ed_norm == "DOOMSDAY"
    portal_theme = "DOOMSDAY" if doomsday else "GTA VI"
    safe_mood = mood if mood in {"bullish", "bearish", "neutral"} else "neutral"
    safe_name = html.escape(operator_name.upper()[:14])
    data_uri = _load_character_data_uri(doomsday=doomsday)

    if doomsday:
        hud_title = "DOOMSDAY AI // LATVERIAN COMMAND"
        char_alt = "Doctor Doom — Avengers: Doomsday AI Tactician"
        primary_accent = "#39ff14"
        secondary_accent = "#ff4500"
        if safe_mood == "bullish":
            border_color, mood_color, mood_label = "#39ff14", "#39ff14", "🛡️ ARCANUM SURGE"
        elif safe_mood == "bearish":
            border_color, mood_color, mood_label = "#ff4500", "#ff6b35", "☢️ DOOM PROTOCOL"
        else:
            border_color, mood_color, mood_label = "#39ff14", "#39ff14", "🛡️ DOOM STANDBY"
        speak_status = "🎙️ DICTATING LIVE"
        listen_status = f"{'🔇 MUTED' if not voice_enabled else '🎧 STANDBY IDLE'} • {mood_label}"
        rim_shadow = (
            f"inset 0 0 42px rgba(57, 255, 20, 0.24), "
            f"inset 0 -54px 68px rgba(4, 14, 7, 0.88), "
            f"0 0 26px {border_color}55"
        )
        obj_pos = "50% 16%"
    else:
        hud_title = "AI TUTOR // LEONIDA BROKER"
        char_alt = "Jason — GTA VI Vice City AI Stock Tutor"
        primary_accent = "#00f5d4"
        secondary_accent = "#ff2a85"
        if safe_mood == "bullish":
            border_color, mood_color, mood_label = "#00f5d4", "#39ff14", "📈 BULLISH STANCE"
        elif safe_mood == "bearish":
            border_color, mood_color, mood_label = "#ff2a85", "#ff4d8d", "🚨 RISK ALERT"
        else:
            border_color, mood_color, mood_label = "#00f5d4", "#00f5d4", "🕶️ STANDBY IDLE"
        speak_status = "🎙️ DICTATING LIVE"
        listen_status = f"{'🔇 MUTED' if not voice_enabled else '🎧 STANDBY IDLE'} • {mood_label}"
        rim_shadow = (
            "inset 18px 0 42px rgba(0, 245, 212, 0.22), "
            "inset -18px 0 42px rgba(255, 42, 133, 0.24), "
            "inset 0 -54px 68px rgba(9, 4, 22, 0.88), "
            f"0 0 26px {border_color}55"
        )
        obj_pos = "50% 14%"

    eq_bars_html = "".join(
        f'<span class="eq-bar" style="--i:{idx}; --d:{0.42 + (idx % 7) * 0.09:.2f}s;"></span>'
        for idx in range(24)
    )

    portrait_markup = (
        f'<img class="char-portrait" src="{data_uri}" alt="{html.escape(char_alt)}" draggable="false" />'
        if data_uri
        else f'<div class="missing-asset">ASSET NOT FOUND: {"doom_character.jpg" if doomsday else "gta_character.jpg"}</div>'
    )

    atmosphere_markup = (
        """
        <div class="doom-mist mist-a"></div>
        <div class="doom-mist mist-b"></div>
        <div class="holo-scanlines"></div>
        <div class="scan-beam"></div>
        """
        if doomsday
        else """
        <div class="vice-sunset-halo"></div>
        <div class="vice-rim-glow"></div>
        <div class="holo-scanlines"></div>
        """
    )

    initial_status = listen_status
    active_class = ""
    speech_driver_js = _build_speech_driver_js(
        portal_theme=portal_theme,
        latest_bot_reply=latest_bot_reply,
        reply_id=reply_id,
        voice_enabled=voice_enabled,
        listen_label=listen_status,
        dictating_label=speak_status,
    )

    stage_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<style>
  @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800;900&family=Share+Tech+Mono&display=swap');
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: transparent;
    font-family: 'Orbitron', sans-serif;
    user-select: none;
  }}

  .stage-viewport {{
    width: 100%;
    height: 100%;
    padding: 8px;
    perspective: 1000px;
    display: flex;
    align-items: stretch;
    justify-content: center;
  }}

  .holo-card {{
    position: relative;
    width: 100%;
    height: 100%;
    border-radius: 14px;
    border: 2px solid {border_color};
    background: {"#050a06" if doomsday else "#0a041a"};
    box-shadow: {rim_shadow};
    transform-style: preserve-3d;
    will-change: transform;
    overflow: hidden;
  }}

  .holo-card.is-speaking {{
    box-shadow:
      0 0 32px {primary_accent}77,
      inset 0 0 36px {primary_accent}38;
  }}

  /* Character Image Layer with Living Breathing Zoom & Float */
  .portrait-wrap {{
    position: absolute;
    inset: -10px;
    transform-style: preserve-3d;
    overflow: hidden;
  }}

  .char-portrait {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: {obj_pos};
    display: block;
    filter: {"contrast(1.06) saturate(1.08)" if doomsday else "contrast(1.05) saturate(1.12)"};
    animation: breathe 5.6s ease-in-out infinite;
    will-change: transform;
  }}

  .holo-card.is-speaking .char-portrait {{
    animation: breatheSpeak 1.6s ease-in-out infinite;
  }}

  @keyframes breathe {{
    0%, 100% {{ transform: scale(1.02) translate3d(0px, 0px, 0px); }}
    50%      {{ transform: scale(1.055) translate3d(0px, -6px, 0px); }}
  }}

  @keyframes breatheSpeak {{
    0%, 100% {{ transform: scale(1.04) translate3d(0px, -2px, 0px); }}
    50%      {{ transform: scale(1.07) translate3d(0px, -7px, 0px); }}
  }}

  /* Interactive Specular Spotlight Tracking Cursor */
  .cursor-spotlight {{
    position: absolute;
    inset: 0;
    pointer-events: none;
    z-index: 3;
    background: radial-gradient(
      circle 220px at var(--mx, 50%) var(--my, 35%),
      {primary_accent}2b 0%,
      {secondary_accent}12 40%,
      transparent 75%
    );
    mix-blend-mode: screen;
  }}

  /* Animated Ambient Diagonal Light Sweep */
  .light-sweep {{
    position: absolute;
    top: -30%;
    left: -70%;
    width: 55%;
    height: 160%;
    z-index: 4;
    pointer-events: none;
    background: linear-gradient(
      110deg,
      transparent 0%,
      rgba(255, 255, 255, 0.04) 38%,
      {primary_accent}33 50%,
      rgba(255, 255, 255, 0.06) 60%,
      transparent 100%
    );
    transform: skewX(-18deg) translate3d(-120%, 0, 0);
    animation: lightSweep 6.4s ease-in-out infinite;
    will-change: transform;
  }}

  @keyframes lightSweep {{
    0%, 18% {{ transform: skewX(-18deg) translate3d(-120%, 0, 0); opacity: 0; }}
    26%     {{ opacity: 0.9; }}
    62%     {{ transform: skewX(-18deg) translate3d(380%, 0, 0); opacity: 0.7; }}
    70%, 100% {{ transform: skewX(-18deg) translate3d(380%, 0, 0); opacity: 0; }}
  }}

  /* Theme-Matched Atmosphere Overlays */
  .vice-sunset-halo {{
    position: absolute;
    inset: 0;
    z-index: 2;
    pointer-events: none;
    background:
      radial-gradient(circle at 50% 22%, rgba(255, 166, 43, 0.24) 0%, transparent 52%),
      linear-gradient(180deg, rgba(16, 6, 36, 0.14) 0%, transparent 38%, rgba(8, 3, 20, 0.88) 100%);
  }}

  .vice-rim-glow {{
    position: absolute;
    inset: 0;
    z-index: 2;
    pointer-events: none;
    background:
      radial-gradient(circle at 8% 50%, rgba(0, 245, 212, 0.24) 0%, transparent 40%),
      radial-gradient(circle at 92% 50%, rgba(255, 42, 133, 0.24) 0%, transparent 40%);
  }}

  .doom-mist {{
    position: absolute;
    inset: -15%;
    z-index: 2;
    pointer-events: none;
    will-change: transform, opacity;
  }}

  .mist-a {{
    background:
      radial-gradient(ellipse at 25% 78%, rgba(57, 255, 20, 0.28) 0%, transparent 52%),
      radial-gradient(ellipse at 78% 26%, rgba(16, 185, 129, 0.22) 0%, transparent 48%);
    animation: mistDriftA 9s ease-in-out infinite alternate;
  }}

  .mist-b {{
    background:
      radial-gradient(ellipse at 72% 84%, rgba(57, 255, 20, 0.24) 0%, transparent 50%),
      linear-gradient(180deg, rgba(4, 12, 6, 0.28) 0%, transparent 36%, rgba(4, 10, 5, 0.90) 100%);
    animation: mistDriftB 11s ease-in-out infinite alternate;
  }}

  @keyframes mistDriftA {{
    0%   {{ transform: translate3d(-4%, 2%, 0) scale(1.0); opacity: 0.72; }}
    100% {{ transform: translate3d(4%, -3%, 0) scale(1.07); opacity: 0.96; }}
  }}

  @keyframes mistDriftB {{
    0%   {{ transform: translate3d(3%, -2%, 0) scale(1.04); opacity: 0.85; }}
    100% {{ transform: translate3d(-3%, 3%, 0) scale(1.0); opacity: 0.65; }}
  }}

  .holo-scanlines {{
    position: absolute;
    inset: 0;
    z-index: 4;
    pointer-events: none;
    background: repeating-linear-gradient(
      0deg,
      rgba(0, 0, 0, 0.0) 0px,
      rgba(0, 0, 0, 0.0) 2px,
      rgba(255, 255, 255, 0.025) 3px,
      rgba(0, 0, 0, 0.12) 4px
    );
  }}

  .scan-beam {{
    position: absolute;
    left: 0;
    right: 0;
    height: 36px;
    z-index: 4;
    pointer-events: none;
    background: linear-gradient(180deg, transparent, rgba(57, 255, 20, 0.22), transparent);
    animation: scanMove 4.5s linear infinite;
    will-change: transform;
  }}

  @keyframes scanMove {{
    0%   {{ transform: translate3d(0, -40px, 0); }}
    100% {{ transform: translate3d(0, 580px, 0); }}
  }}

  /* Floating Particles Canvas */
  #particleCanvas {{
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    z-index: 5;
    pointer-events: none;
  }}

  /* 3D Depth Corner Brackets */
  .bracket {{
    position: absolute;
    width: 18px;
    height: 18px;
    z-index: 7;
    pointer-events: none;
    border-color: {primary_accent};
    border-style: solid;
    transform: translateZ(24px);
  }}
  .b-tl {{ top: 8px; left: 8px; border-width: 2px 0 0 2px; }}
  .b-tr {{ top: 8px; right: 8px; border-width: 2px 2px 0 0; }}
  .b-bl {{ bottom: 8px; left: 8px; border-width: 0 0 2px 2px; }}
  .b-br {{ bottom: 8px; right: 8px; border-width: 0 2px 2px 0; }}

  /* Floating Top HUD Header */
  .hud-header {{
    position: absolute;
    top: 14px;
    left: 14px;
    right: 14px;
    z-index: 8;
    display: flex;
    flex-direction: column;
    gap: 6px;
    pointer-events: none;
    transform: translateZ(34px);
  }}

  .hud-title-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
    padding: 7px 11px;
    border-radius: 7px;
    background: {"rgba(7, 14, 9, 0.84)" if doomsday else "rgba(10, 5, 26, 0.82)"};
    border: 1px solid {primary_accent}aa;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.55);
  }}

  .hud-main-label {{
    font-family: 'Orbitron', sans-serif;
    font-size: 11px;
    font-weight: 900;
    letter-spacing: 0.08em;
    color: {primary_accent};
    text-shadow: 0 0 8px {primary_accent}88;
  }}

  .hud-live-dot {{
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    color: #39ff14;
    letter-spacing: 0.06em;
    white-space: nowrap;
  }}

  .hud-sub-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 6px;
  }}

  .hud-pill {{
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.05em;
    color: {mood_color};
    background: rgba(6, 6, 14, 0.84);
    border: 1px solid {mood_color}88;
    border-radius: 5px;
    padding: 3px 8px;
  }}

  .hud-op {{
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    color: #e2e8f0;
    background: rgba(6, 6, 14, 0.82);
    border: 1px solid {secondary_accent}88;
    border-radius: 5px;
    padding: 3px 8px;
  }}

  /* Bottom Audio Waveform Equalizer Bar */
  .hud-footer {{
    position: absolute;
    left: 14px;
    right: 14px;
    bottom: 14px;
    z-index: 8;
    padding: 9px 12px;
    border-radius: 8px;
    background: {"rgba(7, 14, 9, 0.88)" if doomsday else "rgba(11, 5, 28, 0.86)"};
    border: 1px solid {border_color}99;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.65);
    display: flex;
    flex-direction: column;
    gap: 7px;
    pointer-events: none;
    transform: translateZ(38px);
  }}

  .status-line {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
  }}

  #speakStatus {{
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.07em;
    color: {mood_color};
  }}

  .wave-tag {{
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    color: {secondary_accent if not doomsday else "#fbbf24"};
    letter-spacing: 0.06em;
  }}

  .eq-bars {{
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 3px;
    height: 22px;
    padding: 0 2px;
  }}

  .eq-bar {{
    flex: 1;
    height: 20%;
    border-radius: 2px;
    background: linear-gradient(180deg, {primary_accent}, {secondary_accent});
    transform-origin: bottom center;
    animation: eqIdle calc(var(--d) * 2.4) ease-in-out infinite alternate;
    animation-delay: calc(var(--i) * -0.07s);
    will-change: transform, opacity;
  }}

  .holo-card.is-speaking .eq-bar {{
    height: 92%;
    animation: eqSpeak var(--d) ease-in-out infinite alternate;
    animation-delay: calc(var(--i) * -0.05s);
    box-shadow: 0 0 8px {primary_accent}88;
  }}

  @keyframes eqIdle {{
    0%   {{ transform: scaleY(0.35); opacity: 0.55; }}
    100% {{ transform: scaleY(1.0); opacity: 0.90; }}
  }}

  @keyframes eqSpeak {{
    0%   {{ transform: scaleY(0.18); opacity: 0.72; }}
    50%  {{ transform: scaleY(0.98); opacity: 1.0; }}
    100% {{ transform: scaleY(0.42); opacity: 0.85; }}
  }}

  .missing-asset {{
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
    color: #ff4d8d;
    font-size: 12px;
    text-align: center;
    padding: 20px;
  }}
</style>
</head>
<body>
  <div class="stage-viewport" id="stageViewport">
    <div class="holo-card {active_class}" id="holoCard">
      <div class="portrait-wrap">
        {portrait_markup}
        {atmosphere_markup}
        <div class="cursor-spotlight" id="spotlight"></div>
        <div class="light-sweep"></div>
        <canvas id="particleCanvas"></canvas>
      </div>

      <span class="bracket b-tl"></span>
      <span class="bracket b-tr"></span>
      <span class="bracket b-bl"></span>
      <span class="bracket b-br"></span>

      <div class="hud-header">
        <div class="hud-title-bar">
          <span class="hud-main-label">{hud_title}</span>
          <span class="hud-live-dot">● LIVE</span>
        </div>
        <div class="hud-sub-row">
          <span class="hud-pill">{mood_label}</span>
          <span class="hud-op">OP: {safe_name}</span>
        </div>
      </div>

      <div class="hud-footer">
        <div class="status-line">
          <span id="speakStatus">{initial_status}</span>
          <span class="wave-tag">{"ARCANUM WAVELENGTH" if doomsday else "VOICE SYNTH AUDIO"}</span>
        </div>
        <div class="eq-bars" aria-hidden="true">{eq_bars_html}</div>
      </div>
    </div>
  </div>

  <script>
    (function() {{
      const IS_DOOMSDAY = {json.dumps(doomsday)};
      const INITIAL_SPEAK = {json.dumps(is_speaking)};
      const TURN_ID = {int(turn_id)};

      const viewport = document.getElementById("stageViewport");
      const card = document.getElementById("holoCard");
      const canvas = document.getElementById("particleCanvas");
      const ctx = canvas.getContext("2d");

      let targetRx = 0;
      let targetRy = 0;
      let curRx = 0;
      let curRy = 0;
      let isHovering = false;
      let activeSpeechState = false;

      window.__setActiveSpeechState = function(flag) {{
        activeSpeechState = Boolean(flag);
      }};

      {speech_driver_js}

      viewport.addEventListener("pointermove", function(e) {{
        const rect = viewport.getBoundingClientRect();
        const nx = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        const ny = ((e.clientY - rect.top) / rect.height) * 2 - 1;
        targetRy = nx * 7.5;
        targetRx = -ny * 6.0;
        isHovering = true;
        card.style.setProperty("--mx", ((nx + 1) * 50).toFixed(1) + "%");
        card.style.setProperty("--my", ((ny + 1) * 50).toFixed(1) + "%");
      }}, {{ passive: true }});

      viewport.addEventListener("pointerleave", function() {{
        isHovering = false;
        targetRx = 0;
        targetRy = 0;
        card.style.setProperty("--mx", "50%");
        card.style.setProperty("--my", "35%");
      }}, {{ passive: true }});

      // Lightweight 60fps atmospheric particle emitter
      function resizeCanvas() {{
        const rect = card.getBoundingClientRect();
        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        canvas.width = Math.max(1, Math.floor(rect.width * dpr));
        canvas.height = Math.max(1, Math.floor(rect.height * dpr));
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      }}
      resizeCanvas();
      window.addEventListener("resize", resizeCanvas);

      const palette = IS_DOOMSDAY
        ? ["rgba(57, 255, 20, ", "rgba(16, 185, 129, ", "rgba(163, 230, 53, "]
        : ["rgba(0, 245, 212, ", "rgba(255, 42, 133, ", "rgba(255, 183, 3, "];

      const particles = Array.from({{ length: 28 }}, function(_, i) {{
        return {{
          x: Math.random() * 380,
          y: Math.random() * 540,
          r: 1.2 + Math.random() * 2.4,
          vx: (Math.random() - 0.5) * 0.35,
          vy: -(0.28 + Math.random() * 0.55),
          alpha: 0.25 + Math.random() * 0.5,
          color: palette[i % palette.length],
        }};
      }});

      function frame(now) {{
        requestAnimationFrame(frame);
        const t = now * 0.001;

        // Subtle idle holographic float even when not hovering
        const goalRx = isHovering ? targetRx : Math.sin(t * 0.9) * 1.6;
        const goalRy = isHovering ? targetRy : Math.cos(t * 0.7) * 2.1;

        curRx += (goalRx - curRx) * 0.10;
        curRy += (goalRy - curRy) * 0.10;
        card.style.transform =
          "rotateX(" + curRx.toFixed(2) + "deg) rotateY(" + curRy.toFixed(2) + "deg)";

        // Draw floating particles synced with live Web Speech dictation state
        const w = card.clientWidth || 360;
        const h = card.clientHeight || 540;
        ctx.clearRect(0, 0, w, h);
        const speakingNow = activeSpeechState || (INITIAL_SPEAK && TURN_ID < 0);
        const boost = speakingNow ? 1.85 : 1.0;
        for (let i = 0; i < particles.length; i++) {{
          const p = particles[i];
          p.x += p.vx + Math.sin(t + i) * 0.12;
          p.y += p.vy * boost;
          if (p.y < -10) {{
            p.y = h + 10;
            p.x = Math.random() * w;
          }}
          if (p.x < -10) p.x = w + 10;
          if (p.x > w + 10) p.x = -10;
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
          ctx.fillStyle = p.color + (p.alpha * (speakingNow ? 0.95 : 0.7)).toFixed(2) + ")";
          ctx.fill();
        }}
      }}

      requestAnimationFrame(frame);
    }})();
  </script>
</body>
</html>
"""
    components.html(stage_html, height=560, scrolling=False)
