from __future__ import annotations

from typing import Literal, Optional
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def make_preprocessor(
    *,
    impute: bool = True,
    impute_strategy: Literal["mean", "median", "most_frequent", "constant"] = "median",
    scale: bool = True,
) -> Optional[Pipeline]:
    """
    Build a preprocessing pipeline for numeric features.
    Returns a sklearn Pipeline or None if no steps are requested.
    """
    steps = []
    if impute:
        steps.append(("imputer", SimpleImputer(strategy=impute_strategy)))
    if scale:
        steps.append(("scaler", StandardScaler()))
    return Pipeline(steps) if steps else None
