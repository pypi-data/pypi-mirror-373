"""Time converter that converts time-only columns to hour-of-day."""

from typing import List, Optional
import pandas as pd

from .base_encoder import BaseEncoder
from ..column_detection import find_time_columns
from ..column_conversion import convert_time_to_hour_of_day


class TimeToHourOfDayConverter(BaseEncoder):
    """Converts time-only columns to hour-of-day integers.
    
    This converter finds time-only columns (not datetime) and converts them to 
    hour-of-day values (0-23). For datetime columns, use DateTimeConverter instead.
    """

    def __init__(
        self, *,
        columns: Optional[List[str]] = None,
        drop_original_columns: bool = True
    ):
        """Initialize TimeConverter.
        
        Args:
            columns: Specific columns to convert. If None, auto-detects datetime/time columns
            drop_original_columns: Whether to drop original datetime/time columns after conversion
        """
        super().__init__(
            columns=columns,
            drop_original_columns=drop_original_columns,
            column_detection_function=None,  # We'll handle detection ourselves
            column_conversion_function=None  # We'll handle conversion ourselves
        )

    def fit(self, df: pd.DataFrame) -> 'TimeToHourOfDayConverter':
        """Learn which columns to convert.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Self for method chaining
        """
        if self._input_columns is None:
            # Auto-detect time-only columns (not datetime)
            self._input_columns = find_time_columns(df)
        else:
            # Validate that specified columns exist
            for column in self._input_columns:
                if column not in df.columns:
                    raise KeyError(f"Column '{column}' not found in DataFrame")

        return self

    def transform(self, df: pd.DataFrame, in_place: bool = False) -> pd.DataFrame:
        """Convert time-only columns to hour-of-day.
        
        Args:
            df: Input DataFrame
            in_place: Whether to modify DataFrame in place
            
        Returns:
            DataFrame with time-only columns converted to hour-of-day
            
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
                # Use time converter for time-only columns
                result = convert_time_to_hour_of_day(
                    df,
                    column=column,
                    drop_original_columns=self._drop_original_columns,
                    in_place=True,
                    return_output_columns=True
                )
                df, new_columns = result
                output_columns.extend(new_columns)

        self._output_columns = output_columns
        return df

    def get_feature_names_out(self) -> List[str]:
        """Get the names of the output features.
        
        Returns:
            List of output column names
        """
        return self._output_columns or []
