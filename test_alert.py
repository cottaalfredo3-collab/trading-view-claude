"""
Simulate a TradingView webhook alert locally.
Run:  python test_alert.py
(server must be running on localhost:5000)
"""

import json
import requests

# ── Sample payloads — edit to match your Pine Script alert message ──
SAMPLE_ALERTS = {
    "rsi_overbought": {
        "symbol": "BTCUSDT",
        "exchange": "BINANCE",
        "interval": "1h",
        "close": 67450.50,
        "volume": 1823.4,
        "rsi": 74.2,
        "signal": "RSI Overbought",
        "ema_20": 66100.0,
        "ema_50": 63200.0
    },
    "macd_crossover": {
        "symbol": "AAPL",
        "exchange": "NASDAQ",
        "interval": "4h",
        "close": 228.75,
        "signal": "MACD Bullish Crossover",
        "macd_line": 1.24,
        "signal_line": 0.87,
        "histogram": 0.37,
        "volume": 45_000_000
    },
    "breakout": {
        "symbol": "EURUSD",
        "exchange": "FX",
        "interval": "1D",
        "close": 1.0925,
        "signal": "Resistance Breakout",
        "resistance_level": 1.0910,
        "atr": 0.0048,
        "comment": "Price closed above key weekly resistance"
    }
}

SERVER = "http://localhost:5000/webhook"

def test(alert_name: str):
    alert = SAMPLE_ALERTS[alert_name]
    print(f"\n── Sending '{alert_name}' alert ──")
    print(json.dumps(alert, indent=2))

    resp = requests.post(SERVER, json=alert, timeout=30)
    print(f"\nStatus: {resp.status_code}")
    data = resp.json()
    print("\n🤖 Claude Analysis:")
    print(data.get("analysis", data))


if __name__ == "__main__":
    import sys
    name = sys.argv[1] if len(sys.argv) > 1 else "rsi_overbought"
    if name not in SAMPLE_ALERTS:
        print(f"Unknown alert. Choose: {list(SAMPLE_ALERTS.keys())}")
    else:
        test(name)
