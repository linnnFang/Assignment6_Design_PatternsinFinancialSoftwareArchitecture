import pytest
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from patterns.factory import InstrumentFactory
from patterns.singleton import Config
from patterns.builder import PortfolioBuilder
from patterns.strategy import MeanReversionStrategy, BreakoutStrategy
from patterns.observer import SignalPublisher, LoggerObserver
from patterns.command import ExecuteOrderCommand, CommandInvoker
from analytics import VolatilityDecorator, BetaDecorator, DrawdownDecorator

# tests/test_reporting.py
from reporting import SignalPublisher, LoggerObserver, MetricsObserver

def test_observer_flow(capsys):
    pub = SignalPublisher()
    log = LoggerObserver(prefix="[T]")
    met = MetricsObserver()
    pub.attach(log); pub.attach(met)

    sig = {"action":"BUY","symbol":"AAPL","size":10}
    pub.notify(sig)

    # Logger wrote something
    out = capsys.readouterr().out
    assert "[T]" in out and "AAPL" in out

    # Metrics counted it
    snap = met.snapshot()
    assert snap["count"] == 1
    assert snap["by_action"]["BUY"] == 1
