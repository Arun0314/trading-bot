<<<<<<< HEAD
# Binance Futures Testnet Trading Bot

CLI tool to place MARKET and LIMIT orders on Binance Futures Testnet.

---

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Get testnet API keys from https://testnet.binancefuture.com
cp .env.example .env
# Open .env and paste your keys
```

---

## Run

```bash
# Market BUY
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01

# Limit SELL
python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.1 --price 3200

# Market SELL (lowercase works too)
python cli.py --symbol solusdt --side sell --type market --quantity 1
```

**Sample output:**
```
✓ Order placed successfully
  Order ID  : 3812940123
  Symbol    : BTCUSDT
  Side      : BUY
  Type      : MARKET
  Quantity  : 0.01
  Price     : market
  Status    : FILLED
  Client ID : x-abc123def
```

---

## Logs

All requests, responses and errors are written to `logs/app.log`.
Errors are also printed to stderr in the terminal.

---

## Notes

- LIMIT orders use GTC (Good Till Cancelled) by default
- Symbol and side inputs are normalized — `btcusdt`, `BUY`, `buy` all work
- Quantity precision matters — Binance rejects orders that don't match the symbol's stepSize (e.g. BTC min is 0.001)
- Only works against Binance Futures **Testnet**, not mainnet

---

## Zip & share

```bash
zip -r trading_bot.zip trading_bot/
```
=======
# trading-bot
>>>>>>> 13dc8762e0273698cc8ea755349e34ab1dc1feb3
