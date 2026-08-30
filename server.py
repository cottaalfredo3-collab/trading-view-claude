"""
TradingView → Claude Alert Analysis Server
------------------------------------------
Receives TradingView webhooks, sends them to Claude for analysis,
logs results, and optionally forwards to Telegram/email.
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify
import anthropic

# ── Config ──────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = "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"
WEBHOOK_SECRET    = os.environ.get("WEBHOOK_SECRET", "")      # optional auth token
PORT              = int(os.environ.get("PORT", 5000))
LOG_FILE          = "alerts.log"

# ── Setup ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)
log = logging.getLogger(__name__)

app = Flask(__name__)
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


# ── Claude analysis ──────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a concise trading signal analyst.
When given a TradingView alert payload, you:
1. Identify the asset, direction (bullish/bearish/neutral), and key indicators.
2. Give a 2-3 sentence analysis of what the signal means.
3. List concrete next steps (e.g. watch for confirmation, set alert at X level).
4. Always add a brief risk note.
Keep your response under 200 words. Never give financial advice or recommend specific trades."""


def analyse_with_claude(alert: dict) -> str:
    """Send alert payload to Claude and return analysis text."""
    payload_str = json.dumps(alert, indent=2)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Analyse this TradingView alert:\n\n```json\n{payload_str}\n```"
            }
        ]
    )
    return message.content[0].text


# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "time": datetime.utcnow().isoformat()})


@app.route("/webhook", methods=["POST"])
def webhook():
    # ── Optional secret validation ──
    if WEBHOOK_SECRET:
        token = request.headers.get("X-Webhook-Secret", "")
        if token != WEBHOOK_SECRET:
            log.warning("Rejected request — bad secret")
            return jsonify({"error": "Unauthorized"}), 401

    # ── Parse body (TradingView sends JSON or plain text) ──
    try:
        if request.is_json:
            alert = request.get_json()
        else:
            # TradingView sometimes sends plain text — wrap it
            raw = request.data.decode("utf-8")
            try:
                alert = json.loads(raw)
            except json.JSONDecodeError:
                alert = {"raw_message": raw}
    except Exception as e:
        return jsonify({"error": f"Bad payload: {e}"}), 400

    log.info("Alert received: %s", json.dumps(alert))

    # ── Analyse ──
    try:
        analysis = analyse_with_claude(alert)
    except Exception as e:
        log.error("Claude error: %s", e)
        return jsonify({"error": "Claude analysis failed", "detail": str(e)}), 500

    # ── Log result ──
    result = {
        "timestamp": datetime.utcnow().isoformat(),
        "alert": alert,
        "analysis": analysis
    }
    log.info("Analysis:\n%s", analysis)

    # ── Optionally notify (hook in notifier.py) ──
    try:
        from notifier import send_notification
        send_notification(result)
    except ImportError:
        pass  # notifier.py is optional

    return jsonify(result), 200


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if not ANTHROPIC_API_KEY:
        raise SystemExit("ERROR: set ANTHROPIC_API_KEY environment variable")
    log.info("Server starting on port %d", PORT)
    app.run(host="0.0.0.0", port=PORT, debug=False)
