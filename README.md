# Limitless BTC 1H Probability Arbitrage Bot

Aggressive, fully async probability arbitrage bot for **Limitless Exchange** using 1-hour BTC markets and a live BTC price feed from Binance.

## Features

- Monitors all active BTC 1-hour markets on Limitless.
- Maintains a persistent Binance websocket (btcusdt@trade) for real-time BTC price.
- Computes implied probability edge for each market and auto-trades when edge >= threshold.
- Aggressive compounding position sizing with configurable max risk.
- In-memory position tracking with take-profit and opposite-edge exit logic.
- PAPER and LIVE trading modes.
- Fully async, event-driven architecture suitable for local or Fly.io deployment.

---

## Project Structure

```text
limitless_bot/
├── main.py
├── config.py
├── limitless_client.py
├── binance_feed.py
├── market_discovery.py
├── strategy.py
├── execution.py
├── risk_manager.py
├── position_manager.py
├── logger.py
├── requirements.txt
├── .env.example
├── README.md
```

---

## Installation (Local PC)

1. **Clone the repo**

   ```bash
   git clone <your-private-repo-url> limitless_bot
   cd limitless_bot
   ```

2. **Create and activate virtualenv (recommended)**

   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**

   ```bash
   cp .env.example .env
   ```

   Set:
   - `LIMITLESS_API_KEY` – your Limitless Exchange API key.
   - `PAPER_TRADING=True` (default) for simulation.

5. **Run the bot**

   ```bash
   python main.py
   ```

---

## Configuration

All configuration via `.env` file:

- `LIMITLESS_API_KEY` (required)
- `EDGE_THRESHOLD` – minimum edge to trigger entries (default `0.05`).
- `TAKE_PROFIT_PERCENT` – take-profit threshold (default `0.03` → 3%).
- `PAPER_TRADING` – `True` for simulation, `False` for live trading.
- `MAX_POSITION_PERCENT` – max fraction of balance per trade (default `0.6`).

---

## Trading Logic

### Real Probability

For each BTC 1H market:

```
real_probability = clamp(current_btc_price / target_price, 0, 1)
edge = real_probability - yes_price
```

If `edge >= EDGE_THRESHOLD`, bot considers entering.

### Sizing

- `edge >= 0.10` → use 60% of balance.
- `edge >= 0.07` → use 40% of balance.
- `edge >= 0.05` → use 20% of balance.

### Exit Logic

- Exit when unrealized profit >= `TAKE_PROFIT_PERCENT`.
- Or exit if the edge turns negative.

---

## Fly.io Deployment

1. **Install Fly CLI**

   ```bash
   curl -L https://fly.io/install.sh | sh
   fly auth login
   ```

2. **Create app**

   ```bash
   fly launch --no-deploy
   ```

3. **Set secrets**

   ```bash
   fly secrets set LIMITLESS_API_KEY=your_api_key_here
   fly secrets set PAPER_TRADING=False
   ```

4. **Deploy**

   ```bash
   fly deploy
   ```

---

## Disclaimer

This code is for informational and educational purposes only. Use at your own risk.
