"""
# reporting.py
print(">>> REPORTING FILE USED:", __file__)

from patterns.singleton import Config

class Logger:
    def __init__(self):
        self.cfg = Config()  # ✅ automatic singleton access
        self.level = self.cfg.get("log_level") or "INFO"

    def log_summary(self):
        print(f"Final report using log level: {self.level}")
        print(f"Reports will be saved to: {self.cfg.get('report_path')}")
        print("Reporting completed.")
"""

from __future__ import annotations
from typing import Protocol, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime

# -------- Publisher / Observer interfaces ----------
class Observer(Protocol):
    def update(self, signal: Dict[str, Any]) -> None: ...

class SignalPublisher:
    """Simple publisher that notifies attached observers with a signal dict."""
    def __init__(self) -> None:
        self._observers: List[Observer] = []

    def attach(self, obs: Observer) -> None:
        if obs not in self._observers:
            self._observers.append(obs)

    def detach(self, obs: Observer) -> None:
        if obs in self._observers:
            self._observers.remove(obs)

    def notify(self, signal: Dict[str, Any]) -> None:
        for obs in list(self._observers):
            obs.update(signal)

# -------- Concrete observers ----------
@dataclass
class LoggerObserver:
    """Prints signals (or route to std logging if you prefer)."""
    prefix: str = "[SIGNAL]"
    def update(self, signal: Dict[str, Any]) -> None:
        ts = signal.get("timestamp") or datetime.utcnow().isoformat()
        print(f"{self.prefix} {ts} {signal}")

@dataclass
class MetricsObserver:
    """Keeps simple analytics counters over signals."""
    count: int = 0
    by_action: Dict[str, int] = field(default_factory=dict)
    last_signal: Dict[str, Any] | None = None

    def update(self, signal: Dict[str, Any]) -> None:
        self.count += 1
        act = str(signal.get("action", "UNKNOWN")).upper()
        self.by_action[act] = self.by_action.get(act, 0) + 1
        self.last_signal = signal

    def snapshot(self) -> Dict[str, Any]:
        return {"count": self.count, "by_action": dict(self.by_action), "last": self.last_signal}
