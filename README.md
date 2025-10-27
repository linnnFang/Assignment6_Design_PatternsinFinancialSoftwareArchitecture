
# FINM32500 Assignment 6 

A compact, testable scaffold that demonstrates GoF patterns in a toy trading pipeline:
Factory, Singleton, Builder + Composite, Decorator, Adapter, Strategy, Observer, and Command.

---

## 📦 Project Structure (suggested)

```
.
├── main.py                     # Orchestrates config → ingestion → strategy → observers → execution
├── reporting.py                # Observer-based logging & simple analytics
├── patterns/
│   ├── __init__.py
│   └── adapter.py              # Yahoo/Bloomberg Adapters → MarketDataPoint
├── data/
│   ├── external_data_yahoo.json
│   └── external_data_bloomberg.xml
├── tests/
│   ├── test_reporting.py
│   └── (add more: factory / singleton / decorators / command / strategy)
└── README.md
```

> If you keep `models.py` (e.g., `MarketDataPoint`, `parse_ts`) in the repo root,
> use **absolute imports** from the project root (e.g., `from models import MarketDataPoint`)
> and run with `PYTHONPATH=.` (see below).

---

## ⚙️ Requirements

- Python **3.9+** (3.10+ recommended)
- `pip install -U pytest` (for tests)

Optional (formatting/lint): `pip install -U black ruff`

---

## 🚀 Quick Start

### 1) Run the main demo

From the **project root** (the directory that contains `main.py`):

**macOS/Linux**
```bash
PYTHONPATH=. python main.py
```

**Windows PowerShell**
```powershell
$env:PYTHONPATH="."
python .\main.py
```

This will:
1. Load minimal config (or defaults)  
2. Ingest two example ticks from `data/external_data_yahoo.json` and `data/external_data_bloomberg.xml` via Adapters  
3. Run a tiny Mean-Reversion strategy  
4. Publish signals to Observers (console logger + in‑memory metrics)  
5. Execute orders via a simple Command/Broker pair

You should see signal logs (if any), a metrics snapshot, and final positions.

---

## 🧱 Patterns in This Scaffold

- **Factory**: (your `InstrumentFactory`) creates `Instrument` objects from CSV.
- **Singleton**: `Config` loads `config.json` once; shared instance across modules.
- **Builder + Composite**: `PortfolioBuilder` builds nested `PortfolioGroup` trees of `Position`s.
- **Decorator**: `VolatilityDecorator`, `BetaDecorator`, `DrawdownDecorator` augment `.get_metrics()` results without touching base classes.
- **Adapter**: `YahooFinanceAdapter`, `BloombergXMLAdapter` normalize heterogeneous data into `MarketDataPoint(symbol, timestamp, price, source)`.
- **Strategy**: `MeanReversionStrategy` / `BreakoutStrategy` expose `generate_signals(tick) -> list[dict]`.
- **Observer**: `SignalPublisher` notifies `LoggerObserver`, `MetricsObserver` when signals are generated.
- **Command**: `ExecuteOrderCommand` encapsulates trades; `CommandInvoker` supports `do/undo/redo`.

> The demo focuses on Adapter + Strategy + Observer + Command so you have a runnable end-to-end loop.
> Other patterns are designed to slot in the same flow.

---

## 🧪 Tests

**Run all tests**
```bash
pytest -q
```

**Example test included**
- `tests/test_reporting.py`: validates the Observer flow (logger output + metrics counters).

**What else to test (suggested)**
- Factory: type creation from `instruments.csv`
- Singleton: unique instance + config keys
- Decorator: stacked metrics dict merge (volatility/beta/drawdown)
- Strategy: deterministic signals on fixed sequences
- Command: do/undo/redo evolves positions correctly

---

## 🧰 Adapters: File Formats & Usage

**MarketDataPoint (minimal)**  
```python
@dataclass(frozen=True, slots=True)
class MarketDataPoint:
    symbol: str
    timestamp: datetime    # timezone-aware preferred
    price: float
    source: str            # e.g., "Yahoo" | "Bloomberg"
```

**Yahoo JSON expected shape**
```json
{
  "ticker": "AAPL",
  "last_price": 172.35,
  "timestamp": "2025-10-01T09:30:00Z"
}
```

**Bloomberg XML expected shape**
```xml
<instrument>
  <symbol>MSFT</symbol>
  <price>328.10</price>
  <timestamp>2025-10-01T09:30:00Z</timestamp>
</instrument>
```

Both adapters expose:
```python
.get_data(symbol: str) -> MarketDataPoint
```

---

## 🧭 Running as a Package vs Script

### Option A: Run as scripts (simple)
Use absolute imports and set `PYTHONPATH=.` from the project root:
```bash
PYTHONPATH=. python patterns/adapter.py
```

### Option B: Run as a package (cleaner for multi-module)
Ensure directories are packages (add `__init__.py`), ensure valid package names (no spaces or `-`). Then:
```bash
python -m your_package.patterns.adapter
```

---

## 🐞 Troubleshooting

- **`ModuleNotFoundError: No module named 'models'`**  
  Run from the **project root** and set `PYTHONPATH=.` or use package-style `python -m ...`.

- **`attempted relative import with no known parent package`**  
  You ran a module directly while using **relative imports**. Either switch to absolute imports + `PYTHONPATH=.` or run with `python -m package.module`.

- **`AttributeError: datetime has no attribute fromisoformat`**
  - Make sure you import the class, not the module: `from datetime import datetime` then `datetime.fromisoformat(...)`  
  - For older Python, add a `strptime` fallback.

- **IndentationError / TabError**  
  Convert all tabs to spaces; use 4 spaces per level. `python -m tabnanny your_file.py` helps locate issues.

---

## 📝 Design Notes (short)

- Value objects (`MarketDataPoint`) are `frozen=True, slots=True` → immutable, memory‑efficient.
- Decorators return **new dicts** via `{**base, "metric": value}` shallow-merge to avoid side effects.
- Observer kept synchronous for clarity; production systems often decouple via a queue/bus.
- Strategy parameters can live in `data/strategy_params.json`, loaded via Singleton `Config`.

---

## 📄 License

For coursework/demo purposes. 
