import geopandas as gpd

from libadalina_core.sedona_utils import DEFAULT_EPSG

def shapefile_to_dataframe(path: str) -> gpd.GeoDataFrame:
    """
    Read a Shapefile file into a GeoDataFrame.

    Geometry is automatically converted to the libadalina default EPSG ``DEFAULT_EPSG``.

    Parameters
    ----------
    path : str
        The path to the Shapefile file.

    Returns
    -------
    geopandas.GeoDataFrame
        A GeoDataFrame containing the data from the specified layer.

    Examples
    --------

    >>> gdf = shapefile_to_dataframe('data.shp')

    """
    gdf = gpd.read_file(path)
    gdf.to_crs(DEFAULT_EPSG.value, inplace=True)
    return gdf