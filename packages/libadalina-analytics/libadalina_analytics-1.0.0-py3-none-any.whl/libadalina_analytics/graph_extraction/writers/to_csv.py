import networkx as nx
import pandas as pd
import geopandas as gpd

from libadalina_core.sedona_utils import DEFAULT_EPSG


def graph_to_pandas(graph: nx.Graph) -> pd.DataFrame:
    """
    Convert a networkx graph to a pandas DataFrame.

    Parameters
    ----------
    graph : nx.Graph
        The networkx graph to convert.

    Returns
    -------
    pd.DataFrame
        A pandas DataFrame containing the edges of the graph.
    """
    return pd.DataFrame(({'from': u, 'to': v, **data} for u, v, data in graph.edges(data=True)))


def graph_to_csv(graph: nx.Graph, file_path: str):
    """
    Write a networkx graph to a CSV.

    Parameters
    ----------
    graph : nx.Graph
        The networkx graph to write.
    file_path : str
        The path to the CSV.
    """
    df = graph_to_pandas(graph)
    df.to_csv(file_path, index=False)


def path_to_pandas(graph: nx.Graph, path: list) -> pd.DataFrame:
    """
    Convert a path in a networkx graph to a pandas DataFrame.

    Parameters
    ----------
    graph : nx.Graph
        The networkx graph containing the path.
    path : list
        A list of nodes representing the path.

    Returns
    -------
    pandas.DataFrame
        A pandas DataFrame containing the edges of the path.

    """
    edges = [dict(_from=path[i], _to=path[i + 1], **graph.get_edge_data(path[i], path[i + 1])) for i in
             range(len(path) - 1)]
    return pd.DataFrame(edges)


def path_to_csv(graph: nx.Graph, path: list, file_path: str):
    """
    Save a path in a networkx graph to a CSV file.

    The function first uses `path_to_pandas` to convert the path into a pandas DataFrame and the saves such DataFrame
    as a CSV file.

    Parameters
    ----------
    graph : nx.Graph
        The networkx graph containing the path.
    path : list
        A list of nodes representing the path.
    file_path : str
        The path to the CSV file where the edges will be saved.

    """
    df = path_to_pandas(graph, path)
    gdf_edges = gpd.GeoDataFrame(df, geometry='geometry', crs=DEFAULT_EPSG)
    gdf_edges.to_csv(file_path, index=False)  # Save as CSV


def paths_to_pandas(graph: nx.Graph, paths: list) -> pd.DataFrame:
    """
    Convert paths in a networkx graph to a pandas DataFrame.

    Parameters
    ----------
    graph : nx.Graph
        The networkx graph containing the path.
    paths : list
        A list of paths.

    Returns
    -------
    pandas.DataFrame
        A pandas DataFrame containing the edges of the paths.

    """
    edges = [dict(_from=path[i], _to=path[i + 1], **graph.get_edge_data(path[i], path[i + 1]))
             for path in paths if path is not None for i in range(len(path) - 1)]
    return pd.DataFrame(edges)
