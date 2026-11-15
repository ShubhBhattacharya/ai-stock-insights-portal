"""Voice-to-Text Whisper Flow Service | OpenAI Whisper-1 + Robust Local/Google Fallback.

Provides seamless microphone recording via streamlit-mic-recorder, audio transcription,
and command dispatch for stock analysis, market queries, and AI chatbot conversation.
"""

from __future__ import annotations

import io
import os
import wave
import streamlit as st

# Safe import for streamlit_mic_recorder
try:
    from streamlit_mic_recorder import mic_recorder
    HAS_MIC_RECORDER = True
except Exception:
    HAS_MIC_RECORDER = False
    mic_recorder = None  # type: ignore[assignment]


def get_openai_api_key() -> str:
    """Safely retrieve OpenAI API key from session state, environment, or Streamlit secrets."""
    # 1. User-supplied key in UI session
    sess_key = str(st.session_state.get("openai_api_key", "")).strip()
    if sess_key:
        return sess_key

    # 2. Environment variable
    env_key = str(os.environ.get("OPENAI_API_KEY", "")).strip()
    if env_key:
        return env_key

    # 3. Streamlit secrets (with safe catch if secrets.toml is missing)
    try:
        secret_key = str(st.secrets.get("OPENAI_API_KEY", "")).strip()
        if secret_key:
            return secret_key
    except Exception:
        pass

    return ""


def transcribe_audio_bytes(
    audio_bytes: bytes,
    audio_format: str = "wav",
) -> tuple[str, str, bool]:
    """Transcribe raw audio bytes using OpenAI Whisper-1 API with graceful local/Google STT fallback.

    Returns:
        tuple: (transcribed_text, engine_description, is_success)
    """
    if not audio_bytes or len(audio_bytes) < 64:
        return "", "No audio data recorded", False

    api_key = get_openai_api_key()

    # Step 1: Try OpenAI Whisper-1 API if an API key is available
    if api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            audio_buf = io.BytesIO(audio_bytes)
            audio_buf.name = f"query.{audio_format}"
            
            transcript_obj = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_buf,
                language="en",
            )
            text = str(transcript_obj.text).strip()
            if text:
                return text, "OpenAI Whisper-1 API", True
        except Exception as whisper_err:
            # Fall through gracefully to local / free engine fallback
            pass

    # Step 2: Fallback to SpeechRecognition (free Google/local recognizer)
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        audio_buf = io.BytesIO(audio_bytes)
        with sr.AudioFile(audio_buf) as source:
            audio_data = recognizer.record(source)

        text = recognizer.recognize_google(audio_data, language="en-IN")
        if text and text.strip():
            return text.strip(), "SpeechRecognition Engine (Zero-Config)", True
    except sr.UnknownValueError:
        return "", "Could not understand audio. Please speak clearly into your mic.", False
    except sr.RequestError as req_err:
        return "", f"Speech service unavailable: {req_err}", False
    except Exception as fallback_err:
        return "", f"Transcription error: {fallback_err}", False

    return "", "No speech detected in audio clip", False


def render_voice_input_controls(
    key_prefix: str = "tutor_voice",
    on_transcript_received=None,
    button_label: str = "🎙️ Speak Query (Whisper)",
    stop_label: str = "⏹️ Stop & Transcribe",
) -> str | None:
    """Render the microphone recorder button and handle live transcription into the app.

    Args:
        key_prefix: Unique Streamlit component key prefix.
        on_transcript_received: Optional callable(str) invoked upon successful transcription.
        button_label: Label for starting mic recording.
        stop_label: Label for stopping mic recording.

    Returns:
        The transcribed text if a new recording was processed on this run, otherwise None.
    """
    if not HAS_MIC_RECORDER or mic_recorder is None:
        st.warning("Microphone recorder module not loaded. Please ensure streamlit-mic-recorder is installed.")
        return None

    # Track processed recording IDs so we don't duplicate on subsequent Streamlit script reruns
    last_id_key = f"{key_prefix}_last_processed_id"
    if last_id_key not in st.session_state:
        st.session_state[last_id_key] = None

    v_col1, v_col2 = st.columns([2.5, 1.2], gap="small")

    with v_col1:
        audio_data = mic_recorder(
            start_prompt=button_label,
            stop_prompt=stop_label,
            just_once=False,
            use_container_width=True,
            format="wav",
            key=f"{key_prefix}_mic",
        )

    with v_col2:
        with st.popover("⚙️ Whisper Settings", use_container_width=True):
            st.caption("**Whisper STT Configuration**")
            current_key = get_openai_api_key()
            masked_key = f"{current_key[:4]}...{current_key[-4:]}" if len(current_key) > 8 else ("Configured" if current_key else "None")
            st.markdown(f"**Current Engine:** {'⚡ OpenAI Whisper-1' if current_key else '🌐 Free Speech Engine'}")
            st.markdown(f"**API Key Status:** `{masked_key}`")
            new_key = st.text_input(
                "OpenAI API Key (Optional)",
                value=st.session_state.get("openai_api_key", ""),
                type="password",
                help="Paste an OpenAI key to use whisper-1 model. If empty, the app automatically uses the free engine.",
                key=f"{key_prefix}_api_key_input",
            )
            if new_key != st.session_state.get("openai_api_key", ""):
                st.session_state["openai_api_key"] = new_key.strip()
                st.success("API Key updated for session!")

    # Check if a new recording has arrived
    if audio_data and isinstance(audio_data, dict):
        rec_id = audio_data.get("id")
        audio_bytes = audio_data.get("bytes")

        if rec_id and rec_id != st.session_state[last_id_key] and audio_bytes:
            st.session_state[last_id_key] = rec_id
            
            with st.spinner("⚡ Transcribing audio via Whisper STT..."):
                transcript, engine, success = transcribe_audio_bytes(audio_bytes, audio_format="wav")

            if success and transcript:
                st.toast(f"🎙️ Transcribed via {engine}: \"{transcript}\"", icon="✨")
                st.session_state[f"{key_prefix}_last_transcript"] = transcript
                st.session_state[f"{key_prefix}_last_engine"] = engine
                
                if on_transcript_received:
                    on_transcript_received(transcript)
                return transcript
            else:
                msg = engine if engine else "Could not transcribe audio."
                st.warning(f"⚠️ {msg}")

    # Display last transcribed chip if available
    last_tx = st.session_state.get(f"{key_prefix}_last_transcript")
    last_eng = st.session_state.get(f"{key_prefix}_last_engine")
    if last_tx:
        st.markdown(
            f'<div style="font-size:0.78rem; color:#cbd5e1; margin:0.35rem 0; padding:0.25rem 0.55rem; '
            f'background:rgba(255,42,133,0.08); border-left:3px solid #ff2a85; border-radius:4px;">'
            f'🗣️ <strong>Latest Voice Input ({last_eng}):</strong> <em>"{last_tx}"</em>'
            f'</div>',
            unsafe_allow_html=True,
        )

    return None


def dispatch_voice_command(transcript: str) -> dict[str, str]:
    """Parse a transcribed voice utterance and determine if it's a module switch command or a stock query."""
    t = transcript.strip().lower()

    # Direct module navigation mapping
    nav_map = {
        "market overview": "📊 Market Overview",
        "market": "📊 Market Overview",
        "overview": "📊 Market Overview",
        "nifty": "📊 Market Overview",
        "single stock": "🤖 Single Stock AI & ML Prediction",
        "single": "🤖 Single Stock AI & ML Prediction",
        "prediction": "🤖 Single Stock AI & ML Prediction",
        "forecast": "🤖 Single Stock AI & ML Prediction",
        "comparison": "⚖️ Two-Stock Comparison",
        "compare": "⚖️ Two-Stock Comparison",
        "two stock": "⚖️ Two-Stock Comparison",
        "paper trading": "💼 Virtual Paper Trading",
        "paper": "💼 Virtual Paper Trading",
        "trading": "💼 Virtual Paper Trading",
        "portfolio": "💼 Virtual Paper Trading",
        "risk optimizer": "🎯 Portfolio Risk Optimizer",
        "risk": "🎯 Portfolio Risk Optimizer",
        "optimizer": "🎯 Portfolio Risk Optimizer",
        "price alert": "🚨 Price Alerts",
        "alerts": "🚨 Price Alerts",
        "alarm": "🚨 Price Alerts",
        "ai tutor": "🎓 AI Stock Tutor & Chatbot",
        "tutor": "🎓 AI Stock Tutor & Chatbot",
        "chatbot": "🎓 AI Stock Tutor & Chatbot",
        "chat": "🎓 AI Stock Tutor & Chatbot",
        "synopsis": "📜 Project Synopsis & Credits",
        "credits": "📜 Project Synopsis & Credits",
    }

    # Match short navigation commands (e.g., "go to market overview", "open single stock")
    words = t.split()
    if len(words) <= 5:
        for kw, target_mod in nav_map.items():
            if kw in t:
                return {"action": "navigate", "target": target_mod, "text": transcript}

    # Otherwise treat as interactive equity / tutor query
    return {"action": "query", "target": "🎓 AI Stock Tutor & Chatbot", "text": transcript}


__all__ = [
    "dispatch_voice_command",
    "get_openai_api_key",
    "render_voice_input_controls",
    "transcribe_audio_bytes",
]
