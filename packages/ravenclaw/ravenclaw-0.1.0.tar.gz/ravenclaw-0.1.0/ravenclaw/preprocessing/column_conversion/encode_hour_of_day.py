"""Encode hour-of-day columns to cyclical sin/cos features."""

import pandas as pd
from typing import Union


def encode_hour_of_day_to_sin_cos(
    df: pd.DataFrame,
    *,
    column: str,
    suffixes: tuple[str, str] = ('_sin', '_cos'),
    drop_original_columns: bool = True,
    in_place: bool = False,
    return_output_columns: bool = False,
    return_range: bool = False,
    value_range: tuple[int, int] = None
) -> Union[pd.DataFrame, dict]:
    """Encode hour-of-day column to sin and cos components.
    
    Args:
        df: Input DataFrame
        column: Name of hour-of-day column to encode
        suffixes: Tuple of suffixes for sin and cos columns
        drop_original_columns: Whether to drop the original column
        in_place: Whether to modify DataFrame in place
        return_output_columns: Whether to return output column names
        return_range: Whether to return the range used for encoding
        value_range: Specific range to use (min_hour, max_hour). If None, auto-detect.
        
    Returns:
        DataFrame with sin/cos columns, or dictionary with additional info
        
    Raises:
        TypeError: If df is not a pandas DataFrame
        KeyError: If column is not found in DataFrame
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(df)}")
    
    if column not in df.columns:
        raise KeyError(f"Column '{column}' not found in DataFrame")
    
    if not in_place:
        df = df.copy()
    
    sin_col = column + suffixes[0]
    cos_col = column + suffixes[1]
    
    # Determine the range to use
    if value_range is not None:
        # Use provided range
        used_range = value_range
        from .convert_to_sin_cos import convert_to_sin, convert_to_cos
        sin_series = convert_to_sin(df[column], value_range=used_range)
        cos_series = convert_to_cos(df[column], value_range=used_range)
    else:
        # Auto-detect range from data
        clean_values = df[column].dropna()
        if len(clean_values) > 0:
            used_range = (int(clean_values.min()), int(clean_values.max()))
        else:
            used_range = (0, 23)  # Default range for hours
        
        from .convert_to_sin_cos import convert_to_sin, convert_to_cos
        sin_series = convert_to_sin(df[column], value_range=used_range)
        cos_series = convert_to_cos(df[column], value_range=used_range)
    
    df[sin_col] = sin_series
    df[cos_col] = cos_series
    
    if drop_original_columns:
        df.drop(columns=[column], inplace=True)
    
    # Return based on what's requested
    if return_output_columns or return_range:
        result = {'dataframe': df}
        if return_output_columns:
            result['output_columns'] = (sin_col, cos_col)
        if return_range:
            result['range'] = used_range
        return result
    return df
