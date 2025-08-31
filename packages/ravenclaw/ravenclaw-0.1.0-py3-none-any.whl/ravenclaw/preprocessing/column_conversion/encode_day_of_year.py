import pandas as pd
from .convert_to_sin_cos import convert_to_sin, convert_to_cos


def encode_day_of_year_to_sin_cos_series(values: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Encode day of year values to sin and cos components."""
    # Day of year is typically 1-366, but we'll detect the range
    range_of_values = None
    if values.min() >= 0 and values.max() <= 365:
        range_of_values = (0, 365)  # 0-based
    elif values.min() >= 1 and values.max() <= 366:
        range_of_values = (1, 366)  # 1-based
    
    return convert_to_sin(values, value_range=range_of_values), convert_to_cos(values, value_range=range_of_values)


def encode_day_of_year_to_sin_cos(
    df: pd.DataFrame,
    *,
    column: str,
    suffixes: tuple[str, str] = ('_sin', '_cos'),
    drop_original_columns: bool = True,
    in_place: bool = False,
    return_output_columns: bool = False,
    return_range: bool = False,
    value_range: tuple[int, int] = None
) -> pd.DataFrame:
    """Encode day of year column to sin and cos components."""
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
            used_range = (1, 366)  # Default range
        
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
