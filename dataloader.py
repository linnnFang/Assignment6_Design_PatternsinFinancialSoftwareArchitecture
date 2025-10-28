# dataloader.py
# adapter pattern included

import csv
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from patterns.factory import InstrumentFactory
from patterns.singleton import Config
from models import MarketDataPoint,MarketDataContainer



class YahooFinanceAdapter:

    def __init__(self, file_path: str):
        self.file_path = file_path

    def get_data(self) -> MarketDataPoint:
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    
        timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
        return MarketDataPoint(symbol=data["ticker"], price=float(data["last_price"]), timestamp=timestamp)


class BloombergXMLAdapter:

    def __init__(self, file_path: str):
        self.file_path = file_path

    def get_data(self) -> MarketDataPoint:
        tree = ET.parse(self.file_path)
        root = tree.getroot()

        xml_symbol = root.find("symbol").text
        xml_price = float(root.find("price").text)
        xml_timestamp = datetime.fromisoformat(root.find("timestamp").text.replace("Z", "+00:00"))

        return MarketDataPoint(symbol=xml_symbol, price=xml_price, timestamp=xml_timestamp)



class DataLoader:
    def __init__(self, cfg: Config):   # cfg is a singleton instance
        self.cfg = cfg
        self.data_path = self.cfg.get('data_path')
        self.log_level = self.cfg.get("")
        self.portfolio_structure_path = self.cfg.get("portfolio_structure_path")
        self.report_path = self.cfg.get("report_path")
        self.default_strategy = self.cfg.get("default_strategy")


    def load_instruments_from_csv(self):
        data_path = self.data_path or "./data/" # read the config
        file_path = os.path.join(data_path, "instruments.csv")

        instruments = []
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                inst = InstrumentFactory.create_instrument(row)
                instruments.append(inst)
        return instruments

    def load_market_data(self, path):
        """
        Load one or more market data files, auto-detecting source (Yahoo JSON / Bloomberg XML).

        Args:
            paths: a file path (str) or a list of file paths.

        Returns:
            List[MarketDataPoint]
        """
        data_path_default = self.data_path or "./data/"

        # normalize to list
        if isinstance(path, str):
            # allow caller to pass relative names; join with data_path_default if not absolute
            if not os.path.isabs(path):
                path = [os.path.join(data_path_default, path)]
            else:
                path= [path]

        results = []

        if not os.path.isabs(path):
            file_path = os.path.join(data_path_default, path)

        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".json":
            # Likely Yahoo JSON
            with open(file_path, "r", encoding="utf-8") as f:
                obj = json.load(f)
            # Prefer 'ticker', fallback to 'symbol' if your JSON uses it
            symbol = obj.get("ticker") or obj.get("symbol")
            if not symbol:
                raise ValueError(f"[Yahoo] Could not find symbol key in {file_path}")
            adapter = YahooFinanceAdapter(file_path)
            results.append(adapter.get_data(symbol))

        elif ext == ".xml":
            # Likely Bloomberg XML
            root = ET.parse(file_path).getroot()
            node = root.find("symbol")
            if node is None or not (node.text and node.text.strip()):
                raise ValueError(f"[Bloomberg] <symbol> not found in {file_path}")
            symbol = node.text.strip()
            adapter = BloombergXMLAdapter(file_path)
            results.append(adapter.get_data(symbol))

        else:
            raise ValueError(f"Unsupported file type for {file_path} (expected .json or .xml)")

        return results



if __name__ == "__main__":
    cfg = Config("data/config.json")
    loader = DataLoader(cfg)

    # Load instrument list
    try:
        instruments = loader.load_instruments_from_csv()
        for inst in instruments:
            print(type(inst).__name__, inst.__dict__)
    except FileNotFoundError:
        print("instruments.csv not found — skipping instrument load.")

    # Load market data through adapters
    dataset = MarketDataContainer()
    print("\n--- External Market Data (via Adapters) ---")
    for data in loader.load_market_data():
        dataset.buffer_data(data)
