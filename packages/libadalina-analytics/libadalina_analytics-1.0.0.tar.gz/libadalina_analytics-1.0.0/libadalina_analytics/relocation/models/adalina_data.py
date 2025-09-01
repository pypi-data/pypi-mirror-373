from collections import defaultdict

import numpy as np
import pandas as pd
import geopandas as gpd
import shapely

from libadalina_core.sedona_utils.coordinate_formats import EPSGFormats
from libadalina_analytics.utils import GeometryFormats
from .adalina_model_type import AdalinaModelType
import os
import logging
import json

EPSG_FORMAT_FOR_ALGORITHM = EPSGFormats.EPSG32632

def haversine_distance_matrix_geopandas(gpd_orig: gpd.GeoDataFrame,
                                        gpd_dest: gpd.GeoDataFrame = None):

    if gpd_dest is None:
        gpd_dest = gpd_orig

    distance_matrix = np.zeros((gpd_orig.shape[0], gpd_dest.shape[0]))
    i = 0
    for _, row in gpd_dest.iterrows():
        distance_matrix[:, i] = gpd_orig.geometry.distance(row.geometry).values/1000
        i += 1

    return distance_matrix


class AdalinaData:

    """

    All files are CSV separated by semi-colon ';'.
    Each file has a fixed suffix.
    First line of each file contains the header, with the name of all columns.

    Columns in brackets [] are optional.

    ## AREA FILE
    suffix: `_area.csv'
    columns:

    - "area": unique ID of the area.  str or int
    - "demand" : demand to fulfill (numeric)
    [
      - "cost" : cost of not serving (numeric)
    ]

    ## SHELTER FILE:
    suffix: `_shelters.csv'
    columns:

    - "shelter": unique ID of the shelter. str or int
    - "usable" : to 1 if the shelter can be used, 0 otherwise
    [
        - "cost_open": cost to open the shelter
        - "cost_exceed" : cost to exceed the capacity of the shelter
        - "capacity": capacity of a single resource (deprecated)
    ]

    ## AVAILABILITY OF MOVEMENTS OF DEMAND FROM AREA TO SHELTER
    suffix: `_area_shelter_pair_properties.CSV'
    columns:

    - "area": unique ID of the area (same as the value in _area.csv file)
    - "shelter": unique ID of the shelter (same as the value in _shelters.csv file)
    - "reach": to 1 if the demand of the area can be moved to the shelter, 0 otherwise
    [
        - "cost" : numeric, cost of moving 1 unit of demand from the area to the shelter
    ]

    If a pair (area, shelter) does not allow movements, the corresponding line can be omitted.

    ## RESOURCES
    suffix: `_resources.csv'
    columns:

    - "resources": unique ID of the resource (str or int)
    - "need": numeric, amount of resource needed for unit of demand

    ## AVAILABILITY OF RESOURCES IN SHELTERS
    suffix: `_resources_available.csv'
    columns:

    - "shelter": unique ID of the shelter (same as the value in _shelters.csv file)
    - "resources": unique ID of the resource (same as the value in _resources.csv file)
    - "available": numeric, amount of resource available in shelter
    [
      - "maximum": numeric, maximum amount of resources that the shelter can host. if the value is missing, the value of the field 'available' is used as maximum amount of resources.
            This value is used to compute the usage of the shelter, and is not used as hard constraint on the maximum
            number of resources to be delivered to the shelter
    ]

    If a shelter does not have a resource, the corresponding line can be omitted.

    ## RESOURCE RELOCATION FEASIBILITY
    suffix: "_relocation_feasibility.csv"
    columns:

    - "shelter_from": unique ID of the shelter from which the resources are moved (same as the value in _shelters.csv file)
    - "shelter_to": unique ID of the shelter to which the resources are delivered (same as the value in _shelters.csv file)
    - "reach": binary, value 1 if the relocation of any resource is possible, 0 if no relocation is possible

    There is no need to insert a line for the relocation of a shelter to itself,
    as it will be always considered as allowed.
    If a pair of shelters is missing from the file, the relocation
    will be considered as forbidden.

    ## RESOURCE RELOCATION COST (optional)

    suffix: "_resource_relocation_cost.csv"
    columns:

    - "shelter_from": unique ID of the shelter from which the resources are moved (same as the value in _shelters.csv file)
    - "shelter_to": unique ID of the shelter to which the resources are delivered (same as the value in _shelters.csv file)
    - "resources": : unique ID of the resource to move (same as the value in _resources.csv file)
    - "cost": numeric (cost of moving a unit of resource)

    If a triplet is missing from the file,
    the corresponding relocation is considered as forbidden.

    """

    def __init__(
                self,
                areas : pd.DataFrame,
                shelters  : pd.DataFrame,
                area_shelter_pair_properties  : pd.DataFrame,
                resources  : pd.DataFrame = None,
                resources_available  : pd.DataFrame = None,
                shelter_pair_properties  : pd.DataFrame =None) :

        self.areas = areas
        self.shelters = shelters
        self.area_shelter_pair_properties = area_shelter_pair_properties
        self.resources = resources
        self.resources_available = resources_available
        self.shelter_pair_properties = shelter_pair_properties

        self.sfrom_to = None
        self.distance_facility_list = None
        if self.shelter_pair_properties is not None:
            self.sfrom_to = self.shelter_pair_properties.reset_index()[
                ["shelter_from", "shelter_to"]].values.tolist()

            if 'cost' in self.shelter_pair_properties.columns and 'distance' not in self.shelter_pair_properties.columns:
                self.shelter_pair_properties['distance'] = self.shelter_pair_properties['cost']

        self.R_size = self.R = None

        self.A_size = self.areas.shape[0]
        self.S_size = self.shelters.shape[0]

        self.A = self.areas.index.values
        self.S = self.shelters.index.values

        self.bigM = float(self.areas.demand.sum())

        self.ub_total_unserved_demand = None
        self.ub_total_assignment_distance = None
        self.ub_max_usage = None
        self.ub_sum_usage = None

        if "reach" not in self.area_shelter_pair_properties.columns:
            self.area_shelter_pair_properties["reach"] = True
        else:
            self.area_shelter_pair_properties["reach"] = self.area_shelter_pair_properties["reach"].astype(bool)

        # print("build area - shelter transport feasibility")
        # forbidden_assignments = defaultdict(list)
        # area_shelter_pair_feas = self.area_shelter_pair_properties.index.values.tolist()
        # feedback_i = 1/100
        # for i, s in enumerate(self.S):
        #     for j, a in enumerate(self.A):
        #         if (a, s) not in area_shelter_pair_feas:
        #
        #             feedback= (i*self.A_size+j)/(self.A_size*self.S_size)
        #             if feedback > feedback_i:
        #                 print(f"{feedback_i}")
        #                 feedback_i += 1/100
        #
        #             forbidden_assignments["area"].append(a)
        #             forbidden_assignments["shelter"].append(s)
        #             forbidden_assignments["reach"].append(False)
        #
        #             if 'cost' in self.area_shelter_pair_properties.columns:
        #                 forbidden_assignments["cost"].append(-1)
        # forbidden_assignments = pd.DataFrame.from_dict(forbidden_assignments)
        # self.area_shelter_pair_properties = pd.concat(
        #     [self.area_shelter_pair_properties.reset_index(), forbidden_assignments],
        #                                               ignore_index=True)
        # self.area_shelter_pair_properties = self.area_shelter_pair_properties.set_index(["area", "shelter"])

        if self.resources is not None:

            self.R_size = self.resources.shape[0]
            self.R = self.resources.index.values

            if 'maximum' not in self.resources_available:
                self.resources_available["maximum"] = self.resources_available["available"]

    AMELIA_COLUMNS_MANDATORY = [
        "geometry",
        "demand",
        "resources",
        "IDs"
    ]

    @classmethod
    def from_Amelia(cls,
                    amelia_file : pd.DataFrame,
                    user_input : dict):

        missing_columns = [el for el in AdalinaData.AMELIA_COLUMNS_MANDATORY
                           if el not in user_input.keys()]

        if len(missing_columns) > 0:
            raise ValueError("Error parsing from Amelia dataset: missing columns: " + ' '.join(missing_columns))

        geometry_type = GeometryFormats.WKT
        if 'geometry_type' in user_input:
            geometry_type = user_input["geometry_type"]

        epsg = EPSGFormats.EPSG4326
        if "epsg" in user_input:
            epsg = user_input["epsg"]

        areas = amelia_file[[user_input["IDs"],
                             user_input["demand"],
                             user_input["geometry"] ]].copy()

        area_col_rename = {
            user_input["IDs"] : "area",
            user_input["demand"] : "demand",
            user_input["geometry"] : "geometry"
        }
        areas.rename(columns=area_col_rename, inplace=True)
        areas = areas.loc[ (~areas["demand"].isna()) & (areas["demand"] > 1e-5)].copy()

        areas = areas.reset_index().drop(columns="index")
        areas = AdalinaData.from_dataframe_to_geopandas(areas, epsg, "geometry", geometry_type)

        resources = {"resources": [], "need" : []}
        for el in user_input["resources"]:
            resources["resources"].append(el["name"])
            resources["need"].append(el.get("amount", 1))
        resources = pd.DataFrame.from_dict(resources)

        shelter_cols = [user_input["IDs"], user_input["geometry"]]
        shelter_col_rename = {
            user_input["IDs"]: "shelter",
            user_input["geometry"]: "geometry"
        }
        if "is_server" in user_input:
            shelter_cols.append(user_input["is_server"])
            shelter_col_rename[user_input["is_server"]] = "usable"
        shelter_and_reources = amelia_file.loc[(amelia_file[user_input["demand"]].isna()) | (amelia_file[user_input["demand"]] < 1e-5)].copy()

        # shelter DF
        shelter = shelter_and_reources[shelter_cols].copy()
        shelter.rename(columns=shelter_col_rename, inplace=True)
        if "usable" not in shelter:
            shelter["usable"] = True

        shelter = shelter.reset_index().drop(columns="index")
        shelter = AdalinaData.from_dataframe_to_geopandas(shelter, epsg, "geometry", geometry_type)

        # shelter;resources;available
        shelter_and_reources = shelter_and_reources[
            [user_input["IDs"]] + [el["name"] for el in user_input["resources"]]].copy()
        shelter_and_reources.rename(columns=shelter_col_rename, inplace=True)

        shelter_and_reources = shelter_and_reources.melt(id_vars="shelter", var_name="resources", value_name="available")

        # area;shelter;reach;cost
        dist_area_shelters = haversine_distance_matrix_geopandas(areas, shelter)
        area_shelter_pair_properties = defaultdict(list)
        threshold_val = user_input.get("max_distance_assignment", None)
        for i, row_a in areas.iterrows():
            for j, row_f in shelter.iterrows():
                # print(i,j)
                val = dist_area_shelters[i, j]

                if threshold_val is not None and val > threshold_val:
                    continue

                area_shelter_pair_properties["area"].append(row_a["area"])
                area_shelter_pair_properties["shelter"].append(row_f["shelter"])

                area_shelter_pair_properties["cost"].append(val)
                area_shelter_pair_properties["reach"].append(True)
        area_shelter_pair_properties = pd.DataFrame.from_dict(area_shelter_pair_properties)

        # shelter_from;shelter_to;reach;cost
        dist_shelters = haversine_distance_matrix_geopandas(shelter)
        shelter_pairs_properties = defaultdict(list)
        threshold_val = user_input.get("max_distance_relocation", None)
        for i, row_f1 in shelter.iterrows():
            for j, row_f2 in shelter.iterrows():
                # print(i,j)
                val = dist_shelters[i, j]

                shelter_pairs_properties["shelter_from"].append(row_f1["shelter"])
                shelter_pairs_properties["shelter_to"].append(row_f2["shelter"])

                shelter_pairs_properties["cost"].append(val)
                reach = True
                if threshold_val is not None:
                    reach = val < threshold_val
                shelter_pairs_properties["reach"].append(reach)
        shelter_pairs_properties = pd.DataFrame.from_dict(shelter_pairs_properties)

        areas.set_index(keys="area", inplace=True)
        shelter.set_index(keys="shelter", inplace=True)
        area_shelter_pair_properties.set_index(keys=["area", "shelter"], inplace=True)
        resources.set_index(keys="resources", inplace=True)
        shelter_and_reources.set_index(keys=["shelter","resources"], inplace=True)
        shelter_pairs_properties.set_index(keys=["shelter_from", "shelter_to"], inplace=True)

        return cls(areas,
                   shelter,
                   area_shelter_pair_properties,
                   resources,
                   shelter_and_reources,
                   shelter_pairs_properties)

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

    @classmethod
    def from_CSV(cls, basedir, fileprefix, log_fout=None):

        areas = pd.read_csv(basedir + fileprefix + "_area.csv", sep=";",
                                 index_col="area")

        shelters = pd.read_csv(basedir + fileprefix + "_shelters.csv", sep=";",
                                    index_col="shelter")

        area_shelter_pair_properties = pd.read_csv(basedir + fileprefix + "_area_shelter_pair_properties.csv",
                                                        sep=";",
                                                        index_col=["area", "shelter"])

        resources = None
        resources_available = None
        shelter_pair_properties = None
        if os.path.exists(basedir + fileprefix + "_resources.csv"):

            logging.debug("reading resources", log_fout)

            resources = pd.read_csv(basedir + fileprefix + "_resources.csv", sep=";",
                                         index_col="resources")

            resources_available = pd.read_csv(basedir + fileprefix + "_resources_available.csv", sep=";",
                                               index_col=["shelter","resources"])

            if 'maximum' not in resources_available:
                resources_available["maximum"] = resources_available["available"]

            resource_relocation_cost_filename = basedir + fileprefix + "_resource_relocation_cost.csv"

            if os.path.exists(resource_relocation_cost_filename):

                logging.debug("reading relocation costs")

                shelter_pair_properties = pd.read_csv(resource_relocation_cost_filename, sep=";",
                                                               index_col=["shelter_from", "shelter_to"])

                if "reach" not in shelter_pair_properties.columns:
                    shelter_pair_properties["reach"] = True

                logging.debug("building shelter-shelter feasibility")
                sfrom_to = shelter_pair_properties.reset_index()[
                    ["shelter_from", "shelter_to"]].values.tolist()

                S = shelters.index.values

                additional_shelters_pair = defaultdict(list)
                for s in S:
                    for s1 in S:
                        if [s, s1] not in sfrom_to:

                            if s == s1:
                                additional_shelters_pair["shelter_from"].append(s)
                                additional_shelters_pair["shelter_to"].append(s1)
                                additional_shelters_pair["reach"].append(True)
                                additional_shelters_pair["cost"].append(0)

                            else:

                                additional_shelters_pair["shelter_from"].append(s)
                                additional_shelters_pair["shelter_to"].append(s1)
                                additional_shelters_pair["reach"].append(False)
                                additional_shelters_pair["cost"].append(0)

                if len(additional_shelters_pair["shelter_from"]) > 0:
                    additional_shelters_pair = pd.DataFrame.from_dict(additional_shelters_pair)
                    additional_shelters_pair = additional_shelters_pair.set_index(["shelter_from", "shelter_to"])

                    shelter_pair_properties = pd.concat([shelter_pair_properties, additional_shelters_pair],
                                                        axis="index")

        return cls(
            areas, shelters, area_shelter_pair_properties, resources,
            resources_available, shelter_pair_properties
        )

    @classmethod
    def from_geodataframe(cls,
                          areas_gdf :gpd.GeoDataFrame,
                          facilities_gdf : gpd.GeoDataFrame,
                          areas_facilities_distance_df : pd.DataFrame,
                          facilities_distance_df: pd.DataFrame):

        """
        - "ID" : identifier of the area
        - "ID_level" : identifier of the level of granularity
        - "geometry" : geographical representation of the area
        - "population" : integer value corresponding to the population of the area
        - ["ID_father" : identifier of the area in an higher level of granularity to which the record belong]
        - ["ID_level_father" : identifier of the level of granularity of the father of the record]
        - ["lon" : longitude of a centroid of the area ]
        - ["lat" : latitude of a centroid of the area ]

        """

        areas = pd.DataFrame()
        areas["area"] = areas_gdf["ID"]
        areas["demand"] = areas_gdf["population"]
        areas.set_index("area", inplace=True)

        shelters = pd.DataFrame()
        shelters["shelter"] = facilities_gdf["ID"]
        shelters["X_epsg4326"] = facilities_gdf["geometry"].x
        shelters["Y_epsg4326"] = facilities_gdf["geometry"].y
        shelters["usable"] = facilities_gdf["usable"]
        shelters.set_index("shelter", inplace=True)

        resources = pd.DataFrame()
        # resources;need
        resources_available = defaultdict(list)
        # shelter;resources;available
        for i, row in facilities_gdf.iterrows():
            res_row = json.loads(row["resources"])
            for k, v in res_row.items():
                resources_available["shelter"].append(row["ID"])
                resources_available["resources"].append(k)
                resources_available["available"].append(float(v))
        resources_available = pd.DataFrame.from_dict(resources_available)
        resources_available.set_index(["shelter","resources"], inplace=True)

        # area_shelter_pair_properties (area;shelter;reach;cost) index["area", "shelter"]
        # shelter_pair_cost_transport (shelter_from;shelter_to;reach;cost) index["shelter_from", "shelter_to"]
        areas_facilities_distance_df.set_index(["area", "shelter"], inplace=True)
        facilities_distance_df.set_index(["shelter_from", "shelter_to"], inplace=True)

        return cls(
            areas, shelters, areas_facilities_distance_df, resources,
            resources_available, facilities_distance_df
        )

    @staticmethod
    def from_parquet_to_geodataframe(parquet_table):
        parquet_table = parquet_table.to_pandas()
        # Se contiene dati geografici
        return gpd.GeoDataFrame(parquet_table,
                                 geometry=gpd.GeoSeries.from_wkt(parquet_table["geometry"]))

    @classmethod
    def from_parquet(cls, areas_parquet, facilities_parquet,
                     areas_facilities_distance_parquet,
                     facilities_distance_parquet):

        return cls.from_geodataframe(
            cls.from_parquet_to_geodataframe(areas_parquet),
            cls.from_parquet_to_geodataframe(facilities_parquet),
            areas_facilities_distance_parquet.to_pandas(),
            facilities_distance_parquet.to_pandas()
        )

    def get_distance_facilities_quantile(self, q = None):

        if q is None:
            q = [0.1 * i for i in range(1, 6)]

        if self.distance_facility_list is None:
            self.distance_facility_list = []
            if self.shelter_pair_properties is not None:
                for [s,s1] in self.sfrom_to:
                    self.distance_facility_list.append(self.shelter_pair_properties.loc[[s,s1], "distance"])
            self.distance_facility_list = np.array(self.distance_facility_list)

        return np.quantile(self.distance_facility_list, q=q)

    def get_facilities_distance(self, shelter_from, shelter_to):

        return self.get_shelter_pair_property(shelter_from, shelter_to, "distance")

    def get_resource_need(self, resource):
        return self.resources.loc[resource, "need"]

    def get_resource_available(self, shelter, resource):
        if (shelter, resource) in self.resources_available.index:
            return self.resources_available.loc[(shelter, resource), "available"]
        else:
            return 0

    def get_resource_maximum(self, shelter, resource):
        if (shelter, resource) in self.resources_available.index:
            return self.resources_available.loc[(shelter, resource), "maximum"]
        else:
            return 0


    def get_shelter_pair_property(self, shelter_from, shelter_to, column):

        if self.shelter_pair_properties is None:
            return None

        if [shelter_from, shelter_to] in self.sfrom_to:
            return self.shelter_pair_properties.loc[(shelter_from, shelter_to), column]
        elif [shelter_to, shelter_from] in self.sfrom_to:
            return self.shelter_pair_properties.loc[(shelter_to, shelter_from), column]

        return None

    def get_cost_resource_transport(self, shelter_from, shelter_to, resource, modeltype=None):
        # TODO: consider if cost are symmetric or not

        if modeltype not in [AdalinaModelType.MINSUM_USAGEFAC, AdalinaModelType.MINSUM_RELOCATION, AdalinaModelType.MINSUM_ALLCOST]:
            return 0

        if self.shelter_pair_properties is None:
            return 0
        if shelter_from == shelter_to:
            return 0

        value = self.get_shelter_pair_property(shelter_from, shelter_to, "cost")

        if value is not None:
            return value

        return 0

    def get_transport_possible(self, shelter_from, shelter_to):
        if shelter_from == shelter_to:
            return True

        if (shelter_from, shelter_to) in self.shelter_pair_properties.index:
            return self.shelter_pair_properties.loc[(shelter_from, shelter_to), "reach"]
        elif (shelter_to, shelter_from) in self.shelter_pair_properties.index:
            return self.shelter_pair_properties.loc[(shelter_to, shelter_from), "reach"]

        return False

    def get_demcost_assign(self, shelter, area, modeltype=None):
        if modeltype not in [AdalinaModelType.MINDIST_ASSIGNMENTS, AdalinaModelType.MINSUM_ALLCOST] :
            return 0
        return self.get_cost_assign(shelter, area) * self.get_area_demand(area)

    def get_cost_assign(self, shelter, area):

        if 'cost' not in self.area_shelter_pair_properties.columns:
            return 0

        if (area, shelter) in self.area_shelter_pair_properties.index:

            return self.area_shelter_pair_properties.loc[(area, shelter), 'cost']

        return 0

    def sort_area_by_min_assign_cost(self):
        if 'cost' not in self.area_shelter_pair_properties.columns:
            raise ValueError("ERROR: no 'cost' field present to sort areas")

        _costs =  self.area_shelter_pair_properties.reset_index()

        m =  _costs.groupby(by="area").cost.agg(["min", "idxmin"]).reset_index()

        shelters = []
        for i, row in m.iterrows():
            shelters.append(_costs.shelter.iloc[row["idxmin"]])
        m["shelter"] = shelters

        m = m.rename(columns = {'min' : 'cost'})
        m = m.drop(columns=["idxmin"])
        m = m.sort_values(by="cost", ascending=False)

        return m

    def get_area_demand(self, area):
        return self.areas.loc[area, 'demand']

    def get_fixed_cost_shelter(self, shelter, modeltype=None):

        if modeltype != AdalinaModelType.MINSUM_ALLCOST:
            return 0

        if 'cost_open' in self.shelters.columns:
            return self.shelters.loc[shelter, 'cost_open']

        return 0

    def get_demcost_notserved(self, area, modeltype=None):
        if modeltype == AdalinaModelType.MINSUM_UNSERVED:
            return self.get_area_demand(area)

        if modeltype != AdalinaModelType.MINSUM_ALLCOST:
            return 0

        return self.get_cost_notserved(area)

    def get_cost_notserved(self, area):
        if 'cost' in self.areas.columns:
            return self.areas.loc[area, 'cost']
        else:
            return 0

    def get_cost_exceed_cap(self, shelter, modeltype=None):

        if modeltype is not None:
            if modeltype == AdalinaModelType.MIN_EXTRARESOURCES:
                return 1

            if modeltype != AdalinaModelType.MINSUM_ALLCOST:
                return 0

        if 'cost_exceed' in self.shelters.columns:
            return self.shelters.loc[shelter, 'cost_exceed']
        else:
            return 0

    def get_is_reachable(self, shelter, area):

        return (area, shelter) in self.area_shelter_pair_properties.index

        # return int(self.area_shelter_pair_properties.loc[(area, shelter), "reach"])  # int((area, shelter) in self.area_shelter_pair_properties.index)

    def get_capacity(self, shelter):
        return self.shelters.loc[shelter, 'capacity']

    def get_bigMdemand(self):
        return self.bigM

    def get_shelter_usable(self, shelter):
        return self.shelters.loc[shelter, 'usable']
