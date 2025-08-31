"""
Cluster ML DataFrames for email analysis.

This module provides functions to cluster Email_ML_DataFrame and Sender_ML_DataFrame
objects using the clustering infrastructure.
"""

from typing import Optional, Dict, Any, Tuple, Literal, Union, List, Set
import pandas as pd
import numpy as np

from .cluster import cluster
from .k_selection import find_optimal_k
from ..utils import get_numeric_columns, include_exclude_columns

def auto_cluster(
    df: pd.DataFrame,
    *,
    k: Optional[int] = None,
    auto_select_k: bool = True,
    max_k: int = 10,
    method: Literal["silhouette", "calinski_harabasz", "davies_bouldin", "elbow"] = "silhouette",
    cluster_col: str = "cluster",
    scale: bool = True,
    impute: bool = True,
    random_state: Optional[int] = 42,
    include_columns: Optional[Union[List[str], Set[str], Tuple[str, ...], str]] = None, 
    exclude_columns: Optional[Union[List[str], Set[str], Tuple[str, ...], str]] = None,
    in_place: bool = False,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Automatically cluster a pandas DataFrame using K-means clustering with automatic k-selection.
    
    Args:
        df: pandas DataFrame to cluster
        k: Number of clusters (if None and auto_select_k=True, will be determined automatically)
        auto_select_k: Whether to automatically select optimal k
        max_k: Maximum k to consider when auto-selecting
        method: Method for selecting optimal k ('silhouette', 'calinski_harabasz', 'davies_bouldin', 'elbow')
        cluster_col: Name of the cluster column to add
        scale: Whether to scale features
        impute: Whether to impute missing values
        random_state: Random state for reproducibility
        in_place: Whether to modify the input DataFrame in place or return a new DataFrame

    Returns:
        Tuple of (clustered_df, clustering_info) where clustered_df is the input DataFrame with added cluster column
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"df must be a pandas DataFrame, got {type(df)}")
    
    if df.empty:
        raise ValueError("df is empty")
    
    # if in_place is False, we copy the dataframe and it should stay the same return type and then when we 
    # add clusters to it, the type will stay the same
    # if in_place is True, we modify the dataframe in place and return the same type. 
    # There is absolutely no reason to convert to Pandas dataframe and back. 
    
    # Auto-select k if requested
    included_columns = include_exclude_columns(df, include_columns=include_columns, exclude_columns=exclude_columns)
    numeric_cols = get_numeric_columns(df[included_columns])
    if len(numeric_cols) == 0:
        raise ValueError("No numeric columns found.")

    if auto_select_k and k is None:
        k, diagnostics = find_optimal_k(
            df[numeric_cols],
            max_k=max_k,
            method=method,
            scale=scale,
            impute=impute,
            random_state=random_state
        )
        clustering_info = {
            "k": k,
            "method": method,
            "auto_selected": True,
            "diagnostics": diagnostics
        }
    else:
        k = k or 2  # Default to 2 clusters
        clustering_info = {
            "k": k,
            "method": method,
            "auto_selected": False
        }
    
    # Apply clustering
    clustered_df = cluster(
        df,
        k=k,
        cluster_col=cluster_col,
        scale=scale,
        impute=impute,
        random_state=random_state,
        include_columns=numeric_cols,
        in_place=in_place
    )
    
    return clustered_df, clustering_info


def analyze_clusters(
    clustered_df: pd.DataFrame,
    cluster_col: str = "cluster",
    feature_cols: Optional[list] = None
) -> Dict[str, Any]:
    """
    Analyze clustering results by computing cluster statistics.
    
    Args:
        clustered_df: DataFrame with cluster assignments
        cluster_col: Name of the cluster column
        feature_cols: List of feature columns to analyze (if None, uses all numeric columns)
        
    Returns:
        Dictionary with cluster analysis results
    """
    if cluster_col not in clustered_df.columns:
        raise ValueError(f"Cluster column '{cluster_col}' not found in DataFrame")
    
    if feature_cols is None:
        feature_cols = get_numeric_columns(clustered_df)
        feature_cols = [col for col in feature_cols if col != cluster_col]
    
    cluster_stats = {}
    unique_clusters = clustered_df[cluster_col].unique()
    
    for cluster in unique_clusters:
        cluster_data = clustered_df[clustered_df[cluster_col] == cluster]
        
        cluster_stats[f"cluster_{cluster}"] = {
            "size": len(cluster_data),
            "percentage": len(cluster_data) / len(clustered_df) * 100,
            "features": {}
        }
        
        # Compute feature statistics for this cluster
        for feature in feature_cols:
            if feature in cluster_data.columns:
                values = cluster_data[feature]
                cluster_stats[f"cluster_{cluster}"]["features"][feature] = {
                    "mean": float(values.mean()),
                    "std": float(values.std()),
                    "min": float(values.min()),
                    "max": float(values.max()),
                    "median": float(values.median())
                }
    
    return {
        "total_clusters": len(unique_clusters),
        "total_samples": len(clustered_df),
        "cluster_distribution": cluster_stats
    }
