import os.path
from shapely.io import from_wkt

from libadalina_analytics.exceptions.input_file_exception import InputFileException
from libadalina_analytics.graph_extraction.readers.reader import MapReader, MandatoryColumns, OneWay, RoadTypes
import geopandas as gpd
import pandas as pd

class OpenStreetMapReader(MapReader):
    CRS = 4326

    def read(self, file_path: str) -> gpd.GeoDataFrame:
        if file_path.endswith('.csv'):
            return self.read_csv(file_path)
        elif file_path.endswith('.shp'):
            return self.read_shp(file_path)
        elif file_path.endswith('.gpkg'):
            return self.read_gpkg(file_path)

        raise InputFileException(f'no reader found for file {file_path}')

    def read_csv(self, file_path: str) -> gpd.GeoDataFrame:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'file {file_path} does not exist')

        df = pd.read_csv(file_path, sep=',')
        return self.from_dataframe(df)

    def read_shp(self, file_path: str) -> gpd.GeoDataFrame:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'file {file_path} does not exist')

        return self._map_columns(gpd.read_file(file_path))
    
    def read_gpkg(self, file_path: str) -> gpd.GeoDataFrame:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'file {file_path} does not exist')

        layers = gpd.list_layers(file_path)
        layer_name = layers.loc[0, 'name']

        return self._map_columns(gpd.read_file(file_path, layer=layer_name))

    def from_dataframe(self, df: pd.DataFrame) -> gpd.GeoDataFrame:
        df.loc[:, 'geometry'] = df['geometry'].apply(from_wkt)
        return self._map_columns(gpd.GeoDataFrame(df, geometry='geometry', crs=self.CRS))

    def _map_columns(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        gdf['name'] = gdf['name'].fillna('')
        gdf = self._filter_roads(gdf)
        gdf = self.map_and_reduce(gdf, {
            MandatoryColumns.id: 'osm_id',
            MandatoryColumns.name: 'name',
            MandatoryColumns.oneway: 'oneway'
        })
        
        oneway_mapping = {
            'F': OneWay.Forward.value,
            'T': OneWay.Backward.value,
            'B': OneWay.Both.value
        }
        gdf.loc[:, MandatoryColumns.oneway.value] = gdf[MandatoryColumns.oneway.value].map(oneway_mapping).fillna(
            OneWay.Both.value)
        return gdf

    def _filter_roads(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        if self._road_types == RoadTypes.CAR_ONLY:
            return gdf[(
                ((gdf['code'] >= 5110) & (gdf['code'] <= 5119)) |
                ((gdf['code'] >= 5130) & (gdf['code'] <= 5139)) |
                ((gdf['code'] >= 5121) & (gdf['code'] <= 5122))
            )]
        elif self._road_types == RoadTypes.MAIN_ROADS:
            return gdf[(
                    ((gdf['code'] >= 5110) & (gdf['code'] <= 5119)) |
                    ((gdf['code'] >= 5130) & (gdf['code'] <= 5139))
            )]
        else:
            return gdf
