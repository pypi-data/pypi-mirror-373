import re
from libadalina_core.sedona_utils import DataFrame
from libadalina_core.readers.geopackage import geopackage_to_dataframe
from libadalina_core.readers.csv import csv_to_dataframe

def read_dataset(dataset_path: str) -> DataFrame:
    """
    Read a dataset from a file, supporting both GeoPackage (.gpkg) and CSV (.csv) formats.

    Parameters
    ----------
    dataset_path : str
        Path to the dataset file

    Returns
    -------
    DataFrame
        The loaded dataset as a DataFrame
    """
    # Extract optional layer names from brackets at end of path
    match = re.search(r'\[(.*)\]$', dataset_path)
    optional_layer = match.group(1) if match else None

    # Remove layer specification before getting extension
    path_without_layers = dataset_path.split('[')[0] if '[' in dataset_path else dataset_path

    file_extension = path_without_layers.lower().split('.')[-1]

    if file_extension == 'gpkg':
        return geopackage_to_dataframe(dataset_path, optional_layer)
    elif file_extension == 'csv':
        return csv_to_dataframe(dataset_path)
    else:
        raise ValueError(f"Unsupported file extension: {file_extension}. Supported extensions are: .gpkg, .csv")
