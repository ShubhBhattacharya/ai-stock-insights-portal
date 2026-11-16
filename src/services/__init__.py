"""Service layer for market data, ML forecasting, reporting, voice transcription, database, and tutor engine."""

from src.services.db import (
    authenticate_user,
    db_add_price_alert,
    db_execute_buy_order,
    db_execute_sell_order,
    db_remove_price_alert,
    db_reset_portfolio,
    get_user_alerts,
    get_user_portfolio,
    init_db,
    register_user,
)
from src.services.voice_service import (
    dispatch_voice_command,
    get_openai_api_key,
    render_voice_input_controls,
    transcribe_audio_bytes,
)

__all__ = [
    "authenticate_user",
    "db_add_price_alert",
    "db_execute_buy_order",
    "db_execute_sell_order",
    "db_remove_price_alert",
    "db_reset_portfolio",
    "dispatch_voice_command",
    "get_openai_api_key",
    "get_user_alerts",
    "get_user_portfolio",
    "init_db",
    "register_user",
    "render_voice_input_controls",
    "transcribe_audio_bytes",
]
