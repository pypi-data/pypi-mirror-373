"""
Extreme value selection utilities for DataFrame analysis.

This module provides functions to find rows with minimum or maximum values
in specified columns, with support for groupby operations for more complex
data analysis scenarios.
"""

from typing import Optional, Union, List, Literal
import pandas as pd


def _find_max_row(data: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Find the row with the maximum value in the specified column.
    
    Args:
        data: DataFrame to search
        column: Column name to find maximum value for
        
    Returns:
        DataFrame containing the row with maximum value
    """
    if len(data) == 0:
        return data.copy()
    
    max_idx = data[column].idxmax()
    return data[data.index == max_idx]


def _find_min_row(data: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Find the row with the minimum value in the specified column.
    
    Args:
        data: DataFrame to search
        column: Column name to find minimum value for
        
    Returns:
        DataFrame containing the row with minimum value
    """
    if len(data) == 0:
        return data.copy()
    
    min_idx = data[column].idxmin()
    return data[data.index == min_idx]


def select_extreme(
    data: pd.DataFrame,
    column: str,
    group_by: Optional[Union[str, List[str]]] = None,
    extreme_type: Literal['max', 'min'] = 'max'
) -> pd.DataFrame:
    """
    Select rows with extreme (minimum or maximum) values in a specified column.
    
    This function finds rows containing the minimum or maximum values in a
    specified column, with optional groupby functionality for finding extremes
    within groups.
    
    Args:
        data: DataFrame to search for extreme values
        column: Column name to find extreme values for
        group_by: Column name(s) to group by before finding extremes
        extreme_type: Whether to find 'max' or 'min' values
        
    Returns:
        DataFrame containing rows with extreme values
        
    Raises:
        TypeError: If data is not a pandas DataFrame
        KeyError: If column or group_by columns don't exist in DataFrame
        ValueError: If extreme_type is not 'max' or 'min'
        
    Example:
        >>> df = pd.DataFrame({
        ...     'category': ['A', 'A', 'B', 'B'],
        ...     'value': [10, 20, 15, 5],
        ...     'name': ['x', 'y', 'z', 'w']
        ... })
        >>> select_extreme(df, column='value', extreme_type='max')
        # Returns row with value=20 (global maximum)
        >>> select_extreme(df, column='value', group_by='category', extreme_type='max')
        # Returns rows with value=20 (max in category A) and value=15 (max in category B)
    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(data)}")
    
    if column not in data.columns:
        raise KeyError(f"Column '{column}' not found in DataFrame")
    
    if extreme_type not in ['max', 'min']:
        raise ValueError(f"extreme_type must be 'max' or 'min', got '{extreme_type}'")
    
    # Validate group_by columns if provided
    if group_by is not None:
        if isinstance(group_by, str):
            group_by_cols = [group_by]
        else:
            group_by_cols = list(group_by)
        
        missing_cols = [col for col in group_by_cols if col not in data.columns]
        if missing_cols:
            raise KeyError(f"Group by columns not found in DataFrame: {missing_cols}")
    
    # Select appropriate function based on extreme type
    if extreme_type == 'max':
        find_func = _find_max_row
    else:
        find_func = _find_min_row
    
    # Apply function with or without groupby
    if group_by is None:
        result = find_func(data=data, column=column)
    else:
        # Clean approach: Find extreme values per group, then join with original data
        if extreme_type == 'max':
            extreme_values = data.groupby(group_by)[column].idxmax()
        else:
            extreme_values = data.groupby(group_by)[column].idxmin()
        
        # Get the full rows for these extreme indices
        result = data.loc[extreme_values].reset_index(drop=True)
    
    return result


def select_max(
    data: pd.DataFrame,
    max_column: str,
    group_by: Optional[Union[str, List[str]]] = None
) -> pd.DataFrame:
    """
    Select rows with maximum values in the specified column.
    
    This is a convenience function that finds rows containing the maximum
    values in a specified column, with optional groupby functionality.
    
    Args:
        data: DataFrame to search for maximum values
        max_column: Column name to find maximum values for
        group_by: Column name(s) to group by before finding maximums
        
    Returns:
        DataFrame containing rows with maximum values
        
    Raises:
        TypeError: If data is not a pandas DataFrame
        KeyError: If max_column or group_by columns don't exist in DataFrame
        
    Example:
        >>> df = pd.DataFrame({
        ...     'team': ['A', 'A', 'B', 'B'],
        ...     'score': [85, 92, 78, 88],
        ...     'player': ['Alice', 'Bob', 'Charlie', 'David']
        ... })
        >>> select_max(df, max_column='score')
        # Returns row with Bob's score of 92 (global maximum)
        >>> select_max(df, max_column='score', group_by='team')
        # Returns Bob (92) for team A and David (88) for team B
    """
    return select_extreme(
        data=data,
        column=max_column,
        group_by=group_by,
        extreme_type='max'
    )


def select_min(
    data: pd.DataFrame,
    min_column: str,
    group_by: Optional[Union[str, List[str]]] = None
) -> pd.DataFrame:
    """
    Select rows with minimum values in the specified column.
    
    This is a convenience function that finds rows containing the minimum
    values in a specified column, with optional groupby functionality.
    
    Args:
        data: DataFrame to search for minimum values
        min_column: Column name to find minimum values for
        group_by: Column name(s) to group by before finding minimums
        
    Returns:
        DataFrame containing rows with minimum values
        
    Raises:
        TypeError: If data is not a pandas DataFrame
        KeyError: If min_column or group_by columns don't exist in DataFrame
        
    Example:
        >>> df = pd.DataFrame({
        ...     'department': ['Sales', 'Sales', 'IT', 'IT'],
        ...     'salary': [50000, 60000, 70000, 65000],
        ...     'employee': ['Alice', 'Bob', 'Charlie', 'David']
        ... })
        >>> select_min(df, min_column='salary')
        # Returns Alice with salary 50000 (global minimum)
        >>> select_min(df, min_column='salary', group_by='department')
        # Returns Alice (50000) for Sales and David (65000) for IT
    """
    return select_extreme(
        data=data,
        column=min_column,
        group_by=group_by,
        extreme_type='min'
    )
