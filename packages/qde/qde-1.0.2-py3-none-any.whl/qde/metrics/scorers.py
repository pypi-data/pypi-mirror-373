from __future__ import annotations
from typing import Callable, Optional
import numpy as np
from typing import Tuple
from sklearn.base import BaseEstimator, ClassifierMixin, clone
from sklearn.metrics import accuracy_score

def predictions_between_view(
    train_X, train_y,
    eval_X, eval_y, *, estimator: BaseEstimator | ClassifierMixin
) -> Tuple[np.ndarray, np.ndarray]:
    if train_y is None or eval_y is None:
        raise ValueError("Labels are required to compute predictions/accuracy.")
    est = clone(estimator)
    est.fit(train_X, train_y)
    yhat = est.predict(eval_X)
    return yhat

def accuracy_between_views(
    train_X, train_y,
    eval_X, eval_y, *, estimator: BaseEstimator | ClassifierMixin) -> float:
    yhat = predictions_between_view(train_X, train_y, eval_X, eval_y, estimator=estimator)
    return float(accuracy_score(eval_y, yhat))
