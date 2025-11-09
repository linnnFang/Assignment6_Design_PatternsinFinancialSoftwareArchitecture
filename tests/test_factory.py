# tests/test_factory.py

import pytest
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
# absolute imports so pytest finds modules when run from repo root
from patterns.factory import InstrumentFactory
from models import Stock, Bond, ETF

def test_create_stock_basic():
    row = {
        "type": "stock",
        "symbol": "AAPL",
        "price": "189.12",   # str is fine; factory casts to float
        "sector": "Technology",
        "issuer": "Apple Inc."
    }
    inst = InstrumentFactory.create_instrument(row)
    assert isinstance(inst, Stock)
    assert inst.symbol == "AAPL"
    assert inst.price == pytest.approx(189.12)
    # if your Stock dataclass fields are (symbol, price, sector, issuer)
    assert getattr(inst, "sector", None) == "Technology"
    assert getattr(inst, "issuer", None) == "Apple Inc."

def test_create_bond_with_maturity():
    row = {
        "type": "bond",
        "symbol": "US10Y",
        "price": 99.75,
        "sector": "Government",
        "issuer": "UST",
        "maturity": "2034-11-15",
    }
    inst = InstrumentFactory.create_instrument(row)
    assert isinstance(inst, Bond)
    assert inst.symbol == "US10Y"
    assert inst.price == pytest.approx(99.75)
    assert getattr(inst, "maturity", None) == "2034-11-15"

def test_create_etf_case_insensitive_type():
    row = {
        "type": "ETF",  # factory lower() handles case-insensitive
        "symbol": "SPY",
        "price": 500.0,
        "sector": "Index",
        "issuer": "State Street",
    }
    inst = InstrumentFactory.create_instrument(row)
    assert isinstance(inst, ETF)
    assert inst.symbol == "SPY"
    assert inst.price == pytest.approx(500.0)
    assert getattr(inst, "issuer", None) == "State Street"

def test_unknown_type_raises():
    row = {"type": "crypto", "symbol": "BTC", "price": 65000}
    with pytest.raises(ValueError):
        InstrumentFactory.create_instrument(row)

def test_missing_type_raises():
    row = {"symbol": "ABC", "price": 10.0}
    with pytest.raises(ValueError):
        InstrumentFactory.create_instrument(row)

def test_price_must_be_numeric_like():
    # non-numeric price should raise when float(...) is attempted
    row = {"type": "stock", "symbol": "XYZ", "price": "abc"}
    with pytest.raises(ValueError):
        InstrumentFactory.create_instrument(row)
