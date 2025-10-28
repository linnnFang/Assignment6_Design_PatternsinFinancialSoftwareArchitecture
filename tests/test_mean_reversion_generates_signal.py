def test_mean_reversion_generates_signal():
    from patterns.strategy import MeanReversionStrategy
    from models import MarketDataPoint
    from datetime import datetime
    s = MeanReversionStrategy(lookback=3, thresh=1.0)
    prices = [100, 100, 100, 97]  # 低于均值
    out = []
    for p in prices:
        out += s.generate_signals(MarketDataPoint("XYZ", datetime.now(), p))
    assert any(sig["action"]=="BUY" for sig in out)
