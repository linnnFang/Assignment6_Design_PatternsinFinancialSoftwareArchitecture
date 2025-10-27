# analytics.py
# decorators pattern included

from __future__ import annotations
from typing import Dict, Any
from models import Instrument
import math


class InstrumentDecorator(Instrument):
    def __init__(self, instrument: Instrument):
        super().__init__(instrument.symbol, instrument.price)
        self._instrument = instrument

    def get_metrics(self) -> Dict[str, Any]:
        return self._instrument.get_metrics()


class VolatilityDecorator(InstrumentDecorator):
    def get_metrics(self) -> Dict[str, Any]:
        metrics = super().get_metrics()
        price = float(metrics.get("price", 0.0))
        vol = (math.log1p(price) % 0.2) + 0.01  # deterministic small number
        metrics["volatility"] = round(vol, 6)
        return metrics


class BetaDecorator(InstrumentDecorator):
    def get_metrics(self) -> Dict[str, Any]:
        metrics = super().get_metrics()
        price = float(metrics.get("price", 0.0))
        beta = 0.8 + ((price % 10) / 50)  # deterministic function of price
        metrics["beta"] = round(beta, 6)
        return metrics


class DrawdownDecorator(InstrumentDecorator):
    def get_metrics(self) -> Dict[str, Any]:
        metrics = super().get_metrics()
        price = float(metrics.get("price", 0.0))
        frac = price - float(int(price))
        drawdown = min(0.5, frac)  # between 0 and 0.999..., cap 0.5
        metrics["max_drawdown"] = round(drawdown, 6)
        return metrics
