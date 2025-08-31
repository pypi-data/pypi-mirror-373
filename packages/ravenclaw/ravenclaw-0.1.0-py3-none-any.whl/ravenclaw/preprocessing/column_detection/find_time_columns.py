"""Find time columns in a DataFrame."""

from typing import List
import pandas as pd
from ..utils.sample_size_calculators import calculate_validation_sample_size


def find_time_columns(
    dataframe: pd.DataFrame, *,
    include_timedelta: bool = True,
    check_object_columns: bool = True
) -> List[str]:
    """Find time-only columns in a DataFrame.
    
    Identifies columns containing time information but EXCLUDES datetime
    columns (which contain both date and time). Only finds pure time columns.
    
    Args:
        dataframe: The input DataFrame to analyze.
        include_timedelta: Whether to include timedelta dtype columns.
        check_object_columns: Whether to check object columns for
            parseable time strings.
    
    Returns:
        List[str]: List of column names identified as containing time-only data.
    
    Raises:
        TypeError: If dataframe is not a pandas DataFrame.
        TypeError: If any boolean parameters are not boolean type.
    """
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(dataframe)}")
    
    if not isinstance(include_timedelta, bool):
        raise TypeError(f"Expected bool for include_timedelta, got {type(include_timedelta)}")
    
    if not isinstance(check_object_columns, bool):
        raise TypeError(f"Expected bool for check_object_columns, got {type(check_object_columns)}")
    
    time_columns = []
    
    for column in dataframe.columns:
        dtype = dataframe[column].dtype
        
        # EXCLUDE datetime dtypes (they should be handled by find_date_columns)
        if pd.api.types.is_datetime64_any_dtype(dtype):
            continue
            
        # Check for timedelta dtypes (pure time durations)
        if include_timedelta and pd.api.types.is_timedelta64_dtype(dtype):
            time_columns.append(column)
        elif dtype == 'object' and check_object_columns:
            # Check if it's a time-only column by looking for time patterns
            non_null_values = dataframe[column].dropna()
            if len(non_null_values) > 0:
                # Use random sample for time pattern check
                sample_size = calculate_validation_sample_size(len(non_null_values))
                sample_values = non_null_values.sample(n=sample_size, random_state=42) if len(non_null_values) > sample_size else non_null_values
                try:
                    # Try to parse as time-only (not datetime)
                    # First check if it looks like time format
                    sample_str = str(sample_values.iloc[0])
                    
                    # Skip if it looks like a full datetime (contains date info)
                    if any(char in sample_str for char in ['-', '/']):
                        continue
                    
                    # Try to parse as time
                    parsed_times = pd.to_datetime(sample_values, format='%H:%M:%S', errors='coerce')
                    if parsed_times.isna().sum() < len(sample_values):
                        time_columns.append(column)
                        continue
                    
                    # Try other time formats
                    parsed_times = pd.to_datetime(sample_values, format='%H:%M', errors='coerce')
                    if parsed_times.isna().sum() < len(sample_values):
                        time_columns.append(column)
                except (ValueError, TypeError):
                    continue
    
    return time_columns
