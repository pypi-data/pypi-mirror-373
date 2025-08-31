"""Hour-of-day encoder that converts hour-of-day columns to cyclical sin/cos features."""

from typing import List, Optional, Dict, Tuple
import pandas as pd

from ..column_detection import find_hour_of_day_columns
from ..column_conversion import encode_hour_of_day_to_sin_cos
from .base_encoder import BaseEncoder


class HourOfDayEncoder(BaseEncoder):
    """Encodes hour-of-day columns to cyclical sin/cos features.
    
    This encoder finds hour-of-day columns (0-23) and converts them to 
    sine and cosine components to preserve the cyclical nature of hours.
    """

    def __init__(
        self, *,
        columns: Optional[List[str]] = None,
        drop_original_columns: bool = True
    ):
        """Initialize HourOfDayEncoder.
        
        Args:
            columns: Specific columns to encode. If None, auto-detects hour-of-day columns
            drop_original_columns: Whether to drop original columns after encoding
        """
        super().__init__(
            columns=columns,
            drop_original_columns=drop_original_columns,
            column_detection_function=find_hour_of_day_columns,
            column_conversion_function=None  # We'll handle this ourselves
        )
        self._learned_ranges: Dict[str, Tuple[int, int]] = {}

    def fit(self, df: pd.DataFrame) -> 'HourOfDayEncoder':
        """Learn the ranges for each hour-of-day column.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Self for method chaining
        """
        # First, detect columns if not provided
        detected_columns = self._column_detection_function(df)
        if self._input_columns is None:
            self._input_columns = detected_columns
        else:
            # Validate that specified columns are in detected columns
            for column in self._input_columns:
                if column not in detected_columns:
                    raise KeyError(f"Column {column} not found in the detected columns")

        # Learn ranges for each column using the conversion function
        self._learned_ranges = {}
        for column in self._input_columns:
            # Use the conversion function to learn the range
            result = encode_hour_of_day_to_sin_cos(
                df.copy(),
                column=column,
                drop_original_columns=False,
                in_place=False,
                return_output_columns=True,
                return_range=True
            )
            self._learned_ranges[column] = result['range']

        return self

    def transform(self, df: pd.DataFrame, in_place: bool = False) -> pd.DataFrame:
        """Transform using learned ranges.
        
        Args:
            df: Input DataFrame
            in_place: Whether to modify DataFrame in place
            
        Returns:
            DataFrame with hour-of-day columns encoded to sin/cos
            
        Raises:
            RuntimeError: If fit() has not been called
        """
        if self._input_columns is None:
            raise RuntimeError("fit() must be called before transform()")

        if not in_place:
            df = df.copy()

        output_columns = []
        for column in self._input_columns:
            # Use learned range for consistent encoding
            learned_range = self._learned_ranges.get(column, (0, 23))

            result = encode_hour_of_day_to_sin_cos(
                df,
                column=column,
                drop_original_columns=self._drop_original_columns,
                in_place=True,
                return_output_columns=True,
                value_range=learned_range
            )
            df = result['dataframe']
            output_columns.extend(result['output_columns'])

        self._output_columns = output_columns
        return df

    def get_feature_names_out(self) -> List[str]:
        """Get the names of the output features.
        
        Returns:
            List of output column names (sin/cos columns)
        """
        return self._output_columns or []
