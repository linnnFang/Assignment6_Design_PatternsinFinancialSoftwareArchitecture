# Design Report

## Overview
This codebase demonstrates classic GoF patterns for a small trading/analytics workflow:
- **Factory** creates instruments from CSV.
- **Singleton** centralizes configuration.
- **Builder + Composite** build hierarchical portfolios.
- **Decorator** adds analytics (volatility/beta/drawdown) without touching base classes.
- **Adapter** normalizes heterogeneous external data (Yahoo JSON, Bloomberg XML) into `MarketDataPoint`.
- **Strategy** decouples signal generation from data flow.
- **Observer** broadcasts signals to logging/analytics.
- **Command** encapsulates execution with undo/redo support.

## Key Decisions
- `MarketDataPoint` is an immutable value object to improve safety and caching.
- Decorators return *new* dicts using shallow merge to avoid accidental mutation.
- Observer is kept synchronous and minimal; for production we'd use queues.
- Command history is LIFO with clear `undo/redo` semantics.

## Tradeoffs
- Returning shallow dicts is simple but cannot deep-merge nested metrics.
- In-memory publisher avoids infra complexity but lacks durability.
- Strategy examples are intentionally small; real models will need risk controls and state persistence.

## Testing
- Unit tests cover observer flow; additional tests (factory, decorators, strategies) recommended.
