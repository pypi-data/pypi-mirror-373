from __future__ import annotations

import argparse
import collections
import statistics
import sys
import time
from typing import Deque, List

from purpletrader import Order, TradingEngineClient
from purpletrader.types import OrderSide, OrderType

from .utils import RateLimiter, apply_bps, estimate_mid_price, generate_order_id


def run_momentum(
    base_url: str,
    user_id: str,
    symbols: List[str],
    lookback: int,
    threshold_bps: float,
    quantity: float,
    tick_sec: float,
) -> None:
    client = TradingEngineClient(base_url=base_url, user_id=user_id)
    limiter = RateLimiter(min_interval_sec=tick_sec)

    price_hist: dict[str, Deque[float]] = {s: collections.deque(maxlen=max(lookback, 2)) for s in symbols}

    while True:
        for symbol in symbols:
            try:
                mid = estimate_mid_price(client, symbol)
                dq = price_hist[symbol]
                dq.append(mid)
                if len(dq) < lookback:
                    continue
                old = dq[0]
                change_bps = (mid / old - 1.0) * 10000.0

                if change_bps >= threshold_bps:
                    # breakout up -> buy at slightly above mid
                    px = apply_bps(mid, +2)
                    order = Order(
                        id=generate_order_id("momo_buy"),
                        userId=None,
                        symbol=symbol,
                        type=OrderType.MARKET,
                        side=OrderSide.BUY,
                        quantity=quantity,
                        price=None,
                    )
                    client.submit_order(order)
                    print(f"[{time.strftime('%X')}] {symbol} momentum BUY lookback {lookback}Δ={change_bps:.1f}bps")
                elif change_bps <= -threshold_bps:
                    # breakdown -> sell market
                    order = Order(
                        id=generate_order_id("momo_sell"),
                        userId=None,
                        symbol=symbol,
                        type=OrderType.MARKET,
                        side=OrderSide.SELL,
                        quantity=quantity,
                        price=None,
                    )
                    client.submit_order(order)
                    print(f"[{time.strftime('%X')}] {symbol} momentum SELL lookback {lookback}Δ={change_bps:.1f}bps")
            except Exception as exc:
                print(f"momentum error for {symbol}: {exc}", file=sys.stderr)

            limiter.wait()


def main() -> None:
    parser = argparse.ArgumentParser(description="Simple momentum bot for purpletrader engine")
    parser.add_argument("--base-url", required=True, help="Engine base URL, e.g. http://host:8080")
    parser.add_argument("--user-id", required=True, help="Trading user id")
    parser.add_argument("--symbol", action="append", required=True, help="Symbol(s) to trade; repeat for multiple")
    parser.add_argument("--lookback", type=int, default=20, help="Lookback window length (default 20)")
    parser.add_argument("--threshold-bps", type=float, default=10.0, help="Momentum trigger threshold in bps (default 10)")
    parser.add_argument("--qty", type=float, default=1.0, help="Order quantity (default 1)")
    parser.add_argument("--tick-sec", type=float, default=1.0, help="Seconds between cycles (default 1.0)")
    args = parser.parse_args()

    run_momentum(
        base_url=args.base_url,
        user_id=args.user_id,
        symbols=args.symbol,
        lookback=args.lookback,
        threshold_bps=args.threshold_bps,
        quantity=args.qty,
        tick_sec=args.tick_sec,
    )


if __name__ == "__main__":
    main()


