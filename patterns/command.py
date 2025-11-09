from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List

class Command(ABC):
    @abstractmethod
    def execute(self) -> Any: ...
    @abstractmethod
    def undo(self) -> Any: ...

class Account:
    def __init__(self, cash: float = 100_000.0):
        self.cash = float(cash)
        self.positions: Dict[str, float] = {}
    def apply_trade(self, symbol: str, quantity: float, price: float):
        notional = float(quantity) * float(price)
        self.cash -= notional
        self.positions[symbol] = self.positions.get(symbol, 0.0) + float(quantity)
    def revert_trade(self, symbol: str, quantity: float, price: float):
        notional = float(quantity) * float(price)
        self.cash += notional
        self.positions[symbol] = self.positions.get(symbol, 0.0) - float(quantity)
        if abs(self.positions.get(symbol, 0.0)) < 1e-8:
            self.positions.pop(symbol, None)
    def __repr__(self):
        return f"<Account cash={self.cash:.2f} positions={self.positions}>"

class ExecuteOrderCommand(Command):
    def __init__(self, account: Account, symbol: str, action: str, quantity: float, price: float, meta: Dict[str, Any] | None = None):
        self.account = account
        self.symbol = symbol
        self.action = action.upper()
        self.quantity = float(quantity)  # positive
        self.price = float(price)
        self.meta = dict(meta or {})
        self._signed_qty = self.quantity if self.action == "BUY" else -self.quantity
        self._executed = False
    def execute(self) -> Dict[str, Any]:
        if self._executed: raise RuntimeError("Command already executed")
        self.account.apply_trade(self.symbol, self._signed_qty, self.price)
        self._executed = True
        return {"status": "executed", "symbol": self.symbol, "action": self.action, "quantity": self.quantity, "price": self.price, "meta": self.meta}
    def undo(self) -> Dict[str, Any]:
        if not self._executed: raise RuntimeError("Command not executed yet")
        self.account.revert_trade(self.symbol, self._signed_qty, self.price)
        self._executed = False
        return {"status": "undone", "symbol": self.symbol, "action": self.action, "quantity": self.quantity, "price": self.price, "meta": self.meta}
    @classmethod
    def from_signal(cls, account: Account, signal: Dict[str, Any]) -> "ExecuteOrderCommand":
        return cls(account, signal["symbol"], signal["action"], signal["size"], signal["price"], signal.get("meta"))

class CommandInvoker:
    def __init__(self):
        self._history: List[Command] = []
        self._redo_stack: List[Command] = []
    def execute_cmd(self, cmd: Command):
        res = cmd.execute(); self._history.append(cmd); self._redo_stack.clear(); return res
    def undo(self):
        if not self._history: raise RuntimeError("Nothing to undo")
        cmd = self._history.pop(); res = cmd.undo(); self._redo_stack.append(cmd); return res
    def redo(self):
        if not self._redo_stack: raise RuntimeError("Nothing to redo")
        cmd = self._redo_stack.pop(); res = cmd.execute(); self._history.append(cmd); return res
