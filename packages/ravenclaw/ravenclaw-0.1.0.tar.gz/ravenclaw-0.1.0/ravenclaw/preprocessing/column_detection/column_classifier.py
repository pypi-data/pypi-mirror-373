from typing import List, Dict
import pandas as pd
from .find_date_columns import find_datetime_columns, find_date_columns
from .find_time_columns import find_time_columns
from .find_day_of_week_columns import find_day_of_week_columns, find_day_of_year_columns, find_hour_of_day_columns
from .find_categorical_columns import find_categorical_columns


def classify_columns(df: pd.DataFrame) -> Dict[str, List[str]]:
    datetime_columns = find_datetime_columns(df)
    date_columns = find_date_columns(df)
    time_columns = find_time_columns(df)
    day_of_week_columns = find_day_of_week_columns(df)
    day_of_year_columns = find_day_of_year_columns(df)
    hour_of_day_columns = find_hour_of_day_columns(df)
    categorical_columns = find_categorical_columns(df)

    # these lists should be disjoint - priority order: datetime > date > time > day_of_week > day_of_year > hour_of_day > categorical
    all_columns = []
    all_columns.extend(datetime_columns)

    date_columns = [col for col in date_columns if col not in all_columns]
    all_columns.extend(date_columns)

    time_columns = [col for col in time_columns if col not in all_columns]
    all_columns.extend(time_columns)

    day_of_week_columns = [col for col in day_of_week_columns if col not in all_columns]
    all_columns.extend(day_of_week_columns)

    day_of_year_columns = [col for col in day_of_year_columns if col not in all_columns]
    all_columns.extend(day_of_year_columns)

    hour_of_day_columns = [col for col in hour_of_day_columns if col not in all_columns]
    all_columns.extend(hour_of_day_columns)

    categorical_columns = [col for col in categorical_columns if col not in all_columns]
    all_columns.extend(categorical_columns)

    return {
        'datetime': datetime_columns,
        'date': date_columns,
        'time': time_columns,
        'day_of_week': day_of_week_columns,
        'day_of_year': day_of_year_columns,
        'hour_of_day': hour_of_day_columns,
        'categorical': categorical_columns
    }