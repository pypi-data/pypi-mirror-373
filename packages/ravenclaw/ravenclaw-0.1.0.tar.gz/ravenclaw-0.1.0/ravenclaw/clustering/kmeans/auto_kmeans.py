"""Auto K-Means clusterer that automatically determines optimal number of clusters."""

from __future__ import annotations

from typing import Dict, List, Literal, Optional, Tuple, Union, Set
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.base import BaseEstimator, ClusterMixin

from .k_selection import find_optimal_k
from .preprocessing import make_preprocessor
from ..utils import get_numeric_columns, include_exclude_columns


class AutoKMeans(BaseEstimator, ClusterMixin):
    """K-Means clusterer with automatic or manual k selection.
    
    This class provides a scikit-learn compatible interface for K-means clustering
    with either automatic determination of the optimal number of clusters or
    manual specification. It follows the standard fit/predict pattern like other
    sklearn estimators.
    
    Examples:
        >>> import pandas as pd
        >>> import numpy as np
        >>> from ravenclaw.clustering.kmeans import AutoKMeans
        >>> 
        >>> # Create sample data
        >>> df = pd.DataFrame({
        ...     'x': np.random.randn(100),
        ...     'y': np.random.randn(100),
        ...     'category': ['A', 'B', 'C'] * 33 + ['A']
        ... })
        >>> 
        >>> # Automatic k selection
        >>> clusterer = AutoKMeans(max_k=5)
        >>> clusterer.fit(df)
        >>> labels = clusterer.predict(df)
        >>> 
        >>> # Manual k specification
        >>> clusterer = AutoKMeans(n_clusters=3)
        >>> labels = clusterer.fit_predict(df)
        >>> 
        >>> # Ignore non-numeric columns automatically
        >>> clusterer = AutoKMeans(n_clusters=3, ignore_non_numeric=True)
        >>> labels = clusterer.fit_predict(df)  # Will use only 'x' and 'y'
    """
    
    def __init__(
        self,
        *,
        n_clusters: Optional[int] = None,
        max_k: int = 10,
        min_k: int = 2,
        method: Literal["silhouette", "calinski_harabasz", "davies_bouldin", "elbow"] = "silhouette",
        scale: bool = True,
        impute: bool = True,
        impute_strategy: Literal["mean", "median", "most_frequent", "constant"] = "median",
        random_state: Optional[int] = 42,
        n_init: int | Literal["auto"] = "auto",
        include_columns: Optional[Union[List[str], Set[str], Tuple[str, ...], str]] = None,
        exclude_columns: Optional[Union[List[str], Set[str], Tuple[str, ...], str]] = None,
        ignore_non_numeric: bool = False,
    ):
        """Initialize AutoKMeans clusterer.
        
        Args:
            n_clusters: Fixed number of clusters (if provided, skips automatic k-selection)
            max_k: Maximum number of clusters to consider (ignored if n_clusters is provided)
            min_k: Minimum number of clusters to consider (ignored if n_clusters is provided)
            method: Method for selecting optimal k ('silhouette', 'calinski_harabasz', 'davies_bouldin', 'elbow')
            scale: Whether to scale features before clustering
            impute: Whether to impute missing values
            impute_strategy: Strategy for imputation ('mean', 'median', 'most_frequent', 'constant')
            random_state: Random state for reproducibility
            n_init: Number of random initializations for K-means
            include_columns: Columns to include for clustering (if None, uses all numeric columns)
            exclude_columns: Columns to exclude from clustering
            ignore_non_numeric: If True, silently ignore non-numeric columns instead of raising error
        """
        self.n_clusters = n_clusters
        self.max_k = max_k
        self.min_k = min_k
        self.method = method
        self.scale = scale
        self.impute = impute
        self.impute_strategy = impute_strategy
        self.random_state = random_state
        self.n_init = n_init
        self.include_columns = include_columns
        self.exclude_columns = exclude_columns
        self.ignore_non_numeric = ignore_non_numeric
        
        # Will be set during fit
        self._optimal_k = None
        self._kmeans = None
        self._preprocessor = None
        self._feature_columns = None
        self._diagnostics = None
        self._is_fitted = False
    
    def fit(self, X: pd.DataFrame, y=None) -> 'AutoKMeans':
        """Fit the AutoKMeans clusterer.
        
        Determines the optimal number of clusters and fits a K-means model.
        
        Args:
            X: Input DataFrame with features for clustering
            y: Ignored (for sklearn compatibility)
            
        Returns:
            Self for method chaining
            
        Raises:
            TypeError: If X is not a pandas DataFrame
            ValueError: If no numeric columns found or DataFrame is empty
        """
        if not isinstance(X, pd.DataFrame):
            raise TypeError(f"X must be a pandas DataFrame, got {type(X)}")
        
        if X.empty:
            raise ValueError("Input DataFrame is empty")
        
        # Determine which columns to use for clustering
        included_columns = include_exclude_columns(
            X, 
            include_columns=self.include_columns, 
            exclude_columns=self.exclude_columns
        )
        
        self._feature_columns = get_numeric_columns(X[included_columns])
        if len(self._feature_columns) == 0:
            if self.ignore_non_numeric:
                raise ValueError("No numeric columns found for clustering (all columns were ignored)")
            else:
                raise ValueError("No numeric columns found for clustering")
        
        # Extract feature matrix
        X_features = X[self._feature_columns]
        
        # Determine k (either manual or automatic)
        if self.n_clusters is not None:
            # Manual k specification
            self._optimal_k = self.n_clusters
            self._diagnostics = None
        else:
            # Automatic k selection
            self._optimal_k, self._diagnostics = find_optimal_k(
                X_features,
                max_k=self.max_k,
                min_k=self.min_k,
                method=self.method,
                scale=self.scale,
                impute=self.impute,
                impute_strategy=self.impute_strategy,
                random_state=self.random_state,
                n_init=self.n_init
            )
        
        # Create and fit preprocessor
        self._preprocessor = make_preprocessor(
            impute=self.impute,
            impute_strategy=self.impute_strategy,
            scale=self.scale
        )
        
        X_processed = X_features.values
        if self._preprocessor is not None:
            X_processed = self._preprocessor.fit_transform(X_processed)
        
        # Fit K-means with optimal k
        if self._optimal_k == 1:
            # Special case: single cluster
            self._kmeans = None
        else:
            self._kmeans = KMeans(
                n_clusters=self._optimal_k,
                n_init=self.n_init,
                random_state=self.random_state
            )
            self._kmeans.fit(X_processed)
        
        self._is_fitted = True
        return self
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict cluster labels for new data.
        
        Args:
            X: Input DataFrame with same structure as training data
            
        Returns:
            Array of cluster labels
            
        Raises:
            RuntimeError: If fit() has not been called
            TypeError: If X is not a pandas DataFrame
            ValueError: If required columns are missing
        """
        if not self._is_fitted:
            raise RuntimeError("AutoKMeans must be fitted before predict()")
        
        if not isinstance(X, pd.DataFrame):
            raise TypeError(f"X must be a pandas DataFrame, got {type(X)}")
        
        # Check that required columns are present
        missing_cols = [col for col in self._feature_columns if col not in X.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Extract and preprocess features
        X_features = X[self._feature_columns].values
        if self._preprocessor is not None:
            X_features = self._preprocessor.transform(X_features)
        
        # Predict clusters
        if self._optimal_k == 1:
            # Single cluster case
            return np.zeros(len(X), dtype=int)
        else:
            return self._kmeans.predict(X_features)
    
    def fit_predict(self, X: pd.DataFrame, y=None) -> np.ndarray:
        """Fit the model and predict cluster labels in one step.
        
        Args:
            X: Input DataFrame
            y: Ignored (for sklearn compatibility)
            
        Returns:
            Array of cluster labels
        """
        return self.fit(X, y).predict(X)
    
    @property
    def n_clusters_(self) -> Optional[int]:
        """Number of clusters found by the algorithm."""
        return self._optimal_k
    
    @property
    def cluster_centers_(self) -> Optional[np.ndarray]:
        """Cluster centers (only available if n_clusters > 1)."""
        if not self._is_fitted:
            return None
        if self._kmeans is None:
            return None
        return self._kmeans.cluster_centers_
    
    @property
    def inertia_(self) -> Optional[float]:
        """Sum of squared distances to cluster centers."""
        if not self._is_fitted:
            return None
        if self._kmeans is None:
            return 0.0  # Single cluster has zero inertia
        return self._kmeans.inertia_
    
    def get_diagnostics(self) -> Optional[Dict]:
        """Get k-selection diagnostics from the fitting process.
        
        Returns:
            Dictionary with candidate_ks, scores, and inertias, or None if not fitted
        """
        return self._diagnostics
    
    def get_feature_names_out(self) -> Optional[List[str]]:
        """Get the names of features used for clustering.
        
        Returns:
            List of feature column names, or None if not fitted
        """
        return self._feature_columns.copy() if self._feature_columns else None
    
    def __repr__(self) -> str:
        """String representation of AutoKMeans."""
        if self._is_fitted:
            if self.n_clusters is not None:
                return f"AutoKMeans(n_clusters={self._optimal_k})"
            else:
                return f"AutoKMeans(n_clusters={self._optimal_k}, method='{self.method}')"
        else:
            if self.n_clusters is not None:
                return f"AutoKMeans(n_clusters={self.n_clusters})"
            else:
                return f"AutoKMeans(max_k={self.max_k}, method='{self.method}')"
