"""DateTime converter that extracts both day-of-year and hour-of-day from datetime columns."""

from typing import List, Optional
import pandas as pd

from .base_encoder import BaseEncoder
from ..column_detection import find_datetime_columns
from ..column_detection.find_date_columns import is_datetime_column
from ..column_conversion import convert_datetime_to_day_of_year, convert_datetime_to_hour_of_day


class DateTimeConverter(BaseEncoder):
    """Converts datetime columns to both day-of-year and hour-of-day integers.
    
    This converter finds datetime columns and extracts both temporal features:
    - Day of year (1-366) 
    - Hour of day (0-23)
    
    This ensures datetime columns are fully processed in one step, avoiding
    conflicts between separate date and time converters.
    """

    def __init__(
        self, *,
        columns: Optional[List[str]] = None,
        drop_original_columns: bool = True,
        day_of_year_suffix: str = '_day_of_year',
        hour_of_day_suffix: str = '_hour_of_day'
    ):
        """Initialize DateTimeConverter.
        
        Args:
            columns: Specific columns to convert. If None, auto-detects datetime columns
            drop_original_columns: Whether to drop original datetime columns after conversion
            day_of_year_suffix: Suffix for day-of-year columns
            hour_of_day_suffix: Suffix for hour-of-day columns
        """
        super().__init__(
            columns=columns,
            drop_original_columns=drop_original_columns,
            column_detection_function=find_datetime_columns,
            column_conversion_function=None  # We'll handle conversion ourselves
        )
        self._day_of_year_suffix = day_of_year_suffix
        self._hour_of_day_suffix = hour_of_day_suffix


    def fit(self, df: pd.DataFrame) -> None:
        """Fit the converter by detecting datetime columns and their formats.
        
        Args:
            df: Input DataFrame to analyze
        """
        # Call parent fit to detect columns
        super().fit(df)
        
        # Store detected columns (no format detection needed)
        # Format detection is handled separately by string temporal analyzers
        
        return self

    def transform(self, df: pd.DataFrame, in_place: bool = False) -> pd.DataFrame:
        """Convert datetime columns to day-of-year and hour-of-day.
        
        Args:
            df: Input DataFrame
            in_place: Whether to modify DataFrame in place
            
        Returns:
            DataFrame with datetime columns converted to day-of-year and hour-of-day
            
        Raises:
            RuntimeError: If fit() has not been called
        """
        if self._input_columns is None:
            raise RuntimeError("fit() must be called before transform()")

        if not in_place:
            df = df.copy()

        output_columns = []

        for column in self._input_columns:
            if column in df.columns:  # Column might have been dropped by previous conversions
                # Extract day of year (don't drop original yet)
                result_doy = convert_datetime_to_day_of_year(
                    df,
                    column=column,
                    suffix=self._day_of_year_suffix,
                    drop_original_columns=False,  # Keep original for hour extraction
                    in_place=True,
                    return_output_columns=True
                )
                df, doy_columns = result_doy
                output_columns.extend(doy_columns)
                
                # Extract hour of day (now we can drop original if requested)
                result_hod = convert_datetime_to_hour_of_day(
                    df,
                    column=column,
                    suffix=self._hour_of_day_suffix,
                    drop_original_columns=self._drop_original_columns,
                    in_place=True,
                    return_output_columns=True
                )
                df, hod_columns = result_hod
                output_columns.extend(hod_columns)

        self._output_columns = output_columns
        return df

    def get_feature_names_out(self) -> List[str]:
        """Get the names of the output features.
        
        Returns:
            List of output column names (day-of-year and hour-of-day columns)
        """
        return self._output_columns or []
