"""
Data wrangling utilities for pandas DataFrames.

This module provides a collection of utilities for common DataFrame operations
including smart joins, column standardization, row splitting, and data organization.
All functions follow the ravenclaw package standards with comprehensive type hints,
Google docstrings, and robust error handling.
"""

from .join_wisely import join_wisely, join_and_keep_order
from .standardize_columns import standardize_columns, convert_camel_to_snake
from .column_reordering import move_columns, bring_to_front, send_to_back
from .split_rows import split_rows
from .select_extreme import select_extreme, select_max, select_min

__all__ = [
    # Smart joining functions
    'join_wisely',
    'join_and_keep_order',
    
    # Column standardization
    'standardize_columns',
    'convert_camel_to_snake',
    
    # Column reordering
    'move_columns',
    'bring_to_front', 
    'send_to_back',
    
    # Row transformation
    'split_rows',
    
    # Extreme value selection
    'select_extreme',
    'select_max',
    'select_min',
]
