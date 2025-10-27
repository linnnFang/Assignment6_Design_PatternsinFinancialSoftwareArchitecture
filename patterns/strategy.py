# strategy.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from collections import deque, defaultdict
from dataclasses import dataclass


@dataclass
class Signal:
    symbol: str
    action: str  # "BUY" or "SELL" or "HOLD"
    size: float
    price: float
    meta: Dict[str, Any] = None

    def as_dict(self) -> Dict[str, Any]:
        return {"symbol": self.symbol, "action": self.action, "size": self.size, "price": self.price, "meta": self.meta or {}}


class Strategy(ABC):
    @abstractmethod
    def generate_signals(self, tick: Any) -> List[Dict[str, Any]]:
        raise NotImplementedError


class MeanReversionStrategy(Strategy):

    def __init__(self, window: int = 20, threshold: float = 0.02, size: float = 10.0):
        self.window = window
        self.threshold = threshold
        self.size = size
        self._prices = defaultdict(lambda: deque(maxlen=self.window))

    def generate_signals(self, tick: Any) -> List[Dict[str, Any]]:
        sym = getattr(tick, "symbol", None) or tick.get("symbol")
        price = float(getattr(tick, "price", None) or tick.get("price"))
        dq = self._prices[sym]
        dq.append(price)
        signals = []

        if len(dq) >= max(2, int(self.window / 4)):  # wait for some data
            mean = sum(dq) / len(dq)
            if price < mean * (1 - self.threshold):
                signals.append(Signal(sym, "BUY", self.size, price, {"mean": mean}).as_dict())
            elif price > mean * (1 + self.threshold):
                signals.append(Signal(sym, "SELL", self.size, price, {"mean": mean}).as_dict())
            else:
                # optionally produce HOLD; we will not output HOLD signals to keep noise low
                pass
        return signals


class BreakoutStrategy(Strategy):

    def __init__(self, window: int = 20, size: float = 10.0):
        self.window = window
        self.size = size
        self._prices = defaultdict(lambda: deque(maxlen=self.window))

    def generate_signals(self, tick: Any) -> List[Dict[str, Any]]:
        sym = getattr(tick, "symbol", None) or tick.get("symbol")
        price = float(getattr(tick, "price", None) or tick.get("price"))
        dq = self._prices[sym]
        dq.append(price)
        signals = []
        if len(dq) >= self.window:
            rolling_high = max(dq)
            rolling_low = min(dq)
            if price > rolling_high:
                signals.append(Signal(sym, "BUY", self.size, price, {"rolling_high": rolling_high}).as_dict())
            elif price < rolling_low:
                signals.append(Signal(sym, "SELL", self.size, price, {"rolling_low": rolling_low}).as_dict())
        return signals
