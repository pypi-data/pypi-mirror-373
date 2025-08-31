"""
Column name standardization utilities for DataFrame preprocessing.

This module provides functions to clean and standardize DataFrame column names,
converting them to consistent snake_case format and removing problematic characters.
"""

import re
from typing import Union, List
import pandas as pd


def remove_non_alphanumeric_lower_and_join(
    column_name: Union[str, List[str], tuple],
    camel_to_snake: bool = True,
    replace_with: str = '_',
    join_by: str = '__',
    ignore_errors: bool = False
) -> str:
    """
    Clean and standardize a column name or list of column names.
    
    This function removes non-alphanumeric characters, converts camelCase to snake_case,
    and ensures consistent formatting for DataFrame column names.
    
    Args:
        column_name: Column name(s) to standardize
        camel_to_snake: Whether to convert camelCase to snake_case
        replace_with: Character to replace non-alphanumeric characters with
        join_by: String to join multiple column names with
        ignore_errors: Whether to ignore processing errors
        
    Returns:
        Standardized column name string
        
    Raises:
        TypeError: If column_name is not a string, list, or tuple
        
    Example:
        >>> remove_non_alphanumeric_lower_and_join('firstName')
        'first_name'
        >>> remove_non_alphanumeric_lower_and_join('User ID (Primary)')
        'user_id_primary'
        >>> remove_non_alphanumeric_lower_and_join(['user', 'name'])
        'user__name'
    """
    if isinstance(column_name, tuple):
        column_name = list(column_name)
    
    # Handle list/tuple input
    if isinstance(column_name, list):
        # Remove empty strings and convert to strings
        column_name = [str(s).strip() for s in column_name if s != '']
        column_name = join_by.join(column_name)
    
    if not isinstance(column_name, str):
        if ignore_errors:
            return str(column_name).lower()
        else:
            raise TypeError(f"Expected string, list, or tuple for column_name, got {type(column_name)}")
    
    try:
        # First pass: replace non-alphanumeric with spaces
        cleaned = re.sub(r'[^a-zA-Z0-9]', ' ', str(column_name))
        cleaned = cleaned.strip()
        
        # Second pass: replace spaces with specified character
        cleaned = re.sub(r'\s+', replace_with, cleaned)
        
        # Convert camelCase to snake_case if requested
        if camel_to_snake:
            cleaned = convert_camel_to_snake(cleaned)
        
        # Convert to lowercase
        cleaned = cleaned.lower()
        
        # Remove leading/trailing underscores and collapse multiple underscores
        cleaned = re.sub(r'^_+|_+$', '', cleaned)
        cleaned = re.sub(r'_+', '_', cleaned)
        
        return cleaned
        
    except Exception as e:
        if ignore_errors:
            print(f'Error was ignored for: "{column_name}" {e}')
            return str(column_name).lower()
        else:
            raise e


def convert_camel_to_snake(text: str) -> str:
    """
    Convert camelCase text to snake_case.
    
    Args:
        text: Text to convert from camelCase to snake_case
        
    Returns:
        Text converted to snake_case
        
    Example:
        >>> convert_camel_to_snake('firstName')
        'first_name'
        >>> convert_camel_to_snake('XMLHttpRequest')
        'xml_http_request'
    """
    # Insert underscore before uppercase letters that follow lowercase letters
    s1 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', text)
    # Insert underscore before uppercase letters that are followed by lowercase letters
    s2 = re.sub('([A-Z])([A-Z][a-z])', r'\1_\2', s1)
    # Convert to lowercase
    return s2.lower()


def standardize_columns(
    data: pd.DataFrame,
    in_place: bool = False,
    camel_to_snake: bool = True
) -> pd.DataFrame:
    """
    Standardize all column names in a DataFrame.
    
    This function cleans and standardizes all column names in a DataFrame,
    converting them to consistent snake_case format and removing problematic
    characters that can cause issues in data processing.
    
    Args:
        data: DataFrame with columns to standardize
        in_place: Whether to modify the DataFrame in place
        camel_to_snake: Whether to convert camelCase to snake_case
        
    Returns:
        DataFrame with standardized column names
        
    Raises:
        TypeError: If data is not a pandas DataFrame
        
    Example:
        >>> df = pd.DataFrame({'First Name': [1, 2], 'userID': [3, 4], 'Email Address (Primary)': [5, 6]})
        >>> standardized = standardize_columns(df)
        >>> list(standardized.columns)
        ['first_name', 'user_id', 'email_address_primary']
    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame, got {type(data)}")
    
    if in_place:
        new_data = data
    else:
        new_data = data.copy()
    
    # Standardize all column names
    new_columns = [
        remove_non_alphanumeric_lower_and_join(
            column_name=col,
            camel_to_snake=camel_to_snake
        )
        for col in new_data.columns
    ]
    
    new_data.columns = new_columns
    
    return new_data
