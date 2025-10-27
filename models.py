# models.py
# composite pattern included

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Protocol
from abc import ABC, abstractmethod
import random
import datetime

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

@dataclass(frozen=True, slots=True)
class MarketDataPoint:
    """
    Minimal market data tick.
    - symbol   : ticker
    - timestamp: timezone-aware datetime
    - price    : last price (or mid)
    - source   : data source id (e.g., 'Yahoo', 'Bloomberg')
    """
    symbol: str
    timestamp: datetime
    price: float
    source: str

    def as_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp.isoformat(),
            "price": self.price,
            "source": self.source,
        }

def parse_ts(ts: str) -> datetime:
    """Parse ISO8601 with possible trailing 'Z' into aware UTC datetime."""
    # Handle 'Z' suffix for UTC
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    dt = datetime.fromisoformat(ts)
    # Ensure timezone-aware (if input lacked offset)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt