"""
DGGAL Grid Conversion Module

This module provides comprehensive functionality for converting vector geometries to DGGAL (Discrete Global Grid System) grid cells.
DGGAL supports multiple DGGS types including ISEA3H, ISEA4T, ISEA7H, ISEA9H, and others, each with their own
resolution ranges and cell characteristics. The module uses the external `dgg` CLI tool for grid generation.

Key Features:
- Convert points, lines, and polygons to DGGAL grid cells
- Support for multiple input formats (files, URLs, DataFrames, GeoDataFrames, GeoJSON)
- Multiple spatial predicates for polygon conversion ('intersect', 'within', 'centroid_within', 'largest_overlap')
- DGGAL compact mode to reduce cell count for polygons and lines
- Multiple output formats (GeoJSON, GPKG, Parquet, CSV, Shapefile)
- Command-line interface for batch processing
- Support for various DGGAL types (ISEA3H, ISEA4T, ISEA7H, ISEA9H, etc.)

Functions:
- point2dggal: Convert point geometries to DGGAL cells
- polyline2dggal: Convert line geometries to DGGAL cells
- polygon2dggal: Convert polygon geometries to DGGAL cells with spatial predicates
- geometry2dggal: Convert list of geometries to DGGAL cells
- vector2dggal: Main function for converting various input formats to DGGAL cells
- vector2dggal_cli: Command-line interface for batch processing

The module uses the external `dgg` CLI tool for grid generation and supports
both individual geometry conversion and batch processing of entire datasets.
"""

from __future__ import annotations

import argparse
import sys
import geopandas as gpd 
import pandas as pd

from vgrid.utils.io import process_input_data_vector, convert_to_output_format
from vgrid.utils.constants import OUTPUT_FORMATS, STRUCTURED_FORMATS, DGGAL_TYPES
from vgrid.utils.geometry import check_predicate
from vgrid.conversion.latlon2dggs import latlon2dggal
from vgrid.conversion.dggs2geo.dggal2geo import dggal2geojson
from vgrid.generator.dggalgen import dggalgrid
from vgrid.conversion.dggscompact.dggalcompact import dggalcompact


def point2dggal(
    dggs_type: str | None = None,
    feature=None,
    resolution=None,
    feature_properties=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
    all_points=None,
):
    if feature is None:
        return gpd.GeoDataFrame(columns=["geometry"], crs="EPSG:4326")
    # Compute ZoneID directly for the point, then fetch its geometry
    lat = float(feature.y)
    lon = float(feature.x)
    zone_id = latlon2dggal(dggs_type, lat, lon, resolution)
    fc = dggal2geojson(dggs_type, zone_id)
    features = fc.get("features")
    gdf = gpd.GeoDataFrame.from_features(features, crs="EPSG:4326")
    if include_properties and feature_properties and not gdf.empty:
        try:
            gdf = gdf.assign(**feature_properties)
        except Exception:
            pass
    return gdf


def polyline2dggal(
    dggs_type: str | None = None,
    feature=None,
    resolution=None,
    feature_properties=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
    all_polylines=None,
):
    if feature is None:
        return []
    # Convert bounds from (minx, miny, maxx, maxy) to (min_lat, min_lon, max_lat, max_lon)
    bounds = feature.bounds  # (minx, miny, maxx, maxy) where x=lon, y=lat
    bbox = (bounds[1], bounds[0], bounds[3], bounds[2])  # (min_lat, min_lon, max_lat, max_lon)
    gdf = dggalgrid(dggs_type, resolution, bbox=bbox, compact=False, output_format="gpd")    
    # Filter by simple intersects only
    try:
        selected = gdf[gdf.intersects(feature)]
    except Exception:
        selected = gdf
    # Vectorized attach of properties if requested
    if include_properties and feature_properties and isinstance(selected, gpd.GeoDataFrame) and not selected.empty:
        try:
            selected = selected.assign(**feature_properties)
        except Exception:
            pass
    return selected


def polygon2dggal(
    dggs_type: str | None = None,
    feature=None,
    resolution=None,
    feature_properties=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
    all_polygons=None,
):
    if feature is None:
        return []   
    # Convert bounds from (minx, miny, maxx, maxy) to (min_lat, min_lon, max_lat, max_lon)
    bounds = feature.bounds  # (minx, miny, maxx, maxy) where x=lon, y=lat
    bbox = (bounds[1], bounds[0], bounds[3], bounds[2])  # (min_lat, min_lon, max_lat, max_lon)
    gdf = dggalgrid(dggs_type, resolution,  bbox=bbox, compact=False, output_format="gpd")
    # Apply predicate locally; default to intersects
    if predicate:
        try:
            selected = gdf[gdf.geometry.apply(lambda g: check_predicate(g, feature, predicate))]
        except Exception:
            selected = gdf
    else:
        try:
            selected = gdf[gdf.intersects(feature)]
        except Exception:
            selected = gdf
    if include_properties and feature_properties and isinstance(selected, gpd.GeoDataFrame) and not selected.empty:
        try:
            selected = selected.assign(**feature_properties)
        except Exception:
            pass    
    if compact:
        selected = dggalcompact(dggs_type, selected, output_format="gpd")
    return selected


def geometry2dggal(
    dggs_type: str,
    geometries, 
    resolution=None,
    properties_list=None,
    predicate=None,
    compact=False,
    topology=False,
    include_properties=True,
):
    if resolution is None and not topology:
        raise ValueError("resolution parameter is required when topology=False")
    if not isinstance(geometries, list):
        geometries = [geometries]
    if properties_list is None:
        properties_list = [{} for _ in geometries]
    elif not isinstance(properties_list, list):
        properties_list = [properties_list for _ in geometries]

    gdfs = []
    for idx, geom in enumerate(geometries):
        if geom is None:
            continue
        props = properties_list[idx] if include_properties else {}
        if geom.geom_type == "Point":
            selected = point2dggal(dggs_type=dggs_type, feature=geom, resolution=resolution, feature_properties=props, compact=compact)
            if isinstance(selected, gpd.GeoDataFrame) and not selected.empty:
                gdfs.append(selected)
        elif geom.geom_type == "MultiPoint":
            for pt in geom.geoms:
                selected = point2dggal(dggs_type=dggs_type, feature=pt, resolution=resolution, feature_properties=props, compact=compact)
                if isinstance(selected, gpd.GeoDataFrame) and not selected.empty:
                    gdfs.append(selected)
        elif geom.geom_type in ("LineString", "MultiLineString"):
            selected = polyline2dggal(dggs_type=dggs_type, feature=geom, resolution=resolution, feature_properties=props, predicate=predicate, compact=compact)
            if isinstance(selected, gpd.GeoDataFrame) and not selected.empty:
                gdfs.append(selected)
        elif geom.geom_type in ("Polygon", "MultiPolygon"):
            selected = polygon2dggal(dggs_type=dggs_type, feature=geom, resolution=resolution, feature_properties=props, predicate=predicate, compact=compact)
            if isinstance(selected, gpd.GeoDataFrame) and not selected.empty:
                gdfs.append(selected)
    if gdfs:
        return gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True), geometry="geometry", crs="EPSG:4326")
    else:
        return gpd.GeoDataFrame(columns=["geometry"], crs="EPSG:4326")

def vector2dggal(
    dggs_type: str,
    vector_data,       
    resolution: int,
    predicate: str | None = None,
    compact: bool = False,
    topology: bool = False,
    include_properties: bool = True,
    output_format: str = "gpd",
    **kwargs,
):
    """
    Convert vector data to DGGAL grid cells for a given type and resolution.

    - data: file path/URL/GeoDataFrame/GeoJSON/etc. (see process_input_data_vector)
    - dggs_type: one of DGGAL_TYPES
    - resolution: integer resolution
    - compact: pass -compact to dgg CLI
    - output_format: OUTPUT_FORMATS
    """
    gdf_input = process_input_data_vector(vector_data, **kwargs)   

    # Build GeoDataFrames per geometry type and concatenate for performance
    gdfs = []
    for _, row in gdf_input.iterrows():
        geom = row.geometry
        if geom is None:
            continue
        props = row.drop(labels=[c for c in row.index if c == "geometry"], errors="ignore").to_dict()
        if geom.geom_type == "Point":
            selected = point2dggal(
                dggs_type=dggs_type,
                feature=geom,
                resolution=resolution,
                feature_properties=props,
                compact=compact,
                topology=topology,
                include_properties=include_properties,
            )
            if isinstance(selected, gpd.GeoDataFrame) and not selected.empty:
                gdfs.append(selected)
        elif geom.geom_type == "MultiPoint":
            for pt in geom.geoms:
                selected = point2dggal(
                    dggs_type=dggs_type,
                    feature=pt,
                    resolution=resolution,
                    feature_properties=props,
                    compact=compact,
                    topology=topology,
                    include_properties=include_properties,
                )
                if isinstance(selected, gpd.GeoDataFrame) and not selected.empty:
                    gdfs.append(selected)
        elif geom.geom_type in ("LineString", "MultiLineString"):
            selected = polyline2dggal(
                dggs_type=dggs_type,
                feature=geom,
                resolution=resolution,
                feature_properties=props,
                predicate=predicate,
                compact=compact,
                topology=topology,
                include_properties=include_properties,
            )
            if isinstance(selected, gpd.GeoDataFrame) and not selected.empty:
                gdfs.append(selected)
        elif geom.geom_type in ("Polygon", "MultiPolygon"):
            selected = polygon2dggal(
                dggs_type=dggs_type,
                feature=geom,
                resolution=resolution,
                feature_properties=props,
                predicate=predicate,
                compact=compact,
                topology=topology,
                include_properties=include_properties
            )
            if isinstance(selected, gpd.GeoDataFrame) and not selected.empty:
                gdfs.append(selected)

    if gdfs:
        merged = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True), geometry="geometry", crs="EPSG:4326")
    else:
        merged = gpd.GeoDataFrame(columns=["geometry"], crs="EPSG:4326")

    # Return or export
    output_name = None
    if output_format in OUTPUT_FORMATS:
        # File outputs: prefer a stable name like <type>_grid_<res>
        output_name = f"{dggs_type}_grid_{resolution}"
    return convert_to_output_format(merged, output_format, output_name)


def vector2dggal_cli():
    parser = argparse.ArgumentParser(description="Convert vector data to DGGAL grid cells")
    parser.add_argument("-i", "--input", help="Input file path or URL")
    parser.add_argument(
        "-dggs",
        dest="dggs_type",
        type=str,
        required=True,
        choices=DGGAL_TYPES.keys(),
        help="DGGAL DGGS type",
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
        "-f",
        "--output_format",
        type=str,
        choices=OUTPUT_FORMATS,
        default="gpd",
    )
    args = parser.parse_args()

    try:
        result = vector2dggal(
            dggs_type=args.dggs_type,
            vector_data=args.input,
            resolution=args.resolution,
            predicate=args.predicate,
            compact=args.compact,
            topology=args.topology,
            include_properties=args.include_properties,
            output_format=args.output_format,
        )
        if args.output_format in STRUCTURED_FORMATS:
            print(result)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    vector2dggal_cli()


