import pandas as pd
from typing import List, Optional, Set, Tuple


def encode_one_hot_series(
    values: pd.Series, 
    *,
    prefix: Optional[str] = None,
    categories: Optional[List] = None,
    handle_unknown: str = 'ignore'
) -> pd.DataFrame:
    """Encode a series using one-hot encoding with consistent categories.
    
    Args:
        values: The series to encode
        prefix: Prefix for column names
        categories: Known categories to encode. If None, uses unique values from series
        handle_unknown: How to handle unknown categories ('ignore' or 'error')
        
    Returns:
        DataFrame with one-hot encoded columns
    """
    if prefix is None:
        prefix = values.name if values.name else 'feature'
    
    # If no categories provided, learn from the data
    if categories is None:
        categories = sorted(values.dropna().unique())
        # Add nan category if there are any NaN values
        if values.isna().any():
            categories.append('nan')
    
    # Create output DataFrame
    encoded_df = pd.DataFrame(index=values.index)
    
    # Create columns for each category
    for category in categories:
        col_name = f"{prefix}_{category}"
        if category == 'nan':
            # Handle NaN category
            encoded_df[col_name] = values.isna().astype(int)
        else:
            encoded_df[col_name] = (values == category).astype(int)
    
    # Handle unknown categories
    if handle_unknown == 'error':
        known_categories = set(categories)
        if 'nan' in known_categories:
            known_categories.remove('nan')
        unknown = set(values.dropna().unique()) - known_categories
        if unknown:
            raise ValueError(f"Unknown categories found: {unknown}")
    
    return encoded_df


def encode_one_hot(
    df: pd.DataFrame,
    *,
    column: str,
    prefix: Optional[str] = None,
    categories: Optional[List] = None,
    handle_unknown: str = 'ignore',
    drop_original_columns: bool = True,
    in_place: bool = False,
    return_output_columns: bool = False
) -> Tuple[pd.DataFrame, List[str]]:
    """Encode categorical column using one-hot encoding with consistent categories.
    
    Args:
        df: Input DataFrame
        column: Column name to encode
        prefix: Prefix for new column names (defaults to column name)
        categories: Known categories to encode. If None, learns from data
        handle_unknown: How to handle unknown categories ('ignore' or 'error')
        drop_original_columns: Whether to drop the original column
        in_place: Whether to modify DataFrame in place
        return_output_columns: Whether to return output column names
        
    Returns:
        DataFrame (and optionally list of output column names)
    """
    if not in_place:
        df = df.copy()

    # Use column name as prefix if not provided
    if prefix is None:
        prefix = column
    
    # Get one-hot encoded columns
    encoded_df = encode_one_hot_series(
        df[column], 
        prefix=prefix,
        categories=categories,
        handle_unknown=handle_unknown
    )
    
    # Add encoded columns to dataframe
    for col in encoded_df.columns:
        df[col] = encoded_df[col]
    
    # Track output column names
    output_columns = list(encoded_df.columns)
    
    if drop_original_columns:
        df.drop(columns=[column], inplace=True)

    if return_output_columns:
        return df, output_columns
    return df
