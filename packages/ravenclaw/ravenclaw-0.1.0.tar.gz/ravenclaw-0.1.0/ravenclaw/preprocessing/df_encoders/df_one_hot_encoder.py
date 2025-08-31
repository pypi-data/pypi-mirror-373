from typing import List, Optional, Dict
import pandas as pd

from ..column_detection import find_categorical_columns
from ..column_conversion import encode_one_hot
from ..utils.string_temporal_detector import detect_string_temporal_type
from .base_encoder import BaseEncoder


class OneHotEncoder(BaseEncoder):

    def __init__(
        self, *, 
        columns: Optional[List[str]] = None, 
        drop_original_columns: bool = True,
        handle_unknown: str = 'ignore'
    ):
        super().__init__(
            columns=columns, 
            drop_original_columns=drop_original_columns,
            column_detection_function=find_categorical_columns,
            column_conversion_function=None  # We'll handle this ourselves
        )
        self._handle_unknown = handle_unknown
        self._learned_categories: Dict[str, List] = {}

    def fit(self, df: pd.DataFrame) -> 'OneHotEncoder':
        """Learn the categories for each column."""
        # First, detect columns if not provided
        detected_columns = self._column_detection_function(df)
        
        # Validate that no object columns contain date-like strings
        for column in detected_columns:
            temporal_info = detect_string_temporal_type(df[column])
            if temporal_info is not None and temporal_info.get('type') in ['datetime', 'date', 'time']:
                raise ValueError(f"Column '{column}' contains date/time strings but should have been converted to proper temporal types before one-hot encoding. This indicates a pipeline configuration error.")
        
        if self._input_columns is None:
            self._input_columns = detected_columns
        else:
            # Validate that specified columns are in detected columns
            for column in self._input_columns:
                if column not in detected_columns:
                    raise KeyError(f"Column {column} not found in the detected columns")

        # Learn categories for each column
        self._learned_categories = {}
        for column in self._input_columns:
            # Get unique categories, sorted for consistency
            categories = sorted(df[column].dropna().unique())
            # Add nan category if there are any NaN values
            if df[column].isna().any():
                categories.append('nan')
            self._learned_categories[column] = categories

        return self

    def transform(self, df: pd.DataFrame, in_place: bool = False) -> pd.DataFrame:
        """Transform using learned categories."""
        if self._input_columns is None:
            raise RuntimeError("fit() must be called before transform()")

        if not in_place:
            df = df.copy()

        output_columns = []
        for column in self._input_columns:
            # Use learned categories for consistent encoding
            categories = self._learned_categories.get(column, None)
            
            df, column_output = encode_one_hot(
                df,
                column=column,
                categories=categories,
                handle_unknown=self._handle_unknown,
                drop_original_columns=self._drop_original_columns,
                in_place=True,
                return_output_columns=True
            )
            output_columns.extend(column_output)
            
        self._output_columns = output_columns
        return df
