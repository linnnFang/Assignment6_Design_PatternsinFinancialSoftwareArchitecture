from analytics import *
def test_decorators_stack():
    class Bare:  # 无指标底类
        def get_metrics(self): return {}
    base = Bare()
    dec = DrawdownDecorator(BetaDecorator(VolatilityDecorator(base, [0.01, -0.02], [0.0, 0.0]),
                                          [0.01, -0.02], [0.0, 0.0]),
                            [0.01, -0.02])
    m = dec.get_metrics()
    assert "volatility" in m and "beta" in m and "max_drawdown" in m