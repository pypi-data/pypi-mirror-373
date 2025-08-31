"""
DataFrame column reordering utilities.

This module provides functions to reorder DataFrame columns, bringing specific
columns to the front or sending them to the back for better data organization
and analysis workflows.
"""

from typing import List, Optional, Literal
import pandas as pd


def move_columns(
    data: pd.DataFrame,
    to: Literal['front', 'back'],
    columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Move specified columns to the front or back of a DataFrame.
    
    This function reorders DataFrame columns by moving the specified columns
    to either the front or back, while maintaining the relative order of
    other columns.
    
    Args:
        data: DataFrame to reorder columns for
        to: Where to move the columns ('front' or 'back')
        columns: List of column names to move. If None, returns original DataFrame
        
    Returns:
        DataFrame with reordered columns
        
    Raises:
        TypeError: If data is not a pandas DataFrame
        ValueError: If 'to' is not 'front' or 'back'
        KeyError: If any specified columns don't exist in the DataFrame
        
    Example:
        >>> df = pd.DataFrame({'a': [1, 2], 'b': [3, 4], 'c': [5, 6], 'd': [7, 8]})
        >>> move_columns(df, to='front', columns=['c', 'd'])
        # Returns DataFrame with columns: ['c', 'd', 'a', 'b']
        >>> move_columns(df, to='back', columns=['a'])
        # Returns DataFrame with columns: ['b', 'c', 'd', 'a']
    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(data)}")
    
    if to not in ['front', 'back']:
        raise ValueError(f"Parameter 'to' must be 'front' or 'back', got '{to}'")
    
    if columns is None:
        columns = []
    
    # Remove duplicates while preserving order
    seen = set()
    columns = [col for col in columns if not (col in seen or seen.add(col))]
    
    # Validate that all specified columns exist
    missing_columns = [col for col in columns if col not in data.columns]
    if missing_columns:
        raise KeyError(f"Columns not found in DataFrame: {missing_columns}")
    
    # Get columns that are not being moved
    other_columns = [col for col in data.columns if col not in columns]
    
    if to == 'front':
        new_column_order = columns + other_columns
    else:  # to == 'back'
        new_column_order = other_columns + columns
    
    return data[new_column_order]


def bring_to_front(
    data: pd.DataFrame,
    columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Bring specified columns to the front of a DataFrame.
    
    This is a convenience function that moves the specified columns to the
    beginning of the DataFrame while maintaining the relative order of other columns.
    
    Args:
        data: DataFrame to reorder columns for
        columns: List of column names to bring to front. If None, returns original DataFrame
        
    Returns:
        DataFrame with specified columns moved to front
        
    Raises:
        TypeError: If data is not a pandas DataFrame
        KeyError: If any specified columns don't exist in the DataFrame
        
    Example:
        >>> df = pd.DataFrame({'a': [1, 2], 'b': [3, 4], 'c': [5, 6]})
        >>> bring_to_front(df, columns=['c', 'b'])
        # Returns DataFrame with columns: ['c', 'b', 'a']
    """
    return move_columns(data=data, to='front', columns=columns)


def send_to_back(
    data: pd.DataFrame,
    columns: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Send specified columns to the back of a DataFrame.
    
    This is a convenience function that moves the specified columns to the
    end of the DataFrame while maintaining the relative order of other columns.
    
    Args:
        data: DataFrame to reorder columns for
        columns: List of column names to send to back. If None, returns original DataFrame
        
    Returns:
        DataFrame with specified columns moved to back
        
    Raises:
        TypeError: If data is not a pandas DataFrame
        KeyError: If any specified columns don't exist in the DataFrame
        
    Example:
        >>> df = pd.DataFrame({'a': [1, 2], 'b': [3, 4], 'c': [5, 6]})
        >>> send_to_back(df, columns=['a'])
        # Returns DataFrame with columns: ['b', 'c', 'a']
    """
    return move_columns(data=data, to='back', columns=columns)
