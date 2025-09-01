import csv

import pandas as pd
import os

def csv_to_dataframe(file_path: str, separator=None) -> pd.DataFrame:
    """
    Read a CSV file and return a pandas DataFrame.

    Parameters
    ----------
    file_path : str
        Path to the CSV file.
    separator : str
        The separator used in the CSV file. If None, the separator will be detected automatically.

    Returns
    -------
    pd.DataFrame
        The DataFrame containing the CSV data.

    Raises
    ------
    FileNotFoundError
        If the specified file does not exist.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f'file {file_path} does not exist')

    if separator is None:
        with open(file_path, 'r') as f:
            first_line = f.readline()
        dialect = csv.Sniffer().sniff(first_line)
        separator = dialect.delimiter
    return pd.read_csv(file_path, sep=separator)
