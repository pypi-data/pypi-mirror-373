
"""
S2 to Geographic Coordinate Conversion Module

This module provides functionality to convert S2 cell tokens to geographic coordinates
and various geometric representations. S2 is a hierarchical geospatial indexing system
developed by Google that divides the Earth's surface into cells of different resolutions.

Key Functions:
    s22geo: Convert S2 tokens to Shapely Polygons
    s22geojson: Convert S2 tokens to GeoJSON FeatureCollection
    s22_cli: Command-line interface for polygon conversion
    s22geojson_cli: Command-line interface for GeoJSON conversion
"""

import json
import argparse
from shapely.geometry import Polygon
from vgrid.utils.geometry import geodesic_dggs_to_feature
from vgrid.dggs import s2
from vgrid.utils.antimeridian import fix_polygon

def s22geo(s2_tokens):
    """
    Convert a list of S2 cell tokens to Shapely geometry objects.
    Accepts a single s2_token (string) or a list of s2_tokens.
    Skips invalid or error-prone cells.
    Returns a list of Shapely Polygon objects, or a single Polygon if only one input.
    """
    if isinstance(s2_tokens, str):
        s2_tokens = [s2_tokens]
    s2_polygons = []
    for s2_token in s2_tokens:
        try:
            cell_id = s2.CellId.from_token(s2_token)
            cell = s2.Cell(cell_id)
            vertices = [cell.get_vertex(i) for i in range(4)]
            shapely_vertices = []
            for vertex in vertices:
                lat_lng = s2.LatLng.from_point(vertex)
                longitude = lat_lng.lng().degrees
                latitude = lat_lng.lat().degrees
                shapely_vertices.append((longitude, latitude))
            shapely_vertices.append(shapely_vertices[0])
            cell_polygon = fix_polygon(Polygon(shapely_vertices))
            s2_polygons.append(cell_polygon)
        except Exception:
            continue
    if len(s2_polygons) == 1:
        return s2_polygons[0]
    return s2_polygons


def s22geo_cli():
    """
    Command-line interface for s22geo supporting multiple S2 cell tokens.
    """
    parser = argparse.ArgumentParser(description="Convert S2 cell token(s) to Shapely Polygons")
    parser.add_argument(
        "s2",
        nargs="+",
        help="Input S2 cell token(s), e.g., s22geo 31752f45cc94 31752f45cc95",
    )
    args = parser.parse_args()
    polys = s22geo(args.s2)
    return polys

def s22geojson(s2_tokens):
    """
    Convert a list of S2 cell tokens to a GeoJSON FeatureCollection.
    Accepts a single s2_token (string) or a list of s2_tokens.
    Skips invalid or error-prone cells.
    """
    if isinstance(s2_tokens, str):
        s2_tokens = [s2_tokens]
    s2_features = []
    for s2_token in s2_tokens:
        try:
            cell_id = s2.CellId.from_token(s2_token)
            cell_polygon = s22geo(s2_token)
            resolution = cell_id.level()
            num_edges = 4
            s2_feature = geodesic_dggs_to_feature(
                "s2", s2_token, resolution, cell_polygon, num_edges
            )
            s2_features.append(s2_feature)
        except Exception:
            continue
    return {"type": "FeatureCollection", "features": s2_features}


def s22geojson_cli():
    """
    Command-line interface for s22geojson supporting multiple S2 cell tokens.
    """
    parser = argparse.ArgumentParser(description="Convert S2 cell token(s) to GeoJSON")
    parser.add_argument(
        "s2",
        nargs="+",
        help="Input S2 cell token(s), e.g., s22geojson 31752f45cc94 31752f45cc95",
    )
    args = parser.parse_args()
    geojson_data = json.dumps(s22geojson(args.s2))
    print(geojson_data)