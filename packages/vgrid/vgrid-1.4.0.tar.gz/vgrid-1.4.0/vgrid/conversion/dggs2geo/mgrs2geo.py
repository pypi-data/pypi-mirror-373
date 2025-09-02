"""
Convert MGRS grid cell IDs to Shapely Polygons and GeoJSON.

This module provides functions to convert MGRS (Military Grid Reference System)
cell IDs to Shapely geometry objects and GeoJSON features. MGRS is a grid system
used by the military for geographic coordinate reference.

Key Functions:
    mgrs2geo: Convert MGRS IDs to Shapely Polygon objects
    mgrs2geojson: Convert MGRS IDs to GeoJSON FeatureCollection
    mgrs2geo_cli: Command-line interface for mgrs2geo
    mgrs2geojson_cli: Command-line interface for mgrs2geojson
"""

import json
import os
import argparse
from shapely.geometry import Polygon, shape
from vgrid.utils.geometry import graticule_dggs_to_feature
from vgrid.dggs import mgrs

def mgrs2geo(mgrs_ids):
    """
    Convert a list of MGRS cell IDs to Shapely geometry objects.
    Accepts a single mgrs_id (string) or a list of mgrs_ids.
    Skips invalid or error-prone cells.
    Returns a list of Shapely Polygon objects, or a single Polygon if only one input.
    """
    if isinstance(mgrs_ids, str):
        mgrs_ids = [mgrs_ids]
    mgrs_polygons = []
    for mgrs_id in mgrs_ids:
        try:
            min_lat, min_lon, max_lat, max_lon, resolution = mgrs.mgrscell(mgrs_id)
            cell_polygon = Polygon(
                [
                    (min_lon, min_lat),
                    (max_lon, min_lat),
                    (max_lon, max_lat),
                    (min_lon, max_lat),
                    (min_lon, min_lat),
                ]
            )
            try:
                gzd_json_path = os.path.join(
                    os.path.dirname(__file__), "../generator/gzd.geojson"
                )
                with open(gzd_json_path, "r", encoding="utf-8") as f:
                    gzd_data = json.load(f)
                gzd_features = gzd_data["features"]
                gzd_feature = [
                    feature
                    for feature in gzd_features
                    if feature["properties"].get("gzd") == mgrs_id[:3]
                ][0]
                gzd_geom = shape(gzd_feature["geometry"])
                if mgrs_id[2] not in {"A", "B", "Y", "Z"}:
                    if cell_polygon.intersects(gzd_geom) and not gzd_geom.contains(
                        cell_polygon
                    ):
                        intersected_polygon = cell_polygon.intersection(gzd_geom)
                        if intersected_polygon:
                            cell_polygon = intersected_polygon
            except Exception:
                pass
            mgrs_polygons.append(cell_polygon)
        except Exception:
            continue
    if len(mgrs_polygons) == 1:
        return mgrs_polygons[0]
    return mgrs_polygons


def mgrs2geo_cli():
    """
    Command-line interface for mgrs2geo supporting multiple MGRS cell IDs.
    """
    parser = argparse.ArgumentParser(
        description="Convert MGRS cell ID(s) to Shapely Polygons"
    )
    parser.add_argument(
        "mgrs",
        nargs="+",
        help="Input MGRS cell ID(s), e.g., mgrs2geo 48PXS866916 ...",
    )
    args = parser.parse_args()
    polys = mgrs2geo(args.mgrs)
    return polys


def mgrs2geojson(mgrs_ids):
    if isinstance(mgrs_ids, str):
        mgrs_ids = [mgrs_ids]
    mgrs_features = []
    for mgrs_id in mgrs_ids:
        try:
            min_lat, min_lon, max_lat, max_lon, resolution = mgrs.mgrscell(mgrs_id)
            cell_polygon = Polygon(
                [
                    (min_lon, min_lat),
                    (max_lon, min_lat),
                    (max_lon, max_lat),
                    (min_lon, max_lat),
                    (min_lon, min_lat),
                ]
            )
            mgrs_feature = graticule_dggs_to_feature(
                "mgrs", mgrs_id, resolution, cell_polygon
            )
            try:
                gzd_json_path = os.path.join(
                    os.path.dirname(__file__), "../generator/gzd.geojson"
                )
                with open(gzd_json_path, "r", encoding="utf-8") as f:
                    gzd_data = json.load(f)
                gzd_features = gzd_data["features"]
                gzd_feature = [
                    feature
                    for feature in gzd_features
                    if feature["properties"].get("gzd") == mgrs_id[:3]
                ][0]
                gzd_geom = shape(gzd_feature["geometry"])
                if mgrs_id[2] not in {"A", "B", "Y", "Z"}:
                    if cell_polygon.intersects(gzd_geom) and not gzd_geom.contains(
                        cell_polygon
                    ):
                        intersected_polygon = cell_polygon.intersection(gzd_geom)
                        if intersected_polygon:
                            mgrs_feature = graticule_dggs_to_feature(
                                "mgrs", mgrs_id, resolution, intersected_polygon
                            )
            except Exception:
                pass
            mgrs_features.append(mgrs_feature)
        except Exception:
            continue
    return {"type": "FeatureCollection", "features": mgrs_features}


def mgrs2geojson_cli():
    """
    Command-line interface for mgrs2geojson supporting multiple MGRS cell IDs.
    """
    parser = argparse.ArgumentParser(description="Convert MGRS cell ID(s) to GeoJSON")
    parser.add_argument(
        "mgrs",
        nargs="+",
        help="Input MGRS cell ID(s), e.g., mgrs2geojson 48PXS866916 ...",
    )
    args = parser.parse_args()
    geojson_data = json.dumps(mgrs2geojson(args.mgrs))
    print(geojson_data)
    