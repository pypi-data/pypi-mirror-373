import pandas as pd
from typing import Optional
from .convert_to_sin_cos import convert_to_sin, convert_to_cos

def _map_day_of_week_to_int(day_of_week) -> Optional[int]:
    if day_of_week is None:
        return None

    mapping = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
        'friday': 4, 'saturday': 5, 'sunday': 6,
        'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3,
        'fri': 4, 'sat': 5, 'sun': 6
    }
    key = day_of_week.lower()
    if key not in mapping:
        raise ValueError(f"Invalid day of week: {day_of_week}")
    return mapping[key]

def convert_day_of_week_to_int(values: pd.Series) -> pd.Series:
    return values.apply(_map_day_of_week_to_int)

def encode_day_of_week_to_sin(values: pd.Series) -> pd.Series:
    range_of_values = None
    if pd.api.types.is_string_dtype(values.dtype) or pd.api.types.is_object_dtype(values.dtype):
        values = convert_day_of_week_to_int(values)
        range_of_values = (0, 6)
    # if we did not convert to int outselves, the range might be 1 to 7, therefore we do not assume 0 to 6
    return convert_to_sin(values, value_range=range_of_values)

def encode_day_of_week_to_cos(values: pd.Series) -> pd.Series:
    range_of_values = None
    if pd.api.types.is_string_dtype(values.dtype) or pd.api.types.is_object_dtype(values.dtype):
        values = convert_day_of_week_to_int(values)
        range_of_values = (0, 6)
    # if we did not convert to int outselves, the range might be 1 to 7, therefore we do not assume 0 to 6
    return convert_to_cos(values, value_range=range_of_values)

def encode_day_of_week_to_sin_cos_series(values: pd.Series) -> tuple[pd.Series, pd.Series]:
    range = None
    if pd.api.types.is_string_dtype(values.dtype) or pd.api.types.is_object_dtype(values.dtype):
        values = convert_day_of_week_to_int(values)
        range = (0, 6)
    # if we did not convert to int outselves, the range might be 1 to 7, therefore we do not assume 0 to 6
    return convert_to_sin(values, value_range=range), convert_to_cos(values, value_range=range)


def encode_day_of_week_to_sin_cos(
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
    if not in_place:
        df = df.copy()

    sin_col = column + suffixes[0]
    cos_col = column + suffixes[1]
    
    # Determine the range to use
    if value_range is not None:
        # Use provided range
        used_range = value_range
        values = df[column]
        if pd.api.types.is_string_dtype(values.dtype) or pd.api.types.is_object_dtype(values.dtype):
            values = convert_day_of_week_to_int(values)
        from .convert_to_sin_cos import convert_to_sin, convert_to_cos
        sin_series = convert_to_sin(values, value_range=used_range)
        cos_series = convert_to_cos(values, value_range=used_range)
    else:
        # Auto-detect range
        values = df[column]
        if pd.api.types.is_string_dtype(values.dtype) or pd.api.types.is_object_dtype(values.dtype):
            values = convert_day_of_week_to_int(values)
            used_range = (0, 6)
        else:
            # Learn range from numeric data
            clean_values = values.dropna()
            if len(clean_values) > 0:
                used_range = (int(clean_values.min()), int(clean_values.max()))
            else:
                used_range = (0, 6)
        
        from .convert_to_sin_cos import convert_to_sin, convert_to_cos
        sin_series = convert_to_sin(values, value_range=used_range)
        cos_series = convert_to_cos(values, value_range=used_range)
    
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