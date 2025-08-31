

from typing import List, Optional, Callable
import pandas as pd


class BaseEncoder:
    def __init__(
        self, *, 
        columns: Optional[List[str]] = None, drop_original_columns: bool = True,
        column_detection_function: Callable[[pd.DataFrame], List[str]] = None,
        column_conversion_function: Callable[[pd.DataFrame, str], pd.DataFrame] = None
    ):
        self._input_columns = columns
        self._output_columns = None
        self._drop_original_columns = drop_original_columns
        self._column_detection_function = column_detection_function
        self._column_conversion_function = column_conversion_function

    def fit(self, df: pd.DataFrame) -> None:
        detected_columns = self._column_detection_function(df)
        if self._input_columns is None:
            self._input_columns = detected_columns
        else:
            # make sure all the columns are in the detected columns
            for column in self._input_columns:
                if column not in detected_columns:
                    raise KeyError(f"Column {column} not found in the detected columns")
            # detected columns might be more than the original columns
            # we stick to the original columns.
        return self

    def transform(self, df: pd.DataFrame, in_place: bool = False) -> pd.DataFrame:
        if self._input_columns is None:
            raise RuntimeError("fit() must be called before transform()")
        
        if not in_place:
            df = df.copy()

        output_columns = []
        for column in self._input_columns:
            df, column_output = self._column_conversion_function(
                df,
                column=column,
                drop_original_columns=self._drop_original_columns,
                in_place=True,
                return_output_columns=True
            )
            output_columns.extend(column_output)
        self._output_columns = output_columns
        return df
    
    def fit_transform(self, df: pd.DataFrame, in_place: bool = False) -> pd.DataFrame:
        self.fit(df)
        return self.transform(df, in_place)
    
    def get_feature_names_out(self) -> List[str]:
        return self._input_columns