import pandas as pd
import polars as pl


def to_pandas_categories(df: pl.DataFrame | pd.DataFrame) -> pd.DataFrame:
    """
    As of polars 1.32 categories span the entire dtype, not just the values
    To stay compatible with plotnine, we need to remove unused categories.

    Args:
        df (pl.DataFrame): Input polars DataFrame
    Returns:
        pd.DataFrame: pandas DataFrame with unused categories removed
    """
    if isinstance(df, pl.DataFrame):
        pdf = df.to_pandas()
    else:
        pdf = df.copy()
    for col in pdf.select_dtypes(include="category"):
        pdf[col] = pdf[col].cat.remove_unused_categories()
    return pdf
