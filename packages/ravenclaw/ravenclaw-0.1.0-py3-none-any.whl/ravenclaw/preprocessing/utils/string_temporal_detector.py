"""
String temporal type detection utility.

This module provides functionality to detect temporal patterns in string pandas Series
and classify them as date, time, datetime, or none.
"""

from typing import Optional, Dict, Any
import pandas as pd
from .sampling_helper import get_intelligent_samples
from .sample_size_calculators import calculate_heuristic_sample_size
from .value_constraints import constrain_value


def _looks_like_temporal_data(series: pd.Series, min_temporal_ratio: float = 0.6) -> bool:
    """
    Quick heuristic to check if data might be temporal to avoid unnecessary warnings.
    
    This function checks if a significant portion of the data looks temporal,
    not just whether ANY data looks temporal. This prevents triggering expensive
    flexible parsing on datasets with high junk ratios.
    
    Uses random sampling to get a representative view of the data quality.
    
    Args:
        series: A pandas Series to check.
        min_temporal_ratio: Minimum ratio of temporal-looking values required (default: 0.6)
        
    Returns:
        bool: True if the data looks like it might contain temporal information
              with sufficient quality to warrant flexible parsing.
    """
    non_null_series = series.dropna()
    if len(non_null_series) == 0:
        return False
    
    # Use random sampling for representative assessment
    # Calculate appropriate sample size using principled method
    heuristic_sample_size = calculate_heuristic_sample_size(len(non_null_series))
    sample_size = constrain_value(value=len(non_null_series), min_value=None, max_value=heuristic_sample_size)
    if len(non_null_series) <= sample_size:
        sample = non_null_series
    else:
        sample = non_null_series.sample(n=sample_size, random_state=42)
    
    temporal_count = 0
    for val in sample:
        val_str = str(val)
        # Check for common temporal indicators
        has_digits = any(char.isdigit() for char in val_str)
        has_separators = any(char in val_str for char in ['-', '/', ':', ' ', 'T'])
        has_temporal_words = any(word in val_str.lower() for word in [
            'jan', 'feb', 'mar', 'apr', 'may', 'jun',
            'jul', 'aug', 'sep', 'oct', 'nov', 'dec',
            'am', 'pm', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'
        ])
        
        if has_digits and (has_separators or has_temporal_words):
            temporal_count += 1
    
    # Only return True if a significant portion looks temporal
    temporal_ratio = temporal_count / len(sample)
    return temporal_ratio >= min_temporal_ratio


def detect_string_temporal_type(series: pd.Series, sample_size: int = 1000) -> Optional[Dict[str, Any]]:
    """
    Detect if a pandas Series of strings contains temporal data.
    
    Analyzes a pandas Series containing string values to determine if they represent
    date, time, or datetime values. Returns None if the series does not contain
    temporal data, or a dictionary with classification and format information if it does.
    
    For large DataFrames, this function uses intelligent sampling to avoid processing
    the entire series, making temporal detection much faster on huge datasets.
    
    Args:
        series: A pandas Series containing string values to analyze.
        sample_size: Maximum number of rows to sample for detection (default: 1000).
                    For series smaller than this, all rows are used.
        
    Returns:
        None if the series does not contain temporal data, otherwise a dictionary with:
        - type: str - One of 'date', 'time', or 'datetime'
        - format: str or None - The detected format string, if identifiable
        - converted_values: pd.Series - The successfully converted temporal values
        
    Raises:
        TypeError: If series is not a pandas Series or does not contain string data.
        
    Examples:
        >>> import pandas as pd
        >>> date_series = pd.Series(['2023-01-01', '2023-01-02', '2023-01-03'])
        >>> result = detect_string_temporal_type(date_series)
        >>> result['type']
        'date'
        
        >>> time_series = pd.Series(['14:30:00', '15:45:30', '09:15:45'])
        >>> result = detect_string_temporal_type(time_series)
        >>> result['type']
        'time'
        
        >>> datetime_series = pd.Series(['2023-01-01 14:30:00', '2023-01-02 15:45:30'])
        >>> result = detect_string_temporal_type(datetime_series)
        >>> result['type']
        'datetime'
        
        >>> # For huge DataFrames, sampling is used automatically
        >>> huge_series = pd.Series(['2023-01-01'] * 1000000)
        >>> result = detect_string_temporal_type(huge_series, sample_size=500)
        >>> result['type']  # Still detects correctly using sample
        'date'
        
        >>> non_temporal = pd.Series(['apple', 'banana', 'cherry'])
        >>> detect_string_temporal_type(non_temporal)
        None
    """
    if not isinstance(series, pd.Series):
        raise TypeError(f"Expected pandas Series, got {type(series)}")
    
    if not pd.api.types.is_object_dtype(series.dtype):
        raise TypeError(f"Expected Series with object dtype (strings), got {series.dtype}")
    
    # Get sample of non-null values for analysis
    non_null_series = series.dropna()
    
    # Use intelligent sampling helper with configurable parameters
    sample_values, validation_series = get_intelligent_samples(
        series=non_null_series,
        sample_size=sample_size,
        small_threshold=50,
        initial_sample_size=200,
        sqrt_multiplier=10.0,
        adaptive_min=50
    )
    if len(sample_values) == 0:
        return None
    
    # Define common temporal formats to try
    datetime_formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M:%S.%f',
        '%m/%d/%Y %H:%M:%S',
        '%d/%m/%Y %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%m/%d/%Y %H:%M',
        '%d/%m/%Y %H:%M',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%S.%f',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%d %I:%M:%S %p',
        '%m/%d/%Y %I:%M:%S %p',
        '%b %d, %Y %I:%M %p',  # Jan 15, 2023 2:30 PM
        '%B %d, %Y %I:%M %p',  # January 15, 2023 2:30 PM
        '%b %d, %Y %I:%M:%S %p',  # Jan 15, 2023 2:30:45 PM
        '%B %d, %Y %I:%M:%S %p'   # January 15, 2023 2:30:45 PM
    ]
    
    date_formats = [
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%Y/%m/%d',
        '%d-%m-%Y',
        '%m-%d-%Y',
        '%B %d, %Y',
        '%b %d, %Y',
        '%d %B %Y',
        '%d %b %Y'
    ]
    
    time_formats = [
        '%H:%M:%S',
        '%H:%M:%S.%f',
        '%H:%M',
        '%I:%M:%S %p',
        '%I:%M %p'
    ]
    
    # Try datetime formats first (most specific)
    for fmt in datetime_formats:
        try:
            converted = pd.to_datetime(sample_values, format=fmt, errors='raise')
            # Check if conversion was successful for most values
            if len(converted) > 0:
                # Verify it actually has time components
                # This is a logical check, not statistical - we need to know if ANY value has time
                has_time_component = False
                for val in converted.dropna():
                    if hasattr(val, 'time') and val.time() != pd.Timestamp('00:00:00').time():
                        has_time_component = True
                        break
                
                if has_time_component:
                    # Convert the validation sample using this format
                    validation_converted = pd.to_datetime(validation_series, format=fmt, errors='coerce')
                    success_rate = (len(validation_converted.dropna()) / len(validation_series))
                    
                    if success_rate >= 0.8:  # At least 80% success rate
                        # Convert the entire series using this format
                        full_converted = pd.to_datetime(series, format=fmt, errors='coerce')
                        return {
                            'type': 'datetime',
                            'format': fmt,
                            'converted_values': full_converted
                        }
        except (ValueError, TypeError):
            continue
    
    # Try date formats
    for fmt in date_formats:
        try:
            converted = pd.to_datetime(sample_values, format=fmt, errors='raise')
            if len(converted) > 0:
                # Validate using sample first
                validation_converted = pd.to_datetime(validation_series, format=fmt, errors='coerce')
                success_rate = (len(validation_converted.dropna()) / len(validation_series))
                
                if success_rate >= 0.8:  # At least 80% success rate
                    # Convert the entire series using this format
                    full_converted = pd.to_datetime(series, format=fmt, errors='coerce')
                    return {
                        'type': 'date',
                        'format': fmt,
                        'converted_values': full_converted
                    }
        except (ValueError, TypeError):
            continue
    
    # Try time formats
    for fmt in time_formats:
        try:
            # For time parsing, we need to create a dummy date
            test_values = ['1900-01-01 ' + str(val) for val in sample_values]
            converted = pd.to_datetime(test_values, format='%Y-%m-%d ' + fmt, errors='raise')
            if len(converted) > 0:
                # Validate using sample first
                validation_test_values = ['1900-01-01 ' + str(val) for val in validation_series.fillna('')]
                validation_converted = pd.to_datetime(validation_test_values, format='%Y-%m-%d ' + fmt, errors='coerce')
                success_rate = (len(validation_converted.dropna()) / len(validation_series))
                
                if success_rate >= 0.8:  # At least 80% success rate
                    # Convert the entire series using this format
                    full_test_values = ['1900-01-01 ' + str(val) for val in series.fillna('')]
                    full_converted = pd.to_datetime(full_test_values, format='%Y-%m-%d ' + fmt, errors='coerce')
                    
                    # Extract just the time component and convert back to Series
                    time_converted = pd.Series(full_converted.time, index=series.index)
                    return {
                        'type': 'time',
                        'format': fmt,
                        'converted_values': time_converted
                    }
        except (ValueError, TypeError):
            continue
    
    # Try flexible parsing as fallback for datetime (only if data looks temporal AND sample quality is good)
    if _looks_like_temporal_data(sample_values):
        try:
            # First check if flexible parsing works well on sample
            flexible_converted = pd.to_datetime(sample_values, format=None, errors='coerce')
            sample_success_rate = flexible_converted.notna().sum() / len(sample_values)
            
            # Only proceed with flexible parsing if sample shows good success rate (≥80%)
            # This prevents warnings on data with high junk ratios
            if sample_success_rate >= 0.8:
                # Check if it has time components
                # This is a logical check, not statistical - we need to know if ANY value has time
                has_time_component = False
                for val in flexible_converted.dropna():
                    if hasattr(val, 'time') and val.time() != pd.Timestamp('00:00:00').time():
                        has_time_component = True
                        break
                
                # Validate using larger sample (this should not warn since we pre-validated quality)
                validation_flexible = pd.to_datetime(validation_series, format=None, errors='coerce')
                success_rate = (len(validation_flexible.dropna()) / len(validation_series))
                
                if success_rate >= 0.8:
                    # Convert full series using flexible parsing
                    full_flexible = pd.to_datetime(series, format=None, errors='coerce')
                    
                    if has_time_component:
                        return {
                            'type': 'datetime',
                            'format': None,  # No specific format identified
                            'converted_values': full_flexible
                        }
                    else:
                        return {
                            'type': 'date',
                            'format': None,  # No specific format identified
                            'converted_values': full_flexible
                        }
        except (ValueError, TypeError):
            pass
    
    # If nothing worked, it's not temporal data
    return None
