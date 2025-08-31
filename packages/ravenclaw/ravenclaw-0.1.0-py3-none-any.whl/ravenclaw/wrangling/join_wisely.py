"""
Smart joining utilities for comprehensive DataFrame merge analysis.

This module provides intelligent joining functions that give detailed insights
into merge operations, including what data exists in each DataFrame and what
gets matched during joins.
"""

from typing import Dict, Any, Optional
import pandas as pd


def join_and_keep_order(
    left: pd.DataFrame,
    right: pd.DataFrame,
    remove_duplicates: bool = True,
    keep: str = 'first',
    **kwargs: Any
) -> pd.DataFrame:
    """
    Join two DataFrames while preserving the original row order.
    
    This function performs a merge operation but maintains the original ordering
    of rows from both DataFrames, which is often lost in standard pandas merges.
    
    Args:
        left: Left DataFrame to join
        right: Right DataFrame to join  
        remove_duplicates: Whether to remove duplicate matches
        keep: Which duplicates to keep ('first', 'last', False)
        **kwargs: Additional arguments passed to pandas merge()
        
    Returns:
        Merged DataFrame with original row order preserved
        
    Raises:
        TypeError: If left or right is not a pandas DataFrame
        
    Example:
        >>> left = pd.DataFrame({'key': [1, 2, 3], 'value_left': ['a', 'b', 'c']})
        >>> right = pd.DataFrame({'key': [3, 1, 2], 'value_right': ['x', 'y', 'z']})
        >>> result = join_and_keep_order(left=left, right=right, on='key')
        >>> # Result maintains left DataFrame's original order (1, 2, 3)
    """
    if not isinstance(left, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame for left, got {type(left)}")
    if not isinstance(right, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame for right, got {type(right)}")
    
    # Create copies to avoid modifying originals
    left_copy = left.copy()
    right_copy = right.copy()
    
    # Add temporary ordering columns
    left_copy['_left_id'] = range(left_copy.shape[0])
    right_copy['_right_id'] = range(right_copy.shape[0])
    
    # Perform the merge
    result = left_copy.merge(right=right_copy, **kwargs)
    
    # Restore original order
    result.sort_values(by=['_left_id', '_right_id'], inplace=True)
    
    # Remove duplicates if requested
    if remove_duplicates:
        left_id_mask = ~result['_left_id'].duplicated(keep=keep)
        right_id_mask = ~result['_right_id'].duplicated(keep=keep)
        result = result[left_id_mask & right_id_mask]
    
    # Clean up temporary columns
    result = result.drop(columns=['_left_id', '_right_id'])
    result.reset_index(drop=True, inplace=True)
    
    return result


def join_wisely(
    left: pd.DataFrame,
    right: pd.DataFrame,
    remove_duplicates: bool = True,
    echo: bool = False,
    **kwargs: Any
) -> Dict[str, pd.DataFrame]:
    """
    Perform a comprehensive join analysis between two DataFrames.
    
    This function provides detailed insights into merge operations by returning
    three separate DataFrames: records that match in both, records only in left,
    and records only in right. This is invaluable for data analysis and debugging
    merge operations.
    
    Args:
        left: Left DataFrame to join
        right: Right DataFrame to join
        remove_duplicates: Whether to remove duplicate matches
        echo: Whether to print summary statistics
        **kwargs: Additional arguments passed to pandas merge()
        
    Returns:
        Dictionary containing:
            - 'both': Records that matched in both DataFrames
            - 'left_only': Records that exist only in left DataFrame  
            - 'right_only': Records that exist only in right DataFrame
            
    Raises:
        TypeError: If left or right is not a pandas DataFrame
        
    Example:
        >>> left = pd.DataFrame({'id': [1, 2, 3], 'name': ['Alice', 'Bob', 'Charlie']})
        >>> right = pd.DataFrame({'id': [2, 3, 4], 'age': [25, 30, 35]})
        >>> result = join_wisely(left=left, right=right, on='id', echo=True)
        # Prints: left:(3, 2), right:(3, 2)
        #         both:(2, 3), left_only:(1, 2), right_only:(1, 2)
        >>> result['both']  # Contains Bob and Charlie with ages
        >>> result['left_only']  # Contains Alice without age
        >>> result['right_only']  # Contains person with id=4 without name
    """
    if not isinstance(left, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame for left, got {type(left)}")
    if not isinstance(right, pd.DataFrame):
        raise TypeError(f"Expected pandas DataFrame for right, got {type(right)}")
    
    # Create copies to avoid modifying originals
    left_copy = left.copy()
    right_copy = right.copy()
    
    # Add temporary tracking columns
    left_copy['_left_id'] = range(left_copy.shape[0])
    right_copy['_right_id'] = range(right_copy.shape[0])
    
    # Perform inner join to find matches
    both_data = left_copy.merge(right=right_copy, how='inner', **kwargs)
    
    # Handle duplicates if requested
    if remove_duplicates:
        both_data.sort_values(by=['_left_id', '_right_id'], inplace=True)
        left_id_duplicated = both_data['_left_id'].duplicated(keep='first')
        right_id_duplicated = both_data['_right_id'].duplicated(keep='first')
        both_data = both_data[~left_id_duplicated & ~right_id_duplicated]
    
    # Find records that didn't match
    left_only_data = left_copy[~left_copy['_left_id'].isin(both_data['_left_id'])].copy()
    right_only_data = right_copy[~right_copy['_right_id'].isin(both_data['_right_id'])].copy()
    
    # Clean up temporary columns
    both_data.drop(columns=['_left_id', '_right_id'], inplace=True)
    left_only_data.drop(columns=['_left_id'], inplace=True)
    right_only_data.drop(columns=['_right_id'], inplace=True)
    
    # Reset indices
    both_data.reset_index(drop=True, inplace=True)
    left_only_data.reset_index(drop=True, inplace=True)
    right_only_data.reset_index(drop=True, inplace=True)
    
    # Print summary if requested
    if echo:
        print(f'left:{left.shape}, right:{right.shape}')
        print(f'both:{both_data.shape}, left_only:{left_only_data.shape}, right_only:{right_only_data.shape}')
    
    return {
        'both': both_data,
        'left_only': left_only_data,
        'right_only': right_only_data
    }
