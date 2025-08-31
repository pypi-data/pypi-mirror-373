"""Convert date and datetime columns to day-of-week integers."""

from typing import List, Optional, Union, Tuple
import pandas as pd


def convert_date_to_day_of_week_series(values: pd.Series) -> pd.Series:
    """Convert a Series of date/datetime values to day-of-week integers.
    
    Args:
        values: Series containing date or datetime values
        
    Returns:
        Series with day-of-week integers (0=Monday, 6=Sunday)
        
    Raises:
        TypeError: If values is not a pandas Series
        ValueError: If values don't contain date/datetime data
    """
    if not isinstance(values, pd.Series):
        raise TypeError(f"Expected pandas Series, got {type(values)}")
    
    if not pd.api.types.is_datetime64_any_dtype(values.dtype):
        raise ValueError(f"Expected datetime dtype, got {values.dtype}")
    
    # Extract day of week (0=Monday, 6=Sunday)
    day_of_week = values.dt.dayofweek
    
    return day_of_week


def convert_date_to_day_of_week(
    df: pd.DataFrame,
    column: str,
    suffix: str = '_day_of_week',
    drop_original_columns: bool = True,
    in_place: bool = False,
    return_output_columns: bool = False
) -> Union[pd.DataFrame, Tuple[pd.DataFrame, List[str]]]:
    """Convert a date/datetime column to day-of-week integers.
    
    Args:
        df: Input DataFrame
        column: Name of the column to convert
        suffix: Suffix to add to the new column name
        drop_original_columns: Whether to drop the original column
        in_place: Whether to modify the DataFrame in place
        return_output_columns: Whether to return the list of new column names
        
    Returns:
        DataFrame with day-of-week column added, optionally with list of new column names
        
    Raises:
        TypeError: If df is not a pandas DataFrame
        KeyError: If column doesn't exist in DataFrame
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(df)}")
    
    if column not in df.columns:
        raise KeyError(f"Column '{column}' not found in DataFrame")
    
    if not in_place:
        df = df.copy()
    
    # Create new column name
    new_column = f"{column}{suffix}"
    
    # Convert to day-of-week
    df[new_column] = convert_date_to_day_of_week_series(df[column])
    
    # Drop original column if requested
    if drop_original_columns:
        df = df.drop(columns=[column])
    
    output_columns = [new_column]
    
    if return_output_columns:
        return df, output_columns
    return df
