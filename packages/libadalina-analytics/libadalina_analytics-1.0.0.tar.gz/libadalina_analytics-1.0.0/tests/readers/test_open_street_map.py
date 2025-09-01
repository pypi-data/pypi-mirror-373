import pytest
from libadalina_analytics.graph_extraction.readers import OpenStreetMapReader
import geopandas as gpd
import pathlib

from libadalina_analytics.graph_extraction.readers import MandatoryColumns

SAMPLE_DIR = pathlib.Path(__file__).parent.parent / "samples"

@pytest.fixture
def osm_reader():
    return OpenStreetMapReader()

class TestOpenStreetMapReader:

    @pytest.mark.parametrize("input_map", [
        f"{SAMPLE_DIR}/milano/gis_osm_roads_free_1.shp",
        f"{SAMPLE_DIR}/milano/gis_osm_roads_free_1.csv",
    ])
    def test_read(self, osm_reader, input_map):
        """Test reading OpenStreetMap data."""
        osm_data = osm_reader.read(input_map)
        assert osm_data is not None
        assert isinstance(osm_data, gpd.GeoDataFrame)
        assert len(osm_data) > 0
        assert all(c.value in osm_data.columns for c in MandatoryColumns)

    def test_read_with_invalid_file(self, osm_reader):
        """Test reading with an invalid file."""
        with pytest.raises(FileNotFoundError):
            osm_reader.read("invalid_file.csv")