"""Convert time columns to hour of day."""

import pandas as pd
from typing import List, Tuple, Optional


def convert_time_to_hour_of_day_series(values: pd.Series) -> pd.Series:
    """Convert a time Series to hour of day (0-23).
    
    Args:
        values: Series containing time, datetime, or timedelta values
        
    Returns:
        Series with hour of day values (0-23)
        
    Raises:
        TypeError: If values is not a pandas Series or not time/datetime/timedelta type
    """
    if not isinstance(values, pd.Series):
        raise TypeError(f"Expected pandas Series, got {type(values)}")
    
    # Handle different time formats
    if pd.api.types.is_datetime64_any_dtype(values.dtype):
        # Already datetime, extract hour directly
        hour_of_day = values.dt.hour
    elif pd.api.types.is_timedelta64_dtype(values.dtype):
        # Timedelta, convert to total seconds then to hours
        total_seconds = values.dt.total_seconds()
        hour_of_day = (total_seconds // 3600).astype(int) % 24
    else:
        raise TypeError(f"Expected datetime or timedelta Series, got {values.dtype}")
    
    return hour_of_day


def convert_time_to_hour_of_day(
    df: pd.DataFrame,
    *,
    column: str,
    suffix: str = '_hour_of_day',
    drop_original_columns: bool = True,
    in_place: bool = False,
    return_output_columns: bool = False
) -> pd.DataFrame:
    """Convert time column to hour of day.
    
    Args:
        df: Input DataFrame
        column: Name of time column to convert
        suffix: Suffix for new column name
        drop_original_columns: Whether to drop the original column
        in_place: Whether to modify DataFrame in place
        return_output_columns: Whether to return output column names
        
    Returns:
        DataFrame with hour of day column (and optionally output column names)
        
    Raises:
        TypeError: If df is not a pandas DataFrame or column is not time/datetime/timedelta type
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
    df[new_column] = convert_time_to_hour_of_day_series(df[column])
    
    # Drop original column if requested
    if drop_original_columns:
        df.drop(columns=[column], inplace=True)
    
    if return_output_columns:
        return df, [new_column]
    return df
