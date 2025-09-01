# qde/core/base_strategy.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Tuple
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin, clone
from sklearn.preprocessing import LabelEncoder

from ..core.base import FilterStrategy, SelectionResult, DatasetViews


class BaseFilteringStrategy(FilterStrategy, ABC):
    name: str = "base"

    def fit(
        self,
        datasets: DatasetViews,
        *,
        encode_labels: bool = True,
        **kw: Any,) -> "BaseFilteringStrategy":
        self.views = datasets
        self.train_X, self.train_y = datasets.get("train")
        self.synth_X, self.synth_y = datasets.get("synth") 
        self.test_X, self.test_y = datasets.get("test")

        self.train_y = LabelEncoder().fit_transform(self.train_y) if encode_labels else self.train_y
        self.synth_y = LabelEncoder().fit_transform(self.synth_y) if encode_labels else self.synth_y
        self.test_y = LabelEncoder().fit_transform(self.test_y) if encode_labels else self.test_y

        self.n_classes = len(np.unique(self.train_y))
        self.n_features = self.train_X.shape[1]

        self.train_size = self.train_X.shape[0]
        self.synth_size = self.synth_X.shape[0] 
        self.test_size = self.test_X.shape[0]

        return self
    
    def clone_estimator(self, estimator: BaseEstimator | ClassifierMixin) -> BaseEstimator | ClassifierMixin:
        return clone(estimator)

    @abstractmethod
    def select(
        self,
        **kw: Any,
    ) -> SelectionResult:
        ...
