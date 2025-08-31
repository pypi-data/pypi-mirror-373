"""String temporal converter for detecting and converting string columns to temporal types."""

from typing import List, Optional, Dict, Any
import pandas as pd
import warnings

from .base_encoder import BaseEncoder
from ..utils.string_temporal_detector import detect_string_temporal_type


class StringTemporalConverter(BaseEncoder):
    """Converter that detects string columns containing temporal data and converts them.
    
    This converter analyzes string columns to detect if they contain datetime, date, or time
    data. During fit(), it learns the format of each temporal column. During transform(),
    it converts the string columns to proper temporal types using the learned formats.
    
    Priority order for detection:
    1. datetime (has both date and time components)
    2. date (has only date components)  
    3. time (has only time components)
    
    Examples:
        >>> converter = StringTemporalConverter()
        >>> df = pd.DataFrame({
        ...     'date_str': ['2023-01-15', '2023-06-30'],
        ...     'datetime_str': ['2023-01-15 14:30:00', '2023-06-30 09:15:00'],
        ...     'time_str': ['14:30:00', '09:15:00'],
        ...     'regular_str': ['hello', 'world']
        ... })
        >>> result = converter.fit_transform(df)
        >>> # date_str becomes datetime64 (date), datetime_str becomes datetime64 (datetime)
        >>> # time_str becomes timedelta64 (time), regular_str stays as string
    """
    
    def __init__(
        self,
        *,
        columns: Optional[List[str]] = None,
        drop_original_columns: bool = True,
        priority_order: Optional[List[str]] = None,
        sample_size: int = 1000
    ):
        """Initialize the string temporal converter.
        
        Args:
            columns: Specific columns to process. If None, auto-detects all string columns
            drop_original_columns: Whether to drop original string columns after conversion
            priority_order: Order of temporal type priority. Defaults to ['datetime', 'date', 'time']
            sample_size: Maximum number of rows to sample for temporal detection (default: 1000).
                        For huge DataFrames, this dramatically improves performance.
            
        Raises:
            TypeError: If columns is not a list or None
            ValueError: If priority_order contains invalid temporal types
        """
        if priority_order is None:
            priority_order = ['datetime', 'date', 'time']
        
        valid_types = {'datetime', 'date', 'time'}
        if not all(t in valid_types for t in priority_order):
            invalid_types = [t for t in priority_order if t not in valid_types]
            raise ValueError(f"Invalid temporal types in priority_order: {invalid_types}")
        
        self._priority_order = priority_order
        self._learned_formats: Dict[str, Dict[str, Any]] = {}
        self._is_fitted = False
        self._input_columns = columns
        self._drop_original_columns = drop_original_columns
        
    def _detect_and_learn_string_temporal_columns(self, df: pd.DataFrame, columns_to_check: Optional[List[str]] = None) -> None:
        """Detect string columns that contain temporal data and learn their formats.
        
        Only processes object/string columns - ignores columns that are already
        datetime, date, or time types. Saves format information to _learned_formats.
        
        Args:
            df: Input DataFrame
            columns_to_check: Specific columns to check. If None, checks all columns.
        """
        self._learned_formats = {}
        
        # Determine which columns to check
        if columns_to_check is None:
            columns_to_process = df.columns
        else:
            columns_to_process = [col for col in columns_to_check if col in df.columns]
        
        for column in columns_to_process:
            # Only check object (string) columns - already temporal columns won't be object dtype
            if pd.api.types.is_object_dtype(df[column]):
                # Check if this string column contains temporal data
                temporal_info = detect_string_temporal_type(df[column])
                if temporal_info is not None:
                    # Validate the structure returned by detect_string_temporal_type
                    if not isinstance(temporal_info, dict) or 'type' not in temporal_info:
                        raise TypeError(f"detect_string_temporal_type returned invalid structure for column '{column}': {temporal_info}")
                    
                    # Get the detected type from the utility function
                    detected_type = temporal_info['type']  # 'datetime', 'date', or 'time'
                    
                    # Apply priority order - choose highest priority type that was detected
                    if detected_type in self._priority_order:
                        self._learned_formats[column] = {
                            'temporal_type': detected_type,
                            'format': temporal_info['format'],
                            'converted_values': temporal_info['converted_values']
                        }
    
    def _convert_string_temporal_column(self, series: pd.Series, column_name: str) -> pd.Series:
        """Convert a string column to temporal type using learned format.
        
        Args:
            series: Input string series
            column_name: Name of the column
            
        Returns:
            Converted temporal series
            
        Raises:
            RuntimeError: If converter has not been fitted
            KeyError: If column format was not learned during fit
        """
        if not self._is_fitted:
            raise RuntimeError("StringTemporalConverter must be fitted before transform()")
        
        if column_name not in self._learned_formats:
            raise KeyError(
                f"No learned format for column '{column_name}'. "
                f"Available columns: {list(self._learned_formats.keys())}"
            )
        
        format_info = self._learned_formats[column_name]
        temporal_type = format_info['temporal_type']
        format_string = format_info['format']
        
        try:
            if temporal_type == 'datetime':
                return pd.to_datetime(series, format=format_string, errors='coerce')
            
            elif temporal_type == 'date':
                converted = pd.to_datetime(series, format=format_string, errors='coerce')
                # For date-only, normalize to remove time component
                return converted.dt.normalize()
            
            elif temporal_type == 'time':
                # Convert to datetime first, then extract time as timedelta from midnight
                dt_series = pd.to_datetime(series, format=format_string, errors='coerce')
                
                # Convert to timedelta (time since midnight)
                return pd.to_timedelta(
                    dt_series.dt.hour * 3600 + 
                    dt_series.dt.minute * 60 + 
                    dt_series.dt.second,
                    unit='s'
                )
            
            else:
                raise ValueError(f"Unknown temporal type: {temporal_type}")
                
        except Exception as e:
            warnings.warn(f"Failed to convert column '{column_name}' with format '{format_string}': {e}")
            return series  # Return original if conversion fails
    
    def fit(self, df: pd.DataFrame) -> 'StringTemporalConverter':
        """Fit the converter by learning formats of temporal string columns.
        
        Args:
            df: Input DataFrame to learn from
            
        Returns:
            Self for method chaining
            
        Raises:
            TypeError: If df is not a pandas DataFrame
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Expected pandas DataFrame, got {type(df)}")
        
        # Detect columns and learn formats
        self._detect_and_learn_string_temporal_columns(df, columns_to_check=self._input_columns)
        
        self._is_fitted = True
        return self
    
    def transform(self, df: pd.DataFrame, *, in_place: bool = False) -> pd.DataFrame:
        """Transform string temporal columns to proper temporal types.
        
        Args:
            df: Input DataFrame to transform
            in_place: Whether to modify DataFrame in place
            
        Returns:
            Transformed DataFrame
            
        Raises:
            RuntimeError: If converter has not been fitted
            TypeError: If df is not a pandas DataFrame
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Expected pandas DataFrame, got {type(df)}")
        
        if not self._is_fitted:
            raise RuntimeError("StringTemporalConverter must be fitted before transform()")
        
        if not in_place:
            df = df.copy()
        
        # Transform each learned column
        for column_name in self._learned_formats:
            if column_name in df.columns:
                converted_series = self._convert_string_temporal_column(df[column_name], column_name)
                
                if self._drop_original_columns:
                    # Replace the original column
                    df[column_name] = converted_series
                else:
                    # Keep original and add converted column with suffix
                    df[f"{column_name}_converted"] = converted_series
        
        return df
    
    def fit_transform(self, df: pd.DataFrame, *, in_place: bool = False) -> pd.DataFrame:
        """Fit the converter and transform data in one step.
        
        Args:
            df: Input DataFrame
            in_place: Whether to modify DataFrame in place
            
        Returns:
            Transformed DataFrame
        """
        self.fit(df)
        return self.transform(df, in_place=in_place)
    
    def get_learned_formats(self) -> Dict[str, Dict[str, Any]]:
        """Get the formats learned during fitting.
        
        Returns:
            Dictionary mapping column names to their learned format information
            
        Raises:
            RuntimeError: If converter has not been fitted
        """
        if not self._is_fitted:
            raise RuntimeError("StringTemporalConverter must be fitted before accessing learned formats")
        
        return self._learned_formats.copy()
    
    def get_feature_names_out(self) -> List[str]:
        """Get the names of output features.
        
        Returns:
            List of output column names (same as input for this converter)
        """
        if not self._is_fitted:
            return []
        
        return list(self._learned_formats.keys())
    
    def __repr__(self) -> str:
        """String representation of the converter."""
        if self._is_fitted:
            n_columns = len(self._learned_formats)
            return f"StringTemporalConverter(fitted_columns={n_columns})"
        else:
            return "StringTemporalConverter(not_fitted)"
