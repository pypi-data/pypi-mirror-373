"""Find float columns in a DataFrame."""

from typing import List
import pandas as pd


def is_float_column(values: pd.Series) -> bool:
    """Check if a column contains float values.
    
    Args:
        values: Series containing the column values
        
    Returns:
        bool: True if column contains float values, False otherwise
        
    Raises:
        TypeError: If values is not a pandas Series
    """
    if not isinstance(values, pd.Series):
        raise TypeError(f"Expected pandas Series, got {type(values)}")
    
    return pd.api.types.is_float_dtype(values.dtype)


def find_float_columns(dataframe: pd.DataFrame) -> List[str]:
    """Find columns that contain float values.
    
    Args:
        dataframe: DataFrame to analyze
        
    Returns:
        List[str]: List of column names that contain float values
        
    Raises:
        TypeError: If dataframe is not a pandas DataFrame
    """
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(dataframe)}")
    
    float_columns = []
    
    for column in dataframe.columns:
        if is_float_column(values=dataframe[column]):
            float_columns.append(column)
    
    return float_columns
