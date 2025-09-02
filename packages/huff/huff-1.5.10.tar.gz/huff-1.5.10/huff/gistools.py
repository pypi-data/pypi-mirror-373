#-----------------------------------------------------------------------
# Name:        gistools (huff package)
# Purpose:     GIS tools
# Author:      Thomas Wieland 
#              ORCID: 0000-0001-5168-9846
#              mail: geowieland@googlemail.com              
# Version:     1.4.3
# Last update: 2025-08-07 17:20
# Copyright (c) 2025 Thomas Wieland
#-----------------------------------------------------------------------


import os
import geopandas as gp
import pandas as pd
from pandas.api.types import is_numeric_dtype
from math import pi, sin, cos, acos
from matplotlib.patches import Patch
import matplotlib.pyplot as plt
from shapely.geometry import LineString, box
import contextily as cx
from PIL import Image
from huff.osm import get_basemap


def distance_matrix(
    sources: list,
    destinations: list,
    unit: str = "m",
    lines_gdf: bool = False
    ):

    def euclidean_distance (
        source: list,
        destination: list,
        unit: str = "m"
        ):

        lon1 = source[0]
        lat1 = source[1]
        lon2 = destination[0]
        lat2 = destination[1]

        lat1_r = lat1*pi/180
        lon1_r = lon1*pi/180
        lat2_r = lat2*pi/180
        lon2_r = lon2*pi/180

        distance = 6378 * (acos(sin(lat1_r) * sin(lat2_r) + cos(lat1_r) * cos(lat2_r) * cos(lon2_r - lon1_r)))
        if unit == "m": 
            distance = distance*1000
        if unit == "mile": 
            distance = distance/1.60934

        return distance

    matrix = []

    if lines_gdf:
        line_data = []
        
    for source in sources:
        
        row = []
        for destination in destinations:
            
            dist = euclidean_distance(
                source, 
                destination, 
                unit
                )
            row.append(dist)
            
            if lines_gdf:
                line = LineString([source, destination])
                line_data.append({
                    "source": source,
                    "destination": destination,
                    "distance": dist,
                    "geometry": line
                })
        
        matrix.append(row)

    if lines_gdf:
        return gp.GeoDataFrame(line_data)
    else:
        return matrix


def buffers(
    point_gdf: gp.GeoDataFrame,
    unique_id_col: str,
    distances: list,
    donut: bool = True,
    save_output: bool = True,
    output_filepath: str = "buffers.shp",
    output_crs: str = "EPSG:4326"    
    ):    
    
    if point_gdf.crs.is_geographic:
        print(f"WARNING: Point GeoDataFrame has geographic coordinate system {point_gdf.crs}. Results may be invalid.")
  
    if unique_id_col not in point_gdf.columns:
        raise KeyError(f"No column {unique_id_col} in input GeoDataFrame")
        
    all_buffers_gdf = gp.GeoDataFrame(
        columns=[
            unique_id_col, 
            "segment", 
            "geometry"
            ]
        )

    for idx, row in point_gdf.iterrows():

        point_buffers = []

        for distance in distances:

            point = row["geometry"] 
            point_buffer = point.buffer(distance)

            point_buffer_gdf = gp.GeoDataFrame(
            {
                unique_id_col: row[unique_id_col],
                "geometry": [point_buffer], 
                "segment": [distance]
                },
                crs=point_gdf.crs
            )
        
            point_buffers.append(point_buffer_gdf)

        point_buffers_gdf = pd.concat(
            point_buffers, 
            ignore_index = True
            )

        if donut:
            point_buffers_gdf = overlay_difference(
                polygon_gdf = point_buffers_gdf, 
                sort_col = "segment"
                )
 
        all_buffers_gdf = pd.concat(
            [
                all_buffers_gdf,
                point_buffers_gdf
                ], 
            ignore_index = True)

    all_buffers_gdf = all_buffers_gdf.to_crs(output_crs)

    if save_output:        
        all_buffers_gdf.to_file(output_filepath)        
        print ("Saved as", output_filepath)

    return all_buffers_gdf 


def polygon_select(
    gdf: gp.GeoDataFrame,
    gdf_unique_id_col: str,
    gdf_polygon_select: gp.GeoDataFrame,
    gdf_polygon_select_unique_id_col: str,
    distance: int,
    within: bool = False,
    save_output: bool = True,
    output_filepath: str = "polygon_select.shp",
    output_crs: str = "EPSG:4326"
    ):
    
    if gdf.crs != gdf_polygon_select.crs:
        raise ValueError(f"Coordinate reference systems of inputs do not match. Polygons: {str(gdf.crs)}, points: {str(gdf_polygon_select.crs)}")
        
    if gdf_unique_id_col not in gdf.columns:
        raise KeyError(f"No column {gdf_unique_id_col} in input GeoDataFrame")
    
    if gdf_polygon_select_unique_id_col not in gdf_polygon_select.columns:        
        raise KeyError(f"No column {gdf_polygon_select_unique_id_col} in input GeoDataFrame for selection")
    
    if gdf.crs.is_geographic:
        print(f"WARNING: Input GeoDataFrames have geographic coordinate system {gdf.crs}. Results may be invalid.")
    
    if len(gdf) > 1:
        print(f"WARNING: Input GeoDataFrame 'gdf' includes > 1 objects. Using the first only.")
        gdf = gdf[0]
    
    gdf_buffer = buffers(
        point_gdf = gdf,
        unique_id_col = gdf_unique_id_col,
        distances = [distance],        
        save_output = True,
        output_filepath = "gdf_buffer.shp",
        output_crs = output_crs
        )
    
    gdf_buffer = gdf_buffer.geometry.union_all()
    
    gdf_polygon_select = gdf_polygon_select.to_crs(output_crs)
    
    gdf_select_intersects = gdf_polygon_select[
        gdf_polygon_select.geometry.intersects(gdf_buffer)
        ]
    
    if within:
        gdf_select_intersects = gdf_select_intersects[gdf_select_intersects.geometry.within(gdf_buffer)]
               
    gdf_select_intersects_unique_ids = gdf_select_intersects[gdf_polygon_select_unique_id_col].unique()
    
    gdf_polygon_select_selection = gdf_polygon_select[gdf_polygon_select[gdf_polygon_select_unique_id_col].isin(gdf_select_intersects_unique_ids)]
    
    if save_output:        
        gdf_polygon_select_selection.to_file(output_filepath)        
        print ("Saved as", output_filepath)
        
    return gdf_polygon_select_selection
        

def overlay_difference(
    polygon_gdf: gp.GeoDataFrame, 
    sort_col: str = None,
    ):

    if sort_col is not None:
        polygon_gdf = polygon_gdf.sort_values(by=sort_col).reset_index(drop=True)
    else:
        polygon_gdf = polygon_gdf.reset_index(drop=True)

    new_geometries = []
    new_data = []

    for i in range(len(polygon_gdf) - 1, 0, -1):
        
        current_polygon = polygon_gdf.iloc[i].geometry
        previous_polygon = polygon_gdf.iloc[i - 1].geometry
        difference_polygon = current_polygon.difference(previous_polygon)

        if difference_polygon.is_empty or not difference_polygon.is_valid:
            continue

        new_geometries.append(difference_polygon)
        new_data.append(polygon_gdf.iloc[i].drop("geometry"))

    inner_most_polygon = polygon_gdf.iloc[0].geometry

    if inner_most_polygon.is_valid:

        new_geometries.append(inner_most_polygon)
        new_data.append(polygon_gdf.iloc[0].drop("geometry"))

    polygon_gdf_difference = gp.GeoDataFrame(
        new_data, geometry=new_geometries, crs=polygon_gdf.crs
    )

    return polygon_gdf_difference


def point_spatial_join(
    polygon_gdf: gp.GeoDataFrame,
    point_gdf: gp.GeoDataFrame,
    join_type: str = "inner",
    polygon_ref_cols: list = [],
    point_stat_col: str = None
    ):
    
    if polygon_gdf is None:
        raise ValueError("Parameter 'polygon_gdf' is None")
    if point_gdf is None:
        raise ValueError("Parameter 'point_gdf' is None")
    
    if polygon_gdf.crs != point_gdf.crs:
        raise ValueError(f"Coordinate reference systems of polygon and point data do not match. Polygons: {str(polygon_gdf.crs)}, points: {str(point_gdf.crs)}")
    
    if polygon_ref_cols != []:
        for polygon_ref_col in polygon_ref_cols:
            if polygon_ref_col not in polygon_gdf.columns:
                raise KeyError (f"Column {polygon_ref_col} not in polygon data")
        
    if point_stat_col is not None:
        if point_stat_col not in point_gdf.columns:
            raise KeyError (f"Column {point_stat_col} not in point data")
        if not is_numeric_dtype(point_gdf[point_stat_col]):
            raise TypeError (f"Column {point_stat_col} is not numeric")
               
    shp_points_gdf_join = point_gdf.sjoin(
        polygon_gdf, 
        how=join_type
        )

    spatial_join_stat = None

    if polygon_ref_cols != [] and point_stat_col is not None:
        shp_points_gdf_join_count = shp_points_gdf_join.groupby(polygon_ref_cols)[point_stat_col].count()
        shp_points_gdf_join_sum = shp_points_gdf_join.groupby(polygon_ref_cols)[point_stat_col].sum()
        shp_points_gdf_join_min = shp_points_gdf_join.groupby(polygon_ref_cols)[point_stat_col].min()
        shp_points_gdf_join_max = shp_points_gdf_join.groupby(polygon_ref_cols)[point_stat_col].max()
        shp_points_gdf_join_mean = shp_points_gdf_join.groupby(polygon_ref_cols)[point_stat_col].mean()
        
        shp_points_gdf_join_count = shp_points_gdf_join_count.rename("count").to_frame()
        shp_points_gdf_join_sum = shp_points_gdf_join_sum.rename("sum").to_frame()
        shp_points_gdf_join_min = shp_points_gdf_join_min.rename("min").to_frame()
        shp_points_gdf_join_max = shp_points_gdf_join_max.rename("max").to_frame()
        shp_points_gdf_join_mean = shp_points_gdf_join_mean.rename("mean").to_frame()
        spatial_join_stat = shp_points_gdf_join_count.join(
            [
                shp_points_gdf_join_sum, 
                shp_points_gdf_join_min, 
                shp_points_gdf_join_max,
                shp_points_gdf_join_mean
                ]
            )

    return [
        shp_points_gdf_join,
        spatial_join_stat
        ]
    
      
def map_with_basemap(
    layers: list,
    osm_basemap: bool = True,
    zoom: int = 15,
    figsize=(10, 10),
    bounds_factor = [0.9999, 0.9999, 1.0001, 1.0001],
    styles: dict = {},
    save_output: bool = True,
    output_filepath: str = "osm_map_with_basemap.png",
    output_dpi=300,
    legend: bool = True,
    show_plot: bool = True,
    verbose: bool = False
    ):
    
    if not isinstance(layers, list):
        raise ValueError("Param 'layers' must be a list")
    
    if not layers:
        raise ValueError("List layers is empty")

    if verbose:
        print("Combining layers ...", end = " ")

    layers_combined = gp.GeoDataFrame(
        pd.concat(
            layers, 
            ignore_index=True
            ),
        crs=layers[0].crs
    )

    layers_combined_wgs84 = layers_combined.to_crs(epsg=4326)
    
    if verbose:
        print("OK")        
        print("Retrieving total bounds ...", end = " ")
        
    bounds = layers_combined_wgs84.total_bounds

    sw_lon, sw_lat, ne_lon, ne_lat = bounds[0]*bounds_factor[0], bounds[1]*bounds_factor[1], bounds[2]*bounds_factor[2], bounds[3]*bounds_factor[3]

    if verbose:
        print("OK")        
    
    if osm_basemap:
        
        if verbose:
            print("Retrieving OSM basemap ...", end = " ")
            
        get_basemap(sw_lat, sw_lon, ne_lat, ne_lon, zoom=zoom)       

    fig, ax = plt.subplots(figsize=figsize)

    if osm_basemap:
        
        img = Image.open("osm_map.png")
        extent_img = [sw_lon, ne_lon, sw_lat, ne_lat]
        ax.imshow(img, extent=extent_img, origin="upper")
        
        if verbose:
            print("OK")

    if verbose:
        print("Inserting layers and plotting map ...", end = " ")
            
    i = 0
    legend_handles = []

    for layer in layers:
        
        layer_3857 = layer.to_crs(epsg=3857)

        if styles != {}:
            
            layer_style = styles[i]
            layer_color = layer_style["color"]
            layer_alpha = layer_style["alpha"]
            layer_name = layer_style["name"]           

            if isinstance(layer_color, str):
                layer_3857.plot(
                    ax=ax,
                    color=layer_color,
                    alpha=layer_alpha,
                    label=layer_name                    
                )
                if legend:
                    patch = Patch(
                        facecolor=layer_color, 
                        alpha=layer_alpha, 
                        label=layer_name
                        )
                    legend_handles.append(patch)

            elif isinstance(layer_color, dict):
                color_key = list(layer_color.keys())[0]
                color_mapping = layer_color[color_key]

                if color_key not in layer_3857.columns:
                    raise KeyError("Column " + color_key + " not in layer.")

                for value, color in color_mapping.items():
                    
                    subset = layer_3857[layer_3857[color_key].astype(str) == str(value)]
                    
                    if not subset.empty:
                        
                        subset.plot(
                            ax=ax,
                            color=color,
                            alpha=layer_alpha,
                            label=str(value)
                        )
                        
                        if legend:
                            patch = Patch(facecolor=color, alpha=layer_alpha, label=str(value))
                            legend_handles.append(patch)

        else:
            
            layer_3857.plot(ax=ax, alpha=0.6, label=f"Layer {i+1}")
            
            if legend:
                
                patch = Patch(
                    facecolor="gray", 
                    alpha=0.6, 
                    label=f"Layer {i+1}"
                    )
                
                legend_handles.append(patch)

        i += 1

    bbox = box(sw_lon, sw_lat, ne_lon, ne_lat)
    extent_geom = gp.GeoSeries([bbox], crs=4326).to_crs(epsg=3857).total_bounds
    ax.set_xlim(extent_geom[0], extent_geom[2])
    ax.set_ylim(extent_geom[1], extent_geom[3])

    if osm_basemap:
        cx.add_basemap(
            ax,
            source=cx.providers.OpenStreetMap.Mapnik,
            zoom=zoom
        )

    plt.axis('off')

    if legend and legend_handles:
        ax.legend(handles=legend_handles, loc='lower right', fontsize='small', frameon=True)

    if verbose:
        print("OK")

    if show_plot:
        plt.show()

    if save_output:
        plt.savefig(
            output_filepath,
            dpi=output_dpi,
            bbox_inches="tight"
        )
        plt.close()

    if os.path.exists("osm_map.png"):
        os.remove("osm_map.png")
        
    return fig