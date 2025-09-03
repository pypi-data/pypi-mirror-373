"""
Convert Quadkey identifiers to geographic geometries.

This module provides functionality to convert Quadkey identifiers to Shapely geometry objects
and GeoJSON features. Quadkeys are hierarchical spatial identifiers used in mapping systems
like Bing Maps and other tile-based mapping services.

Functions:
    quadkey2geo: Convert Quadkey IDs to Shapely Polygon objects
    quadkey2geojson: Convert Quadkey IDs to GeoJSON FeatureCollection
    quadkey2geo_cli: Command-line interface for quadkey2geo
    quadkey2geojson_cli: Command-line interface for quadkey2geojson
"""

import json
import argparse
from shapely.geometry import Polygon
from vgrid.dggs import mercantile
from vgrid.utils.geometry import graticule_dggs_to_feature

def quadkey2geo(quadkey_ids):
    """
    Convert a list of Quadkey cell IDs to Shapely geometry objects.
    Accepts a single quadkey_id (string) or a list of quadkey_ids.
    Skips invalid or error-prone cells.
    Returns a list of Shapely Polygon objects, or a single Polygon if only one input.
    """
    if isinstance(quadkey_ids, str):
        quadkey_ids = [quadkey_ids]
    quadkey_polygons = []
    for quadkey_id in quadkey_ids:
        try:
            tile = mercantile.quadkey_to_tile(quadkey_id)
            z = tile.z
            x = tile.x
            y = tile.y
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
            quadkey_polygons.append(cell_polygon)
        except Exception:
            continue
    if len(quadkey_polygons) == 1:
        return quadkey_polygons[0]
    return quadkey_polygons


def quadkey2geo_cli():
    """
    Command-line interface for quadkey2geo supporting multiple Quadkeys.
    """
    parser = argparse.ArgumentParser(
        description="Convert Quadkey(s) to Shapely Polygons"
    )
    parser.add_argument(
        "quadkey", nargs="+", help="Input Quadkey(s), e.g. 13223011131020220011133 ..."
    )
    args = parser.parse_args()
    polys = quadkey2geo(args.quadkey)
    return polys


def quadkey2geojson(quadkey_ids):
    if isinstance(quadkey_ids, str):
        quadkey_ids = [quadkey_ids]
    quadkey_features = []
    for quadkey_id in quadkey_ids:
        try:
            tile = mercantile.quadkey_to_tile(quadkey_id)
            z = tile.z
            x = tile.x
            y = tile.y
            bounds = mercantile.bounds(x, y, z)
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
                quadkey_feature = graticule_dggs_to_feature(
                    "quadkey", quadkey_id, resolution, cell_polygon
                )
                quadkey_features.append(quadkey_feature)
        except Exception:
            continue
    return {"type": "FeatureCollection", "features": quadkey_features}

def quadkey2geojson_cli():
    """
    Command-line interface for quadkey2geojson supporting multiple Quadkeys.
    """
    parser = argparse.ArgumentParser(description="Convert Quadkey(s) to GeoJSON")
    parser.add_argument(
        "quadkey", nargs="+", help="Input Quadkey(s), e.g. 13223011131020220011133 ..."
    )
    args = parser.parse_args()
    geojson_data = json.dumps(quadkey2geojson(args.quadkey))
    print(geojson_data)
