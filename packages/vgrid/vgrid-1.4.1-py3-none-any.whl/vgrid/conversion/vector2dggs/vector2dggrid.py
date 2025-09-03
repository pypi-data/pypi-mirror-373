"""
DGGRID Grid Conversion Module

This module provides comprehensive functionality for converting vector geometries to DGGRID grid cells.
DGGRID supports multiple DGGS types including ISEA4H, FULLER, and others, each with their own
resolution ranges and cell characteristics. The module uses the DGGRIDv7 library for grid operations.

Key Features:
- Convert points, lines, and polygons to DGGRID grid cells
- Support for multiple input formats (files, URLs, DataFrames, GeoDataFrames, GeoJSON)
- Multiple spatial predicates for polygon conversion ('intersect', 'within', 'centroid_within', 'largest_overlap')
- Multiple output address types (SEQNUM, Q2DI, Q2DD, etc.)
- Multiple output formats (GeoJSON, GPKG, Parquet, CSV, Shapefile)
- Command-line interface for batch processing
- Support for various DGGRID types (ISEA4H, FULLER, etc.)

Functions:
- point_to_grid: Convert point geometries to DGGRID cells
- polyline_to_grid: Convert line geometries to DGGRID cells
- polygon_to_grid: Convert polygon geometries to DGGRID cells with spatial predicates
- geometry2dggrid: Convert list of geometries to DGGRID cells
- geodataframe2dggrid: Convert GeoDataFrame to DGGRID cells
- dataframe2dggrid: Convert DataFrame with geometry column to DGGRID cells
- vector2dggrid: Main function for converting various input formats to DGGRID cells
- vector2dggrid_cli: Command-line interface for batch processing

The module uses the DGGRIDv7 library for grid operations and supports
both individual geometry conversion and batch processing of entire datasets.
"""

import argparse
import sys
import os
from tqdm import tqdm
from pyproj import Geod
import geopandas as gpd
import pandas as pd
from shapely.geometry import box
from vgrid.utils.io import validate_dggrid_type, validate_dggrid_resolution, create_dggrid_instance
from vgrid.conversion.latlon2dggs import latlon2dggrid
from vgrid.conversion.dggs2geo.dggrid2geo import dggrid2geo
from vgrid.utils.geometry import check_predicate
from dggrid4py.dggrid_runner import output_address_types

geod = Geod(ellps="WGS84")
from vgrid.utils.io import process_input_data_vector, convert_to_output_format
from vgrid.utils.constants import DGGRID_TYPES, OUTPUT_FORMATS, STRUCTURED_FORMATS    

# Function to generate grid for Point
def point_to_grid(dggrid_instance, dggs_type, feature, resolution, predicate=None, compact=False, topology=False, include_properties=True, feature_properties=None,output_address_type="SEQNUM"):    
    """
    Generate DGGRID cell(s) for a Point or MultiPoint geometry by delegating to
    latlon2dggrid for ID lookup and dggrid2geo for polygonization.

    Returns GeoJSON FeatureCollection as a JSON string.
    """
    dggs_type = validate_dggrid_type(dggs_type)       
    resolution = validate_dggrid_resolution(dggs_type, resolution)

    # Expect a single Point; MultiPoint handled by geometry2dggrid
    lat = float(feature.y)
    lon = float(feature.x)
    seqnum = latlon2dggrid(dggrid_instance, dggs_type, lat, lon, resolution, output_address_type)
    seqnums = [seqnum]

    # Build polygons from SEQNUM ids
    gdf = dggrid2geo(dggrid_instance, dggs_type, seqnums, resolution, output_address_type)
    if include_properties and feature_properties:
        for key, value in feature_properties.items():
            gdf[key] = value
    return gdf


# Function to generate grid for Polyline
def polyline_to_grid(dggrid_instance, dggs_type, feature, resolution, predicate=None, compact=False, topology=False, include_properties=True, feature_properties=None, output_address_type="SEQNUM "):
    """ 
    Generate DGGRID cells intersecting with a LineString or MultiLineString geometry.

    Args:
        dggrid_instance: DGGRIDv7 instance for grid operations.
        dggs_type (str): Type of DGGS (e.g., ISEA4H, FULLER, etc.).
        res (int): Resolution for the DGGRID.
        address_type (str): Address type for the output grid cells.
        geometry (shapely.geometry.LineString or MultiLineString): Input geometry.

    Returns:
        geopandas.GeoDataFrame: GeoDataFrame containing DGGRID cells intersecting with the input geometry.
    """
    # Initialize an empty list to store filtered grid cells
    merged_grids = []

    # Check the geometry type
    if feature.geom_type == "LineString":
        # Handle single LineString
        polylines = [feature]
    elif feature.geom_type == "MultiLineString":
        # Handle MultiLineString: process each line separately
        polylines = list(feature.geoms)

    # Process each polyline
    for polyline in polylines:
        # Get bounding box for the current polyline
        bounding_box = box(*polyline.bounds)

        # Generate grid cells for the bounding box
        dggrid_gdf = dggrid_instance.grid_cell_polygons_for_extent(
            dggs_type,
            resolution,
            clip_geom=bounding_box,
            split_dateline=True,
            output_address_type=output_address_type,
        )        

        # Keep only grid cells that match predicate (defaults to intersects)
        dggrid_gdf = dggrid_gdf[dggrid_gdf.intersects(polyline)]

        try:
            if output_address_type != "SEQNUM":

                def address_transform(
                    dggrid_seqnum, dggal_type, resolution, address_type
                ):
                    address_type_transform = dggrid_instance.address_transform(
                        [dggrid_seqnum],
                        dggs_type=dggs_type,
                        resolution=resolution,
                        mixed_aperture_level=None,
                        input_address_type="SEQNUM",
                        output_address_type=output_address_type,
                    )
                    return address_type_transform.loc[0, address_type]

                dggrid_gdf["name"] = dggrid_gdf["name"].astype(str)
                dggrid_gdf["name"] = dggrid_gdf["name"].apply(
                    lambda val: address_transform(val, dggs_type, resolution, output_address_type)
                )
                dggrid_gdf = dggrid_gdf.rename(columns={"name": output_address_type.lower()})
            else:
                dggrid_gdf = dggrid_gdf.rename(columns={"name": "seqnum"})

        except Exception:
            pass
        # Append the filtered GeoDataFrame to the list
        if include_properties and feature_properties and not dggrid_gdf.empty:
            for key, value in feature_properties.items():
                dggrid_gdf[key] = value
        merged_grids.append(dggrid_gdf)

    # Merge all filtered grids into one GeoDataFrame
    if merged_grids:
        final_grid = gpd.GeoDataFrame(
            pd.concat(merged_grids, ignore_index=True), crs=merged_grids[0].crs
        )
    else:
        final_grid = gpd.GeoDataFrame(columns=["geometry"], crs="EPSG:4326")

    return final_grid


def polygon_to_grid(dggrid_instance, dggs_type, feature, resolution, predicate=None, compact=False, topology=False, include_properties=True, feature_properties=None, output_address_type="SEQNUM"):   
    """
    Generate DGGRID cells intersecting with a given polygon or multipolygon geometry.

    Args:
        dggrid_instance: DGGRIDv7 instance for grid operations.
        dggs_type (str): Type of DGGS (e.g., ISEA4H, FULLER, etc.).
        res (int): Resolution for the DGGRID.
        address_type (str): Address type for the output grid cells.
        geometry (shapely.geometry.Polygon or MultiPolygon): Input geometry.

    Returns:
        geopandas.GeoDataFrame: GeoDataFrame containing DGGRID cells intersecting with the input geometry.
    """ 
    # Initialize an empty list to store filtered grid cells
    merged_grids = []

    # Check the geometry type
    if feature.geom_type == "Polygon":
        # Handle single Polygon
        polygons = [feature]
    elif feature.geom_type == "MultiPolygon":
        # Handle MultiPolygon: process each polygon separately
        polygons = list(feature.geoms)  # Use .geoms to get components of MultiPolygon

    # Process each polygon
    for polygon in polygons:
        # Get bounding box for the current polygon
        bounding_box = box(*feature.bounds)

        # Generate grid cells for the bounding box
        dggrid_gdf = dggrid_instance.grid_cell_polygons_for_extent(
            dggs_type,
            resolution,
            clip_geom=bounding_box,
            split_dateline=True,
            output_address_type=output_address_type,
        )

        # Keep only grid cells that satisfy predicate (defaults to intersects)
        if predicate:
            dggrid_gdf = dggrid_gdf[dggrid_gdf.geometry.apply(lambda cell: check_predicate(cell, feature, predicate))]
        else:
            dggrid_gdf = dggrid_gdf[dggrid_gdf.intersects(feature)]
        try:
            if output_address_type != "SEQNUM":

                def address_transform(
                    dggrid_seqnum, dggal_type, resolution, address_type
                ):
                    address_type_transform = dggrid_instance.address_transform(
                        [dggrid_seqnum],
                        dggs_type=dggs_type,
                        resolution=resolution,
                        mixed_aperture_level=None,
                        input_address_type="SEQNUM",
                        output_address_type=output_address_type,
                    )
                    return address_type_transform.loc[0, address_type]

                dggrid_gdf["name"] = dggrid_gdf["name"].astype(str)
                dggrid_gdf["name"] = dggrid_gdf["name"].apply(
                    lambda val: address_transform(val, dggs_type, resolution, output_address_type)
                )
                dggrid_gdf = dggrid_gdf.rename(columns={"name": output_address_type.lower()})
            else:
                dggrid_gdf = dggrid_gdf.rename(columns={"name": "seqnum"})

        except Exception:
            pass

        # Append the filtered GeoDataFrame to the list
        if include_properties and feature_properties and not dggrid_gdf.empty:
            for key, value in feature_properties.items():
                dggrid_gdf[key] = value
        merged_grids.append(dggrid_gdf)

    # Merge all filtered grids into one GeoDataFrame
    if merged_grids:
        final_grid = gpd.GeoDataFrame(
            pd.concat(merged_grids, ignore_index=True), crs=merged_grids[0].crs
        )
    else:
        final_grid = gpd.GeoDataFrame(columns=["geometry"], crs="EPSG:4326")

    return final_grid


def geometry2dggrid(
    dggrid_instance,
    dggs_type,
    geometries,
    resolution=None,
    properties_list=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
    output_address_type="SEQNUM",
):
    """
    Convert a list of geometries to DGGRID grid cells. Mirrors geometry2isea4t pattern.
    """
    dggs_type = validate_dggrid_type(dggs_type)
    resolution = validate_dggrid_resolution(dggs_type, resolution)

    # Normalize inputs
    if not isinstance(geometries, list):
        geometries = [geometries]

    if properties_list is None:
        properties_list = [{} for _ in geometries]
    elif not isinstance(properties_list, list):
        properties_list = [properties_list for _ in geometries]

    # Optionally collect combined geometries for topology (placeholder; no resolution auto-adjust here)
    all_points = None
    all_polylines = None
    all_polygons = None
    if topology:
        from shapely.geometry import MultiPoint, MultiLineString, MultiPolygon
        points_list = []
        polylines_list = []
        polygons_list = []
        for geom in geometries:
            if geom is None:
                continue
            if geom.geom_type == "Point":
                points_list.append(geom)
            elif geom.geom_type == "MultiPoint":
                points_list.extend(list(geom.geoms))
            elif geom.geom_type == "LineString":
                polylines_list.append(geom)
            elif geom.geom_type == "MultiLineString":
                polylines_list.extend(list(geom.geoms))
            elif geom.geom_type == "Polygon":
                polygons_list.append(geom)
            elif geom.geom_type == "MultiPolygon":
                polygons_list.extend(list(geom.geoms))
        if points_list:
            all_points = MultiPoint(points_list)
        if polylines_list:
            all_polylines = MultiLineString(polylines_list)
        if polygons_list:
            all_polygons = MultiPolygon(polygons_list)

    all_cells = []
    for idx, geom in tqdm(enumerate(geometries), desc="Processing features", total=len(geometries)):
        if geom is None:
            continue
        props = properties_list[idx] if properties_list and idx < len(properties_list) else {}
        if not include_properties:
            props = {}

        if geom.geom_type == "Point":
            gdf = point_to_grid(
                dggrid_instance, dggs_type, geom, resolution, predicate, compact, topology, include_properties, props,output_address_type
            )
            if not gdf.empty:
                all_cells.append(gdf)
        elif geom.geom_type == "MultiPoint":
            for pt in geom.geoms:
                gdf = point_to_grid(
                    dggrid_instance, dggs_type, pt, resolution,  predicate, compact, topology, include_properties, props,output_address_type
                )
                if not gdf.empty:
                    all_cells.append(gdf)
        elif geom.geom_type in ["LineString", "MultiLineString"]:
            gdf = polyline_to_grid(
                dggrid_instance, dggs_type, geom, resolution, predicate, compact, topology, include_properties, props,output_address_type
            )
            if not gdf.empty:
                all_cells.append(gdf)
        elif geom.geom_type in ["Polygon", "MultiPolygon"]:
            gdf = polygon_to_grid(
                dggrid_instance, dggs_type, geom, resolution, predicate, compact, topology, include_properties, props,output_address_type
            )
            if not gdf.empty:
                all_cells.append(gdf)

    if all_cells:
        final_gdf = gpd.GeoDataFrame(
            pd.concat(all_cells, ignore_index=True), crs=all_cells[0].crs
        )
    else:
        final_gdf = gpd.GeoDataFrame(columns=["geometry"], crs="EPSG:4326")
    return final_gdf


def geodataframe2dggrid(
    dggrid_instance,
    dggs_type,
    gdf,
    resolution=None,                            
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
    output_address_type="SEQNUM"    
):
    """
    Convert a GeoDataFrame to DGGRID grid cells using geometry2dggrid.
    """
    geometries = []
    properties_list = []
    for _, row in gdf.iterrows():
        geom = row.geometry
        if geom is not None:
            geometries.append(geom)
            props = row.drop(labels=["geometry"]).to_dict() if include_properties else {}
            properties_list.append(props)

    return geometry2dggrid(
        dggrid_instance,
        dggs_type,
        geometries,
        resolution,
        properties_list,
        predicate,
        compact,
        topology,
        include_properties,
        output_address_type
    )


def dataframe2dggrid(
    dggrid_instance,
    dggs_type,
    df,
    resolution=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
    output_address_type="SEQNUM"    
):
    geometries = []
    properties_list = []
    for _, row in df.iterrows():
        geom = row.geometry if "geometry" in row else row["geometry"]
        if geom is not None:
            geometries.append(geom)
            props = row.to_dict()
            if "geometry" in props:
                del props["geometry"]
            if not include_properties:
                props = {}
            properties_list.append(props)
    return geometry2dggrid(
        dggrid_instance,
        dggs_type,
        geometries,
        resolution,
        properties_list,
        predicate,
        compact,
        topology,
        include_properties,
        output_address_type
    )


def vector2dggrid(
    dggrid_instance,
    dggs_type,
    vector_data,           
    resolution=None,
    predicate=None, 
    compact=False,
    topology=False,
    include_properties=True,
    output_address_type="SEQNUM",
    output_format="gpd",
    **kwargs,
):
    """
    Convert vector data to DGGRID grid cells from various input formats.
    If output_format is a file-based format (csv, geojson, shapefile, gpkg, parquet, geoparquet),
    the output will be saved to a file in the current directory with a default name based on the input.
    Otherwise, returns a Python object (GeoDataFrame, dict, etc.) depending on output_format.
    
    Args:
        data: Input data (file path, URL, GeoDataFrame, GeoJSON, etc.)
        dggrid_instance: DGGRIDv7 instance for grid operations.
        dggs_type: DGGS type (e.g., ISEA4H, FULLER, etc.)
        resolution: Resolution for the DGGRID
        address_type: Output address type (default: SEQNUM)
        output_format: Output format (gpd, geojson, csv, etc.)
        include_properties: Whether to include original feature properties
        **kwargs: Additional arguments passed to process_input_data_vector
        
    Returns:
        GeoDataFrame or file path depending on output_format
    """
    dggs_type = validate_dggrid_type(dggs_type)
    resolution = validate_dggrid_resolution(dggs_type, resolution)
    
    gdf = process_input_data_vector(vector_data, **kwargs)
    result = geodataframe2dggrid(
            dggrid_instance, dggs_type,gdf, resolution, predicate, compact, topology, include_properties, output_address_type
    )                     
        
    output_name = None
    if output_format in OUTPUT_FORMATS:
        if isinstance(vector_data, str):
            base = os.path.splitext(os.path.basename(vector_data))[0]
            output_name = f"{base}2dggrid_{dggs_type}_{resolution}"
        else:
            output_name = f"dggrid_{dggs_type}_{resolution}"
    
    return convert_to_output_format(result, output_format, output_name)
    # return result

def vector2dggrid_cli():        
    parser = argparse.ArgumentParser(description="Convert vector data to DGGRID grid cells")
    parser.add_argument("-i", "--input", help="Input file path or URL")
    parser.add_argument(
        "-dggs",
        dest="dggs_type",
        type=str,
        required=True,
        choices=DGGRID_TYPES.keys(),
        help="DGGRID DGGS type",
    )
    parser.add_argument(
        "-r",
        "--resolution",
        type=int,
        required=True,
        help="Resolution (integer)",
    )  
    parser.add_argument(
        "-p",
        "--predicate",
        choices=["intersect", "within", "centroid_within", "largest_overlap"],
        help="Spatial predicate for polygon conversion",
    )
    parser.add_argument(
        "-c",
        "--compact",
        action="store_true",
        help="Use compact grid generation",
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
        "-a",
        "--output_address_type",
        choices=output_address_types,
        default="SEQNUM",
        nargs="?",  # This makes the argument optional
        help="Select an output address type from the available options.",
    )

    parser.add_argument(
        "-f",
        "--output_format",
        type=str,
        choices=OUTPUT_FORMATS,
        default="gpd",
    )
    args = parser.parse_args()      
    dggrid_instance = create_dggrid_instance()
    
    try:
        result = vector2dggrid(
            dggrid_instance=dggrid_instance,        
            dggs_type=args.dggs_type,
            vector_data=args.input,
            resolution=args.resolution,
            predicate=args.predicate,
            compact=args.compact,
            topology=args.topology,
            include_properties=args.include_properties,
            output_address_type=args.output_address_type,       
            output_format=args.output_format,
        )
        if args.output_format in STRUCTURED_FORMATS:
            print(result)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    vector2dggrid_cli()

