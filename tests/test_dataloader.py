
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from patterns.singleton import Config
from dataloader import YahooFinanceAdapter,BloombergXMLAdapter,DataLoader
def test_adapters():
    
    y = YahooFinanceAdapter("data/external_data_yahoo.json").get_data()
    b = BloombergXMLAdapter("data/external_data_bloomberg.xml").get_data()
    assert y.symbol == "AAPL" and b.symbol == "MSFT"

def test_csv_reader(tmp_path):
    csvp = tmp_path / "market_data.csv"
    csvp.write_text("timestamp,symbol,price\n2025-10-01 09:30:00,AAPL,169.89\n", encoding="utf-8")
    cfg = Config.__new__(Config)       # bypass singleton loader for test
    cfg._data = {"data_path": str(tmp_path)}
    dl = DataLoader(cfg)
    ticks = list(dl.load_market_data("market_data.csv"))
    assert len(ticks) == 1 and ticks[0].symbol == "AAPL"
