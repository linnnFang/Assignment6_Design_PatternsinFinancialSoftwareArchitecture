from datetime import datetime, timezone, timedelta
from models import MarketDataPoint
from patterns.strategy import MeanReversionStrategy, BreakoutStrategy

def mk(symbol, price, t=0):
    return MarketDataPoint(symbol, price, datetime(2025,1,1,9,30,t, tzinfo=timezone.utc))

def test_mean_reversion_emits_buy_sell():
    s = MeanReversionStrategy(window=4, threshold=0.02, size=10)
    # prices around 100; dip to trigger BUY; pop to trigger SELL
    stream = [mk("AAPL", p) for p in (100, 100, 98, 101, 103)]
    out = []
    for tick in stream: out += s.generate_signals(tick)
    acts = [o["action"] for o in out]
    assert "BUY" in acts or "SELL" in acts

def test_breakout_triggers_on_new_high_low():
    b = BreakoutStrategy(window=3, size=5)
    ticks = [mk("MSFT", p, i) for i,p in enumerate((100,101,102,103,  99,98,97))]
    res = []
    for t in ticks:
        res += b.generate_signals(t)
    assert any(x["action"]=="BUY" for x in res) or any(x["action"]=="SELL" for x in res)
