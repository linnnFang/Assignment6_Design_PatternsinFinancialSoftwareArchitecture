
from __future__ import annotations
from patterns.singleton import Config
from typing import Iterable, List, Dict, Tuple
import random

from models import *
from patterns.strategy import  *
from patterns.command import *

'''
class TradingEngine:
    def __init__(self, cfg: Config):   # cfg is a singleton instance
        self.cfg = cfg
        self.level = self.cfg.get("log_level") or "INFO"

    def run(self):
        print("[Engine] run() called. (Temporarily not connected to portfolio and market_data))")
        print(f"Running engine (log level: {self.level})")
        print(f"Using default strategy: {self.cfg.get('default_strategy')}")
        print(f"Engine using data: {self.cfg.get('data_path')}")
        print("Engine run completed.")

'''


''' engine = TradingEngine(data_iter, strats, publisher,portfolio, executor, container)'''

class TradingEngine:
    """
    Ticks -> signals -> orders -> fills -> positions, with resilient logging.
    input: strategies lists
    """
    def __init__(self, data_iter, strategies, publisher,  executor, portfolio_sink):
        self.data_iter = data_iter               # iterable[MarketDataPoint]
        self.strategies = strategies             # list[Strategy]
        self.publisher = publisher               # SignalPublisher
        self.executor = executor                 # wraps CommandInvoker+Account
        self.portfolio_sink = portfolio_sink     # MarketDataContainer or Portfolio



    # ---- lifecycle ----
    def on_tick(self, tick: MarketDataPoint) -> None:
        self.container.buffer_data(tick)

        for strat in self.strategies:
            try:
                signals = strat.generate_signals(tick) or []

                if not signals: continue

                orders = self._create_orders(signals, tick)
                for order in orders:
                    try:
                        self._execute(order)
                    except Exception as ex:
                        order.status = "REJECTED"
                        self.error_log.append(f"{tick.timestamp} {order.symbol} {order.side} x{order.quantity}: EXECUTION ERROR: {ex}")
                    finally:
                        self.order_log.append(order)
            except Exception as ex:
                self.error_log.append(f"{tick.timestamp} Strategy {type(strat).__name__} error: {ex}")

    def run(self, market: Iterable[MarketDataPoint]) -> None:
        print("[Engine] run() called. (Temporarily not connected to portfolio and market_data))")
        for tick in sorted(market, key=lambda t: t.timestamp):
            self.on_tick(tick)

    def report(self) -> Dict:
        return {
            "positions": {k: v.copy() for k, v in self.container.positions.items()},
            "orders": [{
                "time": o.timestamp.isoformat(),
                "symbol": o.symbol,
                "side": o.side,
                "qty": o.quantity,
                "price": o.price,
                "status": o.status
            } for o in self.order_log],
            "errors": list(self.error_log),
        }

    # ---- helpers ----
    def _create_orders(self, signals: List[Tuple], tick: MarketDataPoint) -> List[Order]:
        orders: List[Order] = []
        for s in signals:
            if len(s) == 3:
                side, symbol, qty = s
                price = float(tick.price)
            elif len(s) == 4:
                side, symbol, qty, price = s
            else:
                raise OrderError(f"Bad signal shape: {s}")
            o = Order(side=str(side).upper(), symbol=symbol, quantity=int(qty), price=float(price), timestamp=tick.timestamp)
            o.validate()
            orders.append(o)
        return orders

    def _execute(self, order: Order) -> None:
        # Simulate flaky fills 3% of the time
        if random.random() < 0.03:
            raise ExecutionError("Simulated venue outage")
        # Fill at provided price
        order.status = "FILLED"
        # apply to positions (quantity + avg_price schema)
        self.container.apply_fill(order)
