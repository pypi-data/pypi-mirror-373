
import networkx as nx
import geopandas as gpd
import pandas as pd
import numpy as np
from pandas.api.types import is_float_dtype, is_integer_dtype, is_string_dtype
from sklearn.metrics import DistanceMetric
import time
# from collections import defaultdict
import logging
import shapely

from networkx.algorithms import flow
from scipy.spatial import distance_matrix, distance
# import gower
import json, jsonschema

from libadalina_core.sedona_utils import EPSGFormats
from libadalina_analytics.utils import GeometryFormats

EPSG_FORMAT_FOR_ALGORITHM = EPSGFormats.EPSG32632

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


def validate_json(input_dict : dict, schema_path : str, log_fout = None):
    with open(schema_path, "r") as fin:
        input_schema = json.load(fin)
    try:
        jsonschema.validate(instance=input_dict, schema=input_schema)  # Validazione
        return True
    except jsonschema.exceptions.ValidationError as e:
        logging.error("Errore di validazione input utente: %s " % e.message, log_fout)
        return False

def validate_user_input_json(user_input : dict, log_fout = None):
    return validate_json(user_input, "adalina_zoning_input_schema.json", log_fout=log_fout)

def validate_solution_json(sol_dict : dict, log_fout = None):
    return validate_json(sol_dict, "adalina_zoning_solution_schema.json", log_fout=log_fout)

from shapely.geometry import Polygon

def get_all_vertices(poly : Polygon):
    coords = list(poly.exterior.coords)
    for interior in poly.interiors:
        coords.extend(interior.coords)
    return coords

def extract_vertices(geom):
    if geom.geom_type == 'Polygon':
        return get_all_vertices(geom)
    elif geom.geom_type == 'MultiPolygon':
        all_coords = []
        for poly in geom.geoms:
            all_coords.extend(get_all_vertices(poly))
        return all_coords

    return []

def polygons_vertices_distance(polys : [Polygon]):

    n = len(polys)
    d = np.zeros((n,n))

    polyvert = [get_all_vertices(p) for p in polys]

    for i in range(n-1):
        for j in range(i+1, n):
            d[i,j] = distance.cdist(polyvert[i], polyvert[j]).min()

    return d


class AdalinaZoningData:

    AMELIA_COLUMNS_MANDATORY = [
        "geometry",
    ]

    DISTANCE_FUNCTION_PER_TYPES = {
        "numeric" : ["euclidean", "manhattan", "chebyshev"],
        "geometry" : ["haversine"],
        "string" : ["hamming", "canberra", "braycurtis"],
        "bool" : ["jaccard", "matching", "dice", "kulsinski", "rogerstanimoto", "russellrao", "sokalmichener", "sokalsneath"]
    }

    def __init__(self,
                 geodataFrame : gpd.GeoDataFrame = None,
                 G : nx.Graph = None,
                 nodes_costs : pd.DataFrame = None,
                 user_input : dict = None,
                 log_fout = None):

        if user_input is None:
            user_input = dict()

        self.log_fout = log_fout
        self.gdf = geodataFrame

        self.G = G
        self.node_pairs_costs_df = None
        self.min_geodistance_polygons = None
        self._from_index_to_int = None
        self.old_index_name = None

        if self.gdf is not None:

            self.old_index_name = self.gdf.index.name
            self.gdf.reset_index(inplace=True, names="old_index")

            geom_vect = self.gdf.geometry.array
            n = len(geom_vect)
            self._from_index_to_int = dict()
            for i, idx in enumerate(self.gdf.index):
                self._from_index_to_int[idx] = i

            logging.debug("start computing distance between polygons")
            _st = time.time()
            self.min_geodistance_polygons = np.zeros((n, n))
            for i in range(n - 1):
                logging.debug(f"distance polygon index {i + 1} over {n}")
                self.min_geodistance_polygons[i, (i + 1):] = geom_vect[i].distance(geom_vect[(i + 1):])
            logging.debug(f"distance computed in {time.time() - _st}")

            G = nx.Graph()

            for idx in self.gdf.index:
                G.add_node(idx)

            sindex = self.gdf.sindex

            for i, geom in enumerate(self.gdf.geometry):
                possible_matches_idx = list(sindex.intersection(geom.bounds))
                possible_matches = self.gdf.loc[possible_matches_idx]
                possible_matches = possible_matches.loc[possible_matches.geometry.intersects(geom)]
                for j in possible_matches.index:
                    if i < j: # and geom.touches(geodataFrame.geometry[j]):
                        G.add_edge(i, int(j))

            if "weight" in user_input:
                for idx, row in self.gdf.iterrows():
                    G.nodes[idx]["weight"] = row["weight"]

            self.G = G

            if "distances" not in user_input:
                # Estrai coordinate dei centroidi
                centroid_coords = self.gdf.centroid.apply(lambda p: (p.x, p.y)).tolist()
                # Crea la matrice con SciPy
                self.node_pairs_costs_df = distance_matrix(centroid_coords, centroid_coords)
                # sum_weight_gower = 1
            else:
                sum_weight_gower = 0
                all_dist = []
                for el in user_input["distances"]:
                    col = el["name"]
                    weight = el.get("weight", 1)
                    func = el.get("func", None)

                    val = None

                    if func is not None:
                        if isinstance(self.gdf.dtypes[col], gpd.array.GeometryDtype) and func in AdalinaZoningData.DISTANCE_FUNCTION_PER_TYPES["geometry"]:
                            centroid_coords = self.gdf.centroid.apply(lambda p: (p.x, p.y)).tolist()
                            val = distance_matrix(centroid_coords, centroid_coords)

                        elif ((is_float_dtype(self.gdf.dtypes[col]) or is_integer_dtype(self.gdf.dtypes[col])) and func in AdalinaZoningData.DISTANCE_FUNCTION_PER_TYPES["numeric"]) or \
                            (is_string_dtype(self.gdf.dtypes[col]) and func in AdalinaZoningData.DISTANCE_FUNCTION_PER_TYPES["string"]) or \
                            (self.gdf.dtypes[col] == bool or self.gdf.dtypes[col] == int and func in AdalinaZoningData.DISTANCE_FUNCTION_PER_TYPES["bool"]):

                            val = DistanceMetric.get_metric(func).pairwise(self.gdf[[col]])
                        else:
                            func = None

                    if func is None:
                        if isinstance(self.gdf.dtypes[col], gpd.array.GeometryDtype):
                            centroid_coords = self.gdf.centroid.apply(lambda p: (p.x, p.y)).tolist()
                            val = distance_matrix(centroid_coords, centroid_coords)
                        elif is_float_dtype(self.gdf.dtypes[col]) or is_integer_dtype(self.gdf.dtypes[col]):
                            val = DistanceMetric.get_metric("euclidean").pairwise(self.gdf[[col]])
                        elif is_string_dtype(self.gdf.dtypes[col]):
                            cat_series = pd.Categorical(self.gdf[col])
                            val = DistanceMetric.get_metric("hamming").pairwise(pd.DataFrame(cat_series.codes))
                        elif self.gdf.dtypes[col] == bool or self.gdf.dtypes[col] == int:
                            val = DistanceMetric.get_metric("jaccard").pairwise(self.gdf[[col]].astype(bool))

                    if val is not None:
                        val = (val - val.min()) / (val.max() - val.min())
                        all_dist.append(
                            val * weight
                        )

                        sum_weight_gower += weight

                all_dist = np.array(all_dist)
                all_dist = (all_dist - all_dist.min()) / (all_dist.max() - all_dist.min())

                self.node_pairs_costs_df = all_dist.sum(axis=0)/sum_weight_gower

            self.node_pairs_costs_df = pd.DataFrame(self.node_pairs_costs_df,
                                                    index=self.gdf.index,
                                                    columns=self.gdf.index)

        elif G is not None and nodes_costs is not None:
            self.G = G

            self.gdf = pd.DataFrame.from_dict({'old_index' : nodes_costs.index.values})

            self.node_pairs_costs_df = nodes_costs

            self.node_pairs_costs_df.reset_index(inplace=True, drop=True)

            mp = {}
            for i, row in self.gdf.iterrows():
                mp[row.old_index] = i
            self.G = nx.relabel_nodes(G, mp)

            self.min_geodistance_polygons = nodes_costs.to_numpy()

            self._from_index_to_int = dict()
            for i, idx in enumerate(self.gdf.index):
                self._from_index_to_int[idx] = i

        else:
            raise ValueError("either 'geodataFrame' or both 'G' and 'nodes_costs' must have value")

        self.E1 = []
        self.edges = dict()
        for i in self.G.nodes:
            self.edges[i] = []
            for j in self.G.nodes:
                if j <= i:
                    continue

                self.E1.append((i, j))
                self.edges[i].append(j)

        self.T = None

        self.Fmin = user_input.get("Fmin", 1)
        self.Kmin = user_input.get("Kmin", 1)
        self.V = len(self.G.nodes)
        self.Kmax = user_input.get("Kmax", self.V)
        self.Kmax = min(self.Kmax, self.V)

        if self.Kmin > self.Kmax:
            self.Kmin = self.Kmax

    @classmethod
    def from_shapefile(cls, filename : str):

        gdf = gpd.read_file(filename)
        gdf.reset_index(inplace=True, drop=True)

        return cls(gdf)

    @classmethod
    def from_nxGraph(cls, graph: nx.Graph,
                     nodes_costs : pd.DataFrame):

        return cls(G = graph, nodes_costs=nodes_costs)

    @classmethod
    def from_Amelia(cls, amelia_file : pd.DataFrame,
                    user_input : dict, log_fout = None):

        # if not validate_user_input_json(user_input, log_fout):
        #     raise ValueError("Error parsing user input, check log for more information")

        missing_columns = [el for el in AdalinaZoningData.AMELIA_COLUMNS_MANDATORY
                           if el not in user_input.keys()]

        if len(missing_columns) > 0:
            raise ValueError("Error parsing from Amelia dataset: missing columns: " + ' '.join(missing_columns))

        geometry_type = GeometryFormats.WKT
        if 'geometry_type' in user_input:
            geometry_type = user_input["geometry_type"]

        epsg = EPSGFormats.EPSG4326
        if "epsg" in user_input:
            epsg = user_input["epsg"]

        col_rename = {
            user_input["geometry"]: "geometry"
        }
        if "weight" in user_input:
            col_rename[user_input["weight"]] = "weight"

        amelia_file.rename(columns=col_rename, inplace=True)

        amelia_file.reset_index(inplace=True, drop=True)
        amelia_file = AdalinaZoningData.from_dataframe_to_geopandas(amelia_file, epsg, "geometry", geometry_type)

        # debug!
        # amelia_file = amelia_file.iloc[7:]

        return cls(amelia_file, user_input=user_input)

    def get_node_pair_geographic_distance(self, node1, node2):
        if node1 == node2:
            return 0

        i = self._from_index_to_int[node1]
        j = self._from_index_to_int[node2]

        if i > j:
            i, j = j, i

        return self.get_pair_geographic_distance(i, j)

    def get_pair_geographic_distance(self, i, j):

        if i == j:
            return 0

        return self.min_geodistance_polygons[i,j]

    def get_cost_edge(self, i, j):

        return self.node_pairs_costs_df.loc[i,j]

    def get_weight_node(self, i):

        if "weight" not in self.G.nodes[i]:
            return 1

        return self.G.nodes[i]["weight"]

    def gomory_hu(self, weight : dict):

        for e in self.G.edges:
            w = weight.get(e, 0)
            self.G.edges[e]["weight"] = w

        # for k, v in weight.items():
        #     self.G.edges[k]["weight"] = v

        self.T = nx.gomory_hu_tree(self.G, capacity = "weight", flow_func=flow.boykov_kolmogorov)

        return self.T

    def minimum_edge_weight_in_shortest_path(self, u, v):

        return nx.minimum_cut(self.T, u, v, capacity ="weight")

        # path = nx.shortest_path(self.T, u, v, weight="weight")

        # return min((self.T[u][v]["weight"], (u, v)) for (u, v) in zip(path, path[1:]))

    def check_nodes_subset_connected(self, subset_nodes):
        if len(subset_nodes) < 2:
            return True

        subG = self.G.subgraph(subset_nodes)
        return nx.is_connected(subG)

    @staticmethod
    def from_dataframe_to_geopandas(df : pd.DataFrame,
                                    epsg : EPSGFormats = EPSGFormats.EPSG4326,
                                    wkt_col : str = "geometry",
                                    geometry_format: GeometryFormats = GeometryFormats.WKT):
        gdf = gpd.GeoDataFrame(df)

        if geometry_format == GeometryFormats.WKT:
            gdf["geometry"] = gpd.GeoSeries.from_wkt(df[wkt_col])
        elif geometry_format == GeometryFormats.GEOJSON:
            gdf["geometry"] = df[wkt_col].apply(shapely.from_geojson)

        gdf = gdf.set_geometry(col="geometry")
        gdf = gdf.set_crs(epsg=epsg.value)
        if epsg != EPSG_FORMAT_FOR_ALGORITHM:
            gdf = gdf.to_crs(epsg=EPSG_FORMAT_FOR_ALGORITHM.value)

        return gdf

    def add_clustering(self, clustering : dict):

        # cl_dict = {}
        # kindex = 0
        # for k, v in clustering.items():
        #     for el in v:
        #         cl_dict[el] = kindex
        #     kindex += 1

        res = pd.Series(clustering) # cl_dict)
        ret_gdf = None
        if self.gdf is not None:
            ret_gdf = self.gdf.set_index("old_index")
            ret_gdf.index.name = self.old_index_name
            ret_gdf["zoning_Adalina"] = res


        return ret_gdf

