import pandas as pd
import geopandas as gpd
import pyspark.sql as ps
from sedona.sql import ST_BestSRID, ST_SetSRID, ST_Transform, ST_SRID
import sedona.sql.st_functions as func
from shapely.io import from_wkt
from functools import wraps
from .coordinate_formats import EPSGFormats, DEFAULT_EPSG
from libadalina_core.sedona_configuration import get_sedona_context

"""
Common type alias for DataFrame types used in spatial operations.
Can either be a pandas DataFrame, a GeoPandas GeoDataFrame, or a Spark DataFrame.
"""
DataFrame = pd.DataFrame | gpd.GeoDataFrame | ps.DataFrame

def to_default_epsg(function):
    """
    Decorator to ensure that the geometry column of a DataFrame is transformed to the default EPSG format.

    Parameters
    ----------
    function

    Returns
    -------
        Returns the wrapped function, which will transform the geometry column, if present, to the default EPSG format.
    """
    @wraps(function)
    def wrapper(*args, **kwargs):
        result = function(*args, **kwargs)
        if isinstance(result, ps.DataFrame) and 'geometry' in result.columns:
            result = result.withColumn('geometry', ST_Transform(result.geometry, func.lit(f'EPSG:{DEFAULT_EPSG.value}')))
        return result

    return wrapper

@to_default_epsg
def to_spark_dataframe(df: DataFrame, epsg_format: EPSGFormats | None = None) -> ps.DataFrame:
    """
    Convert a pandas DataFrame or a GeoPandas GeoDataFrame to a Spark DataFrame.
    If the input is already a Spark DataFrame, it will be returned as is.

    This function is useful for converting data to a format suitable for processing with Apache Sedona,
    however, each function of libadalina already converts the input DataFrame to a Spark DataFrame before processing.

    Parameters
    ----------
    df : pandas.DataFrame or geopandas.GeoDataFrame or pyspark.sql.DataFrame
        The DataFrame to convert, which can be a pandas DataFrame, a GeoPandas GeoDataFrame, or a Spark DataFrame.
    epsg_format : EPSGFormats, optional
        The EPSG format to use for converting the pandas DataFrame. If None is provided and the
        geometry is missing the EPSG format, libadalina will try to infer the best fitting format.

    Returns
    -------
    pyspark.sql.DataFrame
        A Spark DataFrame.
    """
    if isinstance(df, ps.DataFrame):
        if 'geometry' not in df.columns:
            raise TypeError(f"Unsupported DataFrame: missing `geometry` column.")
        return df # nothing to do here
    sedona = get_sedona_context()
    if isinstance(df, gpd.GeoDataFrame):
        if 'geometry' not in df.columns:
            raise TypeError(f"Unsupported DataFrame: missing `geometry` column.")
        csr = df.crs
        df = sedona.createDataFrame(df)
        df = df.withColumn('geometry', ST_SetSRID(df.geometry, func.lit(csr.to_epsg())))
        return df
    if isinstance(df, pd.DataFrame):
        if 'geometry' not in df.columns:
            raise TypeError(f"Unsupported DataFrame: missing `geometry` column.")
        # Convert WKT strings to Shapely geometries if necessary
        if df['geometry'].dtype == 'object' and isinstance(df['geometry'].iloc[0], str):
            df.loc[:, 'geometry'] = df['geometry'].apply(from_wkt)
        df = sedona.createDataFrame(gpd.GeoDataFrame(df, geometry='geometry'))
        if epsg_format is None:
            df = df.withColumn('geometry', ST_SetSRID(df.geometry, ST_BestSRID(df.geometry)))
        else:
            df = df.withColumn('geometry', ST_SetSRID(df.geometry, func.lit(epsg_format.value)))
        return df
    raise TypeError(f"Unsupported type {type(df)}. Expected pandas, geopandas, or spark DataFrame.")

