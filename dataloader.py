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
from datetime import timezone
import pandas as pd




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


def read_ticks_csv_pd(path: str):
    df = pd.read_csv(path, parse_dates=["timestamp"])
    # ensure timezone-aware
    if df["timestamp"].dt.tz is None:
        df["timestamp"] = df["timestamp"].dt.tz_localize(timezone.utc)

    ticks = [
        MarketDataPoint(symbol=row.symbol, price=float(row.price), timestamp=row.timestamp.to_pydatetime())
        for row in df.itertuples(index=False)
    ]
    return ticks

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

    def load_market_data(self, paths: str | list[str]):
        """
        Load one or more market data files (.json = Yahoo, .xml = Bloomberg)
        and return a list of MarketDataPoint.
        """
        
        data_path_default = self.data_path or "./data"

        # normalize to list
        if isinstance(paths, str):
            # allow relative path(s)
            paths = [paths]

        results = []

        for file_path in paths:
            # join relative names to default data dir
            if not os.path.isabs(file_path):
                file_path = os.path.join(data_path_default, file_path)

            ext = os.path.splitext(file_path)[1].lower()
            #print(ext)
            
            if ext == ".json":
                with open(file_path, "r", encoding="utf-8") as f:
                    obj = json.load(f)
                symbol = obj.get("ticker") or obj.get("symbol")
                if not symbol:
                    raise ValueError(f"[Yahoo] Missing symbol in {file_path}")
                adapter = YahooFinanceAdapter(file_path)
                results.append(adapter.get_data())

            elif ext == ".xml":
                root = ET.parse(file_path).getroot()
                sym_node = root.find("symbol")
                if sym_node is None or not (sym_node.text and sym_node.text.strip()):
                    raise ValueError(f"[Bloomberg] <symbol> not found in {file_path}")
                symbol = sym_node.text.strip()
                adapter = BloombergXMLAdapter(file_path)
                results.append(adapter.get_data())
            elif ext == ".csv":
                ''' 
                Reads tick data from a CSV (timestamp,symbol,price) into a list of MarketDataPoint.
                     - Parses "timestamp" as datetime and localizes to UTC if tz-naive
                     - Converts each row to MarketDataPoint(symbol, price, timestamp)
                '''

                df = pd.read_csv(file_path, parse_dates=["timestamp"])
                # ensure timezone-aware
                if df["timestamp"].dt.tz is None:
                    df["timestamp"] = df["timestamp"].dt.tz_localize(timezone.utc)
                for row in df.itertuples(index=False):  
                    results.append( MarketDataPoint(symbol=row.symbol, 
                                                    price=float(row.price), 
                                                    timestamp=row.timestamp.to_pydatetime()))

            else:
                raise ValueError(f"Unsupported file type: {file_path} (expect .json or .xml)")
        
        # sort in teh order of timestamp
        results.sort(key=lambda t: t.timestamp)   

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
    paths = ["external_data_bloomberg.xml",
    "external_data_yahoo.json",
    "market_data.csv"]
    iter = iter(loader.load_market_data(paths))
    for data in iter:
        dataset.buffer_data(data)
    print(dataset.buffer[0:5])
