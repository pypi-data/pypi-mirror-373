"""
Maidenhead to Geographic Coordinate Conversion Module

This module provides functionality to convert Maidenhead locator grid cell IDs to 
geographic coordinates and various geometric representations. Maidenhead locators 
are a grid-based coordinate system commonly used in amateur radio for specifying 
geographic locations with high precision.

Key Functions:
    maidenhead2geo: Convert Maidenhead cell IDs to Shapely Polygons
    maidenhead2geojson: Convert Maidenhead cell IDs to GeoJSON FeatureCollection
    maidenhead2geo_cli: Command-line interface for polygon conversion
    maidenhead2geojson_cli: Command-line interface for GeoJSON conversion
"""

import json
import argparse
from shapely.geometry import Polygon
from vgrid.utils.geometry import graticule_dggs_to_feature
from vgrid.dggs import maidenhead

def maidenhead2geo(maidenhead_ids):
    """
    Convert a list of Maidenhead cell IDs to Shapely geometry objects.
    Accepts a single maidenhead_id (string) or a list of maidenhead_ids.
    Skips invalid or error-prone cells.
    Returns a list of Shapely Polygon objects, or a single Polygon if only one input.
    """
    if isinstance(maidenhead_ids, str):
        maidenhead_ids = [maidenhead_ids]
    maidenhead_polygons = []
    for maidenhead_id in maidenhead_ids:
        try:
            _, _, min_lat, min_lon, max_lat, max_lon, _ = maidenhead.maidenGrid(maidenhead_id)
            cell_polygon = Polygon(
                [
                    [min_lon, min_lat],
                    [max_lon, min_lat],
                    [max_lon, max_lat],
                    [min_lon, max_lat],
                    [min_lon, min_lat],
                ]
            )
            maidenhead_polygons.append(cell_polygon)
        except Exception:
            continue
    if len(maidenhead_polygons) == 1:
        return maidenhead_polygons[0]
    return maidenhead_polygons


def maidenhead2geo_cli():
    """
    Command-line interface for maidenhead2geo supporting multiple Maidenhead cell IDs.
    """
    parser = argparse.ArgumentParser(
        description="Convert Maidenhead cell ID(s) to Shapely Polygons"
    )
    parser.add_argument(
        "maidenhead",
        nargs="+",
        help="Input Maidenhead cell ID(s), e.g., maidenhead2geo OK3046.",
    )
    args = parser.parse_args()
    polys = maidenhead2geo(args.maidenhead)
    return polys


def maidenhead2geojson(maidenhead_ids):
    if isinstance(maidenhead_ids, str):
        maidenhead_ids = [maidenhead_ids]
    maidenhead_features = []
    for maidenhead_id in maidenhead_ids:
        try:
            cell_polygon = maidenhead2geo(maidenhead_id)
            resolution = int(len(maidenhead_id) / 2)
            maidenhead_feature = graticule_dggs_to_feature(
                "maidenhead", maidenhead_id, resolution, cell_polygon
            )
            maidenhead_features.append(maidenhead_feature)
        except Exception:
            continue
    return {"type": "FeatureCollection", "features": maidenhead_features}


def maidenhead2geojson_cli():
    """
    Command-line interface for maidenhead2geojson supporting multiple Maidenhead cell IDs.
    """
    parser = argparse.ArgumentParser(
        description="Convert Maidenhead cell ID(s) to GeoJSON"
    )
    parser.add_argument(
        "maidenhead",
        nargs="+",
        help="Input Maidenhead cell ID(s), e.g., maidenhead2geojson OK3046.",
    )
    args = parser.parse_args()
    geojson_data = json.dumps(maidenhead2geojson(args.maidenhead))
    print(geojson_data)