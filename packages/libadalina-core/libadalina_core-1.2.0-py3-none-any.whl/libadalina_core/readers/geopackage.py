import geopandas as gpd
from pyogrio import list_layers

from libadalina_core.sedona_utils import DEFAULT_EPSG


def geopackage_to_dataframe(path: str, layer: str = None) -> gpd.GeoDataFrame:
    """
    Read a GeoPackage file into a GeoDataFrame.

    Geometry is automatically converted to the libadalina default EPSG ``DEFAULT_EPSG``.

    Parameters
    ----------
    path : str
        The path to the GeoPackage file.
    layer : str
        The layer name of the GeoPackage.

    Returns
    -------
    geopandas.GeoDataFrame
        A GeoDataFrame containing the data from the specified layer.

    Examples
    --------

    >>> gdf = geopackage_to_dataframe('data.gpkg', 'layer_name')

    """
    if layer is None:
        layers = list_layers(path)
        if len(layers) == 0:
            raise ValueError(f"No layers found in GeoPackage file: {path}")
        layer, _ = layers[0]
    gdf = gpd.read_file(path, layer=layer)
    gdf.to_crs(DEFAULT_EPSG.value, inplace=True)
    return gdf