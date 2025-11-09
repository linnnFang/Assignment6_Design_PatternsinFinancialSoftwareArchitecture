# tests/test_analytics.py
import math
import copy
import pytest
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
# absolute imports so pytest can find modules when run from repo root
from analytics import VolatilityDecorator, BetaDecorator, DrawdownDecorator
from models import Instrument

# --- A tiny concrete Instrument for testing ---
class DummyInstrument(Instrument):
    def __init__(self, symbol: str, price: float):
        super().__init__(symbol, price)

    def get_metrics(self) -> dict:
        # base instrument exposes symbol/price only
        return {"symbol": self.symbol, "price": float(self.price)}


@pytest.mark.parametrize("price", [12.34, 100.0, 0.01, 257.889])
def test_single_decorators_add_expected_keys(price):
    base = DummyInstrument("TEST", price)

    m_vol = VolatilityDecorator(base).get_metrics()
    assert "symbol" in m_vol and "price" in m_vol and "volatility" in m_vol
    assert 0.01 <= m_vol["volatility"] <= 0.21  # per formula: (log1p(p) % 0.2) + 0.01

    m_beta = BetaDecorator(base).get_metrics()
    assert "beta" in m_beta
    # beta = 0.8 + ((price % 10) / 50)  ∈ [0.8, 1.0)
    assert 0.8 <= m_beta["beta"] < 1.0

    m_dd = DrawdownDecorator(base).get_metrics()
    assert "max_drawdown" in m_dd
    # drawdown = min(0.5, fractional_part(price))  ∈ [0, 0.5]
    assert 0.0 <= m_dd["max_drawdown"] <= 0.5


@pytest.mark.parametrize("price", [45.67, 123.456, 9.999])
def test_stack_all_three_is_order_insensitive(price):
    base = DummyInstrument("STACK", price)

    # stack 1: Drawdown(Beta(Volatility(base)))
    d1 = DrawdownDecorator(BetaDecorator(VolatilityDecorator(base)))
    m1 = d1.get_metrics()

    # stack 2: Volatility(Beta(Drawdown(base)))
    d2 = VolatilityDecorator(BetaDecorator(DrawdownDecorator(base)))
    m2 = d2.get_metrics()

    # All keys present and values are identical because each decorator
    # derives its metric solely from base metrics["price"]
    assert set(m1.keys()) == {"symbol", "price", "volatility", "beta", "max_drawdown"}
    assert m1 == m2


def test_decorators_do_not_mutate_base_metrics():
    base = DummyInstrument("IMMUT", 77.77)

    # snapshot base metrics
    base_metrics_before = base.get_metrics()
    # apply stacked decorators
    decorated = DrawdownDecorator(BetaDecorator(VolatilityDecorator(base)))
    _ = decorated.get_metrics()

    # base metrics should remain unchanged
    base_metrics_after = base.get_metrics()
    assert base_metrics_after == base_metrics_before == {"symbol": "IMMUT", "price": 77.77}


def test_numeric_formulas_reproduce_expected_values():
    price = 12.34
    base = DummyInstrument("FORM", price)

    # expected per analytics.py formulas
    expected_vol = round((math.log1p(price) % 0.2) + 0.01, 6)
    expected_beta = round(0.8 + ((price % 10) / 50), 6)
    expected_dd = round(min(0.5, price - int(price)), 6)

    m = DrawdownDecorator(BetaDecorator(VolatilityDecorator(base))).get_metrics()
    assert m["volatility"] == expected_vol
    assert m["beta"] == expected_beta
    assert m["max_drawdown"] == expected_dd
