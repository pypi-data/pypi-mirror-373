"""Find categorical columns in a DataFrame."""

from typing import List
import pandas as pd


def is_categorical_column(values: pd.Series) -> bool:
    """Check if a column contains categorical values.
    
    Args:
        values: Series containing the column values
        
    Returns:
        bool: True if column contains categorical values, False otherwise
        
    Raises:
        TypeError: If values is not a pandas Series
    """
    if not isinstance(values, pd.Series):
        raise TypeError(f"Expected pandas Series, got {type(values)}")
    
    # Check if it's explicitly a categorical dtype
    if isinstance(values.dtype, pd.CategoricalDtype):
        return True
    
    # Check if it's a string/object dtype (potential categorical)
    if pd.api.types.is_string_dtype(values.dtype) or pd.api.types.is_object_dtype(values.dtype):
        return True
    
    return False


def find_categorical_columns(dataframe: pd.DataFrame) -> List[str]:
    """Find columns that contain categorical values.
    
    Args:
        dataframe: DataFrame to analyze
        
    Returns:
        List[str]: List of column names that contain categorical values
        
    Raises:
        TypeError: If dataframe is not a pandas DataFrame
    """
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(dataframe)}")
    
    categorical_columns = []
    
    for column in dataframe.columns:
        if is_categorical_column(values=dataframe[column]):
            categorical_columns.append(column)
    
    return categorical_columns