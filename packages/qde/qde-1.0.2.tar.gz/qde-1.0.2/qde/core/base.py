from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Optional, Mapping, Any, Tuple, Literal
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin, clone

ArrayLike = np.ndarray | pd.DataFrame | pd.Series
View = Literal["synth", "train", "test", "train+synth"]
distance_modes = Literal["euclidean", "cosine"]

@dataclass(frozen=True)
class DatasetViews:
    sample: Optional[Tuple[ArrayLike, ArrayLike]] = None
    train: Optional[Tuple[ArrayLike, ArrayLike]] = None
    test: Optional[Tuple[ArrayLike, ArrayLike]] = None

    def _to_numpy(self, X, y) -> Tuple[np.ndarray, np.ndarray]:
        if isinstance(X, (pd.DataFrame, pd.Series)):
            X = X.to_numpy()
        if isinstance(y, (pd.DataFrame, pd.Series)):
            y = y.to_numpy()
        X = np.asarray(X)
        y = np.asarray(y).ravel()
        if X.shape[0] != y.shape[0]:
            raise ValueError(f"X and y length mismatch: {X.shape[0]} vs {y.shape[0]}")
        return X, y

    def get_raw(self, view: View) -> Tuple[ArrayLike, ArrayLike]:
        if view == "synth":
            if self.sample is None: raise ValueError("sample view unavailable")
            return self.sample
        if view == "train":
            if self.train is None: raise ValueError("train view unavailable")
            return self.train
        if view == "test":
            if self.test is None: raise ValueError("combined view unavailable")
            return self.test
        if view == "train+synth":
            if self.train is None or self.sample is None:
                raise ValueError("train+sample view requires both train and sample")
            Xtr, ytr = self.train; Xs, ys = self.sample
            X = (pd.concat([Xtr, Xs], ignore_index=True)
                 if isinstance(Xtr, pd.DataFrame) else np.concatenate([Xtr, Xs]))
            y = (pd.concat([ytr, ys], ignore_index=True)
                 if isinstance(ytr, pd.Series) else np.concatenate([ytr, ys]))
            return X, y
        raise ValueError(f"unknown view: {view}")
    
    def get(self, view: View) -> Tuple[np.ndarray, np.ndarray]:
        X, y = self.get_raw(view)
        return self._to_numpy(X, y)

@dataclass(frozen=True)
class SelectionResult:
    indices: np.ndarray              
    meta: Mapping[str, Any] = None

class FilterStrategy(Protocol):
    """Strategy interface for CES/OES and custom methods."""
    name: str

    def fit(
        self,
        datasets: DatasetViews,
        **kw: Any,
    ) -> "FilterStrategy": ...

    def select(
        self,
        **kw: Any,
    ) -> SelectionResult: ...