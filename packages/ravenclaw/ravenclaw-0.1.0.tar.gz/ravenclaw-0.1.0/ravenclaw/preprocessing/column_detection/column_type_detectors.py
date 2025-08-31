"""Column type detection utilities for DataFrame analysis."""

from typing import List
import pandas as pd
import numpy as np
from ..utils.sample_size_calculators import calculate_validation_sample_size


def find_categorical_columns(
    dataframe: pd.DataFrame, *,
    include_object: bool = True,
    include_category: bool = True
) -> List[str]:
    """Find categorical columns in a DataFrame.
    
    Identifies columns that are categorical based on data type.
    Includes object and category dtypes.
    
    Args:
        dataframe: The input DataFrame to analyze.
        include_object: Whether to include object dtype columns.
        include_category: Whether to include category dtype columns.
    
    Returns:
        List[str]: List of column names identified as categorical.
    
    Raises:
        TypeError: If dataframe is not a pandas DataFrame.
        TypeError: If include_object or include_category are not boolean.
    """
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(dataframe)}")
    
    if not isinstance(include_object, bool):
        raise TypeError(f"Expected bool for include_object, got {type(include_object)}")
    
    if not isinstance(include_category, bool):
        raise TypeError(f"Expected bool for include_category, got {type(include_category)}")
    
    categorical_columns = []
    
    for column in dataframe.columns:
        dtype = dataframe[column].dtype
        
        # Check explicit categorical dtypes
        if include_category and pd.api.types.is_categorical_dtype(dtype):
            categorical_columns.append(column)
        # Check object dtypes
        elif include_object and dtype == 'object':
            categorical_columns.append(column)
    
    return categorical_columns


def find_numeric_columns(
    dataframe: pd.DataFrame, *,
    include_integers: bool = True,
    include_floats: bool = True,
    exclude_boolean: bool = True
) -> List[str]:
    """Find numeric columns in a DataFrame.
    
    Identifies columns with numeric data types including integers and floats.
    Can optionally exclude boolean columns which are technically numeric.
    
    Args:
        dataframe: The input DataFrame to analyze.
        include_integers: Whether to include integer dtype columns.
        include_floats: Whether to include float dtype columns.
        exclude_boolean: Whether to exclude boolean dtype columns.
    
    Returns:
        List[str]: List of column names identified as numeric.
    
    Raises:
        TypeError: If dataframe is not a pandas DataFrame.
        TypeError: If any boolean parameters are not boolean type.
    """
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(dataframe)}")
    
    if not isinstance(include_integers, bool):
        raise TypeError(f"Expected bool for include_integers, got {type(include_integers)}")
    
    if not isinstance(include_floats, bool):
        raise TypeError(f"Expected bool for include_floats, got {type(include_floats)}")
    
    if not isinstance(exclude_boolean, bool):
        raise TypeError(f"Expected bool for exclude_boolean, got {type(exclude_boolean)}")
    
    numeric_columns = []
    
    for column in dataframe.columns:
        dtype = dataframe[column].dtype
        
        # Exclude boolean columns if requested
        if exclude_boolean and pd.api.types.is_bool_dtype(dtype):
            continue
        
        # Check for integer types
        if include_integers and pd.api.types.is_integer_dtype(dtype):
            numeric_columns.append(column)
        # Check for float types
        elif include_floats and pd.api.types.is_float_dtype(dtype):
            numeric_columns.append(column)
    
    return numeric_columns


def find_date_columns(
    dataframe: pd.DataFrame, *,
    include_datetime: bool = True,
    include_date: bool = True,
    check_object_columns: bool = True
) -> List[str]:
    """Find date/datetime columns in a DataFrame.
    
    Identifies columns containing date or datetime information.
    Can detect both explicit datetime dtypes and object columns that
    contain parseable date strings. Does NOT include time-only columns.
    
    Args:
        dataframe: The input DataFrame to analyze.
        include_datetime: Whether to include datetime dtype columns.
        include_date: Whether to include date dtype columns.
        check_object_columns: Whether to check object columns for
            parseable date strings.
    
    Returns:
        List[str]: List of column names identified as date/datetime.
    
    Raises:
        TypeError: If dataframe is not a pandas DataFrame.
        TypeError: If any boolean parameters are not boolean type.
    """
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(dataframe)}")
    
    if not isinstance(include_datetime, bool):
        raise TypeError(f"Expected bool for include_datetime, got {type(include_datetime)}")
    
    if not isinstance(include_date, bool):
        raise TypeError(f"Expected bool for include_date, got {type(include_date)}")
    
    if not isinstance(check_object_columns, bool):
        raise TypeError(f"Expected bool for check_object_columns, got {type(check_object_columns)}")
    
    date_columns = []
    
    for column in dataframe.columns:
        dtype = dataframe[column].dtype
        
        # Check for explicit datetime/date dtypes
        if include_datetime and pd.api.types.is_datetime64_any_dtype(dtype):
            date_columns.append(column)
        elif include_date and dtype == 'object':
            # Check if it's actually a date column by trying to parse a sample
            if check_object_columns:
                non_null_values = dataframe[column].dropna()
                if len(non_null_values) > 0:
                    # Use random sample for date parsing check
                    sample_size = calculate_validation_sample_size(len(non_null_values))
                    sample_values = non_null_values.sample(n=sample_size, random_state=42) if len(non_null_values) > sample_size else non_null_values
                    try:
                        parsed = pd.to_datetime(sample_values, errors='coerce')
                        # If more than 50% of sample values can be parsed as dates
                        if parsed.notna().sum() / len(sample_values) > 0.5:
                            date_columns.append(column)
                    except (ValueError, TypeError):
                        continue
    
    return date_columns


def find_time_columns(
    dataframe: pd.DataFrame, *,
    include_datetime: bool = True,
    include_time: bool = True,
    check_object_columns: bool = True
) -> List[str]:
    """Find time columns in a DataFrame.
    
    Identifies columns containing time information including datetime
    columns (which contain time components) and pure time columns.
    
    Args:
        dataframe: The input DataFrame to analyze.
        include_datetime: Whether to include datetime dtype columns
            (which contain time components).
        include_time: Whether to include time dtype columns.
        check_object_columns: Whether to check object columns for
            parseable time strings.
    
    Returns:
        List[str]: List of column names identified as containing time.
    
    Raises:
        TypeError: If dataframe is not a pandas DataFrame.
        TypeError: If any boolean parameters are not boolean type.
    """
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(dataframe)}")
    
    if not isinstance(include_datetime, bool):
        raise TypeError(f"Expected bool for include_datetime, got {type(include_datetime)}")
    
    if not isinstance(include_time, bool):
        raise TypeError(f"Expected bool for include_time, got {type(include_time)}")
    
    if not isinstance(check_object_columns, bool):
        raise TypeError(f"Expected bool for check_object_columns, got {type(check_object_columns)}")
    
    time_columns = []
    
    for column in dataframe.columns:
        dtype = dataframe[column].dtype
        
        # Check for datetime dtypes (which include time)
        if include_datetime and pd.api.types.is_datetime64_any_dtype(dtype):
            time_columns.append(column)
        # Check for time dtypes
        elif include_time and pd.api.types.is_timedelta64_dtype(dtype):
            time_columns.append(column)
        elif dtype == 'object' and check_object_columns:
            # Check if it's a time column by looking for time patterns
            non_null_values = dataframe[column].dropna()
            if len(non_null_values) > 0:
                # Use random sample for time pattern check
                sample_size = calculate_validation_sample_size(len(non_null_values))
                sample_values = non_null_values.sample(n=sample_size, random_state=42) if len(non_null_values) > sample_size else non_null_values
                try:
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


def find_day_of_week_columns(
    dataframe: pd.DataFrame, *,
    check_column_names: bool = True,
    check_values: bool = True,
    case_sensitive: bool = False
) -> List[str]:
    """Find columns representing day of the week.
    
    Identifies columns that contain day of the week information either
    through column naming patterns or by analyzing the actual values.
    
    Args:
        dataframe: The input DataFrame to analyze.
        check_column_names: Whether to check column names for day-of-week
            patterns (e.g., 'day_of_week', 'weekday', 'dow').
        check_values: Whether to analyze column values for day-of-week
            patterns (e.g., Monday-Sunday, Mon-Sun, 0-6).
        case_sensitive: Whether column name matching should be case sensitive.
    
    Returns:
        List[str]: List of column names identified as day-of-week.
    
    Raises:
        TypeError: If dataframe is not a pandas DataFrame.
        TypeError: If any boolean parameters are not boolean type.
    """
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(dataframe)}")
    
    if not isinstance(check_column_names, bool):
        raise TypeError(f"Expected bool for check_column_names, got {type(check_column_names)}")
    
    if not isinstance(check_values, bool):
        raise TypeError(f"Expected bool for check_values, got {type(check_values)}")
    
    if not isinstance(case_sensitive, bool):
        raise TypeError(f"Expected bool for case_sensitive, got {type(case_sensitive)}")
    
    day_of_week_columns = []
    
    # Day of week name patterns
    day_name_patterns = ['day_of_week', 'weekday', 'dow', 'day_name', 'week_day']
    full_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    short_days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    
    for column in dataframe.columns:
        column_found = False
        
        # Check column names
        if check_column_names and not column_found:
            column_name = column if case_sensitive else column.lower()
            for pattern in day_name_patterns:
                pattern_check = pattern if case_sensitive else pattern.lower()
                if pattern_check in column_name:
                    day_of_week_columns.append(column)
                    column_found = True
                    break
        
        # Check values
        if check_values and not column_found:
            non_null_values = dataframe[column].dropna()
            if len(non_null_values) > 0:
                # Use our intelligent sampling helper for consistent sampling logic
                from ...utils.sampling_helper import get_intelligent_samples; raise Exception("WRONG. Should not import here") # WRONG, should not import here
                sample_values, _ = get_intelligent_samples(non_null_values, sample_size=100)
                # Convert to string and lowercase for checking
                str_values = sample_values.astype(str)
                if not case_sensitive:
                    str_values = str_values.str.lower()
                
                # Check for day names
                day_matches = 0
                for value in str_values:
                    value_clean = str(value).strip()
                    if value_clean in full_days or value_clean in short_days:
                        day_matches += 1
                
                # Check for numeric day codes (0-6 or 1-7)
                if day_matches == 0 and pd.api.types.is_numeric_dtype(dataframe[column].dtype):
                    unique_values = set(sample_values.dropna())
                    if unique_values.issubset(set(range(7))) or unique_values.issubset(set(range(1, 8))):
                        day_matches = len(sample_values)
                
                # If more than 50% match day patterns, consider it a day-of-week column
                if day_matches / len(sample_values) > 0.5:
                    day_of_week_columns.append(column)
    
    return day_of_week_columns


def find_day_of_year_columns(
    dataframe: pd.DataFrame, *,
    check_column_names: bool = True,
    check_values: bool = True,
    case_sensitive: bool = False
) -> List[str]:
    """Find columns representing day of the year.
    
    Identifies columns that contain day of the year information (1-366)
    either through column naming patterns or by analyzing value ranges.
    
    Args:
        dataframe: The input DataFrame to analyze.
        check_column_names: Whether to check column names for day-of-year
            patterns (e.g., 'day_of_year', 'doy', 'julian_day').
        check_values: Whether to analyze column values for day-of-year
            patterns (integer values between 1 and 366).
        case_sensitive: Whether column name matching should be case sensitive.
    
    Returns:
        List[str]: List of column names identified as day-of-year.
    
    Raises:
        TypeError: If dataframe is not a pandas DataFrame.
        TypeError: If any boolean parameters are not boolean type.
    """
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(dataframe)}")
    
    if not isinstance(check_column_names, bool):
        raise TypeError(f"Expected bool for check_column_names, got {type(check_column_names)}")
    
    if not isinstance(check_values, bool):
        raise TypeError(f"Expected bool for check_values, got {type(check_values)}")
    
    if not isinstance(case_sensitive, bool):
        raise TypeError(f"Expected bool for case_sensitive, got {type(case_sensitive)}")
    
    day_of_year_columns = []
    
    # Day of year name patterns
    day_of_year_patterns = ['day_of_year', 'doy', 'julian_day', 'yearday', 'day_number']
    
    for column in dataframe.columns:
        column_found = False
        
        # Check column names
        if check_column_names and not column_found:
            column_name = column if case_sensitive else column.lower()
            for pattern in day_of_year_patterns:
                pattern_check = pattern if case_sensitive else pattern.lower()
                if pattern_check in column_name:
                    day_of_year_columns.append(column)
                    column_found = True
                    break
        
        # Check values
        if check_values and not column_found and pd.api.types.is_numeric_dtype(dataframe[column].dtype):
            sample_values = dataframe[column].dropna()
            if len(sample_values) > 0:
                min_val = sample_values.min()
                max_val = sample_values.max()
                
                # Check if values are in the range 1-366 (day of year range)
                if min_val >= 1 and max_val <= 366:
                    # Additional check: if we have a reasonable spread of values
                    unique_count = sample_values.nunique()
                    if unique_count > 1:  # More than one unique value
                        day_of_year_columns.append(column)
    
    return day_of_year_columns


def find_hour_of_day_columns(
    dataframe: pd.DataFrame, *,
    check_column_names: bool = True,
    check_values: bool = True,
    case_sensitive: bool = False,
    include_24_hour: bool = True,
    include_12_hour: bool = True
) -> List[str]:
    """Find columns representing hour of the day.
    
    Identifies columns that contain hour of the day information either
    through column naming patterns or by analyzing value ranges for
    both 24-hour (0-23) and 12-hour (1-12) formats.
    
    Args:
        dataframe: The input DataFrame to analyze.
        check_column_names: Whether to check column names for hour-of-day
            patterns (e.g., 'hour', 'hour_of_day', 'hod').
        check_values: Whether to analyze column values for hour-of-day
            patterns.
        case_sensitive: Whether column name matching should be case sensitive.
        include_24_hour: Whether to detect 24-hour format (0-23).
        include_12_hour: Whether to detect 12-hour format (1-12).
    
    Returns:
        List[str]: List of column names identified as hour-of-day.
    
    Raises:
        TypeError: If dataframe is not a pandas DataFrame.
        TypeError: If any boolean parameters are not boolean type.
    """
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(dataframe)}")
    
    if not isinstance(check_column_names, bool):
        raise TypeError(f"Expected bool for check_column_names, got {type(check_column_names)}")
    
    if not isinstance(check_values, bool):
        raise TypeError(f"Expected bool for check_values, got {type(check_values)}")
    
    if not isinstance(case_sensitive, bool):
        raise TypeError(f"Expected bool for case_sensitive, got {type(case_sensitive)}")
    
    if not isinstance(include_24_hour, bool):
        raise TypeError(f"Expected bool for include_24_hour, got {type(include_24_hour)}")
    
    if not isinstance(include_12_hour, bool):
        raise TypeError(f"Expected bool for include_12_hour, got {type(include_12_hour)}")
    
    hour_of_day_columns = []
    
    # Hour of day name patterns
    hour_patterns = ['hour', 'hour_of_day', 'hod', 'hr', 'time_hour']
    
    for column in dataframe.columns:
        column_found = False
        
        # Check column names
        if check_column_names and not column_found:
            column_name = column if case_sensitive else column.lower()
            for pattern in hour_patterns:
                pattern_check = pattern if case_sensitive else pattern.lower()
                if pattern_check in column_name:
                    hour_of_day_columns.append(column)
                    column_found = True
                    break
        
        # Check values
        if check_values and not column_found and pd.api.types.is_numeric_dtype(dataframe[column].dtype):
            sample_values = dataframe[column].dropna()
            if len(sample_values) > 0:
                min_val = sample_values.min()
                max_val = sample_values.max()
                unique_count = sample_values.nunique()
                
                # Check for 24-hour format (0-23)
                if include_24_hour and min_val >= 0 and max_val <= 23 and unique_count > 1:
                    hour_of_day_columns.append(column)
                    column_found = True
                
                # Check for 12-hour format (1-12)
                if not column_found and include_12_hour and min_val >= 1 and max_val <= 12 and unique_count > 1:
                    hour_of_day_columns.append(column)
    
    return hour_of_day_columns
