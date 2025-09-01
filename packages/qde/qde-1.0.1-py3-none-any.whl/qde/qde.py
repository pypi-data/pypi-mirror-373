# qde/qde.py
from __future__ import annotations
from typing import Optional, Dict, Any
import numpy as np
import pandas as pd
from .core.base import FilterStrategy, SelectionResult, DatasetViews
from .core.registry import StrategyRegistry
from .strategies.ces import CES
from .strategies.oes import OES
from sklearn.base import BaseEstimator as BaseEstimator, ClassifierMixin
from sklearn.naive_bayes import GaussianNB
from qde.metrics.scorers import accuracy_between_views

ArrayLike = np.ndarray | pd.DataFrame | pd.Series

class QDE:
    """
    Orchestrator for Quality Data Extraction.
    Users interact with QDE; strategies are swappable (CES, OES, custom).
    """
    def __init__(
        self,
        strategies: Optional[Dict[str, FilterStrategy]] = None,
        default_strategy: str = "oes"
    ):
        self._registry = StrategyRegistry()
        self._registry.register(CES())
        self._registry.register(OES())

        if strategies:
            for strategy in strategies.values():
                self._registry.register(strategy)

        self._default = default_strategy

    def register(self, strategy: FilterStrategy) -> None:
        self._registry.register(strategy)

    def fit(
        self,
        train_X: ArrayLike, train_y: ArrayLike,
        syn_X: ArrayLike, syn_y: ArrayLike,
        test_X: ArrayLike, test_y: ArrayLike,
        strategy: Optional[str] = None,
        estimator: Optional[BaseEstimator | ClassifierMixin] = GaussianNB(),
        encode_labels: bool = True,
        **kw: Any
    ) -> "QDE":
        self.strategy = self._registry.get(strategy or self._default)
        self.views = DatasetViews(
            sample=(syn_X, syn_y),
            train=(train_X, train_y),
            test=(test_X, test_y)
        )
        self.strategy.fit(self.views, encode_labels=encode_labels, **kw)
        return self

    def extract(
        self,
        estimator: Optional[BaseEstimator | ClassifierMixin] = GaussianNB(),
        compute_filtered_accuracy: bool = True,
        **kw: Any
    ) -> SelectionResult:
        
        result = self.strategy.select(estimator=estimator, **kw)

        X, y = self.views.get_raw("synth")

        if isinstance(X, pd.DataFrame):
            X_sel = X.iloc[result.indices]
            y_sel = None if y is None else (y.iloc[result.indices] if isinstance(y, pd.Series) else y[result.indices])
        else:
            X_sel = X[result.indices]
            y_sel = None if y is None else y[result.indices]

        if compute_filtered_accuracy:
            view = DatasetViews(sample=(X_sel, y_sel), train=self.views.train, test=self.views.test)
            result.meta["filtered-accuracy"] = accuracy_between_views(*view.get("train+synth"), 
                                                                      *view.get("test"), estimator=estimator)

        return result, X_sel, y_sel
