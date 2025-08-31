from typing import List, Optional, Dict, Tuple
import pandas as pd

from ..column_detection import find_day_of_year_columns
from ..column_conversion import encode_day_of_year_to_sin_cos
from .base_encoder import BaseEncoder


class DayOfYearEncoder(BaseEncoder):

    def __init__(
        self, *, 
        columns: Optional[List[str]] = None, 
        drop_original_columns: bool = True
    ):
        super().__init__(
            columns=columns, 
            drop_original_columns=drop_original_columns,
            column_detection_function=find_day_of_year_columns,
            column_conversion_function=None  # We'll handle this ourselves
        )
        self._learned_ranges: Dict[str, Tuple[int, int]] = {}

    def fit(self, df: pd.DataFrame) -> 'DayOfYearEncoder':
        """Learn the ranges for each day-of-year column."""
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
            result = encode_day_of_year_to_sin_cos(
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
        """Transform using learned ranges."""
        if self._input_columns is None:
            raise RuntimeError("fit() must be called before transform()")

        if not in_place:
            df = df.copy()

        output_columns = []
        for column in self._input_columns:
            # Use learned range for consistent encoding
            learned_range = self._learned_ranges.get(column, (1, 366))
            
            result = encode_day_of_year_to_sin_cos(
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
