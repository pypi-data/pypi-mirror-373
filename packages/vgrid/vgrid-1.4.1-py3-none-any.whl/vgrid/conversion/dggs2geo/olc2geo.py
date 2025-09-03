"""
Convert OLC/Google Plus Codes to Shapely Polygons

This module provides functionality to convert Open Location Codes (OLC), also known as 
Google Plus Codes, to geometric representations. It supports conversion to both 
Shapely Polygon objects and GeoJSON format.

Functions:
    olc2geo: Convert OLC codes to Shapely Polygon objects
    olc2geojson: Convert OLC codes to GeoJSON FeatureCollection
    olc2geo_cli: Command-line interface for olc2geo
    olc2geojson_cli: Command-line interface for olc2geojson
"""

import json
import argparse
from shapely.geometry import Polygon
from vgrid.utils.geometry import graticule_dggs_to_feature
from vgrid.dggs import olc

def olc2geo(olc_ids):
    """
    Convert a list of OLC (Open Location Code) cell IDs to Shapely geometry objects.
    Accepts a single olc_id (string) or a list of olc_ids.
    Skips invalid or error-prone cells.
    Returns a list of Shapely Polygon objects, or a single Polygon if only one input.
    """
    if isinstance(olc_ids, str):
        olc_ids = [olc_ids]
    olc_polygons = []
    for olc_id in olc_ids:
        try:
            coord = olc.decode(olc_id)
            min_lat, min_lon = coord.latitudeLo, coord.longitudeLo
            max_lat, max_lon = coord.latitudeHi, coord.longitudeHi
            cell_polygon = Polygon(
                [
                    [min_lon, min_lat],
                    [max_lon, min_lat],
                    [max_lon, max_lat],
                    [min_lon, max_lat],
                    [min_lon, min_lat],
                ]
            )
            olc_polygons.append(cell_polygon)
        except Exception:
            continue
    if len(olc_polygons) == 1:
        return olc_polygons[0]
    return olc_polygons


def olc2geo_cli():
    """
    Command-line interface for olc2geo supporting multiple OLC codes.
    """
    parser = argparse.ArgumentParser(
        description="Convert OLC/Google Plus Codes to Shapely Polygons"
    )
    parser.add_argument(
        "olc",
        nargs="+",
        help="Input OLC(s), e.g., olc2geo 7P28QPG4+4P7 7P28QPG4+4P8",
    )
    args = parser.parse_args()
    polys = olc2geo(args.olc)
    return polys


def olc2geojson(olc_ids):
    if isinstance(olc_ids, str):
        olc_ids = [olc_ids]
    olc_features = []
    for olc_id in olc_ids:
        try:
            cell_polygon = olc2geo(olc_id)
            coord = olc.decode(olc_id) 
            resolution = coord.codeLength
            olc_feature = graticule_dggs_to_feature(
                "olc", olc_id, resolution, cell_polygon
            )
            olc_features.append(olc_feature)
        except Exception:
            continue
    return {"type": "FeatureCollection", "features": olc_features}


def olc2geojson_cli():
    """
    Command-line interface for olc2geojson supporting multiple OLC codes.
    """
    parser = argparse.ArgumentParser(
        description="Convert OLC/ Google Plus Codes to GeoJSON"
    )
    parser.add_argument(
        "olc",
        nargs="+",
        help="Input OLC(s), e.g., olc2geojson 7P28QPG4+4P7 7P28QPG4+4P8",
    )
    args = parser.parse_args()
    geojson_data = json.dumps(olc2geojson(args.olc))
    print(geojson_data)