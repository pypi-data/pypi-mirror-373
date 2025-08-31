"""Feature engineering module for email data analysis.

This module contains utilities and functions for creating and transforming
features from email data for machine learning and analysis purposes.
"""

from .df_encoders import (
    NonNumericEncoder,
    DayOfWeekEncoder,
    DayOfYearEncoder,
    OneHotEncoder,
    DateToDayOfYearConverter,
    DateToDayOfWeekConverter,
    TimeToHourOfDayConverter,
    DateTimeConverter,
    HourOfDayEncoder
)

__all__ = [
    'NonNumericEncoder',
    'DayOfWeekEncoder',
    'DayOfYearEncoder',
    'OneHotEncoder',
    'DateToDayOfYearConverter',
    'DateToDayOfWeekConverter',
    'TimeToHourOfDayConverter',
    'DateTimeConverter',
    'HourOfDayEncoder',
]