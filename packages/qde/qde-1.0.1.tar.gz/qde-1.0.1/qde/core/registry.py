from __future__ import annotations
from typing import Dict
from .base import FilterStrategy

class StrategyRegistry:
    def __init__(self) -> None:
        self._by_name: Dict[str, FilterStrategy] = {}

    def register(self, strategy: FilterStrategy) -> None:
        key = strategy.name.lower()
        self._by_name[key] = strategy

    def get(self, name: str) -> FilterStrategy:
        key = name.lower()
        if key not in self._by_name:
            raise KeyError(f"Unknown strategy '{name}'. Registered: {self.list()}")
        return self._by_name[key]
    
    def list(self) -> list:
        return list(self._by_name)
