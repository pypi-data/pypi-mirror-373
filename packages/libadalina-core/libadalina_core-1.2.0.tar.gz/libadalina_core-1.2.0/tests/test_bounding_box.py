import pytest
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, Polygon

from libadalina_core.sedona_utils import to_spark_dataframe, EPSGFormats
from libadalina_core.spatial_operators.single_table_operators import bounding_box, cut_features


def test_bounding_box_with_points():
    df = pd.DataFrame({
        'geometry': [Point(0, 0), Point(1, 1), Point(-1, 2)]
    })
    df = to_spark_dataframe(df, epsg_format=EPSGFormats.EPSG4326)
    result = bounding_box(df)
    assert isinstance(result, Polygon)
    assert list(result.exterior.coords) == [(-1, 0), (1, 0), (1, 2), (-1, 2), (-1, 0)]


def test_bounding_box_with_polygons():
    polygons = [
        Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
        Polygon([(2, 2), (3, 2), (3, 3), (2, 3)])
    ]
    gdf = gpd.GeoDataFrame({'geometry': polygons}, crs='EPSG:4326')
    result = bounding_box(gdf)
    assert isinstance(result, Polygon)
    assert list(result.exterior.coords) == [(0, 0), (3, 0), (3, 3), (0, 3), (0, 0)]


def test_bounding_box_empty_dataframe():
    df = pd.DataFrame({'geometry': []})
    with pytest.raises(Exception):
        bounding_box(df)


def test_cut_features_with_polygon():
    df = pd.DataFrame({
        'geometry': [Point(0, 0), Point(1, 1), Point(2, 2)]
    })
    df = to_spark_dataframe(df, epsg_format=EPSGFormats.EPSG4326)
    cut_geom = Polygon([(0, 0), (1.5, 0), (1.5, 1.5), (0, 1.5)])
    result = cut_features(df, cut_geom)
    assert len(result.collect()) == 2


def test_cut_features_with_empty_polygon():
    df = pd.DataFrame({
        'geometry': [Point(0, 0), Point(1, 1)]
    })
    df = to_spark_dataframe(df, epsg_format=EPSGFormats.EPSG4326)
    empty_polygon = Polygon([])
    result = cut_features(df, empty_polygon)
    assert len(result.collect()) == 0