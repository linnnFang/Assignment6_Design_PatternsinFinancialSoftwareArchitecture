

# main.py
from patterns.singleton import Config
from dataloader import DataLoader
from engine import TradingEngine
from patterns.builder import PortfolioBuilder
from patterns.command import *
from patterns.observer import *
from patterns.strategy import *
from models import *



import json

def main():
    
    cfg = Config("data/config.json")
    loader = DataLoader(cfg)
    data_iter = iter(loader.load_market_data())  

    # 1) build portfolio
    builder = PortfolioBuilder.from_json(loader.portfolio_structure_path)
    portfolio = builder.build()

    # 2) account & commands
    account = Account(cash=100_000)
    invoker = CommandInvoker()
    executor = ExecuteOrderCommand(account, invoker)

    # 3) observers
    publisher = SignalPublisher()
    publisher.attach(LoggerObserver())
    publisher.attach(AlertObserver(threshold=1000))

    # 4) strategies
    strats = [
        MeanReversionStrategy(window=20, threshold=0.02, size=10.0),
        BreakoutStrategy(window=20, size=10.0),
    ]

    # 5) router & risk
    container = MarketDataContainer()  # sink for fills


    # 7) engine
    engine = TradingEngine(data_iter, strats, publisher,portfolio, executor, container)

    # 8) run
    engine.run()
    print(account)               # see cash/positions
    print(container.positions)   # if you mirror positions here


if __name__ == "__main__":
    main()


