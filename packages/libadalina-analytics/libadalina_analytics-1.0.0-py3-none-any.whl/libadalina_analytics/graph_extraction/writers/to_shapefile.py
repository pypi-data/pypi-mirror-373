import networkx as nx
import geopandas as gpd

from libadalina_core.sedona_utils import DEFAULT_EPSG
from libadalina_analytics.graph_extraction.writers.to_csv import graph_to_pandas


def graph_to_shapefile(graph: nx.Graph, path: str):
    """
    Write a networkx graph to a shapefile.

    Parameters
    ----------
    graph : networkx.Graph
        The networkx graph to write.
    path : str
        The path to the shapefile.
    """
    df = graph_to_pandas(graph)
    gdf_edges = gpd.GeoDataFrame(df, geometry='geometry', crs=DEFAULT_EPSG)
    gdf_edges.to_file(path, driver='ESRI Shapefile')