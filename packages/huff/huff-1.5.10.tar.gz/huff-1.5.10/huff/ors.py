#-----------------------------------------------------------------------
# Name:        ors (huff package)
# Purpose:     OpenRouteService client
# Author:      Thomas Wieland 
#              ORCID: 0000-0001-5168-9846
#              mail: geowieland@googlemail.com              
# Version:     1.4.2
# Last update: 2025-08-13 18:47
# Copyright (c) 2025 Thomas Wieland
#-----------------------------------------------------------------------


import pandas as pd
import requests
import geopandas as gp
from shapely.geometry import Point, MultiPoint, shape, Polygon
from shapely.ops import unary_union


class Isochrone:

    def __init__(
        self, 
        isochrones_gdf, 
        metadata,
        status_code,
        save_config
        ):

        self.isochrones_gdf = isochrones_gdf
        self.metadata = metadata
        self.status_code = status_code
        self.save_config = save_config

    def get_isochrones_gdf(self):

        isochrones_gdf = self.isochrones_gdf
        return isochrones_gdf

    def summary(self):

        metadata = self.metadata
        status_code = self.status_code

        if metadata is not None:
            range_str = [str(range) for range in metadata["query"]["range"]]
            profile = metadata["query"]["profile"]
            range_type = metadata["query"]["range_type"]
            no_locations = len(metadata["query"]["locations"])

            print("Locations    " + str(no_locations))
            print("Segments     " + ", ".join(range_str))
            print("Range type   " + range_type)
            print("Profile      " + profile)
            
        else:
            print("No isochrones were built.")
        
        print("Status code  " + str(status_code))

class TimeDistanceMatrix:

    def __init__(
        self, 
        matrix_df, 
        metadata,
        status_code,
        save_config
        ):

        self.matrix_df = matrix_df
        self.metadata = metadata
        self.status_code = status_code
        self.save_config = save_config

    def get_matrix(self):

        return self.matrix_df
    
    def get_metadata(self):

        return self.metadata
    
    def get_config(self):

        return self.save_config
    
    def summary(self):

        metadata = self.metadata
        status_code = self.status_code

        config = self.save_config

        if metadata is not None:

            profile = metadata["query"]["profile"]
            no_locations = len(metadata["query"]["locations"])
            range_type = config["range_type"]

            print("Locations    " + str(no_locations))
            print("Range type   " + range_type)
            print("Profile      " + profile)
        else:
            print("No time/distance matrix was built.")
        print("Status code  " + str(status_code))

class Client:

    def __init__(
        self,
        server = "https://api.openrouteservice.org/v2/",
        auth: str = None
        ):
        
        self.server = server
        self.auth = auth
            
    def isochrone(
        self,
        locations: list,
        segments: list = [900, 600, 300],
        range_type: str = "time",
        intersections: str = "true",
        profile: str = "driving-car",
        timeout = 10,
        save_output: bool = True,
        output_filepath: str = "isochrones.shp",
        output_crs: str = "EPSG:4326"
        ):

        if len(segments) > 10:
            raise ValueError ("ORS client does not allow >10 intervals in an Isochrones query. See https://openrouteservice.org/restrictions/.")
        
        if len(locations) > 5:
            raise ValueError ("ORS client does not allow >5 locations in an Isochrones query. See https://openrouteservice.org/restrictions/.")
    
        ors_url = self.server + "isochrones/" + profile
        auth = self.auth

        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8",
            "Authorization": auth
        }

        body = {
            "locations": locations,
            "range": segments,
            "intersections": intersections,
            "range_type": range_type
        }

        print("body:") # TODO ?? RAUS
        print(body) # TODO ?? RAUS
        
        save_config = {
            "range_type": range_type,
            "save_output": save_output,
            "output_filepath" : output_filepath,
            "output_crs": output_crs
            }

        try:

            response = requests.post(
                ors_url, 
                headers=headers, 
                json=body,
                timeout=timeout
                )
            
        except Exception as e:

            print ("Error while accessing ORS server: ", str(e))
            
            status_code = 99999
            isochrones_gdf = None 
            metadata = None

            isochrone_output = Isochrone(
                isochrones_gdf, 
                metadata,
                status_code,
                save_config
                )
            
            return isochrone_output

        status_code = response.status_code

        if status_code == 200:

            print ("Accessing ORS server successful")

            response_json = response.json()
            
            metadata = response_json["metadata"]
            
            features = response_json["features"]
            geometries = [shape(feature["geometry"]) for feature in features]

            isochrones_gdf = gp.GeoDataFrame(
                features, 
                geometry=geometries, 
                crs="EPSG:4326"
                )

            isochrones_gdf["segment"] = 0
            isochrones_gdf_properties_dict = dict(isochrones_gdf["properties"])
            
            for i in range(len(isochrones_gdf_properties_dict)):
                isochrones_gdf.iloc[i,3] = isochrones_gdf_properties_dict[i]["value"]

            isochrones_gdf = isochrones_gdf.drop(columns=["properties"])
            isochrones_gdf = isochrones_gdf.to_crs(output_crs)

            if save_output:
                isochrones_gdf.to_file(output_filepath)
                print ("Saved as", output_filepath)

        else:
            
            print(f"Error while accessing ORS server. Status code: {status_code} - {response.reason}")
            
            isochrones_gdf = None
            metadata = None
        
        isochrone_output = Isochrone(
            isochrones_gdf, 
            metadata,
            status_code,
            save_config
            )
        
        return isochrone_output

    def matrix(
        self,
        locations: list,
        sources: list = [],
        destinations: list = [],
        id: str = None,
        range_type: str = "time",
        profile: str = "driving-car",
        metrics: list = [],
        resolve_locations: bool = False,    
        units: str = "mi",
        timeout: int = 10,
        save_output: bool = False,
        output_filepath: str = "matrix.csv",
        csv_sep = ";",
        csv_decimal = ",",
        csv_encoding = None
        ):

        ors_url = self.server + "matrix/" + profile
        auth = self.auth

        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8",
            "Authorization": auth
        }

        body = {
            "locations": locations,
            "resolve_locations": resolve_locations
        }
        if id is not None:
            body["id"] = id
        if metrics != []:
            body["metrics"] = metrics
        if sources != []:
            body["sources"] = sources
        if destinations != []:
            body["destinations"] = destinations
        if units is not None:
            body["units"] = units

        save_config = {
            "range_type": range_type,
            "save_output": save_output,
            "output_filepath": output_filepath
        }

        try:

            response = requests.post(
                ors_url, 
                headers=headers, 
                json=body,
                timeout=timeout
                )
            
        except Exception as e:

            print ("Error while accessing ORS server: ", str(e))
            
            status_code = 99999
            matrix_df = None
            metadata = None

            matrix_output = TimeDistanceMatrix(
                matrix_df, 
                metadata,
                status_code,
                save_config
                )

            return matrix_output

        status_code = response.status_code

        if status_code == 200:

            print ("Accessing ORS server successful")

            response_json = response.json()

            metadata = response_json["metadata"]

            matrix_df = pd.DataFrame(
                columns=[
                    "source",
                    "source_lat",
                    "source_lon",
                    "source_snapped_distance",
                    "destination",
                    "destination_lat",
                    "destination_lon", 
                    "destination_snapped_distance",
                    "source_destination", 
                    range_type
                    ])

            for i, value in enumerate(response_json["durations"]):

                source_lat = response_json["sources"][i]["location"][1]
                source_lon = response_json["sources"][i]["location"][0]
                source_snapped_distance = response_json["sources"][i]["snapped_distance"]
                
                for j, entry in enumerate(value):

                    destination_lat = response_json["destinations"][j]["location"][1]
                    destination_lon = response_json["destinations"][j]["location"][0]
                    destination_snapped_distance = response_json["destinations"][j]["snapped_distance"]

                    matrix_row = pd.Series(
                        {
                            "source": str(i),
                            "source_lat": source_lat,
                            "source_lon": source_lon,
                            "source_snapped_distance": source_snapped_distance,
                            "destination": str(j),
                            "destination_lat": destination_lat,
                            "destination_lon": destination_lon,
                            "destination_snapped_distance": destination_snapped_distance,
                            "source_destination": str(i)+"_"+str(j), 
                            range_type: entry
                            }
                            )

                    matrix_df = pd.concat([
                        matrix_df, 
                        pd.DataFrame([matrix_row])])

            if save_output:
                matrix_df.to_csv(
                    output_filepath, 
                    decimal = csv_decimal, 
                    sep = csv_sep, 
                    encoding = csv_encoding
                    )
                print ("Saved as", output_filepath)

        else:

            print(f"Error while accessing ORS server. Status code: {status_code} - {response.reason}")

            matrix_df = None
            metadata = None

        matrix_output = TimeDistanceMatrix(
            matrix_df, 
            metadata,
            status_code,
            save_config
            )
        
        return matrix_output