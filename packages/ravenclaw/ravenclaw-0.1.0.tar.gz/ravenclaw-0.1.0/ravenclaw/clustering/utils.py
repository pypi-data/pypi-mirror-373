"""Utility functions for clustering operations."""

from typing import List, Set, Tuple, Union, Optional
import pandas as pd
import numpy as np


def get_numeric_columns(df: pd.DataFrame) -> List[str]:
    """Get list of numeric column names from a DataFrame.
    
    Args:
        df: Input DataFrame
        
    Returns:
        List of column names that contain numeric data
        
    Raises:
        TypeError: If df is not a pandas DataFrame
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(df)}")
    
    return df.select_dtypes(include=[np.number]).columns.tolist()


def include_exclude_columns(
    df: pd.DataFrame,
    *,
    include_columns: Optional[Union[List[str], Set[str], Tuple[str, ...], str]] = None,
    exclude_columns: Optional[Union[List[str], Set[str], Tuple[str, ...], str]] = None
) -> List[str]:
    """Filter DataFrame columns based on include/exclude criteria.
    
    Args:
        df: Input DataFrame
        include_columns: Columns to include (if None, includes all columns)
        exclude_columns: Columns to exclude (applied after include)
        
    Returns:
        List of column names after applying include/exclude filters
        
    Raises:
        TypeError: If df is not a pandas DataFrame
        ValueError: If specified columns don't exist in DataFrame
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(df)}")
    
    # Start with all columns or specified include columns
    if include_columns is None:
        result_columns = list(df.columns)
    else:
        # Convert to list if needed
        if isinstance(include_columns, str):
            include_list = [include_columns]
        else:
            include_list = list(include_columns)
        
        # Validate that all included columns exist
        missing_cols = [col for col in include_list if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Include columns not found in DataFrame: {missing_cols}")
        
        result_columns = include_list
    
    # Apply exclusions
    if exclude_columns is not None:
        # Convert to list if needed
        if isinstance(exclude_columns, str):
            exclude_list = [exclude_columns]
        else:
            exclude_list = list(exclude_columns)
        
        # Remove excluded columns
        result_columns = [col for col in result_columns if col not in exclude_list]
    
    return result_columns
