# tests/test_command.py

import pytest
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from patterns.command import Account, ExecuteOrderCommand, CommandInvoker

def test_execute_buy_updates_cash_and_position():
    acct = Account(cash=100_000.0)
    cmd = ExecuteOrderCommand(acct, "AAPL", "BUY", 10, 150.0)
    res = cmd.execute()

    assert res["status"] == "executed"
    # cash down by 1500, position +10
    assert acct.cash == pytest.approx(100_000.0 - 1500.0)
    assert acct.positions["AAPL"] == pytest.approx(10.0)

def test_execute_sell_uses_signed_qty_and_increases_cash():
    acct = Account(cash=100_000.0)
    # seed a position first
    ExecuteOrderCommand(acct, "AAPL", "BUY", 10, 100.0).execute()
    # now sell 4 @ 120
    cmd = ExecuteOrderCommand(acct, "AAPL", "SELL", 4, 120.0)
    cmd.execute()

    # cash: 100k - 100*10 + 120*4
    assert acct.cash == pytest.approx(100_000.0 - 1000.0 + 480.0)
    # position reduced to 6
    assert acct.positions["AAPL"] == pytest.approx(6.0)

def test_undo_reverts_state_and_redo_restores_it():
    acct = Account(100_000.0)
    inv = CommandInvoker()
    cmd = ExecuteOrderCommand(acct, "MSFT", "BUY", 5, 200.0)

    inv.execute_cmd(cmd)
    cash_after = acct.cash
    pos_after = acct.positions["MSFT"]

    undo_res = inv.undo()
    assert undo_res["status"] == "undone"
    # state fully restored
    assert acct.cash == pytest.approx(100_000.0)
    assert acct.positions.get("MSFT", 0.0) == pytest.approx(0.0)

    redo_res = inv.redo()
    assert redo_res["status"] == "executed"
    assert acct.cash == pytest.approx(cash_after)
    assert acct.positions["MSFT"] == pytest.approx(pos_after)

def test_idempotency_guards():
    acct = Account(100_000.0)
    cmd = ExecuteOrderCommand(acct, "AAPL", "BUY", 1, 10.0)
    cmd.execute()
    with pytest.raises(RuntimeError, match="already executed"):
        cmd.execute()
    cmd.undo()
    with pytest.raises(RuntimeError, match="not executed yet"):
        cmd.undo()

def test_from_signal_constructor_preserves_meta_and_fields():
    acct = Account(100_000.0)
    signal = {
        "symbol": "AAPL",
        "action": "BUY",
        "size": 3,
        "price": 99.5,
        "meta": {"origin": "strategy_test", "note": "unit"}
    }
    cmd = ExecuteOrderCommand.from_signal(acct, signal)
    res = cmd.execute()

    assert res["symbol"] == "AAPL"
    assert res["action"] == "BUY"
    assert res["quantity"] == pytest.approx(3.0)
    assert res["price"] == pytest.approx(99.5)
    assert res["meta"]["origin"] == "strategy_test"

def test_clean_small_positions_on_revert():
    acct = Account(100_000.0)
    # buy 1, then undo -> position dict should drop the key
    cmd = ExecuteOrderCommand(acct, "SPY", "BUY", 1, 500.0)
    cmd.execute()
    assert "SPY" in acct.positions
    cmd.undo()
    assert "SPY" not in acct.positions
