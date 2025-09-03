"""
Tilecode to Geographic Conversion Module

This module provides functionality to convert Tilecode identifiers to geographic
representations. Tilecodes are hierarchical spatial identifiers in the format
'z{x}x{y}y{z}' where z is the zoom level and x,y are tile coordinates.

Functions:
    tilecode2: Convert Tilecode IDs to Shapely Polygon objects
    tilecode2geojson: Convert Tilecode IDs to GeoJSON FeatureCollection
    tilecode2geo_cli: Command-line interface for tilecode2eo
    tilecode2geojson_cli: Command-line interface for tilecode2geojson
"""

import json
import re
import argparse
from shapely.geometry import Polygon
from vgrid.dggs import mercantile
from vgrid.utils.geometry import graticule_dggs_to_feature


def tilecode2geo(tilecode_ids):
    """
    Convert a list of Tilecode cell IDs to Shapely geometry objects.
    Accepts a single tilecode_id (string) or a list of tilecode_ids.
    Skips invalid or error-prone cells.
    Returns a list of Shapely Polygon objects, or a single Polygon if only one input.
    """
    if isinstance(tilecode_ids, str):
        tilecode_ids = [tilecode_ids]
    tilecode_polygons = []
    for tilecode_id in tilecode_ids:
        try:
            match = re.match(r"z(\d+)x(\d+)y(\d+)", tilecode_id)
            if not match:
                continue
            z = int(match.group(1))
            x = int(match.group(2))
            y = int(match.group(3))
            bounds = mercantile.bounds(x, y, z)
            min_lat, min_lon = bounds.south, bounds.west
            max_lat, max_lon = bounds.north, bounds.east
            cell_polygon = Polygon(
                [
                    [min_lon, min_lat],
                    [max_lon, min_lat],
                    [max_lon, max_lat],
                    [min_lon, max_lat],
                    [min_lon, min_lat],
                ]
            )
            tilecode_polygons.append(cell_polygon)
        except Exception:
            continue
    if len(tilecode_polygons) == 1:
        return tilecode_polygons[0]
    return tilecode_polygons


def tilecode2geo_cli():
    """
    Command-line interface for tilecode2geo supporting multiple Tilecodes.
    """
    parser = argparse.ArgumentParser(
        description="Convert Tilecode(s) to Shapely Polygons"
    )
    parser.add_argument(
        "tilecode_id", nargs="+", help="Input Tilecode(s), e.g. z0x0y0 z1x1y1"
    )
    args = parser.parse_args()
    polys = tilecode2geo(args.tilecode_id)
    return polys


def tilecode2geojson(tilecode_ids):
    if isinstance(tilecode_ids, str):
        tilecode_ids = [tilecode_ids]
    tilecode_features = []
    for tilecode_id in tilecode_ids:
        try:
            match = re.match(r"z(\d+)x(\d+)y(\d+)", tilecode_id)
            if not match:
                continue
            z = int(match.group(1))
            x = int(match.group(2))
            y = int(match.group(3))
            bounds = mercantile.bounds(x, y, z)
            cell_polygon = tilecode2geo(tilecode_id)
            if bounds:
                min_lat, min_lon = bounds.south, bounds.west
                max_lat, max_lon = bounds.north, bounds.east
                cell_polygon = Polygon(
                    [
                        [min_lon, min_lat],
                        [max_lon, min_lat],
                        [max_lon, max_lat],
                        [min_lon, max_lat],
                        [min_lon, min_lat],
                    ]
                )
                resolution = z
                tilecode_feature = graticule_dggs_to_feature(
                    "tilecode_id", tilecode_id, resolution, cell_polygon
                )
                tilecode_features.append(tilecode_feature)
        except Exception:
            continue
    return {"type": "FeatureCollection", "features": tilecode_features}

def tilecode2geojson_cli():
    """
    Command-line interface for tilecode2geojson supporting multiple Tilecodes.
    """
    parser = argparse.ArgumentParser(description="Convert Tilecode(s) to GeoJSON")
    parser.add_argument(
        "tilecode_id", nargs="+", help="Input Tilecode(s), e.g. z0x0y0 z1x1y1"
    )
    args = parser.parse_args()
    geojson_data = json.dumps(tilecode2geojson(args.tilecode_id))
    print(geojson_data)
