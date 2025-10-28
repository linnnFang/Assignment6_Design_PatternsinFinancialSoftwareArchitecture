# command.py

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Any, List

'''
Command: abstract class
Account: a simple portfolio with cash and positions
ExecuteOrderCommand: execute and undo
CommandInvoker: manage the history and redo
'''
class Command(ABC):
    @abstractmethod
    def execute(self) -> Any:
        raise NotImplementedError

    @abstractmethod
    def undo(self) -> Any:
        raise NotImplementedError


class Account:

    def __init__(self, cash: float = 100000.0):
        self.cash = float(cash)
        self.positions: Dict[str, float] = {}

    def apply_trade(self, symbol: str, quantity: float, price: float):
        notional = float(quantity) * float(price)
        # buying reduces cash, selling increases cash
        self.cash -= notional
        self.positions[symbol] = self.positions.get(symbol, 0.0) + float(quantity)

    def revert_trade(self, symbol: str, quantity: float, price: float):
        notional = float(quantity) * float(price)
        self.cash += notional
        self.positions[symbol] = self.positions.get(symbol, 0.0) - float(quantity)
        # clean small positions
        if abs(self.positions.get(symbol, 0.0)) < 1e-8:
            self.positions.pop(symbol, None)

    def __repr__(self):
        return f"<Account cash={self.cash:.2f} positions={self.positions}>"


class ExecuteOrderCommand(Command):
    def __init__(self, account: Account, symbol: str, quantity: float, price: float):
 
        self.account = account
        self.symbol = symbol
        self.quantity = float(quantity)
        self.price = float(price)
        self._executed = False

    def execute(self):
        if self._executed:
            raise RuntimeError("Command already executed")
        self.account.apply_trade(self.symbol, self.quantity, self.price)
        self._executed = True
        return {"status": "executed", "symbol": self.symbol, "quantity": self.quantity, "price": self.price}

    def undo(self):
        if not self._executed:
            raise RuntimeError("Command not executed yet")
        # to undo, reverse the trade
        self.account.revert_trade(self.symbol, self.quantity, self.price)
        self._executed = False
        return {"status": "undone", "symbol": self.symbol, "quantity": self.quantity, "price": self.price}


class CommandInvoker:
    def __init__(self):
        self._history: List[Command] = []
        self._redo_stack: List[Command] = []

    def execute_cmd(self, cmd: Command):
        result = cmd.execute()
        self._history.append(cmd)
        # clear redo stack when new command executed
        self._redo_stack.clear()
        return result

    def undo(self):
        if not self._history:
            raise RuntimeError("Nothing to undo")
        cmd = self._history.pop()
        result = cmd.undo()
        self._redo_stack.append(cmd)
        return result

    def redo(self):
        if not self._redo_stack:
            raise RuntimeError("Nothing to redo")
        cmd = self._redo_stack.pop()
        result = cmd.execute()
        self._history.append(cmd)
        return result
