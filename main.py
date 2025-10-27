# main.py
"""
from patterns.singleton import Config
from engine import TradingEngine
from reporting import Logger
from dataloader import load_instruments_from_csv
import json
import os

def main():
    # ---- print working directory ----
    print("[CWD]", os.getcwd())

    # ---- First load config (global singleton) ----
    cfg = Config("config.json")
    print("\nCONFIG =", json.dumps(cfg._data, indent=2))

    # ---- Initialize engine and logger ----
    engine = TradingEngine(cfg)    # ✅ External use of Config()
    logger = Logger()           # ✅ Internal use of Config()

    # ---- Run engine ----
    print("\n===== ENGINE RUN =====")
    engine.run()

    # ---- output summary ----
    print("\n===== REPORTING =====")
    logger.log_summary()

    print("\n===== END =====")

if __name__ == "__main__":
    main()
"""
"""
# main.py
from patterns.singleton import Config
from dataloader import DataLoader
from engine import TradingEngine
from reporting import Logger
import json

def main():
    # initialize the singleton with the file path ONCE
    cfg = Config("config.json")
    print("\nCONFIG =", json.dumps(cfg._data, indent=2))

    dataloader = DataLoader(cfg)
    engine = TradingEngine(cfg)
    logger = Logger()

    inst = dataloader.load_instruments_from_csv()
    engine.run()
    logger.log_summary()

if __name__ == "__main__":
    main()

"""

# main.py
from patterns.singleton import Config
from dataloader import DataLoader
from engine import TradingEngine
from reporting import Logger
from patterns.builder import PortfolioBuilder
import json

def main():
    cfg = Config("./data/config.json")
    print("\nCONFIG =", json.dumps(cfg._data, indent=2))

    dataloader = DataLoader(cfg)
    engine = TradingEngine(cfg)
    logger = Logger()

    # instruments
    inst = dataloader.load_instruments_from_csv()

    # only for portfolio building demo
    port_path = cfg.get("portfolio_structure_path", "./data/portfolio_structure.json")
    builder = PortfolioBuilder.from_json(port_path)
    portfolio = builder.build()

    # test output
    print("\n=== Portfolio Summary ===")
    portfolio.summary()
    print("\nFlattened Positions:", portfolio.get_positions())

    engine.run()
    logger.log_summary()

if __name__ == "__main__":
    main()













