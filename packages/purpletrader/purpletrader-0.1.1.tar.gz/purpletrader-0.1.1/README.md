# purpletrader

A lightweight Python client for the Live Trading Engine HTTP API.

## Installation

```bash
pip install purpletrader
```

## Usage

```python
from purpletrader import TradingEngineClient, Order, Timeframe

# Optionally set a default user_id so you don't have to provide it per order
client = TradingEngineClient(base_url="http://localhost:8080", user_id="trader_123")

# Submit order
resp = client.submit_order(Order(
    id="order_001",
    symbol="AAPL",
    type="LIMIT",
    side="BUY",
    quantity=100,
    price=150.25,
))
print(resp)

# Fetch data
print(client.get_orderbook("AAPL"))
print(client.get_stats("AAPL"))
print(client.get_stats_timeframe("AAPL", Timeframe.ONE_MINUTE))
print(client.get_all_stats())
print(client.get_stats_summary())
print(client.get_leaderboard())
print(client.health())
```

## Example Bots (for quick engine testing)

This repo also includes simple example bots under `bots/` to exercise the live trading engine:

- Market maker: continuously quotes around mid.
- Momentum: buys breakouts, sells breakdowns.
- Random: sends random buy/sell orders.

Each bot is a CLI that targets one or more symbols and a user id. They use the `purpletrader` client to interact with the engine's HTTP API.

Quick start:

```bash
# Set the engine base URL (adjust host/port for your deployment)
export ENGINE_URL="http://localhost:8080"

# Market maker on AAPL, user trader_mm
python -m bots.market_maker --base-url "$ENGINE_URL" --user-id trader_mm --symbol AAPL \
  --spread-bps 5 --qty 10 --tick-sec 1.0

# Momentum on AAPL, user trader_momo
python -m bots.momentum --base-url "$ENGINE_URL" --user-id trader_momo --symbol AAPL \
  --lookback 20 --threshold-bps 10 --qty 5 --tick-sec 1.0

# Random bot on AAPL and MSFT
python -m bots.random_bot --base-url "$ENGINE_URL" --user-id trader_rand --symbol AAPL --symbol MSFT \
  --qty-min 1 --qty-max 20 --tick-sec 0.5

# Run multiple bots concurrently from a config file
python -m bots.runner --base-url "$ENGINE_URL" --config bots/examples/bots.yaml
```

### HPC/Slurm example

See `bots/examples/slurm_job.sbatch` for a minimal Slurm job that launches two bots. Submit via:

```bash
sbatch bots/examples/slurm_job.sbatch
```

## Notes
- Raises `HTTPError` on non-2xx responses with `status_code`, `message`, and `body`.
- Default timeout is 30s; override via `TradingEngineClient(timeout=...)`.
- You can still override `userId` per order by passing it in the `Order`.
