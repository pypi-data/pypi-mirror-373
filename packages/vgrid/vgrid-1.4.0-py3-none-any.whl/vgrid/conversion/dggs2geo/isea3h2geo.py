"""
ISEA3H to Geographic Coordinate Conversion Module

This module provides functionality to convert ISEA3H (Icosahedral Snyder Equal Area 
Aperture 3 Hexagon) cell IDs to geographic coordinates and various geometric 
representations. ISEA3H is a hierarchical DGGS that uses hexagonal cells with 
aperture 3 refinement.

The module includes functions to:
- Convert ISEA3H cell IDs to Shapely Polygon objects
- Convert ISEA3H cell IDs to GeoJSON FeatureCollection format
- Provide command-line interfaces for both conversion types
- Calculate cell properties including area, perimeter, and edge lengths

Key Functions:
    isea3h2geo: Convert ISEA3H cell IDs to Shapely Polygons
    isea3h2geojson: Convert ISEA3H cell IDs to GeoJSON FeatureCollection
    isea3h2geo_cli: Command-line interface for polygon conversion
    isea3h2geojson_cli: Command-line interface for GeoJSON conversion

Note: This module is only supported on Windows systems due to OpenEaggr dependency.
"""

import json, argparse
from shapely.geometry import mapping
import platform
if platform.system() == "Windows":
    from vgrid.dggs.eaggr.eaggr import Eaggr
    from vgrid.dggs.eaggr.shapes.dggs_cell import DggsCell
    from vgrid.dggs.eaggr.enums.model import Model
    from vgrid.utils.constants import ISEA3H_ACCURACY_RES_DICT
    isea3h_dggs = Eaggr(Model.ISEA3H)

from vgrid.utils.geometry import isea3h_cell_to_polygon
from pyproj import Geod
geod = Geod(ellps="WGS84")


def isea3h2geo(isea3h_ids):
    """
    Convert a list of ISEA3H cell IDs to Shapely geometry objects.
    Accepts a single isea3h_id (string) or a list of isea3h_ids.
    Skips invalid or error-prone cells.
    Returns a list of Shapely Polygon objects, or a single Polygon if only one input.
    """
    if isinstance(isea3h_ids, str):
        isea3h_ids = [isea3h_ids]
    isea3h_polygons = []
    for isea3h_id in isea3h_ids:
        try:
            isea3h_cell = DggsCell(isea3h_id)
            cell_polygon = isea3h_cell_to_polygon(isea3h_cell)
            isea3h_polygons.append(cell_polygon)
        except Exception:
            continue
    if len(isea3h_polygons) == 1 :
        return isea3h_polygons[0]
    return isea3h_polygons


def isea3h2geo_cli():
    """
    Command-line interface for isea3h2geo supporting multiple ISEA3H cell IDs.
    """
    parser = argparse.ArgumentParser(
        description="Convert ISEA3H cell ID(s) to Shapely Polygons"
    )
    parser.add_argument(
        "isea3h",
        nargs="+",
        help="Input ISEA3H cell ID(s), e.g., isea3h2geo 1327916769,-55086 ...",
    )
    args = parser.parse_args()
    if platform.system() == "Windows":
        polys = isea3h2geo(args.isea3h)
        return polys
    else:
        print("ISEA3H is only supported on Windows systems")


def isea3h2geojson(isea3h_ids):
    if isinstance(isea3h_ids, str):
        isea3h_ids = [isea3h_ids]
    features = []
    for isea3h_id in isea3h_ids:
        try:
            isea3h_cell = DggsCell(isea3h_id)
            cell_polygon = isea3h_cell_to_polygon(isea3h_cell)
            cell_centroid = cell_polygon.centroid
            center_lat = round(cell_centroid.y, 7)
            center_lon = round(cell_centroid.x, 7)
            cell_area = round(abs(geod.geometry_area_perimeter(cell_polygon)[0]), 3)
            cell_perimeter = abs(geod.geometry_area_perimeter(cell_polygon)[1])
            isea3h2point = isea3h_dggs.convert_dggs_cell_to_point(isea3h_cell)
            cell_accuracy = isea3h2point._accuracy
            avg_edge_len = cell_perimeter / 6
            cell_resolution = ISEA3H_ACCURACY_RES_DICT.get(cell_accuracy)
            if cell_resolution == 0:
                avg_edge_len = cell_perimeter / 3
            if cell_accuracy == 0.0:
                if round(avg_edge_len, 2) == 0.06:
                    cell_resolution = 33
                elif round(avg_edge_len, 2) == 0.03:
                    cell_resolution = 34
                elif round(avg_edge_len, 2) == 0.02:
                    cell_resolution = 35
                elif round(avg_edge_len, 2) == 0.01:
                    cell_resolution = 36
                elif round(avg_edge_len, 3) == 0.007:
                    cell_resolution = 37
                elif round(avg_edge_len, 3) == 0.004:
                    cell_resolution = 38
                elif round(avg_edge_len, 3) == 0.002:
                    cell_resolution = 39
                elif round(avg_edge_len, 3) <= 0.001:
                    cell_resolution = 40
            feature = {
                "type": "Feature",
                "geometry": mapping(cell_polygon),
                "properties": {
                    "isea3h": isea3h_id,
                    "resolution": cell_resolution,
                    "center_lat": center_lat,
                    "center_lon": center_lon,
                    "avg_edge_len": round(avg_edge_len, 3),
                    "cell_area": cell_area,
                },
            }
            features.append(feature)
        except Exception:
            continue
    feature_collection = {"type": "FeatureCollection", "features": features}
    return feature_collection


def isea3h2geojson_cli():
    """
    Command-line interface for isea3h2geojson supporting multiple ISEA3H cell IDs.
    """
    parser = argparse.ArgumentParser(description="Convert ISEA3H ID(s) to GeoJSON")
    parser.add_argument(
        "isea3h",
        nargs="+",
        help="Input ISEA3H cell ID(s), e.g., isea3h2geojson 1327916769,-55086 ...",
    )
    args = parser.parse_args()
    if platform.system() == "Windows":
        geojson_data = json.dumps(isea3h2geojson(args.isea3h))
        print(geojson_data)
    else:
        print("ISEA3H is only supported on Windows systems")