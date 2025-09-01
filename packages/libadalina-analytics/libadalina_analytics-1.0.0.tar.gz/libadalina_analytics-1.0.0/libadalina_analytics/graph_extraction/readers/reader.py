from abc import abstractmethod
from enum import Enum

import geopandas as gpd

from libadalina_analytics.exceptions.input_file_exception import InputFileException

class RoadTypes(Enum):
    ALL = 'all'
    CAR_ONLY = 'only_car'
    MAIN_ROADS = 'main_roads'

class MandatoryColumns(Enum):
    id = 'id'
    name = 'name'
    oneway = 'oneway'

class OneWay(Enum):
    Forward = 'forward'
    Backward = 'backward'
    Both = 'both'

class MapReader:

    def __init__(self, road_types: RoadTypes = RoadTypes.ALL):
        self._road_types = road_types

    @abstractmethod
    def _filter_roads(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """
        Filter roads based on the specified road type.
        This method should be implemented by subclasses to apply specific filtering logic.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def map_and_reduce(self, gdf: gpd.GeoDataFrame, column_map: dict[MandatoryColumns, str]) -> gpd.GeoDataFrame:

        for key, value in column_map.items():
            gdf[key.value] = gdf[value]

        gdf = gdf[['geometry'] + [c.value for c in MandatoryColumns]]

        for c in MandatoryColumns:
            if c.value not in gdf.columns:
                raise InputFileException(f"missing column {c.value} in dataframe")
        return gdf


