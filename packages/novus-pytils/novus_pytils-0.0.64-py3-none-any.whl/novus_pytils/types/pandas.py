"""Text and data file operations.

This module provides functions for working with text files, CSV files,
and other data file formats.
"""
import pandas as pd


def to_frame(input) -> pd.DataFrame:
    """Convert input data to a pandas DataFrame.
    
    Args:
        input: A list of lists, dict, or other data structure compatible with pandas DataFrame.
        
    Returns:
        pd.DataFrame: A pandas DataFrame object created from the input data.
    """
    return pd.DataFrame(input)


def write_csv(df: pd.DataFrame, filepath: str) -> None:
    """Write a pandas DataFrame to a CSV file.

    Args:
        df (pd.DataFrame): DataFrame to write to CSV.
        filepath (str): Path to write CSV file.
    """
    df.to_csv(filepath, index=False)