"""Feature engineering pipeline that chains multiple encoders."""

from typing import List, Optional, Union
import pandas as pd

from .base_encoder import BaseEncoder
from .df_datetime_converter import DateTimeConverter
from .df_date_to_day_of_year_converter import DateToDayOfYearConverter
from .df_date_to_day_of_week_converter import DateToDayOfWeekConverter
from .df_time_to_hour_of_day_converter import TimeToHourOfDayConverter
from .df_day_of_week_encoder import DayOfWeekEncoder
from .df_day_of_year_encoder import DayOfYearEncoder
from .df_hour_of_day_encoder import HourOfDayEncoder
from .df_one_hot_encoder import OneHotEncoder
from .df_string_temporal_converter import StringTemporalConverter


class FeatureEngineeringPipeline:
    """Pipeline that chains multiple feature engineering encoders.
    
    This pipeline allows you to compose multiple encoders in sequence,
    providing a clean and modular approach to feature engineering.
    Each encoder focuses on a single responsibility.
    
    Examples:
        >>> # Create a pipeline with specific encoders
        >>> pipeline = FeatureEngineeringPipeline([
        ...     DateTimeConverter(),
        ...     DayOfWeekEncoder(),
        ...     OneHotEncoder()
        ... ])
        >>> 
        >>> # Fit and transform data
        >>> result = pipeline.fit_transform(df)
        
        >>> # Or create a default pipeline for common use cases
        >>> pipeline = FeatureEngineeringPipeline.create_default()
        >>> result = pipeline.fit_transform(df)
    """
    
    def __init__(self, encoders: List[BaseEncoder]):
        """Initialize pipeline with a list of encoders.
        
        Args:
            encoders: List of encoder instances to run in sequence
            
        Raises:
            TypeError: If encoders is not a list or contains non-BaseEncoder items
        """
        if not isinstance(encoders, list):
            raise TypeError(f"Expected list of encoders, got {type(encoders)}")
        
        for i, encoder in enumerate(encoders):
            if not isinstance(encoder, BaseEncoder):
                raise TypeError(f"Encoder at index {i} is not a BaseEncoder, got {type(encoder)}")
        
        self._encoders = encoders
        self._is_fitted = False
        self._output_columns = []
    
    def fit(self, df: pd.DataFrame) -> 'FeatureEngineeringPipeline':
        """Fit all encoders in the pipeline.
        
        Args:
            df: Input DataFrame to fit on
            
        Returns:
            Self for method chaining
            
        Raises:
            TypeError: If df is not a pandas DataFrame
        """
        if len(self._encoders) == 0 and len(self._output_columns) == 0:
            self._is_fitted = True
            return self

        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Expected pandas DataFrame, got {type(df)}")
        
        # Fit each encoder in sequence
        temp_df = df.copy()
        for encoder in self._encoders:
            encoder.fit(temp_df)
            # Transform to get the updated DataFrame for the next encoder
            temp_df = encoder.transform(temp_df, in_place=False)
        
        self._is_fitted = True
        return self
    
    def transform(self, df: pd.DataFrame, *, in_place: bool = False) -> pd.DataFrame:
        """Transform data using all fitted encoders.
        
        Args:
            df: Input DataFrame to transform
            in_place: Whether to modify DataFrame in place
            
        Returns:
            Transformed DataFrame
            
        Raises:
            RuntimeError: If pipeline has not been fitted
            TypeError: If df is not a pandas DataFrame
        """
        if not self._is_fitted:
            raise RuntimeError("Pipeline must be fitted before transform()")

        if len(self._encoders) == 0 and len(self._output_columns) == 0:
            return df
        
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Expected pandas DataFrame, got {type(df)}")
        
        if not in_place:
            df = df.copy()
        
        # Apply each encoder in sequence
        for encoder in self._encoders:
            df = encoder.transform(df, in_place=True)
        
        # Collect output columns from all encoders
        self._output_columns = []
        for encoder in self._encoders:
            if hasattr(encoder, 'get_feature_names_out'):
                encoder_features = encoder.get_feature_names_out()
                if encoder_features:  # Only extend if not empty
                    self._output_columns.extend(encoder_features)
        
        return df
    
    def fit_transform(self, df: pd.DataFrame, *, in_place: bool = False) -> pd.DataFrame:
        """Fit the pipeline and transform data in one step.
        
        Args:
            df: Input DataFrame
            in_place: Whether to modify DataFrame in place
            
        Returns:
            Transformed DataFrame
        """
        self.fit(df)
        return self.transform(df, in_place=in_place)
    
    def get_feature_names_out(self) -> List[str]:
        """Get the names of all output features from all encoders.
        
        Returns:
            List of output column names
        """
        return self._output_columns.copy()
    
    def get_encoders(self) -> List[BaseEncoder]:
        """Get a copy of the encoders in this pipeline.
        
        Returns:
            List of encoder instances
        """
        return self._encoders.copy()
    
    @classmethod
    def create_default(
        cls,
        *,
        include_string_temporal_conversion: bool = True,
        include_datetime_conversion: bool = True,
        include_date_conversion: bool = True,
        include_time_conversion: bool = True,
        include_day_of_week_encoding: bool = True,
        include_day_of_year_encoding: bool = True,
        include_hour_of_day_encoding: bool = True,
        include_one_hot_encoding: bool = True,
        drop_original_temporal: bool = True,
        drop_original_categorical: bool = True
    ) -> 'FeatureEngineeringPipeline':
        """Create a default pipeline with common encoders.
        
        Args:
            include_string_temporal_conversion: Include string temporal converter (first step)
            include_datetime_conversion: Include datetime converter
            include_date_conversion: Include date converter  
            include_time_conversion: Include time converter
            include_day_of_week_encoding: Include day-of-week encoder
            include_day_of_year_encoding: Include day-of-year encoder
            include_hour_of_day_encoding: Include hour-of-day encoder
            include_one_hot_encoding: Include one-hot encoder
            drop_original_temporal: Drop original temporal columns after conversion
            drop_original_categorical: Drop original categorical columns after encoding
            
        Returns:
            Configured pipeline instance
        """
        encoders = []
        
        # String temporal converter (run first to convert string temporal data to proper types)
        if include_string_temporal_conversion:
            encoders.append(StringTemporalConverter(
                columns=None,
                drop_original_columns=drop_original_temporal
            ))
        
        # Temporal converters (run after string conversion to convert temporal data to numeric)
        # Note: We run all temporal feature extraction first, then drop original columns
        if include_datetime_conversion:
            encoders.append(DateTimeConverter(
                columns=None,
                drop_original_columns=False  # Don't drop yet, other converters need the temporal columns
            ))
        
        if include_date_conversion:
            encoders.append(DateToDayOfYearConverter(
                columns=None,
                drop_original_columns=False  # Don't drop yet, DateToDayOfWeekConverter needs the temporal columns
            ))
            encoders.append(DateToDayOfWeekConverter(
                columns=None,
                drop_original_columns=drop_original_temporal  # Now we can drop the original temporal columns
            ))
        
        if include_time_conversion:
            encoders.append(TimeToHourOfDayConverter(
                columns=None,
                drop_original_columns=drop_original_temporal
            ))
        
        # Temporal encoders (convert numeric temporal features to cyclical)
        if include_day_of_week_encoding:
            encoders.append(DayOfWeekEncoder(
                columns=None,
                drop_original_columns=False  # Keep day-of-week as useful numeric
            ))
        
        if include_day_of_year_encoding:
            encoders.append(DayOfYearEncoder(
                columns=None,
                drop_original_columns=True  # Drop after converting to sin/cos
            ))
        
        if include_hour_of_day_encoding:
            encoders.append(HourOfDayEncoder(
                columns=None,
                drop_original_columns=False  # Keep hour-of-day as useful numeric
            ))
        
        # Categorical encoder (run last)
        if include_one_hot_encoding:
            encoders.append(OneHotEncoder(
                columns=None,
                drop_original_columns=drop_original_categorical
            ))
        
        return cls(encoders)
    
    def __repr__(self) -> str:
        """String representation of the pipeline."""
        encoder_names = [type(encoder).__name__ for encoder in self._encoders]
        return f"FeatureEngineeringPipeline({encoder_names})"
