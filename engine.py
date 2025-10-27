# engine.py
print(">>> ENGINE FILE USED:", __file__)

from patterns.singleton import Config

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





