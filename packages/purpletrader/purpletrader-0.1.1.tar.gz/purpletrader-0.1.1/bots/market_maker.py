from __future__ import annotations

import argparse
import math
import random
import sys
import time
from typing import List

from purpletrader import Order, Timeframe, TradingEngineClient
from purpletrader.types import OrderSide, OrderType

from .utils import RateLimiter, apply_bps, estimate_mid_price, generate_order_id


def run_market_maker(
    base_url: str,
    user_id: str,
    symbols: List[str],
    spread_bps: float,
    quantity: float,
    tick_sec: float,
    jitter_bps: float,
) -> None:
    client = TradingEngineClient(base_url=base_url, user_id=user_id)
    limiter = RateLimiter(min_interval_sec=tick_sec)

    while True:
        for symbol in symbols:
            try:
                mid = estimate_mid_price(client, symbol)
                # Add small random jitter to avoid being static
                mid *= 1.0 + random.uniform(-jitter_bps, jitter_bps) / 10000.0
                bid_px = apply_bps(mid, -abs(spread_bps) / 2.0)
                ask_px = apply_bps(mid, abs(spread_bps) / 2.0)

                buy_order = Order(
                    id=generate_order_id("mm_buy"),
                    userId=None,
                    symbol=symbol,
                    type=OrderType.LIMIT,
                    side=OrderSide.BUY,
                    quantity=quantity,
                    price=round(bid_px, 2),
                )
                sell_order = Order(
                    id=generate_order_id("mm_sell"),
                    userId=None,
                    symbol=symbol,
                    type=OrderType.LIMIT,
                    side=OrderSide.SELL,
                    quantity=quantity,
                    price=round(ask_px, 2),
                )

                client.submit_order(buy_order)
                client.submit_order(sell_order)
                print(f"[{time.strftime('%X')}] {symbol} mm posted bid {buy_order.price} ask {sell_order.price}")
            except Exception as exc:
                print(f"market_maker error for {symbol}: {exc}", file=sys.stderr)

            limiter.wait()


def main() -> None:
    parser = argparse.ArgumentParser(description="Simple market maker bot for purpletrader engine")
    parser.add_argument("--base-url", required=True, help="Engine base URL, e.g. http://host:8080")
    parser.add_argument("--user-id", required=True, help="Trading user id")
    parser.add_argument("--symbol", action="append", required=True, help="Symbol(s) to quote; repeat for multiple")
    parser.add_argument("--spread-bps", type=float, default=10.0, help="Target spread in bps (default 10)")
    parser.add_argument("--qty", type=float, default=1.0, help="Order quantity per side (default 1)")
    parser.add_argument("--tick-sec", type=float, default=1.0, help="Seconds between quote cycles (default 1.0)")
    parser.add_argument("--jitter-bps", type=float, default=2.0, help="Random mid jitter in bps (default 2)")
    args = parser.parse_args()

    run_market_maker(
        base_url=args.base_url,
        user_id=args.user_id,
        symbols=args.symbol,
        spread_bps=args.spread_bps,
        quantity=args.qty,
        tick_sec=args.tick_sec,
        jitter_bps=args.jitter_bps,
    )


if __name__ == "__main__":
    main()


