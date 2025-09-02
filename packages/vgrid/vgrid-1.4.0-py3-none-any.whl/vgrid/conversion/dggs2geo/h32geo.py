"""
H3 to Geographic Coordinate Conversion Module

This module provides functionality to convert H3 cell IDs to geographic coordinates 
and various geometric representations. H3 is Uber's hexagonal hierarchical spatial 
index that divides the Earth's surface into hexagonal cells of different resolutions.

Key Functions:
    h32geo: Convert H3 cell IDs to Shapely Polygons
    h32geojson: Convert H3 cell IDs to GeoJSON FeatureCollection
    h32geo_cli: Command-line interface for polygon conversion
    h32geojson_cli: Command-line interface for GeoJSON conversion
"""

import json
import argparse
import h3
from shapely.geometry import Polygon
from vgrid.utils.geometry import fix_h3_antimeridian_cells
from vgrid.utils.geometry import geodesic_dggs_to_feature

def h32geo(h3_ids):
    """
    Convert a list of H3 cell IDs to Shapely geometry objects.
    Accepts a single h3_id (string) or a list of h3_ids.
    Skips invalid or error-prone cells.
    Returns a list of Shapely Polygon objects, or a single Polygon if only one input.
    """
    if isinstance(h3_ids, str):
        h3_ids = [h3_ids]
    h3_polygons = []
    for h3_id in h3_ids:
        try:
            cell_boundary = h3.cell_to_boundary(h3_id)
            filtered_boundary = fix_h3_antimeridian_cells(cell_boundary)
            reversed_boundary = [(lon, lat) for lat, lon in filtered_boundary]
            cell_polygon = Polygon(reversed_boundary)
            h3_polygons.append(cell_polygon)
        except Exception:
            continue
    if len(h3_polygons) == 1:
        return h3_polygons[0]
    return h3_polygons

def h32geo_cli():
    """
    Command-line interface for h32geo supporting multiple H3 cell IDs.
    """
    parser = argparse.ArgumentParser(description="Convert H3 cell ID(s) to Shapely Polygons")
    parser.add_argument(
        "h3",
        nargs="+",
        help="Input H3 cell ID(s), e.g., h32geo 8e65b56628e0d07 8e65b56628e6adf",
    )
    args = parser.parse_args()
    polys = h32geo(args.h3)
    return polys


def h32geojson(h3_ids):
    """
    Convert a list of H3 cell IDs to a GeoJSON FeatureCollection.
    Accepts a single h3_id (string) or a list of h3_ids.
    Skips invalid or error-prone cells.
    """
    if isinstance(h3_ids, str):
        h3_ids = [h3_ids]
    h3_features = []
    for h3_id in h3_ids:
        try:
            cell_polygon = h32geo(h3_id)
            resolution = (h3_id)
            num_edges = 6
            if h3.is_pentagon(h3_id):
                num_edges = 5
            h3_feature = geodesic_dggs_to_feature(
                "h3", h3_id, resolution, cell_polygon, num_edges
            )
            h3_features.append(h3_feature)
        except Exception:
            continue
    return {"type": "FeatureCollection", "features": h3_features}


def h32geojson_cli():
    """
    Command-line interface for h32geojson supporting multiple H3 cell IDs.
    """
    parser = argparse.ArgumentParser(description="Convert H3 cell ID(s) to GeoJSON")
    parser.add_argument(
        "h3",
        nargs="+",
        help="Input H3 cell ID(s), e.g., h32geojson 8e65b56628e0d07 8e65b56628e6adf",
    )
    args = parser.parse_args()
    geojson_data = json.dumps(h32geojson(args.h3))
    print(geojson_data)

if __name__ == "__main__":
    h32geojson_cli()