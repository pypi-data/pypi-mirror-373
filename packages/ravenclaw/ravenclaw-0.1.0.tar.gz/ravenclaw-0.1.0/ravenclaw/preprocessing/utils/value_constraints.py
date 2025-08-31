"""General utility functions for constraining values within bounds."""


def constrain_value(
    value: int, *,
    min_value: int = None,
    max_value: int = None
) -> int:
    """
    Constrain a value within min/max bounds.
    
    This centralizes the common pattern of min(max_value, max(min_value, value))
    to eliminate repetitive min-max logic throughout the codebase.
    
    Args:
        value: The value to constrain. Can be positive or negative. No need to check for 0.
        min_value: Minimum acceptable value (None to ignore minimum)
        max_value: Maximum acceptable value (None to ignore maximum)
        
    Returns:
        Constrained value within bounds
        
    Examples:
        >>> constrain_value(value=5, min_value=10, max_value=100)
        10  # Raised to minimum
        >>> constrain_value(value=50, min_value=10, max_value=100) 
        50  # Within bounds, unchanged
        >>> constrain_value(value=150, min_value=10, max_value=100)
        100  # Capped at maximum
        >>> constrain_value(value=150, min_value=None, max_value=100)
        100  # Only apply max constraint
        >>> constrain_value(value=5, min_value=10, max_value=None)
        10  # Only apply min constraint
        >>> constrain_value(value=50, min_value=None, max_value=None)
        50  # No constraints, unchanged
    """
    if max_value is None and min_value is None:
        raise ValueError("max_value and min_value cannot both be None")
    elif max_value is not None and min_value is not None:
        if max_value < min_value:
            raise ValueError("max_value must be greater than or equal to min_value")
    
    result = value
    
    # Apply minimum constraint if specified
    if min_value is not None:
        result = max(min_value, result)
    
    # Apply maximum constraint if specified
    if max_value is not None:
        result = min(max_value, result)
    
    return result
