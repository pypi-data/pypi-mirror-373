import pytest
import pathlib
import geopandas as gpd

from libadalina_core.readers import geopackage_to_dataframe

SAMPLE_DIR = pathlib.Path(__file__).parent / "samples"

class TestReadGeoPackages:

    @pytest.mark.parametrize("package,layer,n_features", [
        (f"{SAMPLE_DIR}/healthcare/EU_healthcare.gpkg", "EU", 12365),
        (f"{SAMPLE_DIR}/regions/NUTS_RG_20M_2024_4326.gpkg", "NUTS_RG_20M_2024_4326.gpkg", 1798),
    ])
    def test_read(self, package, layer, n_features):
        df = geopackage_to_dataframe(package, layer)
        assert df is not None
        assert isinstance(df, gpd.GeoDataFrame)
        assert len(df) == n_features
        assert 'geometry' in df.columns