from __future__ import annotations

from typing import Literal, Optional
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from typing import List, Set, Tuple, Optional, Union

from .preprocessing import make_preprocessor

from ..utils import get_numeric_columns, include_exclude_columns


def cluster(
    df: pd.DataFrame,
    *,
    k: int,
    cluster_col: str = "cluster",
    scale: bool = True,
    impute: bool = True,
    impute_strategy: Literal["mean", "median", "most_frequent", "constant"] = "median",
    random_state: Optional[int] = 42,
    n_init: int | Literal["auto"] = "auto",
    include_columns: Optional[Union[List[str], Set[str], Tuple[str, ...], str]] = None, 
    exclude_columns: Optional[Union[List[str], Set[str], Tuple[str, ...], str]] = None,
    in_place: bool = False,
) -> pd.DataFrame:
    """
    Fit KMeans with fixed k on numeric columns, return df copy with a new cluster column.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"df must be a pandas DataFrame, got {type(df)}")

    if not in_place:
        df = df.copy()

    if k < 1:
        raise ValueError("k must be >= 1.")

    included_columns = include_exclude_columns(df, include_columns=include_columns, exclude_columns=exclude_columns)
    if not isinstance(included_columns, list):
        raise TypeError(f"included_columns must be a list, got {type(included_columns)}")

    numeric_cols = get_numeric_columns(df[included_columns]) 
    if len(numeric_cols) == 0:
        raise ValueError("No numeric columns found.")
    if k > len(df):
        raise ValueError(f"k={k} cannot exceed number of rows ({len(df)}).")

    preproc = make_preprocessor(impute=impute, impute_strategy=impute_strategy, scale=scale)
    X = df[numeric_cols].values
    if preproc is not None:
        X = preproc.fit_transform(X)

    if k == 1:
        labels = np.zeros(len(df), dtype=int)
    else:
        km = KMeans(n_clusters=k, n_init=n_init, random_state=random_state)
        labels = km.fit_predict(X)

    df[cluster_col] = labels
    return df
