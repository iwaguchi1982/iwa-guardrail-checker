import pandas as pd
import numpy as np

def validate_numeric(series: pd.Series) -> tuple[pd.Series, int]:
    """Converts series to numeric, returning the series and count of failures."""
    numeric_series = pd.to_numeric(series, errors="coerce")
    actual_failures = int(series.notna().sum() - numeric_series.notna().sum())
    return numeric_series, actual_failures

def check_missing(df: pd.DataFrame, columns: list) -> dict:
    """Returns a dictionary of missing counts for specified columns."""
    return {col: int(df[col].isna().sum()) for col in columns if col in df.columns}

def check_event_values(series: pd.Series) -> tuple[list, int]:
    """Returns unique values and count of values outside {0, 1}."""
    unique_raw = series.dropna().unique().tolist()
    unique_str = sorted([str(v) for v in unique_raw])
    
    # Check numeric 0, 1 specifically
    numeric_v = pd.to_numeric(series, errors="coerce")
    invalid_count = int(numeric_v.dropna().map(lambda x: x not in [0, 1, 0.0, 1.0]).sum())
    # Also count ones that couldn't even be turned into numbers
    invalid_count += int(series.notna().sum() - numeric_v.notna().sum())
    return unique_str, invalid_count
