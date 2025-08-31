from __future__ import annotations

import argparse
import random
import sys
import time
from typing import List

from purpletrader import Order, TradingEngineClient
from purpletrader.types import OrderSide, OrderType

from .utils import RateLimiter, estimate_mid_price, generate_order_id


def run_random(
    base_url: str,
    user_id: str,
    symbols: List[str],
    qty_min: float,
    qty_max: float,
    tick_sec: float,
    market_prob: float,
    limit_bps_range: float,
) -> None:
    client = TradingEngineClient(base_url=base_url, user_id=user_id)
    limiter = RateLimiter(min_interval_sec=tick_sec)

    while True:
        for symbol in symbols:
            try:
                side = OrderSide.BUY if random.random() < 0.5 else OrderSide.SELL
                quantity = round(random.uniform(qty_min, qty_max), 4)
                is_market = random.random() < market_prob
                if is_market:
                    order = Order(
                        id=generate_order_id("rand_mkt"),
                        userId=None,
                        symbol=symbol,
                        type=OrderType.MARKET,
                        side=side,
                        quantity=quantity,
                        price=None,
                    )
                else:
                    mid = estimate_mid_price(client, symbol)
                    # place a random limit around mid
                    bps = random.uniform(-limit_bps_range, limit_bps_range)
                    px = mid * (1.0 + bps / 10000.0)
                    order = Order(
                        id=generate_order_id("rand_lim"),
                        userId=None,
                        symbol=symbol,
                        type=OrderType.LIMIT,
                        side=side,
                        quantity=quantity,
                        price=round(px, 2),
                    )
                client.submit_order(order)
                print(f"[{time.strftime('%X')}] {symbol} random {order.type} {order.side} qty={quantity}")
            except Exception as exc:
                print(f"random bot error for {symbol}: {exc}", file=sys.stderr)

            limiter.wait()


def main() -> None:
    parser = argparse.ArgumentParser(description="Random order flow bot for purpletrader engine")
    parser.add_argument("--base-url", required=True, help="Engine base URL, e.g. http://host:8080")
    parser.add_argument("--user-id", required=True, help="Trading user id")
    parser.add_argument("--symbol", action="append", required=True, help="Symbol(s) to trade; repeat for multiple")
    parser.add_argument("--qty-min", type=float, default=1.0, help="Minimum order quantity (default 1.0)")
    parser.add_argument("--qty-max", type=float, default=10.0, help="Maximum order quantity (default 10.0)")
    parser.add_argument("--tick-sec", type=float, default=0.5, help="Seconds between orders per symbol (default 0.5)")
    parser.add_argument("--market-prob", type=float, default=0.5, help="Probability to use MARKET order (default 0.5)")
    parser.add_argument("--limit-bps-range", type=float, default=20.0, help="If LIMIT, random bps offset around mid (default +/-20 bps)")
    args = parser.parse_args()

    run_random(
        base_url=args.base_url,
        user_id=args.user_id,
        symbols=args.symbol,
        qty_min=args.qty_min,
        qty_max=args.qty_max,
        tick_sec=args.tick_sec,
        market_prob=args.market_prob,
        limit_bps_range=args.limit_bps_range,
    )


if __name__ == "__main__":
    main()


