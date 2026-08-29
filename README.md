# TradingView → Claude Alert Analyser

Receives TradingView webhook alerts and returns instant AI analysis via Claude.

---

## Architecture

```
TradingView Alert
      │  (HTTP POST JSON)
      ▼
  server.py  ──► Claude API  ──► Analysis text
      │
      ▼  (optional)
  notifier.py ──► Telegram
```

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set environment variables
```bash
export ANTHROPIC_API_KEY="sk-ant-..."

# Optional
export WEBHOOK_SECRET="any-random-string"   # validates TradingView requests
export TELEGRAM_BOT_TOKEN="123456:ABC..."   # for Telegram notifications
export TELEGRAM_CHAT_ID="-1001234567890"
export PORT=5000
```

### 3. Run the server
```bash
python server.py
```

### 4. Expose to the internet
TradingView needs a public URL. Options:

| Method | Command | Notes |
|--------|---------|-------|
| **ngrok** (dev) | `ngrok http 5000` | Free, temporary URL |
| **Railway** | Deploy repo | Free tier, persistent |
| **Render** | Deploy repo | Free tier, persistent |
| **VPS** | Run directly | Full control |

---

## TradingView Setup

1. Open TradingView → create or open a chart
2. Click the **Alert** (clock) icon → **Create Alert**
3. Set your condition (RSI, MACD, price level, etc.)
4. Under **Notifications**, enable **Webhook URL**
5. Enter your public URL: `https://YOUR-DOMAIN.com/webhook`
6. In the **Message** box, paste structured JSON:

```json
{
  "symbol":   "{{ticker}}",
  "exchange": "{{exchange}}",
  "interval": "{{interval}}",
  "close":    {{close}},
  "volume":   {{volume}},
  "time":     "{{time}}",
  "signal":   "Your signal name here"
}
```

> **Note:** TradingView only sends webhooks on **Pro, Pro+, or Premium** plans.

---

## Test Locally

```bash
# Terminal 1 — run server
python server.py

# Terminal 2 — fire test alerts
python test_alert.py rsi_overbought
python test_alert.py macd_crossover
python test_alert.py breakout
```

---

## Sample Response

```json
{
  "timestamp": "2026-08-29T10:23:01",
  "alert": {
    "symbol": "BTCUSDT",
    "close": 67450.5,
    "rsi": 74.2,
    "signal": "RSI Overbought"
  },
  "analysis": "BTCUSDT is showing an RSI of 74.2 on the 1h chart,
  indicating overbought conditions. Price is trading above both the
  20 and 50 EMAs, confirming the bullish trend but suggesting a
  potential pullback. Watch for RSI to cross back below 70 as a
  short-term bearish signal, or a rejection at current levels.
  Risk note: Overbought signals in strong trends can persist —
  avoid shorting without additional confirmation."
}
```

---

## Customise the Claude Prompt

Edit `SYSTEM_PROMPT` in `server.py` to change Claude's analysis style:
- Add your trading strategy context
- Request specific format (e.g. JSON output, risk/reward levels)
- Add portfolio or position sizing context
