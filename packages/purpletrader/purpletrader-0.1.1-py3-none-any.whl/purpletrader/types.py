from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict


class Timeframe(str, Enum):
    ONE_MINUTE = "1m"
    ONE_HOUR = "1h"
    ONE_DAY = "1d"


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    STOP = "STOP"


@dataclass
class Order:
    id: str
    userId: Optional[str]
    symbol: str
    type: OrderType
    side: OrderSide
    quantity: float
    price: Optional[float] = None

    def to_payload(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "id": self.id,
            "symbol": self.symbol,
            "type": self.type.value if isinstance(self.type, OrderType) else self.type,
            "side": self.side.value if isinstance(self.side, OrderSide) else self.side,
            "quantity": self.quantity,
        }
        if self.userId is not None:
            payload["userId"] = self.userId
        if self.price is not None:
            payload["price"] = self.price
        return payload


class LeaderboardPosition(TypedDict, total=False):
    rank: int
    user_id: str
    net_worth: float
    cash_balance: float
    portfolio_value: float
    realized_pnl: float
    positions: List[Dict[str, Any]]


JsonDict = Dict[str, Any]


