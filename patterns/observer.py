# observer.py

from __future__ import annotations
from typing import List, Dict, Any, Protocol


class Observer(Protocol):
    def update(self, signal: Dict[str, Any]) -> None:
        ...


class SignalPublisher:
    def __init__(self):
        self._observers: List[Observer] = []

    def attach(self, obs: Observer):
        self._observers.append(obs)

    def detach(self, obs: Observer):
        self._observers = [o for o in self._observers if o is not obs]

    def notify(self, signal: Dict[str, Any]):
        for o in list(self._observers):
            try:
                o.update(signal)
            except Exception as e:
                # swallow observer exceptions to avoid breaking the publish flow
                print(f"[SignalPublisher] Observer {o} raised error: {e}")


class LoggerObserver:
    def __init__(self, prefix: str = "[Logger]"):
        self.prefix = prefix

    def update(self, signal: Dict[str, Any]) -> None:
        print(f"{self.prefix} Signal received: {signal}")


class AlertObserver:
    def __init__(self, threshold: float = 10000.0):
        self.threshold = threshold

    def update(self, signal: Dict[str, Any]) -> None:
        size = float(signal.get("size", 0.0))
        price = float(signal.get("price", 0.0))
        notional = size * price
        if notional >= self.threshold:
            print(f"[ALERT] Large trade detected: {signal} (notional={notional})")
