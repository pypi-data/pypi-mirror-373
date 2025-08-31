"""Find numeric columns in a DataFrame."""

from typing import List
import pandas as pd


def is_numeric_column(values: pd.Series) -> bool:
    """Check if a column contains numeric values (integer or float).
    
    Args:
        values: Series containing the column values
        
    Returns:
        bool: True if column contains numeric values, False otherwise
        
    Raises:
        TypeError: If values is not a pandas Series
    """
    if not isinstance(values, pd.Series):
        raise TypeError(f"Expected pandas Series, got {type(values)}")
    
    return pd.api.types.is_numeric_dtype(values.dtype)


def find_numeric_columns(dataframe: pd.DataFrame) -> List[str]:
    """Find columns that contain numeric values (integer or float).
    
    Args:
        dataframe: DataFrame to analyze
        
    Returns:
        List[str]: List of column names that contain numeric values
        
    Raises:
        TypeError: If dataframe is not a pandas DataFrame
    """
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(dataframe)}")
    
    numeric_columns = []
    
    for column in dataframe.columns:
        if is_numeric_column(values=dataframe[column]):
            numeric_columns.append(column)
    
    return numeric_columns