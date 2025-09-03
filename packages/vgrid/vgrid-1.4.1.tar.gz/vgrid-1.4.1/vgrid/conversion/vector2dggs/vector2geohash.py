"""
Vector to Geohash DGGS Grid Conversion Module

This module provides comprehensive functionality for converting vector geometries to Geohash grid cells.
Geohash is a hierarchical geospatial indexing system that divides the Earth's surface into cells of
varying resolutions, from 1 (coarsest) to 10 (finest).

Key Features:
- Convert points, lines, and polygons to Geohash grid cells
- Support for multiple input formats (files, URLs, DataFrames, GeoDataFrames, GeoJSON)
- Multiple spatial predicates for polygon conversion
- Topology preservation mode to ensure disjoint features have disjoint Geohash cells
- Geohash compact mode to reduce cell count for polygons
- Multiple output formats (GeoJSON, GPKG, Parquet, CSV, Shapefile)
- Command-line interface for batch processing
"""

import sys
import os
import argparse
from tqdm import tqdm
from shapely.geometry import MultiPoint
import geopandas as gpd
from vgrid.conversion.dggs2geo.geohash2geo import geohash2geo
from vgrid.dggs import geohash
from vgrid.utils.geometry import graticule_dggs_to_geoseries
from vgrid.generator.geohashgrid import  expand_geohash_bbox
from vgrid.utils.constants import INITIAL_GEOHASHES

from vgrid.conversion.dggscompact.geohashcompact import geohashcompact
from vgrid.utils.geometry import (
    check_predicate,
    shortest_point_distance,
)
from math import sqrt
from vgrid.utils.io import (
    validate_geohash_resolution,
    process_input_data_vector,
    convert_to_output_format,
    DGGS_TYPES
)
from vgrid.utils.constants import OUTPUT_FORMATS, STRUCTURED_FORMATS

min_res = DGGS_TYPES["geohash"]["min_res"]
max_res = DGGS_TYPES["geohash"]["max_res"]   


def point2geohash(
    feature,
    resolution,
    feature_properties=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    """
    Convert a point geometry to Geohash grid cells.

    Args:
        feature (shapely.geometry.Point or shapely.geometry.MultiPoint): Point geometry to convert
        resolution (int): Geohash resolution level [1..10]
        feature_properties (dict, optional): Properties to include in output features
        predicate (str, optional): Spatial predicate to apply (not used for points)
        compact (bool, optional): Enable Geohash compact mode (not used for points)
        topology (bool, optional): Enable topology preserving mode (handled by geodataframe2geohash)
        include_properties (bool, optional): Whether to include properties in output

    Returns:
        list: List of dictionaries representing Geohash cells containing the point(s)

    Example:
        >>> from shapely.geometry import Point
        >>> point = Point(-122.4194, 37.7749)  # San Francisco
        >>> cells = point2geohash(point, 6, {"name": "SF"})
        >>> len(cells)
        1
    """
    geohash_rows = []
    if feature.geom_type in ("Point"):
        points = [feature]
    elif feature.geom_type in ("MultiPoint"):
        points = list(feature.geoms)
    else:
        return []
    
    for point in points:
        longitude = point.x
        latitude = point.y
        geohash_id = geohash.encode(latitude, longitude, resolution)
        cell_polygon = geohash2geo(geohash_id)
        row = graticule_dggs_to_geoseries(
            "geohash", geohash_id, resolution, cell_polygon
        )
        if include_properties and feature_properties:
            row.update(feature_properties)
        geohash_rows.append(row)
    return geohash_rows


def polyline2geohash(
    feature,
    resolution,
    feature_properties=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    """
    Convert a polyline geometry to Geohash grid cells.

    Args:
        feature (shapely.geometry.LineString or shapely.geometry.MultiLineString): Polyline geometry to convert
        resolution (int): Geohash resolution level [1..10]
        feature_properties (dict, optional): Properties to include in output features
        predicate (str, optional): Spatial predicate to apply (not used for polylines)
        compact (bool, optional): Enable Geohash compact mode (not used for polylines)
        topology (bool, optional): Enable topology preserving mode (handled by geodataframe2geohash)
        include_properties (bool, optional): Whether to include properties in output

    Returns:
        list: List of dictionaries representing Geohash cells intersecting the polyline

    Example:
        >>> from shapely.geometry import LineString
        >>> line = LineString([(-122.4194, 37.7749), (-122.4000, 37.7800)])
        >>> cells = polyline2geohash(line, 6, {"name": "route"})
        >>> len(cells) > 0
        True
    """
    geohash_rows = []
    if feature.geom_type in ("LineString"):
        polylines = [feature]
    elif feature.geom_type in ("MultiLineString"):
        polylines = list(feature.geoms)
    else:
        return []
    
    for polyline in polylines:
        intersected_geohashes = {
            gh
            for gh in INITIAL_GEOHASHES
            if geohash2geo(gh).intersects(polyline)
        }
        geohashes_bbox = set()
        for gh in intersected_geohashes:
            expand_geohash_bbox(gh, resolution, geohashes_bbox, polyline)
        
        for gh in geohashes_bbox:
            cell_polygon = geohash2geo(gh)
            row = graticule_dggs_to_geoseries(
                "geohash", gh, resolution, cell_polygon
            )
            if include_properties and feature_properties:
                row.update(feature_properties)
            geohash_rows.append(row)
    return geohash_rows


def polygon2geohash(
    feature,
    resolution,
    feature_properties=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    """
    Convert a polygon geometry to Geohash grid cells.

    Args:
        feature (shapely.geometry.Polygon or shapely.geometry.MultiPolygon): Polygon geometry to convert
        resolution (int): Geohash resolution level [1..10]
        feature_properties (dict, optional): Properties to include in output features
        predicate (str, optional): Spatial predicate to apply ('intersect', 'within', 'centroid_within', 'largest_overlap')
        compact (bool, optional): Enable Geohash compact mode to reduce cell count
        topology (bool, optional): Enable topology preserving mode (handled by geodataframe2geohash)
        include_properties (bool, optional): Whether to include properties in output

    Returns:
        list: List of dictionaries representing Geohash cells based on predicate

    Example:
        >>> from shapely.geometry import Polygon
        >>> poly = Polygon([(-122.5, 37.7), (-122.3, 37.7), (-122.3, 37.9), (-122.5, 37.9)])
        >>> cells = polygon2geohash(poly, 6, {"name": "area"}, predicate="intersect")
        >>> len(cells) > 0
        True
    """
    geohash_rows = []
    if feature.geom_type in ("Polygon"):
        polygons = [feature]
    elif feature.geom_type in ("MultiPolygon"):
        polygons = list(feature.geoms)
    else:
        return []
    
    for polygon in polygons:
        intersected_geohashes = {
            gh for gh in INITIAL_GEOHASHES if geohash2geo(gh).intersects(polygon)
        }
        geohashes_bbox = set()
        for gh in intersected_geohashes:
            expand_geohash_bbox(gh, resolution, geohashes_bbox, polygon)
        
        for gh in geohashes_bbox:
            cell_polygon = geohash2geo(gh)
            row = graticule_dggs_to_geoseries(
                "geohash", gh, resolution, cell_polygon
            )
            cell_geom = row["geometry"]
            if not check_predicate(cell_geom, polygon, predicate):
                continue
            if include_properties and feature_properties:
                row.update(feature_properties)
            geohash_rows.append(row)
    
    # Apply compact mode if enabled
    if compact and geohash_rows:
        # Create a GeoDataFrame from the current results
        temp_gdf = gpd.GeoDataFrame(geohash_rows, geometry="geometry", crs="EPSG:4326")
        
        # Use geohashcompact function directly
        compacted_gdf = geohashcompact(temp_gdf, geohash_id="geohash", output_format="gpd")
        
        if compacted_gdf is not None:
            # Convert back to list of dictionaries
            geohash_rows = compacted_gdf.to_dict('records')
        # If compaction failed, keep original results
    
    return geohash_rows


def geodataframe2geohash(
    gdf,
    resolution=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    """
    Convert a GeoDataFrame to Geohash grid cells.

    Args:
        gdf (geopandas.GeoDataFrame): GeoDataFrame to convert
        resolution (int, optional): Geohash resolution level [1..10]. Required when topology=False, auto-calculated when topology=True
        predicate (str, optional): Spatial predicate to apply for polygons ('intersect', 'within', 'centroid_within', 'largest_overlap')
        compact (bool, optional): Enable Geohash compact mode for polygons
        topology (bool, optional): Enable topology preserving mode to ensure disjoint features have disjoint Geohash cells
        include_properties (bool, optional): Whether to include properties in output

    Returns:
        geopandas.GeoDataFrame: GeoDataFrame with Geohash grid cells

    Example:
        >>> import geopandas as gpd
        >>> from shapely.geometry import Point
        >>> gdf = gpd.GeoDataFrame({
        ...     'name': ['San Francisco'],
        ...     'geometry': [Point(-122.4194, 37.7749)]
        ... })
        >>> result = geodataframe2geohash(gdf, 6)
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
            
            # Find resolution where Geohash cell size is smaller than shortest distance
            # This ensures disjoint points have disjoint Geohash cells
            if shortest_distance > 0:
                # Geohash cell size (approx): each character increases resolution, cell size shrinks by ~1/8 to 1/32
                # We'll use a rough estimate: cell size halves every character, so use a lookup or formula
                # For simplicity, use a fixed table for WGS84 (meters) for geohash length 1-10
                geohash_cell_sizes = [
                    5000000,
                    1250000,
                    156000,
                    39100,
                    4890,
                    1220,
                    153,
                    38.2,
                    4.77,
                    1.19,
                ]  # meters
                for res in range(min_res, max_res+1):
                    cell_diameter = geohash_cell_sizes[res - 1] * sqrt(2) * 2
                    if cell_diameter < shortest_distance:
                        estimated_resolution = res
                        break
                        
        resolution = estimated_resolution

    resolution = validate_geohash_resolution(resolution)        

    geohash_rows = []
    
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
            geohash_rows.extend(
                point2geohash(
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
            geohash_rows.extend(
                polyline2geohash(
                    feature=geom,
                    resolution=resolution,
                    feature_properties=props,
                    predicate=predicate,
                    compact=compact,
                    include_properties=include_properties,
                )
            )
        elif geom.geom_type in ("Polygon", "MultiPolygon"):
            geohash_rows.extend(
                polygon2geohash(
                    feature=geom,
                    resolution=resolution,
                    feature_properties=props,
                    predicate=predicate,
                    compact=compact,
                    include_properties=include_properties,
                )
            )
    return gpd.GeoDataFrame(geohash_rows, geometry="geometry", crs="EPSG:4326")


# --- Main vector2geohash function ---
def vector2geohash(
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
    Convert vector data to Geohash grid cells from various input formats.

    Args:
        vector_data (str, geopandas.GeoDataFrame, pandas.DataFrame, dict, or list): Input vector data
        resolution (int, optional): Geohash resolution level [1..10]. Required when topology=False, auto-calculated when topology=True
        predicate (str, optional): Spatial predicate to apply for polygons ('intersect', 'within', 'centroid_within', 'largest_overlap')
        compact (bool, optional): Enable Geohash compact mode for polygons
        topology (bool, optional): Enable topology preserving mode to ensure disjoint features have disjoint Geohash cells
        output_format (str, optional): Output format ('gpd', 'geojson', 'csv', 'shapefile', 'gpkg', 'parquet', 'geoparquet')
        include_properties (bool, optional): Whether to include properties in output
        **kwargs: Additional arguments passed to process_input_data_vector

    Returns:
        geopandas.GeoDataFrame, dict, or str: Output in the specified format. If output_format is a file-based format,
        the output will be saved to a file in the current directory with a default name based on the input.
        Otherwise, returns a Python object (GeoDataFrame, dict, etc.) depending on output_format.

    Example:
        >>> result = vector2geohash("data/points.geojson", resolution=6, output_format="geojson")
        >>> print(f"Output saved to: {result}")
    """
    # Validate resolution parameter
    if not topology and resolution is None:
        raise ValueError("resolution parameter is required when topology=False")
    
    # Only validate resolution if it's not None
    if resolution is not None:
        resolution = validate_geohash_resolution(resolution)
    
    gdf = process_input_data_vector(vector_data, **kwargs)
    result = geodataframe2geohash(
        gdf, resolution, predicate, compact, topology, include_properties
    )        
    output_name = None
    if output_format in OUTPUT_FORMATS:
        if isinstance(vector_data, str):    
            base = os.path.splitext(os.path.basename(vector_data))[0]
            output_name = f"{base}2geohash"           
        else:
            output_name = f"geohash"           
    return convert_to_output_format(result, output_format, output_name)


# --- CLI ---
def vector2geohash_cli():
    """
    Command-line interface for vector2geohash conversion.
    
    This function provides a command-line interface for converting vector data to Geohash grid cells.
    It supports various input formats and output formats, with options for resolution control,
    spatial predicates, compact mode, and topology preservation.
    
    Usage:
        python vector2geohash.py -i input.geojson -r 6 -f geojson
        python vector2geohash.py -i input.shp -r 5 -p intersect -c -t
    """
    parser = argparse.ArgumentParser(description="Convert vector data to Geohash grid cells")
    parser.add_argument("-i", "--input", help="Input file path, URL")

    parser.add_argument(
        "-r",
        "--resolution",
        type=int,
        choices=range(min_res, max_res+1),
        help=f"Geohash resolution [{min_res}..{max_res}]. Required when topology=False, auto-calculated when topology=True",
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
        help="Enable Geohash compact mode for polygons",
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
        result = vector2geohash(
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
    vector2geohash_cli()
