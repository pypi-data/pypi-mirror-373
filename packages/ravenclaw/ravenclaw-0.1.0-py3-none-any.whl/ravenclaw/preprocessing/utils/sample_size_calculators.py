"""Sample size calculation utilities for data analysis operations.

This module provides functions to calculate appropriate sample sizes for various
data analysis operations like validation, heuristic checks, and component analysis.
"""

from .value_constraints import constrain_value


def calculate_heuristic_sample_size(data_size: int) -> int:
    """Calculate appropriate sample size for heuristic quality checks.
    
    Uses square root of data size (common statistical practice) with reasonable bounds.
    This is suitable for quick quality assessments where we need a representative
    sample but speed is important.
    
    Args:
        data_size: Total size of the dataset
        
    Returns:
        int: Appropriate sample size for heuristic checks
        
    Raises:
        TypeError: If data_size is not an integer
    """
    if not isinstance(data_size, int):
        raise TypeError(f"Expected int for data_size, got {type(data_size)}")
    
    # Use square root for statistical representativeness, constrained to reasonable bounds
    sqrt_based_size = int(data_size ** 0.5)
    return constrain_value(value=sqrt_based_size, min_value=10, max_value=50)


def calculate_validation_sample_size(data_size: int) -> int:
    """Calculate appropriate sample size for pattern validation checks.
    
    For validation operations, we need enough samples to be confident about patterns
    but not so many that processing becomes slow. This is suitable for operations
    like checking if data matches expected formats or patterns.
    
    Args:
        data_size: Total size of the dataset
        
    Returns:
        int: Appropriate sample size for validation checks
        
    Raises:
        TypeError: If data_size is not an integer
    """
    if not isinstance(data_size, int):
        raise TypeError(f"Expected int for data_size, got {type(data_size)}")
    
    # For validation, use all data for small datasets, reasonable limit for large ones
    return constrain_value(value=data_size, min_value=None, max_value=15)


def calculate_component_analysis_sample_size(data_size: int) -> int:
    """Calculate appropriate sample size for component analysis checks.
    
    For analyzing components or properties of data (like checking for time components
    in datetime data), we need enough samples to be confident about the presence
    or absence of specific characteristics.
    
    Args:
        data_size: Total size of the dataset
        
    Returns:
        int: Appropriate sample size for component analysis
        
    Raises:
        TypeError: If data_size is not an integer
    """
    if not isinstance(data_size, int):
        raise TypeError(f"Expected int for data_size, got {type(data_size)}")
    
    # For component analysis, use reasonable sample that gives confidence
    return constrain_value(value=data_size, min_value=None, max_value=25)


def calculate_parsing_sample_size(data_size: int) -> int:
    """Calculate appropriate sample size for parsing validation checks.
    
    For operations that involve parsing data (like checking if strings can be
    parsed as dates or times), we need enough samples to be confident about
    parseability but not so many that parsing becomes slow.
    
    Args:
        data_size: Total size of the dataset
        
    Returns:
        int: Appropriate sample size for parsing validation
        
    Raises:
        TypeError: If data_size is not an integer
    """
    if not isinstance(data_size, int):
        raise TypeError(f"Expected int for data_size, got {type(data_size)}")
    
    # For parsing validation, balance confidence with performance
    return constrain_value(value=data_size, min_value=None, max_value=12)
