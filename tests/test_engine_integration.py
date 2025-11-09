import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from patterns.observer import SignalPublisher
from patterns.strategy import MeanReversionStrategy
from patterns.command import Account, CommandInvoker
from engine import TradingEngine, OrderRouter, BasicRisk
from models import MarketDataPoint
from datetime import datetime, timezone

def test_engine_one_trade(monkeypatch):
    # Data: two prices to cross the lower band
    ticks = [
        MarketDataPoint("AAPL", 100.0, datetime(2025,1,1,9,30,0,tzinfo=timezone.utc)),
        MarketDataPoint("AAPL", 95.0,  datetime(2025,1,1,9,30,1,tzinfo=timezone.utc)),
    ]
    strat = MeanReversionStrategy(window=2, threshold=0.02, size=10)
    pub = SignalPublisher()
    acct = Account(100_000)
    inv = CommandInvoker()
    eng = TradingEngine(
        data=ticks,
        strategies=[strat],
        publisher=pub,
        router=OrderRouter(),
        risk=BasicRisk(positions=acct.positions, max_pos=1_000, max_order=500),
        account=acct,
        invoker=inv,
    )
    eng.run()
    assert acct.positions.get("AAPL", 0.0) != 0.0
