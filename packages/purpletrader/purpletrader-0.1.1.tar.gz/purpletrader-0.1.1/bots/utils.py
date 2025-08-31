from __future__ import annotations

import random
import string
import time
from dataclasses import dataclass
from typing import Iterable, List, Tuple

from purpletrader import TradingEngineClient


def generate_order_id(prefix: str = "order") -> str:
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"{prefix}_{suffix}_{int(time.time() * 1000)}"


def estimate_mid_price(client: TradingEngineClient, symbol: str, fallback: float = 100.0) -> float:
    try:
        ob = client.get_orderbook(symbol)
        best_bid = ob.get("best_bid")
        best_ask = ob.get("best_ask")
        if best_bid is not None and best_ask is not None and best_ask >= best_bid:
            return (best_bid + best_ask) / 2.0
        # If orderbook present, try top of book arrays
        bids = ob.get("bids") or []
        asks = ob.get("asks") or []
        if bids and asks:
            try:
                return (float(bids[0]["price"]) + float(asks[0]["price"])) / 2.0
            except Exception:
                pass
    except Exception:
        pass
    # As a final fallback, try stats summary if available
    try:
        stats = client.get_stats(symbol)
        last_trade_price = stats.get("data", {}).get("last_trade_price") or stats.get("last_trade_price")
        if last_trade_price is not None:
            return float(last_trade_price)
    except Exception:
        pass
    return float(fallback)


def apply_bps(price: float, bps: float) -> float:
    return price * (1.0 + bps / 10000.0)


def chunk(iterable: Iterable[str], size: int) -> List[List[str]]:
    buf: List[str] = []
    out: List[List[str]] = []
    for item in iterable:
        buf.append(item)
        if len(buf) >= size:
            out.append(buf)
            buf = []
    if buf:
        out.append(buf)
    return out


@dataclass
class RateLimiter:
    min_interval_sec: float
    last_ts: float = 0.0

    def wait(self) -> None:
        now = time.time()
        delta = now - self.last_ts
        if delta < self.min_interval_sec:
            time.sleep(self.min_interval_sec - delta)
        self.last_ts = time.time()


