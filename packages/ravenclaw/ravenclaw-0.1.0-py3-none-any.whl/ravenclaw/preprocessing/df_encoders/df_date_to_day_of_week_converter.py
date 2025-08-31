"""Date to day-of-week converter that converts date-only columns to day-of-week."""

from typing import List, Optional
import pandas as pd

from .base_encoder import BaseEncoder
from ..column_detection import find_date_columns, find_datetime_columns
from ..column_conversion import convert_date_to_day_of_week


class DateToDayOfWeekConverter(BaseEncoder):
    """Converts date and datetime columns to day-of-week integers.
    
    This converter finds both date-only and datetime columns and converts them to 
    day-of-week values (0-6 for Monday-Sunday). It extracts the day-of-week component from both types.
    """

    def __init__(
        self, *,
        columns: Optional[List[str]] = None,
        drop_original_columns: bool = True
    ):
        """Initialize DateToDayOfWeekConverter.
        
        Args:
            columns: Specific columns to convert. If None, auto-detects date and datetime columns
            drop_original_columns: Whether to drop original date/datetime columns after conversion
        """
        super().__init__(
            columns=columns,
            drop_original_columns=drop_original_columns,
            column_detection_function=None,  # We'll handle detection ourselves
            column_conversion_function=None  # We'll handle conversion ourselves
        )

    def fit(self, df: pd.DataFrame) -> 'DateToDayOfWeekConverter':
        """Learn which columns to convert.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Self for method chaining
        """
        if self._input_columns is None:
            # Auto-detect both date-only and datetime columns
            date_columns = find_date_columns(df)
            datetime_columns = find_datetime_columns(df)
            self._input_columns = list(set(date_columns + datetime_columns))
        else:
            # Validate that specified columns exist
            for column in self._input_columns:
                if column not in df.columns:
                    raise KeyError(f"Column '{column}' not found in DataFrame")

        return self

    def transform(self, df: pd.DataFrame, in_place: bool = False) -> pd.DataFrame:
        """Convert date and datetime columns to day-of-week.
        
        Args:
            df: Input DataFrame
            in_place: Whether to modify DataFrame in place
            
        Returns:
            DataFrame with date/datetime columns converted to day-of-week
            
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
                # Convert date to day-of-week using convert_date_to_day_of_week
                result = convert_date_to_day_of_week(
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
