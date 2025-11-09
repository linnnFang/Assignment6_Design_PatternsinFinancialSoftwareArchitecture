# models.py
# composite pattern included

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Protocol
from abc import ABC, abstractmethod
import random
import datetime

         
class MarketDataPoint:
    def __init__(self, symbol: str, price: float, timestamp: datetime):
        self.symbol = symbol
        self.price = price
        self.timestamp = timestamp

    def __repr__(self):
        return f"MarketDataPoint(symbol={self.symbol}, price={self.price}, timestamp={self.timestamp})"

@dataclass
class Instrument:
    symbol: str
    price: float

    def get_metrics(self) -> dict:
        return {"symbol": self.symbol, "price": self.price}


@dataclass
class Stock(Instrument):
    sector: str
    issuer: str


@dataclass
class Bond(Instrument):
    sector: str
    issuer: str
    maturity: str


@dataclass
class ETF(Instrument):
    sector: str
    issuer: str



class PortfolioComponent(ABC):
    @abstractmethod
    def get_value(self) -> float:
        ...

    @abstractmethod
    def get_positions(self) -> Dict[str, float]:
        ...


@dataclass
class Position(PortfolioComponent):
    symbol: str
    quantity: float
    price: float

    def get_value(self) -> float:
        return self.quantity * self.price

    def get_positions(self) -> Dict[str, float]:
        return {self.symbol: self.quantity}


@dataclass
class PortfolioGroup(PortfolioComponent):
    name: str
    components: List[PortfolioComponent] = field(default_factory=list)

    def add(self, component: PortfolioComponent):
        self.components.append(component)

    def get_value(self) -> float:
        return sum(c.get_value() for c in self.components)

    def get_positions(self) -> Dict[str, float]:
        flat: Dict[str, float] = {}
        for comp in self.components:
            for sym, qty in comp.get_positions().items():
                flat[sym] = flat.get(sym, 0.0) + qty
        return flat

    def summary(self, indent: int = 0):
        pad = " " * indent
        print(f"{pad}- PortfolioGroup: {self.name}")
        for comp in self.components:
            if isinstance(comp, PortfolioGroup):
                comp.summary(indent + 2)
            else:
                print(f"{pad}  • {comp.symbol} × {comp.quantity}")




@dataclass
class Portfolio:
    name: str
    owner: str | None = None
    positions: List[Dict[str, Any]] = field(default_factory=list)
    subportfolios: List["Portfolio"] = field(default_factory=list)

    def add_position(self, symbol: str, quantity: float, price: float | None = None):
        self.positions.append({"symbol": symbol, "quantity": quantity, "price": price})

    def add_subportfolio(self, sub: "Portfolio"):
        self.subportfolios.append(sub)

    def get_positions(self) -> Dict[str, float]:
        flat: Dict[str, float] = {}
        for p in self.positions:
            flat[p["symbol"]] = flat.get(p["symbol"], 0.0) + float(p["quantity"])
        for sp in self.subportfolios:
            for sym, qty in sp.get_positions().items():
                flat[sym] = flat.get(sym, 0.0) + qty
        return flat

    def summary(self, indent: int = 0):
        pad = " " * indent
        print(f"{pad}- Portfolio: {self.name} (Owner: {self.owner})")
        for p in self.positions:
            print(f"{pad}  • {p['symbol']} × {p['quantity']}")
        for sp in self.subportfolios:
            sp.summary(indent + 2)

@dataclass
class Order:
    side: str                  # "BUY" | "SELL"
    symbol: str
    quantity: int
    price: float
    timestamp: datetime
    status: str = "NEW"        # "NEW" -> "FILLED"/"REJECTED"

    def validate(self) -> None:
        s = self.side.upper()
        if s not in {"BUY","SELL"}:
            raise OrderError(f"Invalid side: {self.side}")
        if self.quantity <= 0:
            raise OrderError("Quantity must be > 0")
        if self.price <= 0:
            raise OrderError("Price must be > 0")
        if not self.symbol:
            raise OrderError("Symbol is required")
        self.side = s

class MarketDataContainer:
    """
    - Buffer incoming MarketDataPoint instances in a list (self.buffer)
    - Store open positions as {'SYM': {'quantity': int, 'avg_price': float}}
    - Collect signals as a list of tuples (action, symbol, qty, price)
    """
    def __init__(self) -> None:
        self.buffer: List[MarketDataPoint] = []
        self.positions: Dict[str, Dict[str, float]] = {}
        self.signals: List[Tuple[str, str, int, float]] = []

    def buffer_data(self, data_point: MarketDataPoint) -> None:
        self.buffer.append(data_point)

    def last(self) -> Optional[MarketDataPoint]:
        return self.buffer[-1] if self.buffer else None

    def recent(self, n: int):
        return self.buffer[-n:] if n > 0 else []

    def __len__(self) -> int:
        return len(self.buffer)

    def __iter__(self):
        return iter(self.buffer)

    # position
    def _ensure_pos(self, symbol: str) -> Dict[str, float]:
        if symbol not in self.positions:
            self.positions[symbol] = {"quantity": 0, "avg_price": 0.0}
        return self.positions[symbol]

    def apply_fill(self, order: Order) -> None:
        pos = self._ensure_pos(order.symbol)
        q = int(order.quantity)
        px = float(order.price)

        if order.side == "BUY":
            old_q = pos["quantity"]
            new_q = old_q + q
            pos["avg_price"] = (pos["avg_price"] * old_q + px * q) / new_q if new_q > 0 else 0.0
            pos["quantity"] = new_q
        elif order.side == "SELL":
            sell_q = min(q, pos["quantity"])
            pos["quantity"] -= sell_q
            if pos["quantity"] == 0:
                pos["avg_price"] = 0.0

    # signal
    def add_signal(self, action: str, symbol: str, qty: int, price: float) -> None:
        self.signals.append((action, symbol, qty, price))

    def clear_signals(self) -> None:
        self.signals.clear()
