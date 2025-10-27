# dataloader.py
# adapter pattern included

import csv
import json
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from patterns.factory import InstrumentFactory
from patterns.singleton import Config


class MarketDataPoint:
    def __init__(self, symbol: str, price: float, timestamp: datetime):
        self.symbol = symbol
        self.price = price
        self.timestamp = timestamp

    def __repr__(self):
        return f"MarketDataPoint(symbol={self.symbol}, price={self.price}, timestamp={self.timestamp})"


class YahooFinanceAdapter:

    def __init__(self, file_path: str):
        self.file_path = file_path

    def get_data(self, symbol: str) -> MarketDataPoint:
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data["ticker"] != symbol:
            raise ValueError(f"Symbol mismatch: expected {symbol}, got {data['ticker']}")
        timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
        return MarketDataPoint(symbol=data["ticker"], price=float(data["last_price"]), timestamp=timestamp)


class BloombergXMLAdapter:

    def __init__(self, file_path: str):
        self.file_path = file_path

    def get_data(self, symbol: str) -> MarketDataPoint:
        tree = ET.parse(self.file_path)
        root = tree.getroot()
        xml_symbol = root.find("symbol").text
        xml_price = float(root.find("price").text)
        xml_timestamp = datetime.fromisoformat(root.find("timestamp").text.replace("Z", "+00:00"))

        if xml_symbol != symbol:
            raise ValueError(f"Symbol mismatch: expected {symbol}, got {xml_symbol}")
        return MarketDataPoint(symbol=xml_symbol, price=xml_price, timestamp=xml_timestamp)



class DataLoader:
    def __init__(self, cfg: Config):   # cfg is a singleton instance
        self.cfg = cfg
        self.data_path = self.cfg.get('data_path')

    def load_instruments_from_csv(self):
        data_path = self.data_path or "./data/"
        file_path = os.path.join(data_path, "instruments.csv")

        instruments = []
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                inst = InstrumentFactory.create_instrument(row)
                instruments.append(inst)
        return instruments

    def load_market_data(self):
        data_path = self.data_path or "./data/"

        yahoo_file = os.path.join(data_path, "external_data_yahoo.json")
        bloomberg_file = os.path.join(data_path, "external_data_bloomberg.xml")

        yahoo_adapter = YahooFinanceAdapter(yahoo_file)
        bloomberg_adapter = BloombergXMLAdapter(bloomberg_file)

        yahoo_data = yahoo_adapter.get_data("AAPL")
        bloomberg_data = bloomberg_adapter.get_data("MSFT")

        return [yahoo_data, bloomberg_data]



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
    print("\n--- External Market Data (via Adapters) ---")
    for data in loader.load_market_data():
        print(data)
