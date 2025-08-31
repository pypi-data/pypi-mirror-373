"""Convert datetime columns to day of year."""

import pandas as pd
from typing import List, Tuple, Optional, Union


def convert_datetime_to_day_of_year_series(values: pd.Series) -> pd.Series:
    """Convert a datetime Series to day of year (1-366).
    
    Args:
        values: Series containing datetime values
        
    Returns:
        Series with day of year values (1-366)
        
    Raises:
        TypeError: If values is not a pandas Series or not datetime type
    """
    if not isinstance(values, pd.Series):
        raise TypeError(f"Expected pandas Series, got {type(values)}")
    
    if not pd.api.types.is_datetime64_any_dtype(values.dtype):
        raise TypeError(f"Expected datetime Series, got {values.dtype}")
    
    # Extract day of year (1-366)
    day_of_year = values.dt.dayofyear
    
    return day_of_year


def convert_datetime_to_day_of_year(
    df: pd.DataFrame,
    *,
    column: str,
    suffix: str = '_day_of_year',
    drop_original_columns: bool = True,
    in_place: bool = False,
    return_output_columns: bool = False
) -> pd.DataFrame:
    """Convert datetime column to day of year.
    
    Args:
        df: Input DataFrame
        column: Name of datetime column to convert
        suffix: Suffix for new column name
        drop_original_columns: Whether to drop the original column
        in_place: Whether to modify DataFrame in place
        return_output_columns: Whether to return output column names
        
    Returns:
        DataFrame with day of year column (and optionally output column names)
        
    Raises:
        TypeError: If df is not a pandas DataFrame or column is not datetime type
        KeyError: If column is not found in DataFrame
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(df)}")
    
    if column not in df.columns:
        raise KeyError(f"Column '{column}' not found in DataFrame")
    
    if not in_place:
        df = df.copy()
    
    # Create new column name
    new_column = column + suffix
    
    # Convert to day of year
    df[new_column] = convert_datetime_to_day_of_year_series(df[column])
    
    # Drop original column if requested
    if drop_original_columns:
        df.drop(columns=[column], inplace=True)
    
    if return_output_columns:
        return df, [new_column]
    return df
