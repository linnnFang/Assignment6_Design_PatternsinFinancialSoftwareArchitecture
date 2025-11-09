"""
from __future__ import annotations
from patterns.singleton import Config
from typing import Iterable, List, Dict, Tuple
import random

from models import *
from patterns.strategy import  *
from patterns.command import *




''' 
engine = TradingEngine(data_iter, strats, publisher,portfolio, executor, container)'''

class TradingEngine:
    
    Ticks -> signals -> orders -> fills -> positions, with resilient logging.
    input: strategies lists

    def __init__(self, data_iter, strategies, publisher, portfolio, account, portfolio_sink):
        self.data_iter = data_iter               # iterable[MarketDataPoint]
        self.strategies = strategies             # list[Strategy]
        self.publisher = publisher                  # SignalPublisher
        self.portfolio = portfolio             
        self.account   = account                # wraps CommandInvoker+Account
        self.portfolio_sink = portfolio_sink     # MarketDataContainer or Portfolio


    
    def run(self):
        '''1. load data from data iter'''
        dataset = MarketDataContainer()
        for data in self.data_iter:
            dataset.buffer_data(data)
        
        ''' 2. generate signals'''
        invoker = CommandInvoker()
        signals = {}
        for strat in self.strategies:
                signals[strat.__name__] = [strat.generate_signals(tick for tick in dataset)]
                for signal in signals[strat.__name__]:
                    cmd = ExecuteOrderCommand(self.account, signal)
                    invoker.execute_cmd(cmd)

                     

        ''' 3. update accounts'''

        return signals"""

from __future__ import annotations
from typing import Iterable, Dict, Any, List, Callable
from models import MarketDataPoint
from patterns.command import Account, ExecuteOrderCommand, CommandInvoker
from patterns.observer import SignalPublisher
from patterns.strategy import Strategy

class OrderRouter:
    def route(self, signal: Dict[str, Any]):
        return signal  # identity: we use signal fields directly

class BasicRisk:
    def __init__(self, positions: Dict[str, float], max_pos=1000, max_order=500):
        self.positions = positions; self.max_pos=max_pos; self.max_order=max_order
    def approve(self, signal: Dict[str, Any]) -> Dict[str, Any] | None:
        qty = float(signal["size"])
        if qty <= 0 or qty > self.max_order: return None
        sym = signal["symbol"]; side = signal["action"].upper()
        curr = self.positions.get(sym, 0.0)
        proj = curr + (qty if side=="BUY" else -qty)
        if abs(proj) > self.max_pos: return None
        return signal

class TradingEngine:
    def __init__(self, data: Iterable[MarketDataPoint], strategies: List[Strategy],
                 publisher: SignalPublisher, router: OrderRouter,
                 risk: BasicRisk, account: Account, invoker: CommandInvoker,
                 on_fill: Callable[[Dict[str, Any]], None] | None = None):
        self.data = data; self.strategies = strategies; self.publisher = publisher
        self.router = router; self.risk = risk; self.account = account; self.invoker = invoker
        self.on_fill = on_fill

    def run(self):
        for tick in self.data:                      # ← one pass over data
            for strat in self.strategies:          # ← BOTH strategies per tick
                for sig in strat.generate_signals(tick):
                    self.publisher.notify(sig)      # observers
                    order_like = self.router.route(sig)
                    approved = self.risk.approve(order_like)
                    if not approved: continue
                    cmd = ExecuteOrderCommand.from_signal(self.account, approved)
                    res = self.invoker.execute_cmd(cmd)
                    if self.on_fill: self.on_fill(res)
