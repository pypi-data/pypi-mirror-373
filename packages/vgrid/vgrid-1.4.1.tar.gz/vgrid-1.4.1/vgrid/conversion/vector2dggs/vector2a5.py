"""
A5 Grid Conversion Module

This module provides comprehensive functionality for converting vector geometries to A5 grid cells.
A5 is a hierarchical geospatial indexing system that divides the Earth's surface into cells of
varying resolutions, from 0 (coarsest) to 28 (finest).

Key Features:
- Convert points, lines, and polygons to A5 grid cells
- Support for multiple input formats (files, URLs, DataFrames, GeoDataFrames, GeoJSON)
- Multiple spatial predicates for polygon conversion ('intersect', 'within', 'centroid_within', 'largest_overlap')
- Topology preservation mode to ensure disjoint features have disjoint A5 cells
- A5 compact mode to reduce cell count for polygons
- Multiple output formats (GeoJSON, GPKG, Parquet, CSV, Shapefile)
- Command-line interface for batch processing
- Automatic resolution calculation for topology preservation mode

Functions:
- point2a5: Convert point geometries to A5 cells
- polyline2a5: Convert line geometries to A5 cells
- polygon2a5: Convert polygon geometries to A5 cells with spatial predicates
- geodataframe2a5: Convert GeoDataFrame to A5 cells with topology support
- vector2a5: Main function for converting various input formats to A5 cells
- vector2a5_cli: Command-line interface for batch processing

The module uses the A5 library for hierarchical geospatial indexing and supports
both individual geometry conversion and batch processing of entire datasets.
"""

import sys
import os
import argparse
from tqdm import tqdm
from pyproj import Geod
import geopandas as gpd
from shapely.geometry import MultiPoint
import a5
from vgrid.utils.geometry import geodesic_dggs_to_geoseries
from vgrid.utils.geometry import (
    check_predicate,
    shortest_point_distance,
)
from vgrid.utils.io import validate_a5_resolution, process_input_data_vector, convert_to_output_format, DGGS_TYPES

from vgrid.conversion.latlon2dggs import latlon2a5
from vgrid.conversion.dggs2geo.a52geo import a52geo
from vgrid.conversion.dggscompact.a5compact import a5compact
from vgrid.stats.a5stats import a5_metrics  
geod = Geod(ellps="WGS84")
from vgrid.utils.constants import OUTPUT_FORMATS, STRUCTURED_FORMATS

min_res= DGGS_TYPES["a5"]["min_res"]
max_res = DGGS_TYPES["a5"]["max_res"]   

def point2a5(
    feature,
    resolution,
    feature_properties=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    """
    Convert a point geometry to A5 grid cells.

    Args:
        feature (shapely.geometry.Point or shapely.geometry.MultiPoint): Point geometry to convert
        resolution (int): A5 resolution level [0..28]
        feature_properties (dict, optional): Properties to include in output features
        predicate (str, optional): Spatial predicate to apply (not used for points)
        compact (bool, optional): Enable A5 compact mode (not used for points)
        topology (bool, optional): Enable topology preserving mode (handled by geodataframe2a5)
        include_properties (bool, optional): Whether to include properties in output

    Returns:
        list: List of dictionaries representing A5 cells containing the point(s)

    Example:
        >>> from shapely.geometry import Point
        >>> point = Point(-122.4194, 37.7749)  # San Francisco
        >>> cells = point2a5(point, 10, {"name": "SF"})
        >>> len(cells)
        1
    """
    a5_rows = []  
    if feature.geom_type in ("Point"):
        points = [feature]
    elif feature.geom_type in ("MultiPoint"):
        points = list(feature.geoms)
    else:
        return []
    for point in points:    
        a5_hex = latlon2a5(point.y, point.x, resolution)
        cell_polygon = a52geo(a5_hex)     
        cell_resolution = a5.get_resolution(a5.hex_to_u64(a5_hex))
        num_edges = 4
        row = geodesic_dggs_to_geoseries(
            "a5", a5_hex, cell_resolution, cell_polygon, num_edges
        )  
        
        # Add properties if requested
        if include_properties and feature_properties:
            row.update(feature_properties)
        
        a5_rows.append(row)
    return a5_rows


def polyline2a5(        
    feature,               
    resolution,
    feature_properties=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    """
    Convert a polyline geometry to A5 grid cells.

    Args:
        feature (shapely.geometry.LineString or shapely.geometry.MultiLineString): Polyline geometry to convert
        resolution (int): A5 resolution level [0..28]
        feature_properties (dict, optional): Properties to include in output features
        predicate (str, optional): Spatial predicate to apply (not used for polylines)
        compact (bool, optional): Enable A5 compact mode (not used for polylines)
        topology (bool, optional): Enable topology preserving mode (handled by geodataframe2a5)
        include_properties (bool, optional): Whether to include properties in output

    Returns:
        list: List of dictionaries representing A5 cells intersecting the polyline

    Example:
        >>> from shapely.geometry import LineString
        >>> line = LineString([(-122.4194, 37.7749), (-122.4000, 37.7800)])
        >>> cells = polyline2a5(line, 10, {"name": "route"})
        >>> len(cells) > 0
        True
    """  
    
    a5_rows = []
    if feature.geom_type in ("LineString"):
        polylines = [feature]
    elif feature.geom_type in ("MultiLineString"):
        polylines = list(feature.geoms)
    else:
        return []
    for polyline in polylines:
        min_lng, min_lat, max_lng, max_lat = polyline.bounds
        
        # Calculate longitude and latitude width based on resolution
        if resolution == 0:
            # For resolution 0, use larger width
            lon_width = 35
            lat_width = 35
        elif resolution == 1:
            lon_width = 18
            lat_width = 18
        elif resolution == 2:
            lon_width = 10
            lat_width = 10
        elif resolution == 3:
            lon_width = 5
            lat_width = 5
        elif resolution > 3:
            base_width = 5  # at resolution 3
            factor = 0.5 ** (resolution - 3)
            lon_width = base_width * factor
            lat_width = base_width * factor
               
        # Generate longitude and latitude arrays
        longitudes = []
        latitudes = []
        
        lon = min_lng
        while lon < max_lng:
            longitudes.append(lon)
            lon += lon_width
        
        lat = min_lat
        while lat < max_lat:
            latitudes.append(lat)
            lat += lat_width
        
        seen_a5_hex = set()  # Track unique A5 hex codes
        
        # Generate and check each grid cell
        for lon in longitudes:
            for lat in latitudes:
                min_lon = lon
                min_lat = lat
                max_lon = lon + lon_width
                max_lat = lat + lat_width
                
                # Calculate centroid
                centroid_lat = (min_lat + max_lat) / 2
                centroid_lon = (min_lon + max_lon) / 2
                
                try:
                    # Convert centroid to A5 cell ID using direct A5 functions
                    a5_hex = latlon2a5(centroid_lat, centroid_lon, resolution)
                    cell_polygon = a52geo(a5_hex)
                    
                    if cell_polygon is not None:                        
                        # Only process if this A5 hex code hasn't been seen before
                        if a5_hex not in seen_a5_hex:
                            seen_a5_hex.add(a5_hex)                            
                            # Check if cell intersects with polyline
                            if cell_polygon.intersects(polyline):
                                cell_resolution = a5.get_resolution(a5.hex_to_u64(a5_hex))
                                num_edges = 4
                                row = geodesic_dggs_to_geoseries(
                                    "a5", a5_hex, cell_resolution, cell_polygon, num_edges
                                )
                                
                                # Add properties if requested
                                if include_properties and feature_properties:
                                    row.update(feature_properties)
                                
                                a5_rows.append(row)
                        
                except Exception as e:
                    # Skip cells that can't be processed
                    continue
    
    return a5_rows


def polygon2a5(
    feature,   
    resolution,
    feature_properties=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    """
    Convert a polygon geometry to A5 grid cells.

    Args:
        feature (shapely.geometry.Polygon or shapely.geometry.MultiPolygon): Polygon geometry to convert
        resolution (int): A5 resolution level [0..28]
        feature_properties (dict, optional): Properties to include in output features
        predicate (str, optional): Spatial predicate to apply ('intersect', 'within', 'centroid_within', 'largest_overlap')
        compact (bool, optional): Enable A5 compact mode to reduce cell count
        topology (bool, optional): Enable topology preserving mode (handled by geodataframe2a5)
        include_properties (bool, optional): Whether to include properties in output

    Returns:
        list: List of dictionaries representing A5 cells based on predicate

    Example:
        >>> from shapely.geometry import Polygon
        >>> poly = Polygon([(-122.5, 37.7), (-122.3, 37.7), (-122.3, 37.9), (-122.5, 37.9)])
        >>> cells = polygon2a5(poly, 10, {"name": "area"}, predicate="intersect")
        >>> len(cells) > 0
        True
    """
    a5_rows = []
    if feature.geom_type in ("Polygon"):
        polygons = [feature]
    elif feature.geom_type in ("MultiPolygon"):
        polygons = list(feature.geoms)
    else:
        return []
    
    for polygon in polygons:
        min_lng, min_lat, max_lng, max_lat = polygon.bounds
        
        # Calculate longitude and latitude width based on resolution
        if resolution == 0:
            lon_width = 35
            lat_width = 35
        elif resolution == 1:
            lon_width = 18
            lat_width = 18
        elif resolution == 2:
            lon_width = 10
            lat_width = 10
        elif resolution == 3:
            lon_width = 5
            lat_width = 5
        elif resolution > 3:
            base_width = 5  # at resolution 3
            factor = 0.5 ** (resolution - 3)
            lon_width = base_width * factor
            lat_width = base_width * factor
                
        # Generate longitude and latitude arrays
        longitudes = []
        latitudes = []
        
        lon = min_lng
        while lon < max_lng:
            longitudes.append(lon)
            lon += lon_width
        
        lat = min_lat
        while lat < max_lat:
            latitudes.append(lat)
            lat += lat_width
        
        seen_a5_hex = set()  # Track unique A5 hex codes
        
        # Generate and check each grid cell
        for lon in longitudes:
            for lat in latitudes:
                min_lon = lon
                min_lat = lat
                max_lon = lon + lon_width
                max_lat = lat + lat_width
                
                # Calculate centroid
                centroid_lat = (min_lat + max_lat) / 2
                centroid_lon = (min_lon + max_lon) / 2
                
                try:
                    # Convert centroid to A5 cell ID using direct A5 functions
                    a5_hex = latlon2a5(centroid_lat, centroid_lon, resolution)
                    cell_polygon = a52geo(a5_hex)
                    
                    # Only process if this A5 hex code hasn't been seen before
                    if a5_hex not in seen_a5_hex:
                        seen_a5_hex.add(a5_hex)
                        
                        # Check if cell satisfies the predicate with polygon
                        if check_predicate(cell_polygon, polygon, predicate):
                            cell_resolution = a5.get_resolution(a5.hex_to_u64(a5_hex))
                            num_edges = 4
                            row = geodesic_dggs_to_geoseries(
                                "a5", a5_hex, cell_resolution, cell_polygon, num_edges
                            )
                            
                            # Add properties if requested
                            if include_properties and feature_properties:
                                row.update(feature_properties)
                            
                            a5_rows.append(row)
                        
                except Exception as e:
                    # Skip cells that can't be processed
                    continue
    
    # Apply compact mode if enabled
    if compact and a5_rows:
        # Create a GeoDataFrame from the current results
        temp_gdf = gpd.GeoDataFrame(a5_rows, geometry="geometry", crs="EPSG:4326")
        
        # Use a5compact function directly
        compacted_gdf = a5compact(temp_gdf, a5_hex="a5", output_format="gpd")
        
        if compacted_gdf is not None:
            # Convert back to list of dictionaries
            a5_rows = compacted_gdf.to_dict('records')
        # If compaction failed, keep original results
    
    return a5_rows

def geodataframe2a5(
    gdf,
    resolution=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    """
    Convert a GeoDataFrame to A5 grid cells.

    Args:
        gdf (geopandas.GeoDataFrame): GeoDataFrame to convert
        resolution (int, optional): A5 resolution level [0..28]. Required when topology=False, auto-calculated when topology=True
        predicate (str, optional): Spatial predicate to apply for polygons ('intersect', 'within', 'centroid_within', 'largest_overlap')
        compact (bool, optional): Enable A5 compact mode for polygons
        topology (bool, optional): Enable topology preserving mode to ensure disjoint features have disjoint A5 cells
        include_properties (bool, optional): Whether to include properties in output

    Returns:
        geopandas.GeoDataFrame: GeoDataFrame with A5 grid cells

    Example:
        >>> import geopandas as gpd
        >>> from shapely.geometry import Point
        >>> gdf = gpd.GeoDataFrame({
        ...     'name': ['San Francisco'],
        ...     'geometry': [Point(-122.4194, 37.7749)]
        ... })
        >>> result = geodataframe2a5(gdf, 10)
        >>> len(result) > 0
        True
    """   
    # Process topology for points and multipoints if enabled
    if topology:
        estimated_resolution = resolution
        # Collect all points for topology preservation
        points_list = []
        for _, row in gdf.iterrows():
            geom = row.geometry
            if geom is None:
                continue
            if geom.geom_type == "Point":
                points_list.append(geom)
            elif geom.geom_type == "MultiPoint":
                points_list.extend(list(geom.geoms))
        
        if points_list:
            all_points = MultiPoint(points_list)
            
            # Calculate the shortest distance between all points
            shortest_distance = shortest_point_distance(all_points)
            
            # Find resolution where A5 cell size is smaller than shortest distance
            # This ensures disjoint points have disjoint A5 cells
            if shortest_distance > 0:
                for res in range(min_res, max_res+1):
                    _, avg_edge_length, _, _ = a5_metrics(res)
                    # Use a factor to ensure sufficient separation (cell diameter is ~2x edge length)
                    cell_diameter = avg_edge_length*1.4
                    if cell_diameter < shortest_distance:
                        estimated_resolution = res
                        break

        resolution = estimated_resolution
   
    resolution = validate_a5_resolution(resolution)
        
    a5_rows = []
    
    for _, row in tqdm(gdf.iterrows(), desc="Processing features", total=len(gdf)):
        geom = row.geometry
        if geom is None:
            continue
        
        props = row.to_dict()
        if "geometry" in props:
            del props["geometry"]
        
        if not include_properties:
            props = {}
        
        if geom.geom_type == "Point" or geom.geom_type == "MultiPoint":
            a5_rows.extend(
                point2a5(
                    feature=geom,
                    resolution=resolution,
                    feature_properties=props,
                    predicate=predicate,
                    compact=compact,
                    topology=topology,  # Topology already processed above
                    include_properties=include_properties,
                )
            )
        
        elif geom.geom_type in ("LineString", "MultiLineString"):
            a5_rows.extend(
                polyline2a5(
                    feature=geom,
                    resolution=resolution,
                    feature_properties=props,
                    predicate=predicate,
                    compact=compact,
                    include_properties=include_properties,
                )
            )
        elif geom.geom_type in ("Polygon", "MultiPolygon"):
            a5_rows.extend(
                polygon2a5(
                    feature=geom,
                    resolution=resolution,
                    feature_properties=props,
                    predicate=predicate,
                    compact=compact,
                    include_properties=include_properties,
                )
            )
    return gpd.GeoDataFrame(a5_rows, geometry="geometry", crs="EPSG:4326")


# --- Main vector2a5 function ---
def vector2a5(
    vector_data,
    resolution=None,
    predicate=None,
    compact=False,
    topology=False,
    output_format="gpd",
    include_properties=True,
    **kwargs,
):
    """
    Convert vector data to A5 grid cells from various input formats.

    Args:
        vector_data (str, geopandas.GeoDataFrame, pandas.DataFrame, dict, or list): Input vector data
        resolution (int, optional): A5 resolution level [0..28]. Required when topology=False, auto-calculated when topology=True
        predicate (str, optional): Spatial predicate to apply for polygons ('intersect', 'within', 'centroid_within', 'largest_overlap')
        compact (bool, optional): Enable A5 compact mode for polygons
        topology (bool, optional): Enable topology preserving mode to ensure disjoint features have disjoint A5 cells
        output_format (str, optional): Output format ('gpd', 'geojson', 'csv', 'shapefile', 'gpkg', 'parquet', 'geoparquet')
        include_properties (bool, optional): Whether to include properties in output
        **kwargs: Additional arguments passed to process_input_data_vector

    Returns:
        geopandas.GeoDataFrame, dict, or str: Output in the specified format. If output_format is a file-based format,
        the output will be saved to a file in the current directory with a default name based on the input.
        Otherwise, returns a Python object (GeoDataFrame, dict, etc.) depending on output_format.

    Example:
        >>> result = vector2a5("data/points.geojson", resolution=10, output_format="geojson")
        >>> print(f"Output saved to: {result}")
    """
    # Validate resolution parameter
    if not topology and resolution is None:
        raise ValueError("resolution parameter is required when topology=False")
    
    # Only validate resolution if it's not None
    if resolution is not None:
        resolution = validate_a5_resolution(resolution)
    
    gdf = process_input_data_vector(vector_data, **kwargs)
    result = geodataframe2a5(
        gdf, resolution, predicate, compact, topology, include_properties
    )        
    output_name = None
    if output_format in OUTPUT_FORMATS:
        if isinstance(vector_data, str):    
            base = os.path.splitext(os.path.basename(vector_data))[0]
            output_name = f"{base}2a5"           
        else:
            output_name = f"a5"           
    return convert_to_output_format(result, output_format, output_name)


# --- CLI ---
def vector2a5_cli():
    """
    Command-line interface for vector2a5 conversion.
    
    This function provides a command-line interface for converting vector data to A5 grid cells.
    It supports various input formats and output formats, with options for resolution control,
    spatial predicates, compact mode, and topology preservation.
    
    Usage:
        python vector2a5.py -i input.geojson -r 10 -f geojson
        python vector2a5.py -i input.shp -r 8 -p intersect -c -t
    """
    parser = argparse.ArgumentParser(description="Convert vector data to A5 grid cells")
    parser.add_argument("-i", "--input", help="Input file path, URL")

    parser.add_argument(
        "-r",
        "--resolution",
        type=int,
        choices=range(min_res, max_res+1),
        help=f"A5 resolution [{min_res}..{max_res}]. Required when topology=False, auto-calculated when topology=True",
    )
    parser.add_argument(
        "-p",
        "--predicate",
        choices=["intersect", "within", "centroid_within", "largest_overlap"],
        help="Spatial predicate: intersect, within, centroid_within, largest_overlap for polygons",
    )
    parser.add_argument(
        "-c",
        "--compact",
        action="store_true",
        help="Enable A5 compact mode for polygons",
    )
    parser.add_argument(
        "-t", "--topology", action="store_true", help="Enable topology preserving mode"
    )
    parser.add_argument(
        "-np",
        "-no-props",
        dest="include_properties",
        action="store_false",
        help="Do not include original feature properties.",
    )
    parser.add_argument(
        "-f",
        "--output_format",
        type=str,
        choices=OUTPUT_FORMATS,
        default="gpd",
        help="Output format (default: gpd).",       
    )
    args = parser.parse_args()
    
    try:
        result = vector2a5(
            vector_data=args.input,
            resolution=args.resolution,
            predicate=args.predicate,
            compact=args.compact,
            topology=args.topology,
            output_format=args.output_format,
            include_properties=args.include_properties,
        )
        if args.output_format in STRUCTURED_FORMATS:
            print(result)
        # For file outputs, the utility prints the saved path
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    vector2a5_cli()
