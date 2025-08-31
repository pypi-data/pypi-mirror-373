import pandas as pd
import numpy as np
from typing import Union, Optional

def _get_range(values: pd.Series, *, value_range: Optional[tuple[float, float]] = None) -> tuple[float, float]:
    if value_range is None:
        return (values.min(), values.max())

    if not isinstance(value_range, (list, tuple)) or len(value_range) != 2:
        raise TypeError(f"Expected tuple of length 2, got {type(value_range)}")

    min_val, max_val = value_range
    if min_val is None:
        min_val = values.min()
    if max_val is None:
        max_val = values.max()

    min_val, max_val = min(min_val, max_val), max(min_val, max_val)

    if min_val > values.min() or max_val < values.max():
        raise ValueError(f"Range ({min_val}, {max_val}) is not compatible with values {values.min()} to {values.max()}")

    return (min_val, max_val)

def convert_to_sin(values: pd.Series, *, value_range: Optional[tuple[float, float]] = None) -> pd.Series:
    min_val, max_val = _get_range(values, value_range=value_range)
    return np.sin(2 * np.pi * (values - min_val) / (max_val - min_val))

def convert_to_cos(values: pd.Series, *, value_range: Optional[tuple[float, float]] = None) -> pd.Series:
    min_val, max_val = _get_range(values, value_range=value_range)
    return np.cos(2 * np.pi * (values - min_val) / (max_val - min_val))
