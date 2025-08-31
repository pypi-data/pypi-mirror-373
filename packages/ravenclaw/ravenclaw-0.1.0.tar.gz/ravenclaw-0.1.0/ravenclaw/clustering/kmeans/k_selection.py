from __future__ import annotations

from typing import Dict, List, Literal, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import (
    silhouette_score,
    calinski_harabasz_score,
    davies_bouldin_score,
)

from .preprocessing import make_preprocessor


def find_optimal_k(
    df: pd.DataFrame,
    *,
    max_k: int = 10,
    min_k: int = 2,
    method: Literal["silhouette", "calinski_harabasz", "davies_bouldin", "elbow"] = "silhouette",
    scale: bool = True,
    impute: bool = True,
    impute_strategy: Literal["mean", "median", "most_frequent", "constant"] = "median",
    random_state: Optional[int] = 42,
    n_init: int | Literal["auto"] = "auto",
) -> Tuple[int, Dict[str, object]]:
    """
    Choose k for KMeans using numeric columns only.
    Returns (best_k, diagnostics) where diagnostics has candidate_ks, scores, inertias.
    """
    num_df = df.select_dtypes(include=[np.number])
    if num_df.shape[1] == 0:
        raise ValueError("No numeric columns found.")

    preproc = make_preprocessor(impute=impute, impute_strategy=impute_strategy, scale=scale)
    X = num_df.values
    if preproc is not None:
        X = preproc.fit_transform(X)

    n = X.shape[0]
    candidate_ks: List[int] = [k for k in range(min_k, max_k + 1) if 2 <= k <= n]
    if not candidate_ks:
        return 1, {"candidate_ks": [], "scores": {}, "inertias": {}}

    scores: Dict[int, float] = {}
    inertias: Dict[int, float] = {}

    for k in candidate_ks:
        km = KMeans(n_clusters=k, n_init=n_init, random_state=random_state)
        labels = km.fit_predict(X)
        inertias[k] = float(km.inertia_)
        if method == "silhouette":
            if k < n:  # undefined when every sample is its own cluster
                scores[k] = silhouette_score(X, labels)
        elif method == "calinski_harabasz":
            scores[k] = calinski_harabasz_score(X, labels)
        elif method == "davies_bouldin":
            scores[k] = davies_bouldin_score(X, labels)
        elif method == "elbow":
            pass
        else:
            raise ValueError(f"Unknown method {method}")

    if method == "silhouette":
        best_k = max(scores, key=scores.get) if scores else candidate_ks[0]
    elif method == "calinski_harabasz":
        best_k = max(scores, key=scores.get)
    elif method == "davies_bouldin":
        best_k = min(scores, key=scores.get)
    elif method == "elbow":
        ks = np.array(sorted(inertias.keys()))
        ys = np.array([inertias[k] for k in ks], dtype=float)

        x = (ks - ks.min()) / (ks.max() - ks.min()) if ks.max() > ks.min() else np.zeros_like(ks, float)
        y = (ys - ys.min()) / (ys.max() - ys.min()) if ys.max() > ys.min() else np.zeros_like(ys, float)

        p1, p2 = np.array([x[0], y[0]]), np.array([x[-1], y[-1]])
        chord = p2 - p1
        denom = np.linalg.norm(chord)
        if denom == 0:
            best_k = int(ks[0])
        else:
            pts = np.stack([x, y], axis=1)
            # Calculate perpendicular distance from points to line using 2D formula
            # Distance = |ax + by + c| / sqrt(a² + b²) where line is ax + by + c = 0
            # For line from p1 to p2: (p2[1]-p1[1])x - (p2[0]-p1[0])y + (p2[0]-p1[0])p1[1] - (p2[1]-p1[1])p1[0] = 0
            a = chord[1]  # p2[1] - p1[1]
            b = -chord[0]  # -(p2[0] - p1[0])
            c = chord[0] * p1[1] - chord[1] * p1[0]
            dists = np.abs(a * pts[:, 0] + b * pts[:, 1] + c) / denom
            best_k = int(ks[int(np.argmax(dists))])
    else:
        raise ValueError(f"Unknown method {method}")

    return best_k, {"candidate_ks": candidate_ks, "scores": scores, "inertias": inertias}
