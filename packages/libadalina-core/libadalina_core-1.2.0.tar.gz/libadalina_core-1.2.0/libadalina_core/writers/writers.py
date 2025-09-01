import pandas as pd
import geopandas as gpd
import pyspark.sql as ps

from libadalina_core.sedona_utils import DEFAULT_EPSG, DataFrame

def dataframe_to_csv(df: DataFrame, path: str, separator: str = ','):
    if isinstance(df, ps.DataFrame):
        df = df.toPandas()
    elif isinstance(df, gpd.GeoDataFrame):
        df = pd.DataFrame(df)
    elif isinstance(df, pd.DataFrame):
        pass # already a Pandas DataFrame
    else:
        raise TypeError(f"Unsupported type {type(df)}. Expected pandas DataFrame, geopandas GeoDataFrame, or spark DataFrame.")
    df.to_csv(path, sep=separator, index=False)

def dataframe_to_geopackage(df: DataFrame, path: str):
    """
    Write a DataFrame to a GeoPackage file.
    The DataFrame geometry is assumed to use the coordinate reference system specified by `libadalina_core.sedona_utils.DEFAULT_EPSG`.

    Parameters
    ----------
    df : pandas.DataFrame or geopandas.GeoDataFrame or pyspark.sql.DataFrame
        The DataFrame to write, which can be a pandas DataFrame, a GeoPandas GeoDataFrame, or a Spark DataFrame.
    path : str
        The path to the GeoPackage file where the DataFrame will be saved.

    Examples
    --------

    >>> df = pd.DataFrame({'id': [1, 2], 'geometry': ['POINT(1 1)', 'POINT(2 2)']})
    >>> dataframe_to_geopackage(df, 'output.gpkg')

    """
    if isinstance(df, ps.DataFrame):
        df = gpd.GeoDataFrame(df.toPandas(), geometry = 'geometry', crs = DEFAULT_EPSG.value)
    elif isinstance(df,  pd.DataFrame):
        df = gpd.GeoDataFrame(df, geometry='geometry', crs=DEFAULT_EPSG.value)
    elif isinstance(df, gpd.GeoDataFrame):
        pass # already a GeoDataFrame
    else:
        raise TypeError(f"Unsupported type {type(df)}. Expected pandas DataFrame, geopandas GeoDataFrame, or spark DataFrame.")
    df.to_file(path, layer='dataframe', driver="GPKG")