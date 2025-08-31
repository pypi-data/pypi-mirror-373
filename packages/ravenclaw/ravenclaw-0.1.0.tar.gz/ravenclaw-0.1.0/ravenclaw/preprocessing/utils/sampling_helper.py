"""Intelligent sampling utilities for large DataFrame processing."""

from typing import Tuple
import pandas as pd
from .value_constraints import constrain_value

def get_intelligent_samples(
    series: pd.Series,
    sample_size: int = 1000,
    small_threshold: int = 50,
    initial_sample_size: int = 200,
    sqrt_multiplier: float = 10.0,
    adaptive_min: int = 50
) -> Tuple[pd.Series, pd.Series]:
    """
    Get intelligent samples for temporal detection with adaptive sizing.
    
    This function implements a three-tier sampling strategy based on dataset size:
    - Very small datasets (≤small_threshold): Use all data
    - Medium datasets: Use adaptive sampling based on square root scaling
    - Large datasets: Use fixed sampling sizes for performance
    
    Args:
        series: The pandas Series to sample from (should be non-null values)
        sample_size: Maximum sample size for validation (default: 1000)
        small_threshold: Threshold below which all data is used (default: 50)
        initial_sample_size: Fixed sample size for initial detection in large datasets (default: 200)
        sqrt_multiplier: Multiplier for square root in adaptive sampling (default: 10.0)
        adaptive_min: Minimum sample size for adaptive sampling (default: 50)
        
    Returns:
        Tuple of (sample_values, validation_series):
        - sample_values: Series for initial pattern detection
        - validation_series: Series for validation (success rate calculation)
        
    Examples:
        >>> import pandas as pd
        >>> series = pd.Series(['2023-01-01'] * 1000).dropna()
        >>> sample_vals, validation_vals = get_intelligent_samples(series)
        >>> len(sample_vals)  # Will be 200 for large dataset
        200
        >>> len(validation_vals)  # Will be 1000 (or series length if smaller)
        1000
        
        >>> small_series = pd.Series(['2023-01-01'] * 30).dropna()
        >>> sample_vals, validation_vals = get_intelligent_samples(small_series)
        >>> len(sample_vals) == len(validation_vals) == 30  # Uses all data
        True
    """
    if not isinstance(series, pd.Series):
        raise TypeError(f"Expected pandas Series, got {type(series)}")
    
    total_size = len(series)
    
    if total_size == 0:
        # Empty series - return empty series
        return series, series
    
    
    
    if total_size <= small_threshold:
        # Very small dataset - use everything
        return series, series
    
    elif total_size <= sample_size:
        # Medium dataset - use adaptive sampling
        # For initial detection: use square root of size (statistical rule of thumb)
        # but constrain between adaptive_min and initial_sample_size
        sqrt_based_size = int(total_size ** 0.5 * sqrt_multiplier)
        # First constrain to initial_sample_size limit
        size_limited = constrain_value(value=sqrt_based_size, min_value=None, max_value=initial_sample_size)
        # Then ensure it's at least adaptive_min
        adaptive_sample_size = constrain_value(value=size_limited, min_value=adaptive_min, max_value=None)
        
        # Ensure we don't try to sample more than available
        actual_sample_size = constrain_value(value=adaptive_sample_size, min_value=None, max_value=total_size)
        sample_values = series.sample(n=actual_sample_size, random_state=42)
        validation_series = series  # Use full series for validation
        
    else:
        # Large dataset - use fixed sampling sizes for performance
        # Initial detection: fixed size for pattern diversity
        actual_initial_size = constrain_value(value=initial_sample_size, min_value=None, max_value=total_size)
        sample_values = series.sample(n=actual_initial_size, random_state=42)
        # Validation: user-specified sample_size for statistical confidence
        actual_validation_size = constrain_value(value=sample_size, min_value=None, max_value=total_size)
        validation_series = series.sample(n=actual_validation_size, random_state=42)
    
    return sample_values, validation_series


def calculate_adaptive_sample_size(
    total_size: int,
    sqrt_multiplier: float = 10.0,
    min_size: int = 50,
    max_size: int = 200
) -> int:
    """
    Calculate adaptive sample size based on dataset size using square root scaling.
    
    This implements the statistical rule of thumb: sample size ∝ √(population_size)
    with practical constraints for temporal detection.
    
    Args:
        total_size: Total size of the dataset
        sqrt_multiplier: Multiplier for the square root (default: 10.0)
        min_size: Minimum sample size (default: 50)
        max_size: Maximum sample size (default: 200)
        
    Returns:
        Optimal sample size for the given dataset size
        
    Examples:
        >>> calculate_adaptive_sample_size(100)  # Small dataset
        50
        >>> calculate_adaptive_sample_size(400)  # Medium dataset  
        200
        >>> calculate_adaptive_sample_size(10000)  # Large dataset
        200
    """
    if total_size <= 0:
        return 0
    
    # Square root scaling with multiplier
    adaptive_size = int(total_size ** 0.5 * sqrt_multiplier)
    
    # Apply constraints
    return max(min_size, min(max_size, adaptive_size))



