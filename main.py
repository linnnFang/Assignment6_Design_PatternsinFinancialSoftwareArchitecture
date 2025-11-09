

from __future__ import annotations
from patterns.singleton import Config
from patterns.observer import SignalPublisher, LoggerObserver, AlertObserver
from patterns.command import Account, CommandInvoker
from patterns.strategy import MeanReversionStrategy, BreakoutStrategy
from dataloader import DataLoader
from engine import TradingEngine, OrderRouter, BasicRisk

def main():
    cfg = Config("data/config.json")
    loader = DataLoader(cfg)

    # Build data stream: mix adapters + CSV
    ext_ticks = loader.load_market_data(["external_data_bloomberg.xml", "external_data_yahoo.json"])
    csv_ticks = list(loader.load_market_data("market_data.csv"))
    data_stream = sorted([*ext_ticks, *csv_ticks], key=lambda t: t.timestamp)

    # Strategies
    strategies = [
        MeanReversionStrategy(window=20, threshold=0.02, size=10.0),
        BreakoutStrategy(window=20, size=10.0),
    ]

    # Observers
    publisher = SignalPublisher()
    publisher.attach(LoggerObserver())
    publisher.attach(AlertObserver(threshold=500))

    # Execution
    account = Account(cash=100_000)
    invoker = CommandInvoker()
    router = OrderRouter()
    risk = BasicRisk(positions=account.positions, max_pos=1000, max_order=200)

    engine = TradingEngine(
        data=data_stream,
        strategies=strategies,
        publisher=publisher,
        router=router,
        risk=risk,
        account=account,
        invoker=invoker,
        on_fill=lambda res: None,
    )

    engine.run()
    print("\n--- Done ---")
    print(account)

if __name__ == "__main__":
    main()
