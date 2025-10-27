# builder.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, List
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models import Portfolio
import json

@dataclass
class PortfolioBuilder:
    """fluent builder for Portfolio objects"""
    _name: str = "Portfolio"
    _owner: str | None = None
    _positions: List[Dict[str, Any]] = field(default_factory=list)
    _subbuilders: List["PortfolioBuilder"] = field(default_factory=list)
    _meta: Dict[str, Any] = field(default_factory=dict)

    # ==== fluent API ====
    def set_name(self, name: str) -> "PortfolioBuilder":
        self._name = name
        return self

    def set_owner(self, owner: str) -> "PortfolioBuilder":
        self._owner = owner
        return self

    def add_position(self, symbol: str, quantity: float, price: float | None = None) -> "PortfolioBuilder":
        self._positions.append({"symbol": symbol, "quantity": quantity, "price": price})
        return self

    def add_subportfolio(self, builder: "PortfolioBuilder") -> "PortfolioBuilder":
        self._subbuilders.append(builder)
        return self

    def set_meta(self, **kwargs) -> "PortfolioBuilder":
        self._meta.update(kwargs)
        return self

    # ==== build ====
    def build(self) -> Portfolio:
        """really build the Portfolio object"""
        port = Portfolio(name=self._name, owner=self._owner)
        for p in self._positions:
            port.add_position(p["symbol"], p["quantity"], p.get("price"))
        for b in self._subbuilders:
            port.add_subportfolio(b.build())
        return port

    # ==== json ====
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "PortfolioBuilder":
        b = PortfolioBuilder().set_name(data.get("name", "Portfolio"))
        if data.get("owner"):
            b.set_owner(data["owner"])
        for p in data.get("positions", []):
            b.add_position(p["symbol"], p["quantity"], p.get("price"))
        for sub in data.get("subportfolios", []):
            child_builder = PortfolioBuilder.from_dict(sub)
            b.add_subportfolio(child_builder)
        return b

    @staticmethod
    def from_json(path: str) -> "PortfolioBuilder":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return PortfolioBuilder.from_dict(data)

