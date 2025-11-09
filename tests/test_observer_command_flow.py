# tests/test_observer_command_flow.py

import pytest

from patterns.observer import SignalPublisher, LoggerObserver, AlertObserver
from patterns.command import Account, ExecuteOrderCommand, CommandInvoker


def test_logger_and_alert_receive_notifications(capsys):
    pub = SignalPublisher()
    pub.attach(LoggerObserver(prefix="[TLOG]"))
    pub.attach(AlertObserver(threshold=1000.0))  # triggers if size*price >= 1000

    # Notional = 10 * 150 = 1500 -> should trigger AlertObserver
    sig = {"symbol": "AAPL", "action": "BUY", "size": 10, "price": 150.0}
    pub.notify(sig)

    out = capsys.readouterr().out
    assert "[TLOG] Signal received:" in out
    assert "[ALERT] Large trade detected" in out
    assert "AAPL" in out


def test_alert_not_triggered_below_threshold(capsys):
    pub = SignalPublisher()
    pub.attach(LoggerObserver(prefix="[TLOG]"))
    pub.attach(AlertObserver(threshold=10_000.0))  # high threshold

    # Notional = 10 * 150 = 1500 -> should NOT trigger alert
    sig = {"symbol": "AAPL", "action": "BUY", "size": 10, "price": 150.0}
    pub.notify(sig)

    out = capsys.readouterr().out
    assert "[TLOG] Signal received:" in out
    assert "[ALERT]" not in out


def test_observer_exception_is_swallowed_and_flow_continues(capsys):
    class BadObserver:
        def update(self, signal):
            raise RuntimeError("boom")

    pub = SignalPublisher()
    pub.attach(BadObserver())
    pub.attach(LoggerObserver(prefix="[OK]"))

    pub.notify({"symbol": "SPY", "action": "SELL", "size": 1, "price": 1.0})

    out = capsys.readouterr().out
    # Error message from publisher AND logger output should both appear
    assert "Observer" in out and "boom" in out
    assert "[OK] Signal received:" in out


def test_detach_removes_observer(capsys):
    log = LoggerObserver(prefix="[LEFT]")
    pub = SignalPublisher()
    pub.attach(log)
    pub.detach(log)  # remove it

    pub.notify({"symbol": "MSFT", "action": "BUY", "size": 1, "price": 1.0})
    out = capsys.readouterr().out
    assert "[LEFT]" not in out  # no output since detached


def test_observer_triggers_command_execution():
    """
    Integration: an observer that EXECUTES a command when a signal arrives.
    Verifies end-to-end: publisher -> observer -> command -> account state.
    """
    account = Account(cash=100_000.0)
    invoker = CommandInvoker()

    class ExecObserver:
        def __init__(self, account, invoker):
            self.account = account
            self.invoker = invoker
        def update(self, signal):
            cmd = ExecuteOrderCommand.from_signal(self.account, signal)
            self.invoker.execute_cmd(cmd)

    pub = SignalPublisher()
    pub.attach(ExecObserver(account, invoker))

    # BUY 10 @ 100 -> cash down 1000, position +10
    sig = {"symbol": "AAPL", "action": "BUY", "size": 10, "price": 100.0}
    pub.notify(sig)

    assert account.positions.get("AAPL", 0.0) == pytest.approx(10.0)
    assert account.cash == pytest.approx(99_000.0)
