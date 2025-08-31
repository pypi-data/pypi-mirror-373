"""
Row splitting utilities for DataFrame transformation.

This module provides functions to split delimited values in DataFrame columns
into multiple rows, which is useful for normalizing data that contains
comma-separated or otherwise delimited values.
"""

from typing import Optional
import pandas as pd


def split_rows(
    data: pd.DataFrame,
    by_column: str,
    separator: str = ',',
    split_column_name: Optional[str] = None,
    keep_original: bool = False
) -> pd.DataFrame:
    """
    Split delimited values in a column into multiple rows.
    
    This function takes a DataFrame column containing delimited values and
    creates multiple rows for each delimited value, duplicating other column
    values as needed. This is useful for normalizing data.
    
    Args:
        data: DataFrame containing the column to split
        by_column: Name of the column containing delimited values
        separator: Delimiter used to split values
        split_column_name: Name for the new split column. If None, uses by_column + '_split'
        keep_original: Whether to keep the original column with delimited values
        
    Returns:
        DataFrame with split values as separate rows
        
    Raises:
        TypeError: If data is not a pandas DataFrame
        KeyError: If by_column doesn't exist in the DataFrame
        
    Example:
        >>> df = pd.DataFrame({
        ...     'id': [1, 2],
        ...     'tags': ['python,data,ml', 'sql,analytics'],
        ...     'score': [95, 87]
        ... })
        >>> split_rows(df, by_column='tags')
        # Returns:
        #    id      tags  score
        # 0   1    python     95
        # 1   1      data     95  
        # 2   1        ml     95
        # 3   2       sql     87
        # 4   2 analytics     87
    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(data)}")
    
    if by_column not in data.columns:
        raise KeyError(f"Column '{by_column}' not found in DataFrame")
    
    if split_column_name is None:
        split_column_name = f"{by_column}_split"
    
    # Extract the column to split
    split_data_list = []
    
    for idx, row in data.iterrows():
        original_value = row[by_column]
        if pd.isna(original_value):
            # Handle NaN values by keeping them as single entries
            split_values = [original_value]
        else:
            # Split the value and strip whitespace
            split_values = [val.strip() for val in str(original_value).split(separator)]
            # Remove empty strings that might result from splitting
            split_values = [val for val in split_values if val]
        
        # Create a row for each split value
        for split_val in split_values:
            new_row = row.copy()
            new_row[split_column_name] = split_val
            split_data_list.append(new_row)
    
    # Create the result DataFrame
    if split_data_list:
        result = pd.DataFrame(split_data_list)
    else:
        # Handle empty result case
        result = data.copy()
        result[split_column_name] = result[by_column]
    
    # Handle column management based on keep_original flag
    if not keep_original:
        # Remove original column and rename split column
        if by_column in result.columns:
            result = result.drop(columns=[by_column])
        result = result.rename(columns={split_column_name: by_column})
    
    # Reset index
    result = result.reset_index(drop=True)
    
    return result
