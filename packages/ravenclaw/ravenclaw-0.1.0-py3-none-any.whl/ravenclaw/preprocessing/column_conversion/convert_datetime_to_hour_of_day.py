"""Convert datetime columns to hour of day."""

import pandas as pd
from typing import List, Tuple, Optional


def convert_datetime_to_hour_of_day_series(values: pd.Series) -> pd.Series:
    """Convert a datetime Series to hour of day (0-23).
    
    Args:
        values: Series containing datetime values
        
    Returns:
        Series with hour of day values (0-23)
        
    Raises:
        TypeError: If values is not a pandas Series or not datetime type
    """
    if not isinstance(values, pd.Series):
        raise TypeError(f"Expected pandas Series, got {type(values)}")
    
    if not pd.api.types.is_datetime64_any_dtype(values.dtype):
        raise TypeError(f"Expected datetime Series, got {values.dtype}")
    
    # Extract hour of day (0-23)
    hour_of_day = values.dt.hour
    
    return hour_of_day


def convert_datetime_to_hour_of_day(
    df: pd.DataFrame,
    *,
    column: str,
    suffix: str = '_hour_of_day',
    drop_original_columns: bool = True,
    in_place: bool = False,
    return_output_columns: bool = False
) -> pd.DataFrame:
    """Convert datetime column to hour of day.
    
    Args:
        df: Input DataFrame
        column: Name of datetime column to convert
        suffix: Suffix for new column name
        drop_original_columns: Whether to drop the original column
        in_place: Whether to modify DataFrame in place
        return_output_columns: Whether to return output column names
        
    Returns:
        DataFrame with hour of day column (and optionally output column names)
        
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
    
    # Convert to hour of day
    df[new_column] = convert_datetime_to_hour_of_day_series(df[column])
    
    # Drop original column if requested
    if drop_original_columns:
        df.drop(columns=[column], inplace=True)
    
    if return_output_columns:
        return df, [new_column]
    return df
