import networkx as nx
import geopandas as gpd
from libadalina_core.sedona_utils import DEFAULT_EPSG

from libadalina_analytics.graph_extraction.writers.to_csv import graph_to_pandas, path_to_pandas, paths_to_pandas


def graph_to_geopackage(graph: nx.Graph, file_path: str):
    """
    Write a networkx graph to a geopackage.

    The function first uses `graph_to_pandas` to convert the graph into a pandas DataFrame, and then save it to
    file as a GeoDataFrame in a geopackage format.

    Parameters
    ----------
    graph : networkx.Graph
        The networkx graph to write.
    file_path : str 
        The path to the geopackage.
    """
    df = graph_to_pandas(graph)
    gdf_edges = gpd.GeoDataFrame(df, geometry='geometry', crs=DEFAULT_EPSG.value)
    gdf_edges.to_file(file_path, driver='GPKG', layer='graph')


def path_to_geopackage(graph: nx.Graph, path: list, file_path: str):
    """
    Save a path in a networkx graph to a geopackage file.

    The function first uses `path_to_pandas` to convert the path into a pandas DataFrame and then saves it
    as a file in a geopackage format.

    Parameters
    ----------
    graph : networkx.Graph
        The networkx graph containing the path.
    path : list
        A list of nodes representing the path.
    file_path : str
        The path to the geopackage file where the edges will be saved.

    """
    df = path_to_pandas(graph, path)
    gdf_edges = gpd.GeoDataFrame(df, geometry='geometry', crs=DEFAULT_EPSG.value)
    gdf_edges.to_file(file_path, driver='GPKG', layer='path')

def paths_to_geopackage(graph: nx.Graph, paths: list, file_path: str):
    """
    Save paths in a networkx graph to a geopackage file.

    The function first uses `paths_to_pandas` to convert the path into a pandas DataFrame and then saves it
    as a file in a geopackage format.

    Parameters
    ----------
    graph : networkx.Graph
        The networkx graph containing the path.
    paths : list[list]
        A list of paths
    file_path : str
        The path to the geopackage file where the edges will be saved.

    """
    df = paths_to_pandas(graph, paths)
    gdf_edges = gpd.GeoDataFrame(df, geometry='geometry', crs=DEFAULT_EPSG.value)
    gdf_edges.to_file(file_path, driver='GPKG', layer='paths')