def test_observer_command_flow(capsys):
    from patterns.observer import SignalPublisher, LoggerObserver
    from patterns.command import Broker, ExecuteOrderCommand, CommandInvoker

    pub = SignalPublisher(); pub.attach(LoggerObserver())
    signal = {"action":"BUY","symbol":"MSFT","size":10}
    pub.notify(signal)

    broker = Broker(); inv = CommandInvoker()
    inv.do(ExecuteOrderCommand(broker, "MSFT", 10))
    assert broker.positions["MSFT"] == 10
    inv.undo(); assert broker.positions["MSFT"] == 0
    inv.redo(); assert broker.positions["MSFT"] == 10
