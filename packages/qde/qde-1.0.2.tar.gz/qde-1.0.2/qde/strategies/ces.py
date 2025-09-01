from __future__ import annotations
import numpy as np
from typing import Any
from dataclasses import replace
from ..core.base import SelectionResult
from .base_strategy import BaseFilteringStrategy
from qde.metrics.scorers import accuracy_between_views
from sklearn.base import clone
from sklearn.metrics import accuracy_score
from sklearn.naive_bayes import GaussianNB

class CES(BaseFilteringStrategy):
    name = "ces"

    def select(
        self,
        *,
        estimator,
        **kw: Any
    ) -> SelectionResult:
        original_accuracy = accuracy_between_views(*self.views.get("train"), 
                                                   *self.views.get("test"), estimator=estimator)
        augmented_accuracy = accuracy_between_views(*self.views.get("train+synth"), 
                                                    *self.views.get("test"), estimator=estimator)
        temp_train_X, temp_train_y = np.copy(self.train_X), np.copy(self.train_y)

        indices = []
        for i in range(self.synth_size):
            try:
                temp_train_X = np.r_[temp_train_X,[self.synth_X[i]]]
                temp_train_y = np.r_[temp_train_y,[self.synth_y[i]]]
            except Exception as e:
                raise ValueError("Inconsistent dimensions between training and synthetic samples.", str(e))

            new_accuracy = accuracy_between_views(
                temp_train_X, temp_train_y,
                self.test_X, self.test_y,
                estimator=estimator
            )
            if new_accuracy >= original_accuracy:
                indices.append(i)
            
            temp_train_X, temp_train_y = np.copy(self.train_X), np.copy(self.train_y)

        return SelectionResult(
            indices=np.asarray(indices),
            meta={"strategy": self.name,
                "selected-samples": len(indices),
                "original-accuracy": original_accuracy, 
                "augmented-accuracy": augmented_accuracy}
        )
