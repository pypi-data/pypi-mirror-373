"""
QTM (Ternary Triangular Mesh) to Geographic Conversion Module.

This module provides functionality to convert QTM cell IDs to geographic representations
including Shapely geometry objects and GeoJSON features. QTM is a hierarchical triangular
mesh system based on an octahedron that tessellates the globe.

Functions:
    qtm2geo: Convert QTM cell IDs to Shapely Polygon objects
    qtm2geojson: Convert QTM cell IDs to GeoJSON FeatureCollection
    qtm2geo_cli: Command-line interface for qtm2geo
    qtm2geojson_cli: Command-line interface for qtm2geojson

"""

import json
import argparse
from vgrid.dggs.qtm import constructGeometry, qtm_id_to_facet
from vgrid.utils.geometry import geodesic_dggs_to_feature

def qtm2geo(qtm_ids):
    """
    Convert a list of QTM cell IDs to Shapely geometry objects.
    Accepts a single qtm_id (string) or a list of qtm_ids.
    Skips invalid or error-prone cells.
    Returns a list of Shapely Polygon objects, or a single Polygon if only one input.
    """
    if isinstance(qtm_ids, str):
        qtm_ids = [qtm_ids]
    qtm_polygons = []
    for qtm_id in qtm_ids:
        try:
            facet = qtm_id_to_facet(qtm_id)
            cell_polygon = constructGeometry(facet)
            qtm_polygons.append(cell_polygon)
        except Exception:
            continue
    if len(qtm_polygons) == 1:
        return qtm_polygons[0]
    return qtm_polygons


def qtm2geo_cli():
    """
    Command-line interface for qtm2geo supporting multiple QTM cell IDs.
    """
    parser = argparse.ArgumentParser(
        description="Convert QTM cell ID(s) to Shapely Polygons"
    )
    parser.add_argument(
        "qtm",
        nargs="+",
        help="Input QTM cell ID(s), e.g., qtm2geo 42012321 42012322",
    )
    args = parser.parse_args()
    polys = qtm2geo(args.qtm)
    return polys


def qtm2geojson(qtm_ids):
    """
    Convert a list of QTM cell IDs to a GeoJSON FeatureCollection.
    Accepts a single qtm_id (string) or a list of qtm_ids.
    Skips invalid or error-prone cells.
    """
    if isinstance(qtm_ids, str):
        qtm_ids = [qtm_ids]
    qtm_features = []
    for qtm_id in qtm_ids:
        try:
            cell_polygon = qtm2geo(qtm_id)
            resolution = len(qtm_id)
            num_edges = 3
            qtm_feature = geodesic_dggs_to_feature(
                "qtm", qtm_id, resolution, cell_polygon, num_edges
            )
            qtm_features.append(qtm_feature)
        except Exception:
            continue
    return {"type": "FeatureCollection", "features": qtm_features}


def qtm2geojson_cli():
    """
    Command-line interface for qtm2geojson supporting multiple QTM cell IDs.
    """
    parser = argparse.ArgumentParser(description="Convert QTM cell ID(s) to GeoJSON")
    parser.add_argument(
        "qtm",
        nargs="+",
        help="Input QTM cell ID(s), e.g., qtm2geojson 42012321 42012322",
    )
    args = parser.parse_args()
    geojson_data = json.dumps(qtm2geojson(args.qtm))
    print(geojson_data)