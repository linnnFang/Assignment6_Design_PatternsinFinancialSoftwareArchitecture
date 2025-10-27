# factory.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models import Stock, Bond, ETF, Instrument

class InstrumentFactory:
    @staticmethod
    def create_instrument(data: dict) -> Instrument:
        t = (data.get("type") or "").strip().lower()
        symbol = data["symbol"]
        price = float(data["price"])
        sector = data.get("sector", "")
        issuer = data.get("issuer", "")
        maturity = data.get("maturity", "")

        if t == "stock":
            return Stock(symbol, price, sector, issuer)
        elif t == "bond":
            return Bond(symbol, price, sector, issuer, maturity)
        elif t == "etf":
            return ETF(symbol, price, sector, issuer)
        else:
            raise ValueError(f"Unknown instrument type: {t}")

