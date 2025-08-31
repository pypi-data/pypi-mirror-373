"""Find date and datetime columns in a DataFrame."""

from typing import List, Union
import pandas as pd
from ..utils.sample_size_calculators import calculate_component_analysis_sample_size


def is_datetime_column(values: pd.Series) -> bool:
    """Check if a column contains datetime values (both date and time).
    
    Args:
        values: Series containing the column values
        
    Returns:
        bool: True if column contains datetime values, False otherwise
        
    Raises:
        TypeError: If values is not a pandas Series
    """
    if not isinstance(values, pd.Series):
        raise TypeError(f"Expected pandas Series, got {type(values)}")
    
    # Only check if it's already datetime dtype - no string parsing
    if pd.api.types.is_datetime64_any_dtype(values.dtype):
        # Check if it has time component (not just date)
        non_null_values = values.dropna()
        if len(non_null_values) == 0:
            return True  # Assume datetime if we can't check
        
        # Use random sample for time component check
        sample_size = calculate_component_analysis_sample_size(len(non_null_values))
        sample_values = non_null_values.sample(n=sample_size, random_state=42) if len(non_null_values) > sample_size else non_null_values
        
        # Check if any values have non-zero time components
        for val in sample_values:
            if hasattr(val, 'time') and val.time() != pd.Timestamp('00:00:00').time():
                return True
        
        return False
    
    # No string parsing - only work with proper datetime types
    return False


def is_date_only_column(values: pd.Series) -> bool:
    """Check if a column contains date-only values (no time component).
    
    Args:
        values: Series containing the column values
        
    Returns:
        bool: True if column contains date-only values, False otherwise
        
    Raises:
        TypeError: If values is not a pandas Series
    """
    if not isinstance(values, pd.Series):
        raise TypeError(f"Expected pandas Series, got {type(values)}")
    
    # Only check if it's already datetime dtype - no string parsing
    if pd.api.types.is_datetime64_any_dtype(values.dtype):
        # Check if it has NO time component (just date)
        non_null_values = values.dropna()
        if len(non_null_values) == 0:
            return False
        
        # Use random sample for time component check
        sample_size = calculate_component_analysis_sample_size(len(non_null_values))
        sample_values = non_null_values.sample(n=sample_size, random_state=42) if len(non_null_values) > sample_size else non_null_values
        
        # Check if all values have zero time components
        for val in sample_values:
            if hasattr(val, 'time') and val.time() != pd.Timestamp('00:00:00').time():
                return False
        
        return True
    
    # No string parsing - only work with proper datetime types
    return False


def find_datetime_columns(dataframe: pd.DataFrame) -> List[str]:
    """Find columns that contain datetime values (both date and time).
    
    Args:
        dataframe: DataFrame to analyze
        
    Returns:
        List[str]: List of column names that contain datetime values
        
    Raises:
        TypeError: If dataframe is not a pandas DataFrame
    """
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(dataframe)}")
    
    datetime_columns = []
    
    for column in dataframe.columns:
        if is_datetime_column(values=dataframe[column]):
            datetime_columns.append(column)
    
    return datetime_columns


def find_date_columns(dataframe: pd.DataFrame) -> List[str]:
    """Find columns that contain date-only values (no time component).
    
    Args:
        dataframe: DataFrame to analyze
        
    Returns:
        List[str]: List of column names that contain date-only values
        
    Raises:
        TypeError: If dataframe is not a pandas DataFrame
    """
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(dataframe)}")
    
    date_columns = []
    
    for column in dataframe.columns:
        if is_date_only_column(values=dataframe[column]):
            date_columns.append(column)
    
    return date_columns