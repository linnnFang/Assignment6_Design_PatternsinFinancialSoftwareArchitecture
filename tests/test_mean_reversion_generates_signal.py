def test_mean_reversion_generates_signal():
    from patterns.strategy import MeanReversionStrategy
    from models import MarketDataPoint
    from datetime import datetime
    s = MeanReversionStrategy()
    prices = [100, 100, 100, 100, 97]  # now len(dq)=5 when 97 arrives

    out = []
    for p in prices:
        out += s.generate_signals(MarketDataPoint("XYZ",p,datetime.now()))
    assert any(sig["action"]=="BUY" for sig in out)
