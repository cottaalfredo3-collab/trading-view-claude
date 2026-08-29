"""
Optional notifier — sends Claude's analysis to Telegram.
Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID env vars to enable.
"""

import os
import requests

TELEGRAM_TOKEN   = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")


def send_notification(result: dict):
    """Forward Claude analysis to Telegram."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return  # silently skip if not configured

    alert    = result.get("alert", {})
    analysis = result.get("analysis", "")
    ts       = result.get("timestamp", "")

    symbol  = alert.get("symbol", alert.get("ticker", "Unknown"))
    close   = alert.get("close", alert.get("price", "—"))
    message = (
        f"📊 *TradingView Alert — {symbol}*\n"
        f"🕐 {ts[:19].replace('T', ' ')} UTC\n"
        f"💲 Price: `{close}`\n\n"
        f"🤖 *Claude Analysis:*\n{analysis}"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }, timeout=10)
