#-----------------------------------------------------------------------
# Name:        models (huff package)
# Purpose:     Huff Model classes and functions
# Author:      Thomas Wieland 
#              ORCID: 0000-0001-5168-9846
#              mail: geowieland@googlemail.com              
# Version:     1.5.7
# Last update: 2025-08-13 18:47
# Copyright (c) 2025 Thomas Wieland
#-----------------------------------------------------------------------


import pandas as pd
import geopandas as gp
import numpy as np
from math import sqrt
import time
from pandas.api.types import is_numeric_dtype
from statsmodels.formula.api import ols
from scipy.optimize import minimize, Bounds, LinearConstraint, NonlinearConstraint
from shapely.geometry import Point
from shapely import wkt
import copy
from huff.ors import Client, TimeDistanceMatrix, Isochrone
from huff.gistools import overlay_difference, distance_matrix, buffers


class CustomerOrigins:

    def __init__(
        self,
        geodata_gpd, 
        geodata_gpd_original, 
        metadata,
        isochrones_gdf,
        buffers_gdf
        ):

        self.geodata_gpd = geodata_gpd
        self.geodata_gpd_original = geodata_gpd_original
        self.metadata = metadata
        self.isochrones_gdf = isochrones_gdf
        self.buffers_gdf = buffers_gdf

    def get_geodata_gpd(self):

        return self.geodata_gpd

    def get_geodata_gpd_original(self):

        return self.geodata_gpd_original

    def get_metadata(self):
        
        return self.metadata
    
    def get_isochrones_gdf(self):

        return self.isochrones_gdf

    def get_buffers_gdf(self):

        return self.buffers_gdf

    def summary(self):

        metadata = self.metadata

        print("Customer Origins")
        print("No. locations              " + str(metadata["no_points"]))
        
        if metadata["marketsize_col"] is None:
            print("Market size column         not defined")
        else:
            print("Market size column         " + metadata["marketsize_col"])
        
        if metadata["weighting"][0]["func"] is None and metadata["weighting"][0]["param"] is None:
            print("Transport cost weighting    not defined")
        elif metadata["weighting"][0]["func"] in ["power", "exponential"]:
            print("Transport cost weighting   " + str(round(metadata["weighting"][0]["param"],3)) + " (" + metadata["weighting"][0]["func"] + ")")
        elif metadata["weighting"][0]["func"] == "logistic":
            print("Transport cost weighting   " + str(round(metadata["weighting"][0]["param"][0],3)) + ", " + str(round(metadata["weighting"][0]["param"][1],3)) + " (" + metadata["weighting"][0]["func"] + ")")

        print("Unique ID column           " + metadata["unique_id"])
        print("Input CRS                  " + str(metadata["crs_input"]))

        if self.isochrones_gdf is None:
            print("Including isochrones       NO")
        else:
            print("Including isochrones       YES")

        if self.buffers_gdf is None:
            print("Including buffers          NO")
        else:
            print("Including buffers          YES")

        return metadata
    
    def define_marketsize(
        self,
        marketsize_col
        ):

        geodata_gpd_original = self.geodata_gpd_original
        metadata = self.metadata

        if marketsize_col not in geodata_gpd_original.columns:
            raise KeyError ("Error while defining market size variable: Column " + marketsize_col + " not in data")
        else:
            metadata["marketsize_col"] = marketsize_col

        self.metadata = metadata

        return self

    def define_transportcosts_weighting(
        self,
        func = "power",
        param_lambda = -2
        ):

        """
        metadata["weighting"] = {
            0: {
                "name": "t_ij",
                "func": "power",
                "param": -2
            }
        }
        
        metadata["weighting"] = {
            0: {
                "name": "t_ij",
                "func": "logistic",
                "param": [10, -0.5]
            }
        }
        """
                
        metadata = self.metadata

        if func not in ["power", "exponential", "logistic"]:
            raise ValueError("Error while defining transport costs weighting: Parameter 'func' must be 'power', 'exponential' or 'logistic'")

        if isinstance(param_lambda, list) and func != "logistic":
            raise ValueError("Error while defining transport costs weighting: Function type "+ func + " requires one single parameter value")
        
        if isinstance(param_lambda, (int, float)) and func == "logistic":
            raise ValueError("Error while defining transport costs weighting: Function type "+ func + " requires two parameters in a list")
        
        metadata["weighting"][0]["name"] = "t_ij"
        metadata["weighting"][0]["func"] = func

        if isinstance(param_lambda, list):
            metadata["weighting"][0]["param"] = [float(param_lambda[0]), float(param_lambda[1])]
        else:
            metadata["weighting"][0]["param"] = float(param_lambda)

        self.metadata = metadata
        
        return self

    def isochrones(
        self,
        segments: list = [5, 10, 15],
        range_type: str = "time",
        intersections: str = "true",
        profile: str = "driving-car",
        donut: bool = True,
        ors_server: str = "https://api.openrouteservice.org/v2/",
        ors_auth: str = None,
        timeout: int = 10,
        delay: int = 1,
        save_output: bool = True,
        output_filepath: str = "customer_origins_isochrones.shp",
        output_crs: str = "EPSG:4326"
        ):

        geodata_gpd = self.get_geodata_gpd()
        metadata = self.get_metadata()

        isochrones_gdf = get_isochrones( 
            geodata_gpd = geodata_gpd,
            unique_id_col = metadata["unique_id"],
            segments = segments,
            range_type = range_type,
            intersections = intersections,
            profile = profile,
            donut = donut,
            ors_server = ors_server,
            ors_auth = ors_auth,
            timeout = timeout,
            delay = delay,
            save_output = save_output,
            output_filepath = output_filepath,
            output_crs = output_crs
            )

        self.isochrones_gdf = isochrones_gdf

        return self

    def buffers(
        self,
        segments_distance: list = [500, 1000],
        donut: bool = True,
        save_output: bool = True,
        output_filepath: str = "customer_origins_buffers.shp",
        output_crs: str = "EPSG:4326"
        ):

        geodata_gpd_original = self.get_geodata_gpd_original()
        metadata = self.metadata

        buffers_gdf = buffers(
            point_gdf = geodata_gpd_original,
            unique_id_col = metadata["unique_id"],
            distances = segments_distance,
            donut = donut,
            save_output = save_output,
            output_filepath = output_filepath,
            output_crs = output_crs
            )
        
        self.buffers_gdf = buffers_gdf

        return self

class SupplyLocations:

    def __init__(
        self,
        geodata_gpd, 
        geodata_gpd_original, 
        metadata,
        isochrones_gdf,
        buffers_gdf
        ):

        self.geodata_gpd = geodata_gpd
        self.geodata_gpd_original = geodata_gpd_original
        self.metadata = metadata
        self.isochrones_gdf = isochrones_gdf
        self.buffers_gdf = buffers_gdf

    def get_geodata_gpd(self):

        return self.geodata_gpd

    def get_geodata_gpd_original(self):

        return self.geodata_gpd_original

    def get_metadata(self):

        return self.metadata
    
    def get_isochrones_gdf(self):

        return self.isochrones_gdf
    
    def get_buffers_gdf(self):

        return self.buffers_gdf

    def summary(self):

        metadata = self.metadata

        print("Supply Locations")
        print("No. locations         " + str(metadata["no_points"]))

        if metadata["attraction_col"][0] is None or metadata["attraction_col"] == []:
            print("Attraction column(s)  not defined")
        else:
            print("Attraction column(s)  " + ",".join(metadata["attraction_col"]))
        
        if metadata["weighting"][0]["func"] is None and metadata["weighting"][0]["param"] is None:
            print("Attraction weighting  not defined")
        else:
            print("Attraction weighting  " + metadata["weighting"][0]["func"] + " with gamma = " + str(round(metadata["weighting"][0]["param"],3)))
        
        print("Unique ID column      " + metadata["unique_id"])
        print("Input CRS             " + str(metadata["crs_input"]))

        if self.isochrones_gdf is None:
            print("Including isochrones  NO")
        else:
            print("Including isochrones  YES")

        return metadata

    def define_attraction(
        self,
        attraction_col
        ):

        geodata_gpd_original = self.geodata_gpd_original
        metadata = self.metadata

        if attraction_col not in geodata_gpd_original.columns:
            raise KeyError ("Error while defining attraction variable: Column " + attraction_col + " not in data")
        else:
            metadata["attraction_col"][0] = attraction_col

        self.metadata = metadata

        return self
    
    def define_attraction_weighting(
        self,
        func = "power",
        param_gamma = 1
        ):

        metadata = self.metadata

        if metadata["attraction_col"] is None:
            raise ValueError ("Error while defining attraction weighting: Attraction column is not yet defined. Use SupplyLocations.define_attraction()")
        
        metadata["weighting"][0]["name"] = "A_j"
        metadata["weighting"][0]["func"] = func
        metadata["weighting"][0]["param"] = float(param_gamma)
        
        self.metadata = metadata

        return self

    def add_var(
        self,
        var: str = None,
        func: str = None,
        param: float = None
        ):

        metadata = self.metadata

        if metadata["attraction_col"] is None:
            raise ValueError ("Error while adding utility variable: Attraction column is not yet defined. Use SupplyLocations.define_attraction()")

        no_attraction_vars = len(metadata["attraction_col"])
        new_key = no_attraction_vars

        metadata["attraction_col"] = metadata["attraction_col"] + [var] 

        metadata["weighting"][new_key] = {
            "name": var,
            "func": func,
            "param": param
            }

        self.metadata = metadata

        return self
    
    def add_new_destinations(
        self,
        new_destinations,
        ):
        
        geodata_gpd_original = self.get_geodata_gpd_original()
        geodata_gpd = self.get_geodata_gpd()
        metadata = self.get_metadata()

        new_destinations_gpd_original = new_destinations.get_geodata_gpd_original()
        new_destinations_gpd_original["j_update"] = 1
        
        new_destinations_gpd = new_destinations.get_geodata_gpd()
        new_destinations_gpd["j_update"] = 1
        
        new_destinations_metadata = new_destinations.get_metadata()

        if list(new_destinations_gpd_original.columns) != list(geodata_gpd_original.columns):
            raise KeyError("Error while adding new destinations: Supply locations and new destinations data have different column names.")
        if list(new_destinations_gpd.columns) != list(geodata_gpd.columns):
            raise KeyError("Error while adding new destinations: Supply locations and new destinations data have different column names.")

        geodata_gpd_original = pd.concat(
            [
                geodata_gpd_original, 
                new_destinations_gpd_original
                ], 
            ignore_index=True
            )
                
        geodata_gpd = pd.concat(
            [
                geodata_gpd, 
                new_destinations_gpd
                ], 
                ignore_index=True
            )
        
        metadata["no_points"] = metadata["no_points"]+new_destinations_metadata["no_points"]
        
        self.geodata_gpd = geodata_gpd
        self.geodata_gpd_original = geodata_gpd_original
        self.metadata = metadata

        return self
    
    def isochrones(
        self,
        segments: list = [5, 10, 15],
        range_type: str = "time",
        intersections: str = "true",
        profile: str = "driving-car",
        donut: bool = True,
        ors_server: str = "https://api.openrouteservice.org/v2/",
        ors_auth: str = None,
        timeout: int = 10,
        delay: int = 1,
        save_output: bool = True,
        output_filepath: str = "supply_locations_isochrones.shp",
        output_crs: str = "EPSG:4326"
        ):

        geodata_gpd = self.get_geodata_gpd()
        metadata = self.get_metadata()

        isochrones_gdf = get_isochrones( 
            geodata_gpd = geodata_gpd,
            unique_id_col = metadata["unique_id"],
            segments = segments,
            range_type = range_type,
            intersections = intersections,
            profile = profile,
            donut = donut,
            ors_server = ors_server,
            ors_auth = ors_auth,
            timeout = timeout,
            delay = delay,
            save_output = save_output,
            output_filepath = output_filepath,
            output_crs = output_crs
            )

        self.isochrones_gdf = isochrones_gdf

        return self

    def buffers(
        self,
        segments_distance: list = [500, 1000],
        donut: bool = True,
        save_output: bool = True,
        output_filepath: str = "supply_locations_buffers.shp",
        output_crs: str = "EPSG:4326"
        ):

        geodata_gpd_original = self.get_geodata_gpd_original()
        metadata = self.metadata

        buffers_gdf = buffers(
            point_gdf = geodata_gpd_original,
            unique_id_col = metadata["unique_id"],
            distances = segments_distance,
            donut = donut,
            save_output = save_output,
            output_filepath = output_filepath,
            output_crs = output_crs
            )
        
        self.buffers_gdf = buffers_gdf

        return self    

class InteractionMatrix:

    def __init__(
        self, 
        interaction_matrix_df,
        customer_origins,
        supply_locations,
        metadata
        ):

        self.interaction_matrix_df = interaction_matrix_df
        self.customer_origins = customer_origins
        self.supply_locations = supply_locations
        self.metadata = metadata

    def get_interaction_matrix_df(self):
        return self.interaction_matrix_df
    
    def get_customer_origins(self):
        return self.customer_origins

    def get_supply_locations(self):
        return self.supply_locations
    
    def get_metadata(self):
        return self.metadata

    def summary(self):

        customer_origins_metadata = self.get_customer_origins().get_metadata()
        supply_locations_metadata = self.get_supply_locations().get_metadata()
        interaction_matrix_metadata = self.get_metadata()

        print("Interaction Matrix")
        print("----------------------------------")
        
        print("Supply locations    " + str(supply_locations_metadata["no_points"]))
        if supply_locations_metadata["attraction_col"][0] is None:
            print("Attraction column   not defined")
        else:
            print("Attraction column   " + supply_locations_metadata["attraction_col"][0])
        print("Customer origins    " + str(customer_origins_metadata["no_points"]))
        if customer_origins_metadata["marketsize_col"] is None:
            print("Market size column not defined")
        else:
            print("Market size column  " + customer_origins_metadata["marketsize_col"])

        if interaction_matrix_metadata != {} and "transport_costs" in interaction_matrix_metadata:
            print("----------------------------------")
            if interaction_matrix_metadata["transport_costs"]["network"]:
                print("Transport cost type Time")
                print("Transport cost unit " + interaction_matrix_metadata["transport_costs"]["time_unit"])
            else:
                print("Transport cost type Distance")
                print("Transport cost unit " + interaction_matrix_metadata["transport_costs"]["distance_unit"])

        print("----------------------------------")
        print("Partial utilities")
        print("                    Weights")

        if supply_locations_metadata["weighting"][0]["func"] is None and supply_locations_metadata["weighting"][0]["param"] is None:
            print("Attraction          not defined")
        else:
            if supply_locations_metadata["weighting"][0]["param"] is not None:
                print("Attraction          " + str(round(supply_locations_metadata["weighting"][0]["param"],3)) + " (" + supply_locations_metadata["weighting"][0]["func"] + ")")
            else:
                print("Attraction          NA" + " (" + supply_locations_metadata["weighting"][0]["func"] + ")")   

        if customer_origins_metadata["weighting"][0]["func"] is None and customer_origins_metadata["weighting"][0]["param"] is None:
            print("Transport costs     not defined")
        elif customer_origins_metadata["weighting"][0]["func"] in ["power", "exponential"]:
            if customer_origins_metadata["weighting"][0]["param"] is not None:
                print("Transport costs     " + str(round(customer_origins_metadata["weighting"][0]["param"],3)) + " (" + customer_origins_metadata["weighting"][0]["func"] + ")")
            else:
                print("Transport costs     NA" + " (" + customer_origins_metadata["weighting"][0]["func"] + ")")
        elif customer_origins_metadata["weighting"][0]["func"] == "logistic":
            if customer_origins_metadata["weighting"][0]["param"] is not None:
                print("Transport costs    " + str(round(customer_origins_metadata["weighting"][0]["param"][0],3)) + ", " + str(round(customer_origins_metadata["weighting"][0]["param"][1],3)) + " (" + customer_origins_metadata["weighting"][0]["func"] + ")")
            else:
                print("Transport costs     NA" + " (" + customer_origins_metadata["weighting"][0]["func"] + ")")

        attrac_vars = supply_locations_metadata["attraction_col"]
        attrac_vars_no = len(attrac_vars)
        
        if attrac_vars_no > 1:
                        
            for key, attrac_var in enumerate(attrac_vars):
                
                if key == 0:
                    continue
                
                if key not in supply_locations_metadata["weighting"].keys():
                    
                    print(f"{attrac_vars[key][:16]:16}    not defined")
                    
                else:
                    
                    if supply_locations_metadata["weighting"][key]["func"] is None and supply_locations_metadata["weighting"][key]["param"]:
                        
                        print(f"{attrac_vars[key][:16]:16}    not defined")

                    else:

                        if supply_locations_metadata["weighting"][key]["param"] is not None:

                            name = supply_locations_metadata["weighting"][key]["name"]
                            param = supply_locations_metadata["weighting"][key]["param"]
                            func = supply_locations_metadata["weighting"][key]["func"]
                            
                            print(f"{name[:16]:16}    {round(param, 3)} ({func})")

                        else:

                            print(f"{attrac_vars[key][:16]:16}    NA" + " (" + supply_locations_metadata["weighting"][0]["func"] + ")") 


        print("----------------------------------")

        if interaction_matrix_metadata != {} and "fit" in interaction_matrix_metadata and interaction_matrix_metadata["fit"]["function"] is not None:
            print("Parameter estimation")
            print("Fit function        " + interaction_matrix_metadata["fit"]["function"])
            print("Fit by              " + interaction_matrix_metadata["fit"]["fit_by"])
            if interaction_matrix_metadata["fit"]["function"] == "huff_ml_fit":
                print("Fit method          " + interaction_matrix_metadata["fit"]["method"] + " (Converged: " + str(interaction_matrix_metadata["fit"]["minimize_success"]) + ")")

        return [
            customer_origins_metadata,
            supply_locations_metadata,
            interaction_matrix_metadata
            ]

    def transport_costs(
        self,
        network: bool = True,
        range_type: str = "time",
        time_unit: str = "minutes",
        distance_unit: str = "kilometers",
        ors_server: str = "https://api.openrouteservice.org/v2/",
        ors_auth: str = None,
        save_output: bool = False,
        output_filepath: str = "transport_costs_matrix.csv"
        ):

        if not network and range_type == "time":
            print ("Calculating euclidean distances (network = False). Setting range_type = 'distance'")
            range_type = "distance"
        
        interaction_matrix_df = self.get_interaction_matrix_df()
        interaction_matrix_metadata = self.get_metadata()

        customer_origins = self.get_customer_origins()
        customer_origins_geodata_gpd = customer_origins.get_geodata_gpd()
        customer_origins_metadata = customer_origins.get_metadata()
        customer_origins_uniqueid = customer_origins_metadata["unique_id"]
        customer_origins_coords = [[point.x, point.y] for point in customer_origins_geodata_gpd.geometry]
        customer_origins_ids = customer_origins_geodata_gpd[customer_origins_uniqueid].tolist()

        supply_locations = self.get_supply_locations()
        supply_locations_geodata_gpd = supply_locations.get_geodata_gpd()
        supply_locations_metadata = supply_locations.get_metadata()
        supply_locations_uniqueid = supply_locations_metadata["unique_id"]
        supply_locations_coords = [[point.x, point.y] for point in supply_locations_geodata_gpd.geometry]
        supply_locations_ids = supply_locations_geodata_gpd[supply_locations_uniqueid].tolist()
   
        locations_coords = customer_origins_coords + supply_locations_coords        
        
        customer_origins_index = list(range(len(customer_origins_coords)))
        locations_coords_index = list(range(len(customer_origins_index), len(locations_coords)))

        if network:

            ors_client = Client(
                server = ors_server,
                auth = ors_auth
                )
            time_distance_matrix = ors_client.matrix(
                locations = locations_coords,
                save_output = save_output,
                output_filepath = output_filepath, 
                sources = customer_origins_index,
                destinations = locations_coords_index,
                range_type = range_type
                )
            
            if time_distance_matrix.get_metadata() is None:
                raise ValueError ("Error in transport costs calculation: No transport costs matrix was built.")

            transport_costs_matrix = time_distance_matrix.get_matrix()
            transport_costs_matrix_config = time_distance_matrix.get_config()
            range_type = transport_costs_matrix_config["range_type"]

            transport_costs_matrix["source"] = transport_costs_matrix["source"].astype(int)
            transport_costs_matrix["source"] = transport_costs_matrix["source"].map(dict(enumerate(customer_origins_ids)))
            
            transport_costs_matrix["destination"] = transport_costs_matrix["destination"].astype(int)
            transport_costs_matrix["destination"] = transport_costs_matrix["destination"].map(dict(enumerate(supply_locations_ids)))
            
            transport_costs_matrix["source_destination"] = transport_costs_matrix["source"].astype(str)+"_"+transport_costs_matrix["destination"].astype(str)
            transport_costs_matrix = transport_costs_matrix[["source_destination", range_type]]

            interaction_matrix_df = interaction_matrix_df.merge(
                transport_costs_matrix,
                left_on="ij",
                right_on="source_destination"
                )
            
            interaction_matrix_df["t_ij"] = interaction_matrix_df[range_type]
            if time_unit == "minutes":
                interaction_matrix_df["t_ij"] = interaction_matrix_df["t_ij"]/60
            if time_unit == "hours":
                interaction_matrix_df["t_ij"] = interaction_matrix_df["t_ij"]/60/60

            interaction_matrix_df = interaction_matrix_df.drop(columns=["source_destination", range_type])

        else:

            distance_matrix_result = distance_matrix(
                sources = customer_origins_coords,
                destinations = supply_locations_coords,
                unit = "m"
                )
            
            distance_matrix_result_flat = [distance for sublist in distance_matrix_result for distance in sublist]

            interaction_matrix_df["t_ij"] = distance_matrix_result_flat

            if distance_unit == "kilometers":
                interaction_matrix_df["t_ij"] = interaction_matrix_df["t_ij"]/1000

        interaction_matrix_metadata["transport_costs"] = {
            "network": network,
            "range_type": range_type,
            "time_unit": time_unit,
            "distance_unit": distance_unit,
            "ors_server": ors_server,
            "ors_auth": ors_auth
            }

        self.interaction_matrix_df = interaction_matrix_df
        self.metadata = interaction_matrix_metadata

        return self
    
    def define_weightings(
        self,
        vars_funcs: dict
        ):
        
        """
        vars_funcs = {
            0: {
                "name": "A_j",
                "func": "power",
                "param": 1
            },
            1: {
                "name": "t_ij",
                "func": "logistic"
            },
            2: {
                "name": "second_attraction_variable",
                "func": "power"
            },
            3: {
                "name": "third_attraction_variable",
                "func": "exponential"
            },
            ...
        }
        """

        supply_locations_metadata = self.supply_locations.metadata
        customer_origins_metadata = self.customer_origins.metadata

        supply_locations_metadata["weighting"][0]["name"] = vars_funcs[0]["name"]
        supply_locations_metadata["weighting"][0]["func"] = vars_funcs[0]["func"]
        if "param" in vars_funcs[0]:
            supply_locations_metadata["weighting"][0]["param"] = vars_funcs[0]["param"]
    
        customer_origins_metadata["weighting"][0]["name"] = vars_funcs[1]["name"]
        customer_origins_metadata["weighting"][0]["func"] = vars_funcs[1]["func"]
        if "param" in vars_funcs[1]:
            customer_origins_metadata["weighting"][0]["param"] = vars_funcs[1]["param"]

        if len(vars_funcs) > 2:
            
            for key, var in vars_funcs.items():

                if key < 2:
                    continue
                
                if key not in supply_locations_metadata["weighting"]:
                    supply_locations_metadata["weighting"][key-1] = {
                        "name": "attrac"+str(key),
                        "func": "power",
                        "param": None
                        }

                supply_locations_metadata["weighting"][key-1]["name"] = var["name"]
                supply_locations_metadata["weighting"][key-1]["func"] = var["func"]

                if "param" in var:
                    supply_locations_metadata["weighting"][key-1]["param"] = var["param"]

        self.supply_locations.metadata = supply_locations_metadata
        self.customer_origins.metadata = customer_origins_metadata

    def utility(
        self,
        check_df_vars: bool = True
        ):
        
        interaction_matrix_df = self.interaction_matrix_df

        interaction_matrix_metadata = self.get_metadata()

        if "t_ij" not in interaction_matrix_df.columns:
            raise ValueError ("Error in utility calculation: No transport cost variable in interaction matrix")
        if "A_j" not in interaction_matrix_df.columns:
            raise ValueError ("Error in utility calculation: No attraction variable in interaction matrix")
        if interaction_matrix_df["t_ij"].isna().all():
            raise ValueError ("Error in utility calculation: Transport cost variable is not defined")
        if interaction_matrix_df["A_j"].isna().all():
            raise ValueError ("Error in utility calculation: Attraction variable is not defined")

        if check_df_vars:
            check_vars(
                df = interaction_matrix_df,
                cols = ["A_j", "t_ij"]
                )
        
        customer_origins = self.customer_origins
        customer_origins_metadata = customer_origins.get_metadata()
        tc_weighting = customer_origins_metadata["weighting"][0]
        
        if tc_weighting["func"] == "power":
            interaction_matrix_df["t_ij_weighted"] = interaction_matrix_df["t_ij"] ** tc_weighting["param"]
        elif tc_weighting["func"] == "exponential":
            interaction_matrix_df["t_ij_weighted"] = np.exp(tc_weighting["param"] * interaction_matrix_df["t_ij"])
        elif tc_weighting["func"] == "logistic":
            interaction_matrix_df["t_ij_weighted"] = 1+np.exp(tc_weighting["param"][0] + tc_weighting["param"][1] * interaction_matrix_df["t_ij"])
        else:
            raise ValueError ("Error in utility calculation: Transport costs weighting is not defined.")
                           
        supply_locations = self.supply_locations
        supply_locations_metadata = supply_locations.get_metadata()
        attraction_weighting = supply_locations_metadata["weighting"][0]
        
        if attraction_weighting["func"] == "power":
            interaction_matrix_df["A_j_weighted"] = interaction_matrix_df["A_j"] ** attraction_weighting["param"]
        elif tc_weighting["func"] == "exponential":
            interaction_matrix_df["A_j_weighted"] = np.exp(attraction_weighting["param"] * interaction_matrix_df["A_j"])
        else:
            raise ValueError ("Error in utility calculation: Attraction weighting is not defined.")
        
        attrac_vars = supply_locations_metadata["attraction_col"]
        attrac_vars_no = len(attrac_vars)
        attrac_var_key = 0

        if attrac_vars_no > 1:
            
            for key, attrac_var in enumerate(attrac_vars):
                
                attrac_var_key = key
                if attrac_var_key == 0:
                    continue
                
                name = supply_locations_metadata["weighting"][attrac_var_key]["name"]
                param = supply_locations_metadata["weighting"][attrac_var_key]["param"]
                func = supply_locations_metadata["weighting"][attrac_var_key]["func"]

                if func == "power":
                    interaction_matrix_df[name+"_weighted"] = interaction_matrix_df[name] ** param
                elif func == "exponential":
                    interaction_matrix_df[name+"_weighted"] = np.exp(param * interaction_matrix_df[name])
                else:
                    raise ValueError ("Error in utility calculation: Weighting for " + name + " is not defined.")
                
                interaction_matrix_df["A_j_weighted"] = interaction_matrix_df["A_j_weighted"]*interaction_matrix_df[name+"_weighted"]

                interaction_matrix_df = interaction_matrix_df.drop(columns=[name+"_weighted"])

        interaction_matrix_df["U_ij"] = interaction_matrix_df["A_j_weighted"]*interaction_matrix_df["t_ij_weighted"]
        
        interaction_matrix_df = interaction_matrix_df.drop(columns=["A_j_weighted", "t_ij_weighted"])

        interaction_matrix_metadata["model"] = {
            "model_type": "Huff"
            }

        self.interaction_matrix_df = interaction_matrix_df
        self.metadata = interaction_matrix_metadata
        
        return self
    
    def probabilities (
        self,
        check_df_vars: bool = True
        ):

        interaction_matrix_df = self.interaction_matrix_df

        if "U_ij" not in interaction_matrix_df.columns or interaction_matrix_df["U_ij"].isna().all():
            self.utility()
            interaction_matrix_df = self.interaction_matrix_df

        if check_df_vars:
            check_vars(
                df = interaction_matrix_df,
                cols = ["U_ij"]
                )

        utility_i = pd.DataFrame(interaction_matrix_df.groupby("i")["U_ij"].sum())
        utility_i = utility_i.rename(columns = {"U_ij": "U_i"})

        interaction_matrix_df = interaction_matrix_df.merge(
            utility_i,
            left_on="i",
            right_on="i",
            how="inner"
            )

        interaction_matrix_df["p_ij"] = (interaction_matrix_df["U_ij"]) / (interaction_matrix_df["U_i"])

        interaction_matrix_df = interaction_matrix_df.drop(columns=["U_i"])

        self.interaction_matrix_df = interaction_matrix_df

        return self
        
    def flows (
        self,
        check_df_vars: bool = True
        ):

        interaction_matrix_df = self.interaction_matrix_df

        if "C_i" not in interaction_matrix_df.columns:
            raise ValueError ("Error in flows calculation: No market size variable in interaction matrix")
        if interaction_matrix_df["C_i"].isna().all():
            raise ValueError ("Error in flows calculation: Market size column in customer origins not defined. Use CustomerOrigins.define_marketsize()")

        if check_df_vars:
            check_vars(
                df = interaction_matrix_df,
                cols = ["C_i"]
                )

        if interaction_matrix_df["p_ij"].isna().all():
            self.probabilities()
            interaction_matrix_df = self.interaction_matrix_df

        interaction_matrix_df["E_ij"] = interaction_matrix_df["p_ij"] * interaction_matrix_df["C_i"]

        self.interaction_matrix_df = interaction_matrix_df

        return self

    def marketareas(
        self,
        check_df_vars: bool = True
        ):

        interaction_matrix_df = self.interaction_matrix_df
        
        if check_df_vars:
            check_vars(
                df = interaction_matrix_df,
                cols = ["E_ij"],
                check_zero = False
                )
        
        market_areas_df = pd.DataFrame(interaction_matrix_df.groupby("j")["E_ij"].sum())
        market_areas_df = market_areas_df.reset_index(drop=False)
        market_areas_df = market_areas_df.rename(columns={"E_ij": "T_j"})

        huff_model = HuffModel(
            self,
            market_areas_df
            )
        
        return huff_model

    def hansen(
        self,
        from_origins: bool = True,
        exclude_self: bool = True,
        check_df_vars: bool = True
        ):

        interaction_matrix_df = self.interaction_matrix_df

        if exclude_self:

            interaction_matrix_df = interaction_matrix_df[interaction_matrix_df["i"] != interaction_matrix_df["j"]]

        if from_origins:

            if "U_ij" not in interaction_matrix_df.columns or interaction_matrix_df["U_ij"].isna().all():
                self.utility(check_df_vars = check_df_vars)
                interaction_matrix_df = self.interaction_matrix_df

            hansen_df = pd.DataFrame(interaction_matrix_df.groupby("i")["U_ij"].sum()).reset_index()
            hansen_df = hansen_df.rename(columns = {"U_ij": "A_i"})

        else:
            
            if "C_i" not in interaction_matrix_df.columns or interaction_matrix_df["C_i"].isna().all():
                raise ValueError("Error in hansen accessibility calculation: Customer origins market size is not available")            
            
            customer_origins_metadata = self.customer_origins.get_metadata()
            tc_weighting = customer_origins_metadata["weighting"][0]
            if tc_weighting["func"] == "power":
                interaction_matrix_df["t_ij_weighted"] = interaction_matrix_df["t_ij"] ** tc_weighting["param"]
            elif tc_weighting["func"] == "exponential":
                interaction_matrix_df["t_ij_weighted"] = np.exp(tc_weighting["param"] * interaction_matrix_df["t_ij"])
            elif tc_weighting["func"] == "logistic":
                interaction_matrix_df["t_ij_weighted"] = 1+np.exp(tc_weighting["param"][0] + tc_weighting["param"][1] * interaction_matrix_df["t_ij"])
            else:
                raise ValueError ("Error in hansen accessibility calculation: Transport costs weighting is not defined.")
                        
            interaction_matrix_df["U_ji"] = interaction_matrix_df["C_i"]*interaction_matrix_df["t_ij_weighted"]           
            hansen_df = pd.DataFrame(interaction_matrix_df.groupby("j")["U_ji"].sum()).reset_index()
            hansen_df = hansen_df.rename(columns = {"U_ji": "A_j"})

        return hansen_df

    def mci_transformation(
        self,
        cols: list = ["A_j", "t_ij"]
        ):

        cols = cols + ["p_ij"]

        interaction_matrix_df = self.interaction_matrix_df

        interaction_matrix_df = log_centering_transformation(
            df = interaction_matrix_df,
            ref_col = "i",
            cols = cols
            )
        
        self.interaction_matrix_df = interaction_matrix_df

        return self

    def mci_fit(
        self,
        cols: list = ["A_j", "t_ij"],
        alpha = 0.05
        ):

        supply_locations = self.get_supply_locations()
        supply_locations_metadata = supply_locations.get_metadata()

        customer_origins = self.get_customer_origins()
        customer_origins_metadata = customer_origins.get_metadata()

        interaction_matrix_df = self.get_interaction_matrix_df()

        interaction_matrix_metadata = self.get_metadata()

        cols_t = [col + "__LCT" for col in cols]

        if "p_ij__LCT" not in interaction_matrix_df.columns:
            interaction_matrix = self.mci_transformation(
                cols = cols
                )
            interaction_matrix_df = self.get_interaction_matrix_df()

        mci_formula = f'p_ij__LCT ~ {" + ".join(cols_t)} -1'

        mci_ols_model = ols(mci_formula, data = interaction_matrix_df).fit()

        mci_ols_coefficients = mci_ols_model.params
        mci_ols_coef_standarderrors = mci_ols_model.bse
        mci_ols_coef_t = mci_ols_model.tvalues
        mci_ols_coef_p = mci_ols_model.pvalues
        mci_ols_coef_ci = mci_ols_model.conf_int(alpha = alpha)

        coefs = {}
        for i, col in enumerate(cols_t):
            coefs[i] = {
                "Coefficient": col[:-5],
                "Estimate": float(mci_ols_coefficients[col]),
                "SE": float(mci_ols_coef_standarderrors[col]),
                "t": float(mci_ols_coef_t[col]),
                "p": float(mci_ols_coef_p[col]),
                "CI_lower": float(mci_ols_coef_ci.loc[col, 0]),
                "CI_upper": float(mci_ols_coef_ci.loc[col, 1]),
                }

        customer_origins_metadata["weighting"][0] = {
            "func": "power",
            "param": mci_ols_coefficients["t_ij__LCT"]
            }

        coefs2 = coefs.copy()
        for key, value in list(coefs2.items()):
            if value["Coefficient"] == "t_ij":
                del coefs2[key]

        for key, value in coefs2.items():
            supply_locations_metadata["weighting"][key] = {
                "func": "power",
                "param": value["Estimate"]
            }

            supply_locations_metadata["attraction_col"].append(None)
            supply_locations_metadata["attraction_col"][key] = value["Coefficient"]

        customer_origins.metadata = customer_origins_metadata
        supply_locations.metadata = supply_locations_metadata
        
        interaction_matrix_metadata = {
            "fit": {
                "function": "mci_fit",
                "fit_by": "probabilities",
                "method": "OLS"
                }
            }
               
        interaction_matrix = InteractionMatrix(
            interaction_matrix_df,
            customer_origins,
            supply_locations,
            metadata=interaction_matrix_metadata
            )
        
        mci_model = MCIModel(
            interaction_matrix,
            coefs,
            mci_ols_model,
            None
            )
        
        return mci_model

    def loglik(
        self,
        params,
        fit_by = "probabilities",
        check_df_vars: bool = True
        ):
        
        if fit_by not in ["probabilities", "flows"]:
            raise ValueError ("Error in loglik: Parameter 'fit_by' must be 'probabilities' or 'flows'")

        if not isinstance(params, list):
            if isinstance(params, np.ndarray):
                params = params.tolist()
            else:
                raise ValueError("Error in loglik: Parameter 'params' must be a list or np.ndarray with at least 2 parameter values")
        
        if len(params) < 2:
            raise ValueError("Error in loglik: Parameter 'params' must be a list or np.ndarray with at least 2 parameter values")
        
        customer_origins = self.customer_origins
        customer_origins_metadata = customer_origins.get_metadata()
        
        param_gamma, param_lambda = params[0], params[1]
            
        if customer_origins_metadata["weighting"][0]["func"] == "logistic":
            
            if len(params) < 3:
                raise ValueError("Error in loglik: When using logistic weighting, parameter 'params' must be a list or np.ndarray with at least 3 parameter values")
        
            param_gamma, param_lambda, param_lambda2 = params[0], params[1], params[2]

        interaction_matrix_df = self.interaction_matrix_df
        
        supply_locations = self.supply_locations
        supply_locations_metadata = supply_locations.get_metadata()        

        supply_locations_metadata["weighting"][0]["param"] = float(param_gamma)
        supply_locations.metadata = supply_locations_metadata

        if customer_origins_metadata["weighting"][0]["func"] in ["power", "exponential"]:
            
            if len(params) >= 2:

                customer_origins_metadata["weighting"][0]["param"] = float(param_lambda)
            
            else:
                
                raise ValueError ("Error in loglik: Huff Model with transport cost weighting of type " + customer_origins_metadata["weighting"][0]["func"] + " must have >= 2 input parameters")
        
        elif customer_origins_metadata["weighting"][0]["func"] == "logistic":
            
            if len(params) >= 3:
                
                customer_origins_metadata["weighting"][0]["param"] = [float(param_lambda), float(param_lambda2)]
            
            else:

                raise ValueError("Error in loglik: Huff Model with transport cost weightig of type " + customer_origins_metadata["weighting"][0]["func"] + " must have >= 3 input parameters")

        if (customer_origins_metadata["weighting"][0]["func"] in ["power", "exponential"] and len(params) > 2): 
            
            for key, param in enumerate(params):

                if key <= 1:
                    continue

                supply_locations_metadata["weighting"][key-1]["param"] = float(param)

        if (customer_origins_metadata["weighting"][0]["func"] == "logistic" and len(params) > 3):

            for key, param in enumerate(params):

                if key <= 2:
                    continue

                supply_locations_metadata["weighting"][key-2]["param"] = float(param)

        customer_origins.metadata = customer_origins_metadata

        if "p_ij_emp" not in interaction_matrix_df.columns:
            p_ij_emp = interaction_matrix_df["p_ij"]
        else:
            p_ij_emp = interaction_matrix_df["p_ij_emp"]

        if "E_ij_emp" not in interaction_matrix_df.columns:
            E_ij_emp = interaction_matrix_df["E_ij"]         
        else:
            E_ij_emp = interaction_matrix_df["E_ij_emp"]
        
        interaction_matrix_copy = copy.deepcopy(self)

        interaction_matrix_copy.utility(check_df_vars = check_df_vars)
        interaction_matrix_copy.probabilities(check_df_vars = check_df_vars)
        interaction_matrix_copy.flows(check_df_vars = check_df_vars)

        interaction_matrix_df_copy = interaction_matrix_copy.get_interaction_matrix_df()
        
        if fit_by == "flows":            
                       
            E_ij = interaction_matrix_df_copy["E_ij"]
        
            observed = E_ij_emp
            expected = E_ij            
            
        else:
        
            p_ij = interaction_matrix_df_copy["p_ij"]
            
            observed = p_ij_emp
            expected = p_ij
        
        modelfit_metrics = modelfit(
            observed = observed,
            expected = expected
        )

        LL = modelfit_metrics[1]["LL"]       
       
        return -LL
    
    def huff_ml_fit(
        self,
        initial_params: list = [1.0, -2.0],
        method: str = "L-BFGS-B",
        bounds: list = [(0.5, 1), (-3, -1)],        
        constraints: list = [],
        fit_by = "probabilities",
        update_estimates: bool = True,
        check_df_vars: bool = True
        ):       

        supply_locations = self.supply_locations
        supply_locations_metadata = supply_locations.get_metadata()
        
        customer_origins = self.customer_origins
        customer_origins_metadata = customer_origins.get_metadata()

        if customer_origins_metadata["weighting"][0]["param"] is None:            
            params_metadata_customer_origins = 1            
        else:            
            if customer_origins_metadata["weighting"][0]["param"] is not None:
                if isinstance(customer_origins_metadata["weighting"][0]["param"], (int, float)):
                    params_metadata_customer_origins = 1
                else:
                    params_metadata_customer_origins = len(customer_origins_metadata["weighting"][0]["param"])
            
        if customer_origins_metadata["weighting"][0]["func"] == "logistic":
            params_metadata_customer_origins = 2
        else:
            params_metadata_customer_origins = 1
            
        params_metadata_supply_locations = len(supply_locations_metadata["weighting"])
        
        params_metadata = params_metadata_customer_origins+params_metadata_supply_locations

        if len(initial_params) < 2 or len(initial_params) != params_metadata:
            raise ValueError("Error in huff_ml_fit: Parameter 'initial_params' must be a list with " + str(params_metadata) + " entries (Attaction: " + str(params_metadata_supply_locations) + ", Transport costs: " + str(params_metadata_customer_origins) + ")")
        
        if len(bounds) != len(initial_params):            
            raise ValueError("Error in huff_ml_fit: Parameter 'bounds' must have the same length as parameter 'initial_params' (" + str(len(bounds)) + ", " + str(len(initial_params)) + ")")

        ml_result = minimize(
            self.loglik,
            initial_params,
            args=(fit_by, check_df_vars),
            method = method,
            bounds = bounds,
            constraints = constraints,
            options={'disp': 3}
            )      

        attrac_vars = len(supply_locations_metadata["weighting"])

        if ml_result.success:
            
            fitted_params = ml_result.x
            
            param_gamma = fitted_params[0]
            supply_locations_metadata["weighting"][0]["param"] = float(param_gamma)
            
            if customer_origins_metadata["weighting"][0]["func"] in ["power", "exponential"]:
                            
                param_lambda = fitted_params[1]                
                param_results = [
                    float(param_gamma), 
                    float(param_lambda)
                    ]
                                
                customer_origins_metadata["weighting"][0]["param"] = float(param_lambda)
                
            elif customer_origins_metadata["weighting"][0]["func"] == "logistic":
        
                param_lambda = fitted_params[1]
                param_lambda2 = fitted_params[2]                
                param_results = [
                    float(param_gamma), 
                    float(param_lambda), 
                    float(param_lambda2)
                    ]
                
                customer_origins_metadata["weighting"][0]["param"][0] = float(param_lambda)
                customer_origins_metadata["weighting"][0]["param"][1] = float(param_lambda2)
                
            if attrac_vars > 1:

                if customer_origins_metadata["weighting"][0]["func"] == "logistic":
                    fitted_params_add = 3
                else:
                    fitted_params_add = 2 

                for key, var in supply_locations_metadata["weighting"].items():

                    if key > len(supply_locations_metadata["weighting"])-fitted_params_add:
                        break
                    
                    param = float(fitted_params[key+fitted_params_add])
                    
                    param_results = param_results + [param]

                    supply_locations_metadata["weighting"][(key+1)]["param"] = float(param)
                    
            print(f"Optimization via {method} algorithm succeeded with parameters: {', '.join(str(round(par, 3)) for par in param_results)}.")
   
        else:
                
            print(f"Optimiziation via {method} algorithm failed with error message: '{ml_result.message}'. See https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html for all available algorithms.")

        self.supply_locations.metadata = supply_locations_metadata    
        self.customer_origins.metadata = customer_origins_metadata       
        
        if update_estimates:

            if "p_ij_emp" not in self.interaction_matrix_df.columns:
                
                self.interaction_matrix_df["p_ij_emp"] = self.interaction_matrix_df["p_ij"]
                
                print("NOTE: Probabilities in interaction matrix are treated as empirical probabilities")
                
            else:
                
                print("NOTE: Interaction matrix contains empirical probabilities")

            if "E_ij_emp" not in self.interaction_matrix_df.columns:
                
                self.interaction_matrix_df["E_ij_emp"] = self.interaction_matrix_df["E_ij"]
                
                print("NOTE: Customer interactions in interaction matrix are treated as empirical interactions")
                
            else:
                
                print("NOTE: Interaction matrix contains empirical customer interactions")

            if np.isnan(ml_result.x).any():

                print("WARNING: No update of estimates because fit parameters contain NaN")

                update_estimates = False

            else:

                self = self.utility()
                self = self.probabilities()
                self = self.flows()            
        
        self.metadata["fit"] = {
            "function": "huff_ml_fit",
            "fit_by": fit_by,
            "initial_params": initial_params,
            "method": method,
            "bounds": bounds,
            "constraints": constraints,
            "minimize_success": ml_result.success,
            "minimize_fittedparams": ml_result.x,
            "update_estimates": update_estimates
            }
        
        return self    

    def update(self):

        interaction_matrix_df = self.get_interaction_matrix_df()
        
        interaction_matrix_metadata = self.get_metadata()

        customer_origins = self.get_customer_origins()

        supply_locations = self.get_supply_locations()        
     
        supply_locations_geodata_gpd = supply_locations.get_geodata_gpd().copy()
        supply_locations_geodata_gpd_new = supply_locations_geodata_gpd[supply_locations_geodata_gpd["j_update"] == 1]
        
        if len(supply_locations_geodata_gpd_new) < 1:
            raise ValueError("Error in InteractionMatrix update: There are no new destinations for an interaction matrix update. Use SupplyLocations.add_new_destinations()")

        supply_locations_geodata_gpd_original = supply_locations.get_geodata_gpd_original().copy()        
        supply_locations_geodata_gpd_original_new = supply_locations_geodata_gpd_original[supply_locations_geodata_gpd_original["j_update"] == 1]
        if len(supply_locations_geodata_gpd_original_new) < 1:
            raise ValueError("Error in InteractionMatrix update: There are no new destinations for an interaction matrix update. Use SupplyLocations.add_new_destinations()")

        supply_locations_new = SupplyLocations(
            geodata_gpd=supply_locations_geodata_gpd_new,
            geodata_gpd_original=supply_locations_geodata_gpd_original_new,
            metadata=supply_locations.metadata,
            isochrones_gdf=supply_locations.isochrones_gdf,
            buffers_gdf=supply_locations.buffers_gdf
        )

        interaction_matrix_new = create_interaction_matrix(
            customer_origins=customer_origins,
            supply_locations=supply_locations_new
        )
        
        interaction_matrix_new_df = interaction_matrix_new.get_interaction_matrix_df() 
     
        if "transport_costs" not in interaction_matrix_metadata:
            
            print("WARNING: New destination(s) included. No transport costs calculation because not defined in original interaction matrix.")
            
            interaction_matrix_df = pd.concat(
                [
                interaction_matrix_df, 
                interaction_matrix_new_df
                ], 
                ignore_index=True
                )
            
            interaction_matrix_df = interaction_matrix_df.sort_values(by = "ij")
        
            self.interaction_matrix_df = interaction_matrix_df   
            
        else:
            
            network = interaction_matrix_metadata["transport_costs"]["network"]
            range_type = interaction_matrix_metadata["transport_costs"]["range_type"]
            time_unit = interaction_matrix_metadata["transport_costs"]["time_unit"]
            distance_unit = interaction_matrix_metadata["transport_costs"]["distance_unit"]
            ors_server = interaction_matrix_metadata["transport_costs"]["ors_server"]
            ors_auth = interaction_matrix_metadata["transport_costs"]["ors_auth"]
            
            interaction_matrix_new.transport_costs(
                network=network,
                range_type=range_type,
                time_unit=time_unit,
                distance_unit=distance_unit,
                ors_server=ors_server,
                ors_auth=ors_auth
            )
            
            interaction_matrix_df = pd.concat(
                [
                    interaction_matrix_df, 
                    interaction_matrix_new_df
                ], 
                ignore_index=True
                )
        
            interaction_matrix_df = interaction_matrix_df.sort_values(by = "ij")
            
            self.interaction_matrix_df = interaction_matrix_df
            
            self.utility()
            self.probabilities()
            self.flows()

        return self

class MarketAreas:

    def __init__(
        self, 
        market_areas_df,        
        metadata
        ):

        self.market_areas_df = market_areas_df
        self.metadata = metadata
   
    def get_market_areas_df(self):
        return self.market_areas_df
    
    def get_metadata(self):
        return self.metadata
    
    def add_to_model(
        self,
        model_object,
        output_model = "Huff"
        ):
        
        if not isinstance(model_object, (HuffModel, MCIModel, InteractionMatrix)):
            raise ValueError("Error while adding MarketAreas to model: Parameter 'interaction_matrix' must be of class HuffModel,  MCIModel, or InteractionMatrix")
        
        if isinstance(model_object, MCIModel):
                        
            model = MCIModel(
                interaction_matrix = model_object.interaction_matrix,
                coefs = model_object.get_coefs_dict(),
                mci_ols_model = model_object.get_mci_ols_model(),
                market_areas_df = self.market_areas_df
                )            
    
        elif isinstance(model_object, HuffModel):
            
            model = HuffModel(
                interaction_matrix = model_object.interaction_matrix,
                market_areas_df = self.market_areas_df
            )

        elif isinstance(model_object, InteractionMatrix):

            if output_model not in ["Huff", "MCI"]:
                raise ValueError("Error while adding MarketAreas to model: Parameter 'output_model' must be either 'Huff' or 'MCI'")
            
            if output_model == "Huff":

                model = HuffModel(
                    interaction_matrix=model_object,
                    market_areas_df=self.market_areas_df
                )

            if output_model == "MCI":

                model = MCIModel(
                    coefs=model_object.coefs,
                    mci_ols_model=model_object.mci_ols_model,
                    market_areas_df=self.market_areas_df
                )

        return model

class HuffModel:

    def __init__(
        self,
        interaction_matrix, 
        market_areas_df
        ):

        self.interaction_matrix = interaction_matrix
        self.market_areas_df = market_areas_df

    def get_interaction_matrix_df(self):

        interaction_matrix = self.interaction_matrix
        interaction_matrix_df = interaction_matrix.get_interaction_matrix_df()

        return interaction_matrix_df
    
    def get_supply_locations(self):

        interaction_matrix = self.interaction_matrix
        supply_locations = interaction_matrix.get_supply_locations()

        return supply_locations

    def get_customer_origins(self):

        interaction_matrix = self.interaction_matrix
        customer_origins = interaction_matrix.get_customer_origins()

        return customer_origins

    def get_market_areas_df(self):

        return self.market_areas_df
        
    def summary(self):

        interaction_matrix = self.interaction_matrix

        customer_origins_metadata = interaction_matrix.get_customer_origins().get_metadata()
        supply_locations_metadata = interaction_matrix.get_supply_locations().get_metadata()
        interaction_matrix_metadata = interaction_matrix.get_metadata()

        print("Huff Model")
        print("----------------------------------")
        print("Supply locations    " + str(supply_locations_metadata["no_points"]))
        if supply_locations_metadata["attraction_col"][0] is None:
            print("Attraction column   not defined")
        else:
            print("Attraction column   " + supply_locations_metadata["attraction_col"][0])
        print("Customer origins    " + str(customer_origins_metadata["no_points"]))
        if customer_origins_metadata["marketsize_col"] is None:
            print("Market size column  not defined")
        else:
            print("Market size column  " + customer_origins_metadata["marketsize_col"])
        print("----------------------------------")

        print("Partial utilities")
        print("                    Weights")

        if supply_locations_metadata["weighting"][0]["func"] is None and supply_locations_metadata["weighting"][0]["param"] is None:
            print("Attraction          not defined")
        else:
            if supply_locations_metadata["weighting"][0]["param"] is not None:
                print("Attraction          " + str(round(supply_locations_metadata["weighting"][0]["param"],3)) + " (" + supply_locations_metadata["weighting"][0]["func"] + ")")
            else:
                print("Attraction          NA" + " (" + supply_locations_metadata["weighting"][0]["func"] + ")")   

        if customer_origins_metadata["weighting"][0]["func"] is None and customer_origins_metadata["weighting"][0]["param"] is None:
            print("Transport costs     not defined")
        elif customer_origins_metadata["weighting"][0]["func"] in ["power", "exponential"]:
            if customer_origins_metadata["weighting"][0]["param"] is not None:
                print("Transport costs     " + str(round(customer_origins_metadata["weighting"][0]["param"],3)) + " (" + customer_origins_metadata["weighting"][0]["func"] + ")")
            else:
                print("Transport costs     NA" + " (" + customer_origins_metadata["weighting"][0]["func"] + ")")
        elif customer_origins_metadata["weighting"][0]["func"] == "logistic":
            if customer_origins_metadata["weighting"][0]["param"] is not None:
                print("Transport costs    " + str(round(customer_origins_metadata["weighting"][0]["param"][0],3)) + ", " + str(round(customer_origins_metadata["weighting"][0]["param"][1],3)) + " (" + customer_origins_metadata["weighting"][0]["func"] + ")")
            else:
                print("Transport costs     NA" + " (" + customer_origins_metadata["weighting"][0]["func"] + ")")

        attrac_vars = supply_locations_metadata["attraction_col"]
        attrac_vars_no = len(attrac_vars)
        
        if attrac_vars_no > 1:
                        
            for key, attrac_var in enumerate(attrac_vars):
                
                if key == 0:
                    continue
                
                if key not in supply_locations_metadata["weighting"].keys():
                    
                    print(f"{attrac_vars[key][:16]:16}    not defined")
                    
                else:

                    name = supply_locations_metadata["weighting"][key]["name"]
                    func = supply_locations_metadata["weighting"][key]["func"]

                    if "param" in supply_locations_metadata["weighting"][key]: 
                    
                        param = supply_locations_metadata["weighting"][key]["param"]
                        
                        if param is not None:

                            print(f"{name[:16]:16}    {round(param, 3)} ({func})")

                        else:

                            print(f"{attrac_vars[key][:16]:16}    NA ({func})")
                    
        print("----------------------------------")

        huff_modelfit = None

        if interaction_matrix_metadata != {} and "fit" in interaction_matrix_metadata and interaction_matrix_metadata["fit"]["function"] is not None:
            print("Parameter estimation")
            print("Fit function        " + interaction_matrix_metadata["fit"]["function"])
            print("Fit by              " + interaction_matrix_metadata["fit"]["fit_by"])
            if interaction_matrix_metadata["fit"]["function"] == "huff_ml_fit":
                print("Fit method          " + interaction_matrix_metadata["fit"]["method"] + " (Converged: " + str(interaction_matrix_metadata["fit"]["minimize_success"]) + ")")

            huff_modelfit = self.modelfit(by = interaction_matrix_metadata["fit"]["fit_by"])
            
            if huff_modelfit is not None:
                
                print ("Goodness-of-fit for " + interaction_matrix_metadata["fit"]["fit_by"])
                        
                print("Sum of squared residuals       ", round(huff_modelfit[1]["SQR"], 2))
                print("R-squared                      ", round(huff_modelfit[1]["Rsq"], 2))
                print("Mean squared error             ", round(huff_modelfit[1]["MSE"], 2))
                print("Root mean squared error        ", round(huff_modelfit[1]["RMSE"], 2))
                print("Mean absolute error            ", round(huff_modelfit[1]["MAE"], 2))
                if huff_modelfit[1]["MAPE"] is not None:
                    print("Mean absolute percentage error ", round(huff_modelfit[1]["MAPE"], 2))
                else:
                    print("Mean absolute percentage error  Not calculated")
                print("Symmetric MAPE                 ", round(huff_modelfit[1]["sMAPE"], 2))
                print("Absolute percentage errors")
                
                APE_list = [
                    ["< 5 % ", round(huff_modelfit[1]["APE"]["resid_below5"], 2), "  < 30 % ", round(huff_modelfit[1]["APE"]["resid_below30"], 2)],
                    ["< 10 % ", round(huff_modelfit[1]["APE"]["resid_below10"], 2), "  < 35 % ", round(huff_modelfit[1]["APE"]["resid_below35"], 2)],
                    ["< 15 % ", round(huff_modelfit[1]["APE"]["resid_below15"], 2), "  < 40 % ", round(huff_modelfit[1]["APE"]["resid_below40"], 2)],
                    ["< 20 % ", round(huff_modelfit[1]["APE"]["resid_below20"], 2), "  < 45 % ", round(huff_modelfit[1]["APE"]["resid_below45"], 2)],
                    ["< 25% ", round(huff_modelfit[1]["APE"]["resid_below25"], 2), "  < 50 % ", round(huff_modelfit[1]["APE"]["resid_below50"], 2)]
                    ]
                APE_df = pd.DataFrame(
                    APE_list,
                    columns=["Resid.", "%", "Resid.", "%"]
                    )
                print(APE_df.to_string(index=False))
                    
                print("----------------------------------")

        return [
            customer_origins_metadata,
            supply_locations_metadata,
            interaction_matrix_metadata,
            huff_modelfit
            ]

    def mci_fit(
        self,
        cols: list = ["A_j", "t_ij"],
        alpha = 0.05
        ):

        interaction_matrix = self.interaction_matrix
        interaction_matrix_df = interaction_matrix.get_interaction_matrix_df()
        interaction_matrix_metadata = interaction_matrix.get_metadata()       

        supply_locations = interaction_matrix.get_supply_locations()
        supply_locations_metadata = supply_locations.get_metadata()

        customer_origins = interaction_matrix.get_customer_origins()
        customer_origins_metadata = customer_origins.get_metadata()
        
        cols_t = [col + "__LCT" for col in cols]

        if "p_ij__LCT" not in interaction_matrix_df.columns:
            interaction_matrix = interaction_matrix.mci_transformation(
                cols = cols
                )
            interaction_matrix_df = interaction_matrix.get_interaction_matrix_df()

        mci_formula = f'p_ij__LCT ~ {" + ".join(cols_t)} -1'

        mci_ols_model = ols(mci_formula, data = interaction_matrix_df).fit()

        mci_ols_coefficients = mci_ols_model.params
        mci_ols_coef_standarderrors = mci_ols_model.bse
        mci_ols_coef_t = mci_ols_model.tvalues
        mci_ols_coef_p = mci_ols_model.pvalues
        mci_ols_coef_ci = mci_ols_model.conf_int(alpha = alpha)

        coefs = {}
        for i, col in enumerate(cols_t):
            coefs[i] = {
                "Coefficient": col[:-5],
                "Estimate": float(mci_ols_coefficients[col]),
                "SE": float(mci_ols_coef_standarderrors[col]),
                "t": float(mci_ols_coef_t[col]),
                "p": float(mci_ols_coef_p[col]),
                "CI_lower": float(mci_ols_coef_ci.loc[col, 0]),
                "CI_upper": float(mci_ols_coef_ci.loc[col, 1]),
                }

        customer_origins_metadata["weighting"][0] = {
            "func": "power",
            "param": mci_ols_coefficients["t_ij__LCT"]
            }

        coefs2 = coefs.copy()
        for key, value in list(coefs2.items()):
            if value["Coefficient"] == "t_ij":
                del coefs2[key]

        for key, value in coefs2.items():
            supply_locations_metadata["weighting"][(key)] = {
                "func": "power",
                "param": value["Estimate"]
            }
            supply_locations_metadata["attraction_col"][key] = value["Coefficient"]

        customer_origins.metadata = customer_origins_metadata
        supply_locations.metadata = supply_locations_metadata
        
        interaction_matrix_metadata = {
            "fit": {
                "function": "mci_fit",
                "fit_by": "probabilities",
                "method": "OLS"
                }
            }
        
        interaction_matrix = InteractionMatrix(
            interaction_matrix_df,
            customer_origins,
            supply_locations,
            metadata=interaction_matrix_metadata
            )
        
        mci_model = MCIModel(
            interaction_matrix,
            coefs,
            mci_ols_model,
            None
            )
        
        return mci_model

    def loglik(
        self,
        params,
        check_df_vars: bool = True
        ):

        if not isinstance(params, list):
            if isinstance(params, np.ndarray):
                params = params.tolist()
            else:
                raise ValueError("Error in loglik: Parameter 'params' must be a list or np.ndarray with at least 2 parameter values")
        
        if len(params) < 2:
            raise ValueError("Error in loglik: Parameter 'params' must be a list or np.ndarray with at least 2 parameter values")
        
        market_areas_df = self.market_areas_df
        
        customer_origins = self.interaction_matrix.customer_origins
        customer_origins_metadata = customer_origins.get_metadata()
        
        param_gamma, param_lambda = params[0], params[1]
            
        if customer_origins_metadata["weighting"][0]["func"] == "logistic":
            
            if len(params) < 3:
                raise ValueError("Error in loglik: When using logistic weighting, parameter 'params' must be a list or np.ndarray with at least 3 parameter values")
        
            param_gamma, param_lambda, param_lambda2 = params[0], params[1], params[2]

        supply_locations = self.interaction_matrix.supply_locations
        supply_locations_metadata = supply_locations.get_metadata()        

        supply_locations_metadata["weighting"][0]["param"] = float(param_gamma)
        supply_locations.metadata = supply_locations_metadata

        if customer_origins_metadata["weighting"][0]["func"] in ["power", "exponential"]:
            
            if len(params) >= 2:

                customer_origins_metadata["weighting"][0]["param"] = float(param_lambda)
            
            else:
                
                raise ValueError ("Error in loglik: Huff Model with transport cost weighting of type " + customer_origins_metadata["weighting"][0]["func"] + " must have >= 2 input parameters")
        
        elif customer_origins_metadata["weighting"][0]["func"] == "logistic":
            
            if len(params) >= 3:
                
                customer_origins_metadata["weighting"][0]["param"] = [float(param_lambda), float(param_lambda2)]
            
            else:

                raise ValueError("Error in loglik: Huff Model with transport cost weightig of type " + customer_origins_metadata["weighting"][0]["func"] + " must have >= 3 input parameters")

        if (customer_origins_metadata["weighting"][0]["func"] in ["power", "exponential"] and len(params) > 2): 
            
            for key, param in enumerate(params):

                if key <= 1:
                    continue

                supply_locations_metadata["weighting"][key-1]["param"] = float(param)

        if (customer_origins_metadata["weighting"][0]["func"] == "logistic" and len(params) > 3):

            for key, param in enumerate(params):

                if key <= 2:
                    continue

                supply_locations_metadata["weighting"][key-2]["param"] = float(param)

        customer_origins.metadata = customer_origins_metadata        
       
        if "T_j_emp" not in market_areas_df.columns:
            T_j_emp = market_areas_df["T_j"]
        else:
            T_j_emp = market_areas_df["T_j_emp"]


        huff_model_copy = copy.deepcopy(self)

        interaction_matrix_copy = copy.deepcopy(huff_model_copy.interaction_matrix)

        interaction_matrix_copy = interaction_matrix_copy.utility(check_df_vars = check_df_vars)
        interaction_matrix_copy = interaction_matrix_copy.probabilities(check_df_vars = check_df_vars)
        interaction_matrix_copy = interaction_matrix_copy.flows(check_df_vars = check_df_vars)

        huff_model_copy = interaction_matrix_copy.marketareas()

        market_areas_df_copy = huff_model_copy.market_areas_df

        observed = T_j_emp
        expected = market_areas_df_copy["T_j"]
        
        modelfit_metrics = modelfit(
            observed = observed,
            expected = expected
        )

        LL = modelfit_metrics[1]["LL"]
      
        return -LL

    def ml_fit(
        self,
        initial_params: list = [1.0, -2.0],
        method: str = "L-BFGS-B",
        bounds: list = [(0.5, 1), (-3, -1)],        
        constraints: list = [],
        fit_by = "probabilities",
        update_estimates: bool = True,
        check_numbers: bool = True,
        check_df_vars: bool = True
        ):
        
        if fit_by in ["probabilities", "flows"]:

            self.interaction_matrix.huff_ml_fit(
                initial_params = initial_params,
                method = method,
                bounds = bounds,        
                constraints = constraints,
                fit_by = fit_by,
                update_estimates = update_estimates,
                check_df_vars = check_df_vars
                )
        
        elif fit_by == "totals":
            
            if check_numbers:
                
                market_areas_df = self.market_areas_df
                interaction_matrix_df = self.get_interaction_matrix_df()
                T_j_market_areas_df = sum(market_areas_df["T_j"])
                T_j_interaction_matrix_df = sum(interaction_matrix_df["E_ij"])
                
                if T_j_market_areas_df != T_j_interaction_matrix_df:
                    print("WARNING: Sum of total market areas (" + str(int(T_j_market_areas_df)) + ") is not equal to sum of customer flows (" + str(int(T_j_interaction_matrix_df)) + ")")
            
            supply_locations = self.interaction_matrix.supply_locations
            supply_locations_metadata = supply_locations.get_metadata()
        
            customer_origins = self.interaction_matrix.customer_origins
            customer_origins_metadata = customer_origins.get_metadata()

            if customer_origins_metadata["weighting"][0]["param"] is None:            
                params_metadata_customer_origins = 1            
            else:            
                if customer_origins_metadata["weighting"][0]["param"] is not None:
                    if isinstance(customer_origins_metadata["weighting"][0]["param"], (int, float)):
                        params_metadata_customer_origins = 1
                    else:
                        params_metadata_customer_origins = len(customer_origins_metadata["weighting"][0]["param"])
            
            if customer_origins_metadata["weighting"][0]["func"] == "logistic":
                params_metadata_customer_origins = 2
            else:
                params_metadata_customer_origins = 1
                
            params_metadata_supply_locations = len(supply_locations_metadata["weighting"])
            
            params_metadata = params_metadata_customer_origins+params_metadata_supply_locations

            if len(initial_params) < 2 or len(initial_params) != params_metadata:
                raise ValueError("Error in ml_fit: Parameter 'initial_params' must be a list with " + str(params_metadata) + " entries (Attaction: " + str(params_metadata_supply_locations) + ", Transport costs: " + str(params_metadata_customer_origins) + ")")
            
            if len(bounds) != len(initial_params):            
                raise ValueError("Error in ml_fit: Parameter 'bounds' must have the same length as parameter 'initial_params' (" + str(len(bounds)) + ", " + str(len(initial_params)) + ")")

            ml_result = minimize(
                self.loglik,
                initial_params,
                args=check_df_vars,
                method = method,
                bounds = bounds,
                constraints = constraints,
                options={'disp': 3}
                )
            
            attrac_vars = len(supply_locations_metadata["weighting"])

            if ml_result.success:
                
                fitted_params = ml_result.x
                
                param_gamma = fitted_params[0]
                supply_locations_metadata["weighting"][0]["param"] = float(param_gamma)
                
                if customer_origins_metadata["weighting"][0]["func"] in ["power", "exponential"]:
                                
                    param_lambda = fitted_params[1]                
                    param_results = [
                        float(param_gamma), 
                        float(param_lambda)
                        ]
                                    
                    customer_origins_metadata["weighting"][0]["param"] = float(param_lambda)
                    
                elif customer_origins_metadata["weighting"][0]["func"] == "logistic":
            
                    param_lambda = fitted_params[1]
                    param_lambda2 = fitted_params[2]                
                    param_results = [
                        float(param_gamma), 
                        float(param_lambda), 
                        float(param_lambda2)
                        ]
                    
                    customer_origins_metadata["weighting"][0]["param"][0] = float(param_lambda)
                    customer_origins_metadata["weighting"][0]["param"][1] = float(param_lambda2)
                    
                if attrac_vars > 1:

                    if customer_origins_metadata["weighting"][0]["func"] == "logistic":
                        fitted_params_add = 3
                    else:
                        fitted_params_add = 2 

                    for key, var in supply_locations_metadata["weighting"].items():

                        if key > len(supply_locations_metadata["weighting"])-fitted_params_add:
                            break
                        
                        param = float(fitted_params[key+fitted_params_add])
                        
                        param_results = param_results + [param]

                        supply_locations_metadata["weighting"][(key+1)]["param"] = float(param)
                        
                print(f"Optimization via {method} algorithm succeeded with parameters: {', '.join(str(round(par, 3)) for par in param_results)}.")
    
            else:
                   
                print(f"Optimiziation via {method} algorithm failed with error message: '{ml_result.message}'. See https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html for all available algorithms.")

            self.interaction_matrix.supply_locations.metadata = supply_locations_metadata    
            self.interaction_matrix.customer_origins.metadata = customer_origins_metadata

            if update_estimates:

                if "T_j_emp" not in self.market_areas_df.columns:

                    self.market_areas_df["T_j_emp"] = self.market_areas_df["T_j"]
                    
                    print("NOTE: Total values in market areas df are treated as empirical total values")
                
                else:

                    print("NOTE: Total market areas df contains empirical total values")

                if np.isnan(ml_result.x).any():

                    print("WARNING: No update of estimates because fit parameters contain NaN")

                    update_estimates = False

                else:
                                       
                    self.interaction_matrix.utility(check_df_vars = check_df_vars)
                    self.interaction_matrix.probabilities(check_df_vars = check_df_vars)
                    self.interaction_matrix.flows(check_df_vars = check_df_vars) 
                    
                    huff_model_new_marketareas = self.interaction_matrix.marketareas(check_df_vars = check_df_vars)
                    self.market_areas_df["T_j"] = huff_model_new_marketareas.get_market_areas_df()["T_j"]
            
            self.interaction_matrix.metadata["fit"] = {
                "function": "huff_ml_fit",
                "fit_by": fit_by,
                "initial_params": initial_params,
                "method": method,
                "bounds": bounds,
                "constraints": constraints,
                "minimize_success": ml_result.success,
                "minimize_fittedparams": ml_result.x,
                "update_estimates": update_estimates
                }
            
        else:

            raise ValueError("Error in ml_fit: Parameter 'fit_by' must be 'probabilities', 'flows' or 'totals'")

        return self
    
    def confint(
        self,
        alpha = 0.05,
        repeats = 3,
        sample_size = 0.75,
        replace = True
        ):
        
        if self.interaction_matrix.metadata["fit"] is None or self.interaction_matrix.metadata["fit"] == {}:
            raise ValueError("Error while estimating confidence intervals: Model object does not contain information towards fit procedure")

        keys_necessary = [
            "function", 
            "fit_by", 
            "initial_params",
            "method",
            "bounds",
            "constraints"            
            ]

        for key_necessary in keys_necessary:
            if key_necessary not in self.interaction_matrix.metadata["fit"]:
                raise KeyError(f"Error while estimating confidence intervals: Model object does not contain full information towards fit procedure. Missing key {key_necessary}")
        
        fitted_params_repeats = []

        alpha_lower = alpha/2
        alpha_upper = 1-alpha/2

        huff_model_copy = copy.deepcopy(self)     

        if self.interaction_matrix.metadata["fit"]["fit_by"] in ["probabilities", "flows"]:
        
            for i in range(repeats):
                
                try:
                
                    n_samples = int(len(huff_model_copy.interaction_matrix.interaction_matrix_df)*sample_size)
                    
                    huff_model_copy.interaction_matrix.interaction_matrix_df = huff_model_copy.interaction_matrix.interaction_matrix_df.sample(
                        n = n_samples, 
                        replace = replace
                        )
                    
                    huff_model_copy.ml_fit(
                        initial_params = self.interaction_matrix.metadata["fit"]["initial_params"],
                        method = self.interaction_matrix.metadata["fit"]["method"],
                        bounds = self.interaction_matrix.metadata["fit"]["bounds"],        
                        constraints = self.interaction_matrix.metadata["fit"]["constraints"],
                        fit_by = self.interaction_matrix.metadata["fit"]["fit_by"],
                        update_estimates = True,
                        check_numbers = True
                    )
                    
                    minimize_fittedparams = huff_model_copy.interaction_matrix.metadata["fit"]["minimize_fittedparams"]
                        
                    fitted_params_repeats.append(minimize_fittedparams)

                except Exception as err:

                    print (f"Error in repeat {str(i)}: {err}")
        
        elif self.metadata["fit"]["fit_by"] == "totals":
            
            for i in range(repeats):

                n_samples = int(len(huff_model_copy.market_areas_df)*sample_size)

                huff_model_copy.market_areas_df = huff_model_copy.market_areas_df.sample(
                    n = n_samples, 
                    replace = replace
                    )
            
                huff_model_copy.interaction_matrix.interaction_matrix_df = huff_model_copy.interaction_matrix.interaction_matrix_df[
                    huff_model_copy.interaction_matrix.interaction_matrix_df["j"].isin(huff_model_copy.market_areas_df["j"])
                    ]
                
                huff_model_copy.ml_fit(
                    initial_params = self.interaction_matrix.metadata["fit"]["initial_params"],
                    method = self.interaction_matrix.metadata["fit"]["method"],
                    bounds = self.interaction_matrix.metadata["fit"]["bounds"],        
                    constraints = self.interaction_matrix.metadata["fit"]["constraints"],
                    fit_by = self.interaction_matrix.metadata["fit"]["fit_by"],
                    update_estimates = True,
                    check_numbers = True
                )
                
                minimize_fittedparams = huff_model_copy.interaction_matrix.metadata["fit"]["minimize_fittedparams"]
                    
                fitted_params_repeats.append(minimize_fittedparams)

        else:
            
            raise ValueError("Error while estimating confidence intervals: Parameter 'fit_by' must be 'probabilities', 'flows' or 'totals'")
        
        fitted_params_repeats_array = np.array(fitted_params_repeats)
        fitted_params_repeats_array_transposed = fitted_params_repeats_array.T
        
        param_ci = pd.DataFrame(columns=["lower", "upper"])

        for i, col in enumerate(fitted_params_repeats_array_transposed):
            
            param_ci.loc[i, "lower"] = np.quantile(col, alpha_lower)
            param_ci.loc[i, "upper"] = np.quantile(col, alpha_upper)
        
        return param_ci

    def update(self):
        
        self.interaction_matrix = self.interaction_matrix.update()
        
        self.market_areas_df = self.interaction_matrix.marketareas().get_market_areas_df()
        
        return self
    
    def modelfit(
        self,
        by = "probabilities"
        ):       
        
        if by == "probabilities":

            interaction_matrix = self.interaction_matrix        
            interaction_matrix_df = interaction_matrix.get_interaction_matrix_df()

            if ("p_ij" in interaction_matrix_df.columns and "p_ij_emp" in interaction_matrix_df.columns):
                
                try:
                
                    huff_modelfit = modelfit(
                        interaction_matrix_df["p_ij_emp"],
                        interaction_matrix_df["p_ij"]
                    )
                    
                    return huff_modelfit
                    
                except:
                    
                    print("WARNING: Goodness-of-fit metrics could not be calculated due to NaN values.")
                    return None
            
            else:
                
                print("WARNING: Goodness-of-fit metrics could not be calculated. No empirical values of probabilities in interaction matrix.")

                return None
            
        elif by == "flows":

            interaction_matrix = self.interaction_matrix        
            interaction_matrix_df = interaction_matrix.get_interaction_matrix_df()

            if ("E_ij" in interaction_matrix_df.columns and "E_ij_emp" in interaction_matrix_df.columns):
                
                try:
                
                    huff_modelfit = modelfit(
                        interaction_matrix_df["E_ij_emp"],
                        interaction_matrix_df["E_ij"]
                    )
                    
                    return huff_modelfit
                    
                except:
                    
                    print("WARNING: Goodness-of-fit metrics could not be calculated due to NaN values.")
                    return None
            
            else:
                
                print("WARNING: Goodness-of-fit metrics could not be calculated. No empirical values of customer flows in interaction matrix.")

                return None
            
        elif by == "totals":

            market_areas_df = self.market_areas_df

            if ("T_j" in market_areas_df.columns and "T_j_emp" in market_areas_df.columns):
                
                try:
                
                    huff_modelfit = modelfit(
                        market_areas_df["T_j_emp"],
                        market_areas_df["T_j"]
                    )
                    
                    return huff_modelfit
                    
                except:
                    
                    print("WARNING: Goodness-of-fit metrics could not be calculated due to NaN values.")
                    return None
                
            else:
                
                print("WARNING: Goodness-of-fit metrics could not be calculated. No empirical values of T_j in market areas data.")

                return None

        else:

            raise ValueError("Error in HuffModel.modelfit: Parameter 'by' must be 'probabilities', 'flows', or 'totals'")
    
class MCIModel:

    def __init__(
        self,
        interaction_matrix: InteractionMatrix,
        coefs: dict,
        mci_ols_model,
        market_areas_df
        ):

        self.interaction_matrix = interaction_matrix
        self.coefs = coefs
        self.mci_ols_model = mci_ols_model
        self.market_areas_df = market_areas_df

    def get_interaction_matrix_df(self):

        interaction_matrix = self.interaction_matrix
        interaction_matrix_df = interaction_matrix.get_interaction_matrix_df()

        return interaction_matrix_df
    
    def get_supply_locations(self):

        interaction_matrix = self.interaction_matrix
        supply_locations = interaction_matrix.get_supply_locations()

        return supply_locations

    def get_customer_origins(self):

        interaction_matrix = self.interaction_matrix
        customer_origins = interaction_matrix.get_customer_origins()

        return customer_origins
    
    def get_mci_ols_model(self):

        return self.mci_ols_model
    
    def get_coefs_dict(self):

        return self.coefs
    
    def get_market_areas_df(self):

        return self.market_areas_df

    def modelfit(self):
        
        interaction_matrix = self.interaction_matrix        
        interaction_matrix_df = interaction_matrix.get_interaction_matrix_df()
        
        if ("p_ij" in interaction_matrix_df.columns and "p_ij_emp" in interaction_matrix_df.columns):
            
            try:
            
                mci_modelfit = modelfit(
                    interaction_matrix_df["p_ij_emp"],
                    interaction_matrix_df["p_ij"]
                )
                
                return mci_modelfit
                
            except:
                
                print("WARNING: Goodness-of-fit metrics could not be calculated due to NaN values.")
                return None
        
        else:
            
            return None
        
    def summary(self):

        interaction_matrix = self.interaction_matrix
        coefs = self.coefs

        customer_origins_metadata = interaction_matrix.get_customer_origins().get_metadata()
        supply_locations_metadata = interaction_matrix.get_supply_locations().get_metadata()
        interaction_matrix_metadata = interaction_matrix.get_metadata()

        print("Multiplicative Competitive Interaction Model")
        print("--------------------------------------------")
        print("Supply locations   " + str(supply_locations_metadata["no_points"]))
        print("Customer origins   " + str(customer_origins_metadata["no_points"]))
        print("--------------------------------------------")
        print("Partial utilities")

        coefficients_rows = []
        for key, value in coefs.items():
            coefficient_name = value["Coefficient"]
            if coefficient_name == "A_j":
                coefficient_name = "Attraction"
            if coefficient_name == "t_ij":
                coefficient_name = "Transport costs"
            coefficients_rows.append({
                "": coefficient_name,
                "Estimate": round(value["Estimate"], 3),
                "SE": round(value["SE"], 3),
                "t": round(value["t"], 3),
                "p": round(value["p"], 3),
                "CI lower": round(value["CI_lower"], 3),
                "CI upper": round(value["CI_upper"], 3)
            })
        coefficients_df = pd.DataFrame(coefficients_rows)
        
        print (coefficients_df)

        print("--------------------------------------------")
        
        mci_modelfit = None

        mci_modelfit = self.modelfit()

        if mci_modelfit is not None:
            
            print ("Goodness-of-fit for probabilities")
                    
            print("Sum of squared residuals       ", round(mci_modelfit[1]["SQR"], 2))
            print("R-squared                      ", round(mci_modelfit[1]["Rsq"], 2))
            print("Mean squared error             ", round(mci_modelfit[1]["MSE"], 2))
            print("Root mean squared error        ", round(mci_modelfit[1]["RMSE"], 2))
            print("Mean absolute error            ", round(mci_modelfit[1]["MAE"], 2))
            if mci_modelfit[1]["MAPE"] is not None:
                print("Mean absolute percentage error ", round(mci_modelfit[1]["MAPE"], 2))
            else:
                print("Mean absolute percentage error  Not calculated")
            print("Symmetric MAPE                 ", round(mci_modelfit[1]["sMAPE"], 2))
            
            print("Absolute percentage errors")
            APE_list = [
                ["< 5 % ", round(mci_modelfit[1]["APE"]["resid_below5"], 2), "  < 30 % ", round(mci_modelfit[1]["APE"]["resid_below30"], 2)],
                ["< 10 % ", round(mci_modelfit[1]["APE"]["resid_below10"], 2), "  < 35 % ", round(mci_modelfit[1]["APE"]["resid_below35"], 2)],
                ["< 15 % ", round(mci_modelfit[1]["APE"]["resid_below15"], 2), "  < 40 % ", round(mci_modelfit[1]["APE"]["resid_below40"], 2)],
                ["< 20 % ", round(mci_modelfit[1]["APE"]["resid_below20"], 2), "  < 45 % ", round(mci_modelfit[1]["APE"]["resid_below45"], 2)],
                ["< 25% ", round(mci_modelfit[1]["APE"]["resid_below25"], 2), "  < 50 % ", round(mci_modelfit[1]["APE"]["resid_below50"], 2)]
                ]
            APE_df = pd.DataFrame(
                APE_list,
                columns=["Resid.", "%", "Resid.", "%"]
                )
            print(APE_df.to_string(index=False))
            
            print("--------------------------------------------")

        return [
            customer_origins_metadata,
            supply_locations_metadata,
            interaction_matrix_metadata,
            mci_modelfit
            ]
                  
    def utility(
        self,
        transformation = "LCT",
        check_df_vars: bool = True
        ):
        
        interaction_matrix = self.interaction_matrix        
        interaction_matrix_df = interaction_matrix.get_interaction_matrix_df()
        interaction_matrix_metadata = interaction_matrix.get_metadata()

        if interaction_matrix_df["t_ij"].isna().all():
            raise ValueError ("Error in utility calculation: Transport cost variable is not defined")
        if interaction_matrix_df["A_j"].isna().all():
            raise ValueError ("Error in utility calculation: Attraction variable is not defined")

        if check_df_vars:
            check_vars(
                df = interaction_matrix_df,
                cols = ["A_j", "t_ij"]
                )

        customer_origins = interaction_matrix.get_customer_origins()
        customer_origins_metadata = customer_origins.get_metadata()
        
        t_ij_weighting = customer_origins_metadata["weighting"][0]["param"]

        if transformation == "ILCT":
            mci_formula = f"{t_ij_weighting}*t_ij"
        else:
            mci_formula = f"t_ij**{t_ij_weighting}"
        
        supply_locations = interaction_matrix.get_supply_locations()
        supply_locations_metadata = supply_locations.get_metadata()
        attraction_col = supply_locations_metadata["attraction_col"]
        attraction_weighting = supply_locations_metadata["weighting"]

        if transformation == "ILCT":
            for key, value in attraction_weighting.items():
                mci_formula = mci_formula + f" + {value['param']}*{attraction_col[key]}"
        else:
            for key, value in attraction_weighting.items():
                mci_formula = mci_formula + f" * {attraction_col[key]}**{value['param']}"

        interaction_matrix_df["U_ij"] = interaction_matrix_df.apply(lambda row: eval(mci_formula, {}, row.to_dict()), axis=1)

        if transformation == "ILCT":
            interaction_matrix_df["U_ij"] = np.exp(interaction_matrix_df["U_ij"])

        interaction_matrix_metadata["model"] = {
            "model_type": "MCI",
            "transformation": transformation
            }

        interaction_matrix = InteractionMatrix(
            interaction_matrix_df,
            customer_origins,
            supply_locations,
            metadata=interaction_matrix_metadata
            )
        self.interaction_matrix = interaction_matrix

        return self
    
    def probabilities (
        self,
        transformation = "LCT"
        ):

        interaction_matrix = self.interaction_matrix        
        interaction_matrix_df = interaction_matrix.get_interaction_matrix_df()
        
        if "p_ij" in interaction_matrix_df.columns and "p_ij_emp" not in interaction_matrix_df.columns:
            print("NOTE: Probabilities in interaction matrix are treated as empirical probabilities")
            interaction_matrix_df["p_ij_emp"] = interaction_matrix_df["p_ij"]
        else:
            print("NOTE: Interaction matrix contains empirical probabilities")

        if "U_ij" not in interaction_matrix_df.columns:
            self.utility(transformation = transformation)
            interaction_matrix = self.interaction_matrix
            interaction_matrix_df = interaction_matrix.get_interaction_matrix_df()

        if interaction_matrix_df["U_ij"].isna().all():
            self.utility(transformation = transformation)
            interaction_matrix = self.interaction_matrix
            interaction_matrix_df = interaction_matrix.get_interaction_matrix_df()

        utility_i = pd.DataFrame(interaction_matrix_df.groupby("i")["U_ij"].sum())
        utility_i = utility_i.rename(columns = {"U_ij": "U_i"})

        interaction_matrix_df = interaction_matrix_df.merge(
            utility_i,
            left_on="i",
            right_on="i",
            how="inner"
            )

        interaction_matrix_df["p_ij"] = (interaction_matrix_df["U_ij"]) / (interaction_matrix_df["U_i"])

        interaction_matrix_df = interaction_matrix_df.drop(columns=["U_i"])

        interaction_matrix.interaction_matrix_df = interaction_matrix_df
        self.interaction_matrix = interaction_matrix

        return self
        
    def flows (
        self,
        transformation = "LCT",
        check_df_vars: bool = True
        ):

        interaction_matrix = self.interaction_matrix
        interaction_matrix_df = interaction_matrix.get_interaction_matrix_df()

        if "C_i" not in interaction_matrix_df.columns:
            raise ValueError ("Error in flows calculation: No market size column defined in interaction matrix.")
        
        if interaction_matrix_df["C_i"].isna().all():
            raise ValueError ("Error in flows calculation: Market size column in customer origins not defined. Use CustomerOrigins.define_marketsize()")

        if check_df_vars:
            check_vars(
                df = interaction_matrix_df,
                cols = ["C_i"]
                )

        if interaction_matrix_df["p_ij"].isna().all():
            self.probabilities(transformation=transformation)
            interaction_matrix = self.interaction_matrix
            interaction_matrix_df = interaction_matrix.get_interaction_matrix_df()

        interaction_matrix_df["E_ij"] = interaction_matrix_df["p_ij"] * interaction_matrix_df["C_i"]

        self.interaction_matrix_df = interaction_matrix_df

        return self

    def marketareas (
        self,
        check_df_vars: bool = True
        ):

        interaction_matrix = self.interaction_matrix
        interaction_matrix_df = interaction_matrix.get_interaction_matrix_df()
        
        if check_df_vars:
            check_vars(
                df = interaction_matrix_df,
                cols = ["E_ij"]
                )
        
        market_areas_df = pd.DataFrame(interaction_matrix_df.groupby("j")["E_ij"].sum())
        market_areas_df = market_areas_df.reset_index(drop=False)
        market_areas_df = market_areas_df.rename(columns={"E_ij": "T_j"})

        mci_model = MCIModel(
            interaction_matrix = interaction_matrix,
            coefs = self.get_coefs_dict(),
            mci_ols_model = self.get_mci_ols_model(),
            market_areas_df = market_areas_df
            )

        return mci_model

def load_geodata (
    data, 
    location_type: str, 
    unique_id: str,
    x_col: str = None, 
    y_col: str = None,
    data_type = "shp", 
    csv_sep = ";", 
    csv_decimal = ",", 
    csv_encoding="unicode_escape", 
    crs_input = "EPSG:4326"    
    ):

    if location_type is None or (location_type != "origins" and location_type != "destinations"):
        raise ValueError ("Error while loading geodata: Argument location_type must be either 'origins' or 'destinations'")

    if isinstance(data, gp.GeoDataFrame):
        geodata_gpd_original = data
        if not all(geodata_gpd_original.geometry.geom_type == "Point"):
            raise ValueError ("Error while loading geodata: Input geopandas.GeoDataFrame must be of type 'Point'")
        crs_input = geodata_gpd_original.crs
    elif isinstance(data, pd.DataFrame):
        geodata_tab = data
    elif isinstance(data, str):
        if data_type == "shp":
            geodata_gpd_original = gp.read_file(data)
            if not all(geodata_gpd_original.geometry.geom_type == "Point"):
                raise ValueError ("Error while loading geodata: Input shapefile must be of type 'Point'")
            crs_input = geodata_gpd_original.crs
        elif data_type == "csv" or data_type == "xlsx":
            if x_col is None:
                raise ValueError ("Error while loading geodata: Missing value for X coordinate column")
            if y_col is None:
                raise ValueError ("Error while loading geodata: Missing value for Y coordinate column")
        elif data_type == "csv":
            geodata_tab = pd.read_csv(
                data, 
                sep = csv_sep, 
                decimal = csv_decimal, 
                encoding = csv_encoding
                ) 
        elif data_type == "xlsx":
            geodata_tab = pd.read_excel(data)
        else:
            raise TypeError("Error while loading geodata: Unknown type of data")
    else:
        raise TypeError("Error while loading geodata: Param 'data' must be pandas.DataFrame, geopandas.GeoDataFrame or file (.csv, .xlsx, .shp)")

    if data_type == "csv" or data_type == "xlsx" or (isinstance(data, pd.DataFrame) and not isinstance(data, gp.GeoDataFrame)):
        
        check_vars(
            df = geodata_tab,
            cols = [x_col, y_col]
            )
        
        geodata_gpd_original = gp.GeoDataFrame(
            geodata_tab, 
            geometry = gp.points_from_xy(
                geodata_tab[x_col], 
                geodata_tab[y_col]
                ), 
            crs = crs_input
            )
        
    crs_output = "EPSG:4326"

    geodata_gpd = geodata_gpd_original.to_crs(crs_output)
    geodata_gpd = geodata_gpd[[unique_id, "geometry"]]
    
    metadata = {
        "location_type": location_type,
        "unique_id": unique_id,
        "attraction_col": [None],
        "marketsize_col": None,
        "weighting": {
            0: {
                "name": None,
                "func": None, 
                "param": None
                }
            },
        "crs_input": crs_input,
        "crs_output": crs_output,
        "no_points": len(geodata_gpd)
        }
    
    if location_type == "origins":

        geodata_object = CustomerOrigins(
            geodata_gpd, 
            geodata_gpd_original, 
            metadata,
            None,
            None
            )
                
    elif location_type == "destinations":
        
        geodata_gpd["j_update"] = 0
        geodata_gpd_original["j_update"] = 0

        geodata_object = SupplyLocations(
            geodata_gpd, 
            geodata_gpd_original, 
            metadata,
            None,
            None
            )

    return geodata_object
    
def create_interaction_matrix(
    customer_origins,
    supply_locations    
    ):

    if not isinstance(customer_origins, CustomerOrigins):
        raise ValueError ("Error while creating interaction matrix: customer_origins must be of class CustomerOrigins")
    if not isinstance(supply_locations, SupplyLocations):
        raise ValueError ("Error while creating interaction matrix: supply_locations must be of class SupplyLocations")

    customer_origins_metadata = customer_origins.get_metadata()
    if customer_origins_metadata["marketsize_col"] is None:
        raise ValueError("Error while creating interaction matrix: Market size column in customer origins not defined. Use CustomerOrigins.define_marketsize()")
    
    supply_locations_metadata = supply_locations.get_metadata()
    if supply_locations_metadata["attraction_col"][0] is None:
        raise ValueError("Error while creating interaction matrix: Attraction column in supply locations not defined. Use SupplyLocations.define_attraction()")

    customer_origins_unique_id = customer_origins_metadata["unique_id"]
    customer_origins_marketsize = customer_origins_metadata["marketsize_col"]

    customer_origins_geodata_gpd = pd.DataFrame(customer_origins.get_geodata_gpd())
    customer_origins_geodata_gpd_original = pd.DataFrame(customer_origins.get_geodata_gpd_original())
    
    customer_origins_geodata_gpd[customer_origins_unique_id] = customer_origins_geodata_gpd[customer_origins_unique_id].astype(str)
    customer_origins_geodata_gpd_original[customer_origins_unique_id] = customer_origins_geodata_gpd_original[customer_origins_unique_id].astype(str)

    customer_origins_data = pd.merge(
        customer_origins_geodata_gpd,
        customer_origins_geodata_gpd_original[[customer_origins_unique_id, customer_origins_marketsize]],
        left_on = customer_origins_unique_id,
        right_on = customer_origins_unique_id 
        )
    customer_origins_data = customer_origins_data.rename(columns = {
        customer_origins_unique_id: "i",
        customer_origins_marketsize: "C_i",
        "geometry": "i_coords"
        }
        )

    supply_locations_unique_id = supply_locations_metadata["unique_id"]
    supply_locations_attraction = supply_locations_metadata["attraction_col"][0]

    supply_locations_geodata_gpd = pd.DataFrame(supply_locations.get_geodata_gpd())
    supply_locations_geodata_gpd_original = pd.DataFrame(supply_locations.get_geodata_gpd_original())
    supply_locations_data = pd.merge(
        supply_locations_geodata_gpd,
        supply_locations_geodata_gpd_original[[supply_locations_unique_id, supply_locations_attraction]],
        left_on = supply_locations_unique_id,
        right_on = supply_locations_unique_id 
        )
    supply_locations_data = supply_locations_data.rename(columns = {
        supply_locations_unique_id: "j",
        supply_locations_attraction: "A_j",
        "geometry": "j_coords"
        }
        )

    interaction_matrix_df = customer_origins_data.merge(
        supply_locations_data, 
        how = "cross"
        )
    interaction_matrix_df["ij"] = interaction_matrix_df["i"].astype(str)+"_"+interaction_matrix_df["j"].astype(str)
    interaction_matrix_df["t_ij"] = None
    interaction_matrix_df["U_ij"] = None
    interaction_matrix_df["p_ij"] = None
    interaction_matrix_df["E_ij"] = None

    metadata = {}

    interaction_matrix = InteractionMatrix(
        interaction_matrix_df,
        customer_origins,
        supply_locations,
        metadata
        )
         
    return interaction_matrix

def load_interaction_matrix(
    data,
    customer_origins_col: str,
    supply_locations_col: str,
    attraction_col: list,
    transport_costs_col: str,
    flows_col: str = None,
    probabilities_col: str = None,
    market_size_col: str = None,
    customer_origins_coords_col = None,
    supply_locations_coords_col = None,
    data_type = "csv", 
    csv_sep = ";", 
    csv_decimal = ",", 
    csv_encoding="unicode_escape",
    xlsx_sheet: str = None,
    crs_input = "EPSG:4326",
    crs_output = "EPSG:4326",
    check_df_vars: bool = True
    ):    

    if isinstance(data, pd.DataFrame):
        interaction_matrix_df = data
    elif isinstance(data, str):
        if data_type not in ["csv", "xlsx"]:
            raise ValueError ("Error while loading interaction matrix: param 'data_type' must be 'csv' or 'xlsx'")
        if data_type == "csv":
            interaction_matrix_df = pd.read_csv(
                data, 
                sep = csv_sep, 
                decimal = csv_decimal, 
                encoding = csv_encoding
                )    
        elif data_type == "xlsx":
            if xlsx_sheet is not None:
                interaction_matrix_df = pd.read_excel(
                    data, 
                    sheet_name=xlsx_sheet
                    )
            else:
                interaction_matrix_df = pd.read_excel(data)
        else:
            raise TypeError("Error while loading interaction matrix: Unknown type of data")
    else:
        raise TypeError("Error while loading interaction matrix: param 'data' must be pandas.DataFrame or file (.csv, .xlsx)")
    
    if customer_origins_col not in interaction_matrix_df.columns:
        raise KeyError ("Error while loading interaction matrix: Column " + customer_origins_col + " not in data")
    if supply_locations_col not in interaction_matrix_df.columns:
        raise KeyError ("Error while loading interaction matrix: Column " + supply_locations_col + " not in data")
    
    cols_check = attraction_col + [transport_costs_col]
    if flows_col is not None:
        cols_check = cols_check + [flows_col]
    if probabilities_col is not None:
        cols_check = cols_check + [probabilities_col]
    if market_size_col is not None:
        cols_check = cols_check + [market_size_col]

    if check_df_vars:
        check_vars(
            interaction_matrix_df,
            cols = cols_check
            )

    if customer_origins_coords_col is not None:

        if isinstance(customer_origins_coords_col, str):

            if customer_origins_coords_col not in interaction_matrix_df.columns:
                raise KeyError ("Error while loading interaction matrix: Column " + customer_origins_coords_col + " not in data.")    
            
            customer_origins_geodata_tab = interaction_matrix_df[[customer_origins_col, customer_origins_coords_col]]
            customer_origins_geodata_tab = customer_origins_geodata_tab.drop_duplicates()
            customer_origins_geodata_tab["geometry"] = customer_origins_geodata_tab[customer_origins_coords_col].apply(lambda x: wkt.loads(x))
            customer_origins_geodata_gpd = gp.GeoDataFrame(
                customer_origins_geodata_tab, 
                geometry="geometry",
                crs = crs_input)
            customer_origins_geodata_gpd = customer_origins_geodata_gpd.drop(
                columns = customer_origins_coords_col
                )

        elif isinstance(customer_origins_coords_col, list):

            if len(customer_origins_coords_col) != 2:
                raise ValueError ("Error while loading interaction matrix: Column " + customer_origins_coords_col + " must be a geometry column OR TWO columns with X and Y")
            
            check_vars (
                df = interaction_matrix_df, 
                cols = customer_origins_coords_col
                )

            customer_origins_geodata_tab = interaction_matrix_df[[customer_origins_col, customer_origins_coords_col[0], customer_origins_coords_col[1]]]
            customer_origins_geodata_tab = customer_origins_geodata_tab.drop_duplicates()
            customer_origins_geodata_tab["geometry"] = customer_origins_geodata_tab.apply(lambda row: Point(row[customer_origins_coords_col[0]], row[customer_origins_coords_col[1]]), axis=1)
            customer_origins_geodata_gpd = gp.GeoDataFrame(customer_origins_geodata_tab, geometry="geometry")
                      
        customer_origins_geodata_gpd.set_crs(crs_output, inplace=True)

    else:

        customer_origins_geodata_gpd = interaction_matrix_df[customer_origins_col]
        customer_origins_geodata_gpd = customer_origins_geodata_gpd.drop_duplicates()

    if market_size_col is not None:
        customer_origins_cols = [customer_origins_col] + [market_size_col]
    else:
        customer_origins_cols = [customer_origins_col]
    customer_origins_geodata_original_tab = customer_origins_geodata_tab = interaction_matrix_df[customer_origins_cols]

    customer_origins_metadata = {
        "location_type": "origins",
        "unique_id": customer_origins_col,
        "attraction_col": [None],
        "marketsize_col": market_size_col,
        "weighting": {
            0: {
                "name": None,
                "func": None, 
                "param": None
                }
            },
        "crs_input": crs_input,
        "crs_output": crs_output,
        "no_points": len(customer_origins_geodata_gpd)
        }

    customer_origins = CustomerOrigins(
        geodata_gpd = customer_origins_geodata_gpd,
        geodata_gpd_original = customer_origins_geodata_original_tab,
        metadata = customer_origins_metadata,
        isochrones_gdf = None,
        buffers_gdf = None
        )

    if supply_locations_coords_col is not None:

        if isinstance(supply_locations_coords_col, str):

            if supply_locations_coords_col not in interaction_matrix_df.columns:
                raise KeyError ("Error while loading interaction matrix: Column " + supply_locations_coords_col + " not in data.")    
            
            supply_locations_geodata_tab = interaction_matrix_df[[supply_locations_col, supply_locations_coords_col]]
            supply_locations_geodata_tab = supply_locations_geodata_tab.drop_duplicates()
            supply_locations_geodata_tab["geometry"] = supply_locations_geodata_tab[supply_locations_coords_col].apply(lambda x: wkt.loads(x))
            supply_locations_geodata_gpd = gp.GeoDataFrame(
                supply_locations_geodata_tab, 
                geometry="geometry",
                crs = crs_input)
            supply_locations_geodata_gpd = supply_locations_geodata_gpd.drop(
                columns = supply_locations_coords_col
                )

        if isinstance(supply_locations_coords_col, list):

            if len(supply_locations_coords_col) != 2:
                raise ValueError ("Error while loading interaction matrix: Column " + supply_locations_coords_col + " must be a geometry column OR TWO columns with X and Y")
            
            check_vars (
                df = interaction_matrix_df, 
                cols = supply_locations_coords_col
                )

            supply_locations_geodata_tab = interaction_matrix_df[[supply_locations_col, supply_locations_coords_col[0], supply_locations_coords_col[1]]]
            supply_locations_geodata_tab = supply_locations_geodata_tab.drop_duplicates()
            supply_locations_geodata_tab["geometry"] = supply_locations_geodata_tab.apply(lambda row: Point(row[supply_locations_coords_col[0]], row[supply_locations_coords_col[1]]), axis=1)
            supply_locations_geodata_gpd = gp.GeoDataFrame(supply_locations_geodata_tab, geometry="geometry")
                      
        supply_locations_geodata_gpd.set_crs(crs_output, inplace=True)

    else:

        supply_locations_geodata_gpd = interaction_matrix_df[supply_locations_col]
        supply_locations_geodata_gpd = supply_locations_geodata_gpd.drop_duplicates()

    supply_locations_cols = [supply_locations_col] + attraction_col
    supply_locations_geodata_original_tab = supply_locations_geodata_tab = interaction_matrix_df[supply_locations_cols]

    supply_locations_metadata = {
        "location_type": "destinations",
        "unique_id": supply_locations_col,
        "attraction_col": attraction_col,
        "marketsize_col": None,
        "weighting": {
            0: {
                "name": None,
                "func": None, 
                "param": None
                }
            },
        "crs_input": crs_input,
        "crs_output": crs_output,
        "no_points": len(supply_locations_geodata_gpd)
        }

    supply_locations = SupplyLocations(
        geodata_gpd = supply_locations_geodata_gpd,
        geodata_gpd_original = supply_locations_geodata_original_tab,
        metadata = supply_locations_metadata,
        isochrones_gdf = None,
        buffers_gdf = None
        )
    
    interaction_matrix_df = interaction_matrix_df.rename(
        columns = {
            customer_origins_col: "i",
            supply_locations_col: "j",
            attraction_col[0]: "A_j",
            transport_costs_col: "t_ij"
        }
        )

    if flows_col is not None:
        interaction_matrix_df = interaction_matrix_df.rename(
            columns = {
                flows_col: "E_ij"
            }
            )

    if probabilities_col is not None:
        interaction_matrix_df = interaction_matrix_df.rename(
            columns = {
                probabilities_col: "p_ij"
            }
            )

    if market_size_col is not None:
        interaction_matrix_df = interaction_matrix_df.rename(
            columns = {
                market_size_col: "C_i"
            }
            )
    
    metadata = {
        "fit": {
            "function": None,
            "fit_by": None
        }
    }

    interaction_matrix = InteractionMatrix(
        interaction_matrix_df=interaction_matrix_df,
        customer_origins=customer_origins,
        supply_locations=supply_locations,
        metadata=metadata
        )
    
    return interaction_matrix

def load_marketareas(
    data,
    supply_locations_col: str,
    total_col: str,  
    data_type = "csv", 
    csv_sep = ";", 
    csv_decimal = ",", 
    csv_encoding="unicode_escape",
    xlsx_sheet: str = None,
    check_df_vars: bool = True
    ):    

    if isinstance(data, pd.DataFrame):
        market_areas_df = data
    elif isinstance(data, str):
        if data_type not in ["csv", "xlsx"]:
            raise ValueError ("Error while loading market areas: data_type must be 'csv' or 'xlsx'")
        if data_type == "csv":
            market_areas_df = pd.read_csv(
                data, 
                sep = csv_sep, 
                decimal = csv_decimal, 
                encoding = csv_encoding
                )    
        elif data_type == "xlsx":            
            if xlsx_sheet is not None:
                market_areas_df = pd.read_excel(
                    data, 
                    sheet_name=xlsx_sheet
                    )
            else:
                market_areas_df = pd.read_excel(data)
        else:
            raise TypeError("Error while loading market areas: Unknown type of data")
    else:
        raise TypeError("Error while loading market areas: data must be pandas.DataFrame or file (.csv, .xlsx)")
    
    if supply_locations_col not in market_areas_df.columns:
        raise KeyError ("Error while loading market areas: Column " + supply_locations_col + " not in data")
    if total_col not in market_areas_df.columns:
        raise KeyError ("Error while loading market areas: Column " + supply_locations_col + " not in data")
    
    if check_df_vars:
        check_vars(
            market_areas_df,
            cols = [total_col]
            )
    
    market_areas_df = market_areas_df.rename(
        columns = {
            supply_locations_col: "j",
            total_col: "T_j"
        }
        )
    
    metadata = {
        "unique_id": supply_locations_col,
        "total_col": total_col,
        "no_points": len(market_areas_df)
        }
    
    market_areas = MarketAreas(
        market_areas_df,
        metadata
        )
    
    return market_areas  

def market_shares(
    df: pd.DataFrame,
    turnover_col: str,
    ref_col: str = None,
    marketshares_col: str = "p_ij"
    ):

    check_vars(
        df = df,
        cols = [turnover_col]
        )
    
    if ref_col is not None:

        if ref_col not in df.columns:
            raise KeyError(f"Error while calculating market shares: Column '{ref_col}' not in dataframe.")
        
        ms_refcol = pd.DataFrame(df.groupby(ref_col)[turnover_col].sum())
        ms_refcol = ms_refcol.rename(columns = {turnover_col: "total"})
        ms_refcol = ms_refcol.reset_index()

        df = df.merge(
            ms_refcol,
            how = "left",
            left_on = ref_col,
            right_on= ref_col 
        )

    else:

        ms_norefcol = pd.DataFrame([df[turnover_col].sum()], columns=["total"])
        ms_norefcol = ms_norefcol.reset_index()

        df["key_temp"] = 1
        ms_norefcol["key_temp"] = 1
        df = pd.merge(
            df, 
            ms_norefcol, 
            on="key_temp"
            ).drop(
                "key_temp", 
                axis=1
                )

    df[marketshares_col] = df[turnover_col]/df["total"]
    
    df = df.drop(columns="total")

    return df

def log_centering_transformation(
    df: pd.DataFrame,
    ref_col: str,
    cols: list,
    suffix: str = "__LCT"
    ):
   
    check_vars(
        df = df,
        cols = cols
        )
    
    if ref_col not in df.columns:
        raise KeyError(f"Error in log-centering transformation: Column '{ref_col}' not in dataframe.")

    def lct (x):

        x_geom = np.exp(np.log(x).mean())
        x_lct = np.log(x/x_geom)

        return x_lct
    
    for var in cols:
        
        unique_values = df[var].unique()
        if set(unique_values).issubset({0, 1}):
            df[var+suffix] = df[var]
            print ("Column " + str(var) + " is a dummy variable and requires/allows no log-centering transformation")
            continue

        if (df[var] <= 0).any():
            df[var+suffix] = float("nan")
            print ("Column " + str(var) + " contains values <= 0. No log-centering transformation possible.")
            continue

        var_t = df.groupby(ref_col)[var].apply(lct)
        var_t = var_t.reset_index()
        df[var+suffix] = var_t[var]

    return df


def get_isochrones(
    geodata_gpd: gp.GeoDataFrame,
    unique_id_col: str,
    segments: list = [5, 10, 15],
    range_type: str = "time",
    intersections: str = "true",
    profile: str = "driving-car",
    donut: bool = True,
    ors_server: str = "https://api.openrouteservice.org/v2/",
    ors_auth: str = None,    
    timeout = 10,
    delay = 1,
    save_output: bool = True,
    output_filepath: str = "isochrones.shp",
    output_crs: str = "EPSG:4326"
    ):

    coords = [(point.x, point.y) for point in geodata_gpd.geometry]
    
    unique_id_values = geodata_gpd[unique_id_col].values

    ors_client = Client(
        server = ors_server,
        auth = ors_auth
        )
    
    isochrones_gdf = gp.GeoDataFrame(columns=[unique_id_col, "geometry"])
    
    if range_type == "time":
        segments = [segment*60 for segment in segments]
    if range_type == "distance":
        segments = [segment*1000 for segment in segments]

    i = 0

    for x, y in coords:
        
        isochrone_output = ors_client.isochrone(
            locations = [[x, y]],
            segments = segments,
            range_type = range_type,
            intersections = intersections,
            profile = profile,
            timeout = timeout,
            save_output = False,
            output_crs = output_crs
            )
        
        if isochrone_output.status_code != 200:
            continue        
        
        isochrone_gdf = isochrone_output.get_isochrones_gdf()
        
        if donut:
            isochrone_gdf = overlay_difference(
                polygon_gdf = isochrone_gdf, 
                sort_col = "segment"
                )
            
        time.sleep(delay)

        isochrone_gdf[unique_id_col] = unique_id_values[i]
        
        if range_type == "time":
            isochrone_gdf["segm_min"] = isochrone_gdf["segment"]/60
        if range_type == "distance":
            isochrone_gdf["segm_km"] = isochrone_gdf["segment"]/1000        

        isochrones_gdf = pd.concat(
            [
                isochrones_gdf, 
                isochrone_gdf
                ], 
            ignore_index=True
            )
        
        i = i+1

    isochrones_gdf["segment"] = isochrones_gdf["segment"].astype(int)
    
    if range_type == "time":
        isochrones_gdf["segm_min"] = isochrones_gdf["segm_min"].astype(int)
    if range_type == "distance":
        isochrones_gdf["segm_km"] = isochrones_gdf["segm_km"].astype(int)
    
    isochrones_gdf.set_crs(
        output_crs, 
        allow_override=True, 
        inplace=True
        )
        
    if save_output:

        isochrones_gdf.to_file(filename = output_filepath)

    return isochrones_gdf


def modelfit(
    observed, 
    expected,
    remove_nan: bool = True,
    verbose: bool = False
    ):

    observed_no = len(observed)
    expected_no = len(expected)

    if not observed_no == expected_no:
        raise ValueError("Error while calculating fit metrics: Observed and expected differ in length")
    
    if not isinstance(observed, np.number): 
        if not is_numeric_dtype(observed):
            raise ValueError("Error while calculating fit metrics: Observed column is not numeric")
    if not isinstance(expected, np.number):
        if not is_numeric_dtype(expected):
            raise ValueError("Error while calculating fit metrics: Expected column is not numeric")
    
    if remove_nan:
        
        observed = observed.reset_index(drop=True)
        expected = expected.reset_index(drop=True)

        obs_exp = pd.DataFrame(
            {
                "observed": observed, 
                "expected": expected
                }
            )
        
        obs_exp_clean = obs_exp.dropna(subset=["observed", "expected"])

        if len(obs_exp_clean) < len(observed) or len(obs_exp_clean) < len(expected):
            if verbose:
                print("NOTE: Vectors 'observed' and/or 'expected' contain zeros which are dropped.")
        
        observed = obs_exp_clean["observed"].to_numpy()
        expected = obs_exp_clean["expected"].to_numpy()
    
    else:
        
        if np.isnan(observed).any():
            raise ValueError("Error while calculating fit metrics: Vector with observed data contains NaN and 'remove_nan' is False")
        if np.isnan(expected).any():
            raise ValueError("Error while calculating fit metrics: Vector with expected data contains NaN and 'remove_nan' is False")
    
    residuals = np.array(observed)-np.array(expected)
    residuals_sq = residuals**2
    residuals_abs = abs(residuals)
 
    if any(observed == 0):
        if verbose:
            print ("Vector 'observed' contains values equal to zero. No APE/MAPE calculated.")
        APE = np.full_like(observed, np.nan)
        MAPE = None
    else:
        APE = abs(observed-expected)/observed*100
        MAPE = float(np.mean(APE))
        
    sAPE = abs(observed-expected)/((abs(observed)+abs(expected))/2)*100
    
    data_residuals = pd.DataFrame({
        "observed": observed,
        "expected": expected,
        "residuals": residuals,
        "residuals_sq": residuals_sq,
        "residuals_abs": residuals_abs,
        "APE": APE,
        "sAPE": sAPE
        })

    SQR = float(np.sum(residuals_sq))
    SAR = float(np.sum(residuals_abs))    
    observed_mean = float(np.sum(observed)/observed_no)
    SQT = float(np.sum((observed-observed_mean)**2))
    Rsq = float(1-(SQR/SQT))
    MSE = float(SQR/observed_no)
    RMSE = float(sqrt(MSE))
    MAE = float(SAR/observed_no)
    LL = np.sum(np.log(residuals_sq))
    
    sMAPE = float(np.mean(sAPE))

    resid_below5 = float(len(data_residuals[data_residuals["APE"] < 5])/expected_no*100)
    resid_below10 = float(len(data_residuals[data_residuals["APE"] < 10])/expected_no*100)
    resid_below15 = float(len(data_residuals[data_residuals["APE"] < 15])/expected_no*100)
    resid_below20 = float(len(data_residuals[data_residuals["APE"] < 20])/expected_no*100)
    resid_below25 = float(len(data_residuals[data_residuals["APE"] < 25])/expected_no*100)
    resid_below30 = float(len(data_residuals[data_residuals["APE"] < 30])/expected_no*100)
    resid_below35 = float(len(data_residuals[data_residuals["APE"] < 35])/expected_no*100)
    resid_below40 = float(len(data_residuals[data_residuals["APE"] < 40])/expected_no*100)
    resid_below45 = float(len(data_residuals[data_residuals["APE"] < 45])/expected_no*100)
    resid_below50 = float(len(data_residuals[data_residuals["APE"] < 50])/expected_no*100)

    data_lossfunctions = {
        "SQR": SQR,
        "SAR": SAR,
        "SQT": SQT,
        "Rsq": Rsq,
        "MSE": MSE,
        "RMSE": RMSE,
        "MAE": MAE,
        "MAPE": MAPE,
        "sMAPE": sMAPE,
        "LL": -LL,
        "APE": {
            "resid_below5": resid_below5,
            "resid_below10": resid_below10,
            "resid_below15": resid_below15,
            "resid_below20": resid_below20,
            "resid_below25": resid_below25,
            "resid_below30": resid_below30,
            "resid_below35": resid_below35,
            "resid_below40": resid_below40,
            "resid_below45": resid_below45,
            "resid_below50": resid_below50,
        }   
    }    
    
    modelfit_results = [
        data_residuals,
        data_lossfunctions
    ]

    return modelfit_results

def check_vars(
    df: pd.DataFrame,
    cols: list,
    check_numeric: bool = True,
    check_zero: bool = True
    ):

    for col in cols:
        if col not in df.columns:
            raise KeyError(f"Column '{col}' not in dataframe.")
    
    if check_numeric:
        for col in cols:
            if not pd.api.types.is_numeric_dtype(df[col]):
                raise ValueError(f"Column '{col}' is not numeric. All stated columns must be numeric.")
    
    if check_zero:
        for col in cols:
            if (df[col] <= 0).any():
                raise ValueError(f"Column '{col}' includes values <= 0. All values must be numeric and positive.")