"""Find integer columns in a DataFrame."""

from typing import List
import pandas as pd

def is_integer_or_null(x):
    if x is None or pd.isna(x):
        return True
    return round(x) == x


def is_integer_column(values: pd.Series) -> bool:
    """Check if a column contains integer values.
    
    Accepts both integer dtypes and numeric dtypes where all non-NaN values 
    are integers (i.e., rounding them gives the same value).
    
    Args:
        values: Series containing the column values
        
    Returns:
        bool: True if column contains integer values, False otherwise
        
    Raises:
        TypeError: If values is not a pandas Series
    """
    if not isinstance(values, pd.Series):
        raise TypeError(f"Expected pandas Series, got {type(values)}")
    
    # Accept integer dtypes directly
    if pd.api.types.is_integer_dtype(values.dtype):
        return True

    # Handle all-null series (can be considered integer-compatible)
    if values.isna().all():
        return True

    if not pd.api.types.is_numeric_dtype(values.dtype):
        return False
    
    are_they_integers = values.apply(is_integer_or_null)
    return bool(are_they_integers.all())


def find_integer_columns(dataframe: pd.DataFrame) -> List[str]:
    """Find columns that contain integer values.
    
    Args:
        dataframe: DataFrame to analyze
        
    Returns:
        List[str]: List of column names that contain integer values
        
    Raises:
        TypeError: If dataframe is not a pandas DataFrame
    """
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(dataframe)}")
    
    integer_columns = []
    
    for column in dataframe.columns:
        if is_integer_column(values=dataframe[column]):
            integer_columns.append(column)
    
    return integer_columns
