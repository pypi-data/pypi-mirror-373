from typing import List, Optional
import pandas as pd

from .base_encoder import BaseEncoder
from .df_day_of_week_encoder import DayOfWeekEncoder
from .df_day_of_year_encoder import DayOfYearEncoder
from .df_one_hot_encoder import OneHotEncoder
from .df_date_to_day_of_year_converter import DateToDayOfYearConverter
from .df_time_to_hour_of_day_converter import TimeToHourOfDayConverter
from .df_datetime_converter import DateTimeConverter
from .df_hour_of_day_encoder import HourOfDayEncoder
from ..column_detection import classify_columns



class NonNumericEncoder(BaseEncoder):
    def __init__(
        self, *, 
        columns: Optional[List[str]] = None, 
        drop_original_columns: bool = True,
        drop_datetime_original_columns: bool = True,  # Drop original datetime (converted to useful features)
        drop_date_original_columns: bool = True,      # Drop original date (converted to day-of-year)
        drop_time_original_columns: bool = True,      # Drop original time (converted to hour-of-day)
        drop_hour_of_day_original_columns: bool = False,  # Keep original hour-of-day (converted to hour-of-day)
        drop_day_of_week_original_columns: bool = False,  # Keep day-of-week (useful numeric for ML)
        drop_day_of_year_original_columns: bool = True,  # Drop day-of-year (converted to sin/cos)
        drop_one_hot_original_columns: bool = True,       # Drop categorical (becomes many one-hot columns)
    ):
        super().__init__(
            columns=columns,
            drop_original_columns=drop_original_columns,
            column_detection_function=None,
            column_conversion_function=None
        )
        
        # Converters run first to convert date/time columns to numeric
        self._datetime_converter = DateTimeConverter(
            columns=None,
            drop_original_columns=drop_datetime_original_columns
        )
        self._date_converter = DateToDayOfYearConverter(
            columns=None,
            drop_original_columns=drop_date_original_columns
        )
        self._time_converter = TimeToHourOfDayConverter(
            columns=None,
            drop_original_columns=drop_time_original_columns
        )

        self._hour_of_day_encoder = HourOfDayEncoder(
            columns=None,
            drop_original_columns=drop_hour_of_day_original_columns
        )
        
        # Encoders run after converters on the numeric columns
        self._day_of_week_encoder = DayOfWeekEncoder(
            columns=None,
            drop_original_columns=drop_day_of_week_original_columns
        )
        self._day_of_year_encoder = DayOfYearEncoder(
            columns=None,
            drop_original_columns=drop_day_of_year_original_columns
        )
        self._one_hot_encoder = OneHotEncoder(
            columns=None,
            drop_original_columns=drop_one_hot_original_columns
        )

    def fit(self, df: pd.DataFrame) -> None:
        classified_columns = classify_columns(df)
        
        # Fit converters first (they convert date/time columns to numeric)
        # DateTime converter handles datetime columns (extracts both day-of-year and hour-of-day)
        self._datetime_converter._input_columns = classified_columns['datetime']
        # Date converter handles date-only columns
        self._date_converter._input_columns = classified_columns['date']
        # Time converter handles time-only columns
        self._time_converter._input_columns = classified_columns['time']
        
        if self._datetime_converter._input_columns:
            self._datetime_converter.fit(df)
        if self._date_converter._input_columns:
            self._date_converter.fit(df)
        if self._time_converter._input_columns:
            self._time_converter.fit(df)
        
        # Apply converters to get the transformed DataFrame for encoder fitting
        temp_df = df.copy()
        if self._datetime_converter._input_columns:
            temp_df = self._datetime_converter.transform(temp_df, in_place=True)
        if self._date_converter._input_columns:
            temp_df = self._date_converter.transform(temp_df, in_place=True)
        if self._time_converter._input_columns:
            temp_df = self._time_converter.transform(temp_df, in_place=True)
        
        # Re-classify columns after conversion (date/datetime/time become day_of_year/hour_of_day)
        post_conversion_classified = classify_columns(temp_df)
        
        # Set the input columns for each encoder based on post-conversion classification
        self._hour_of_day_encoder._input_columns = post_conversion_classified.get('hour_of_day', [])
        self._day_of_week_encoder._input_columns = post_conversion_classified['day_of_week']
        self._day_of_year_encoder._input_columns = post_conversion_classified['day_of_year']
        self._one_hot_encoder._input_columns = post_conversion_classified['categorical']
        
        # Fit each encoder on the converted DataFrame
        if self._hour_of_day_encoder._input_columns:
            self._hour_of_day_encoder.fit(temp_df)
        if self._day_of_week_encoder._input_columns:
            self._day_of_week_encoder.fit(temp_df)
        if self._day_of_year_encoder._input_columns:
            self._day_of_year_encoder.fit(temp_df)
        if self._one_hot_encoder._input_columns:
            self._one_hot_encoder.fit(temp_df)
        
        return self

    def transform(self, df: pd.DataFrame, in_place: bool = False) -> pd.DataFrame:
        if not in_place:
            df = df.copy()
        
        output_columns = []
        
        # Apply converters first (date/time -> numeric)
        if self._datetime_converter._input_columns:
            df = self._datetime_converter.transform(df, in_place=True)
            output_columns.extend(self._datetime_converter._output_columns or [])
            
        if self._date_converter._input_columns:
            df = self._date_converter.transform(df, in_place=True)
            output_columns.extend(self._date_converter._output_columns or [])
            
        if self._time_converter._input_columns:
            df = self._time_converter.transform(df, in_place=True)
            output_columns.extend(self._time_converter._output_columns or [])
        
        # Then apply encoders (numeric -> encoded features)
        if self._hour_of_day_encoder._input_columns:
            df = self._hour_of_day_encoder.transform(df, in_place=True)
            output_columns.extend(self._hour_of_day_encoder._output_columns or [])
            
        if self._day_of_week_encoder._input_columns:
            df = self._day_of_week_encoder.transform(df, in_place=True)
            output_columns.extend(self._day_of_week_encoder._output_columns or [])
            
        if self._day_of_year_encoder._input_columns:
            df = self._day_of_year_encoder.transform(df, in_place=True)
            output_columns.extend(self._day_of_year_encoder._output_columns or [])
            
        if self._one_hot_encoder._input_columns:
            df = self._one_hot_encoder.transform(df, in_place=True)
            output_columns.extend(self._one_hot_encoder._output_columns or [])

        self._output_columns = output_columns
        return df

    def get_feature_names_out(self) -> List[str]:
        """Get the names of the output features."""
        return self._output_columns or []
