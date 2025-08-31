"""Find day-of-week columns in a DataFrame."""

from typing import List, Union
import pandas as pd

def _check_pattern(string: str, list_of_patterns: List[str]) -> bool:
    """Check if a string matches any pattern in a list of patterns."""
    for pattern in list_of_patterns:
        if pattern in string:
            return True
    return False

def _check_range(values: pd.Series, min_value: int, max_value: int, type: str='int') -> bool:
    """if type is int and values are not int, return False"""
    if not isinstance(values, pd.Series):
        raise TypeError(f"Expected pandas Series, got {type(values)}")

    if type == 'int':
        if not pd.api.types.is_numeric_dtype(values.dtype):
            return False
    
    # Drop NaN values before checking range
    clean_values = values.dropna()
    if len(clean_values) == 0:
        return False
    
    return min_value <= clean_values.min() and max_value >= clean_values.max()

def _check_values(values: pd.Series, acceptable_values: List[str]) -> bool:
    if not isinstance(values, pd.Series):
        raise TypeError(f"Expected pandas Series, got {type(values)}")
    
    unique_values = set(values.dropna())
    acceptable_values_set = set(acceptable_values)
    return unique_values.issubset(acceptable_values_set)


_DAY_OF_WEEK_COLUMN_NAME_PATTERNS = ['day_of_week', 'weekday', 'dow', 'day_name', 'week_day', 'day_0_to_6', 'day_1_to_7']
_DAY_OF_WEEK_VALUES = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
_DAY_OF_WEEK_VALUES_SHORT = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
_DAY_OF_YEAR_COLUMN_NAME_PATTERNS = ['day_of_year', 'doy', 'day_0_to_365', 'day_1_to_366']
_HOUR_OF_DAY_COLUMN_NAME_PATTERNS = ['hour_of_day', 'hod', 'hour']

def _is_day_of_week_column(column_name: str, values: pd.Series) -> bool:
    """Check if values match day-of-week patterns."""
    if not isinstance(values, pd.Series):
        raise TypeError(f"Expected pandas Series, got {type(values)}")
    
    if not _check_pattern(column_name, _DAY_OF_WEEK_COLUMN_NAME_PATTERNS):
        return False
    
    # if is numeric
    if pd.api.types.is_numeric_dtype(values.dtype):
        if _check_range(values, 0, 6, 'int') or _check_range(values, 1, 7, 'int'):
            return True
    
    # if is string or object dtype (which often contains strings)
    if pd.api.types.is_string_dtype(values.dtype) or pd.api.types.is_object_dtype(values.dtype):
        if _check_values(values, _DAY_OF_WEEK_VALUES + _DAY_OF_WEEK_VALUES_SHORT):
            return True
    
    return False

def _is_day_of_year_column(column_name: str, values: pd.Series) -> bool:
    """Check if values match day-of-year patterns."""
    if not isinstance(values, pd.Series):
        raise TypeError(f"Expected pandas Series, got {type(values)}")
    
    if not _check_pattern(column_name, _DAY_OF_YEAR_COLUMN_NAME_PATTERNS):
        return False
    return _check_range(values, 1, 366, 'int') or _check_range(values, 0, 365, 'int')

def _is_hour_of_day_column(column_name: str, values: pd.Series) -> bool:
    """Check if values match hour-of-day patterns."""
    if not isinstance(values, pd.Series):
        raise TypeError(f"Expected pandas Series, got {type(values)}")
    
    if not _check_pattern(column_name, _HOUR_OF_DAY_COLUMN_NAME_PATTERNS):
        return False
    return _check_range(values, 0, 23, 'int') or _check_range(values, 1, 24, 'int')

def find_day_of_week_columns(dataframe: pd.DataFrame) -> List[str]:

    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(dataframe)}")
    
    day_of_week_columns = []
    
    for column in dataframe.columns:
        if _is_day_of_week_column(column, values=dataframe[column]):
            day_of_week_columns.append(column)
    
    return day_of_week_columns

def find_day_of_year_columns(dataframe: pd.DataFrame) -> List[str]:
    """Find columns representing day of the year."""
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(dataframe)}")

    day_of_year_columns = []
    
    for column in dataframe.columns:
        if _is_day_of_year_column(column, values=dataframe[column]):
            day_of_year_columns.append(column)
    
    return day_of_year_columns

def find_hour_of_day_columns(
    dataframe: pd.DataFrame
) -> List[str]:
    """Find columns representing hour of the day."""
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(dataframe)}")

    hour_of_day_columns = []
    
    for column in dataframe.columns:
        if _is_hour_of_day_column(column, values=dataframe[column]):
            hour_of_day_columns.append(column)
    
    return hour_of_day_columns