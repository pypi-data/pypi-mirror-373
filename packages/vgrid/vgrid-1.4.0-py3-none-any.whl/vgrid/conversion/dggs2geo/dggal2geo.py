"""
Convert DGGAL ZoneID(s) to GeoJSON using the external `dgg` CLI.

Usage (CLI):
  dggal2geo <dggs_type> <ZoneID> [ZoneID ...]

Notes:
- Requires the `dgg` command (from the `dggal` package) to be installed and on PATH.
- Resolution is inferred from each `ZoneID` (e.g., "8-E1-32F" -> res=8). Grids
  are fetched per unique resolution and merged.
"""

import argparse
import json
# Try to import dggal library, handle gracefully if import fails
from dggal import *
app = Application(appGlobals=globals())
pydggal_setup(app)
   
from vgrid.utils.geometry import geodesic_dggs_to_feature
from vgrid.utils.constants import DGGAL_TYPES
from vgrid.utils.geometry import dggal_to_geo
from vgrid.utils.io import validate_dggal_type

def dggal2geo(dggs_type: str, zone_ids: str, options: dict = {}):    
    if isinstance(zone_ids, str):
        zone_ids = [zone_ids]
    zone_polygons = []
    for zone_id in zone_ids:
        try:
            zone_polygon = dggal_to_geo(dggs_type, zone_id, options)
            zone_polygons.append(zone_polygon)
        except Exception:
            continue
    if len(zone_polygons) == 1:
        return zone_polygons[0]
    return zone_polygons


def dggal2geo_cli():
    parser = argparse.ArgumentParser(
        description=(
            "Convert DGGAL ZoneID to Shapely geometry. "
            "Usage: dggal2geo <dggs_type> <ZoneID> [ZoneID ...]"
        )
    )
    parser.add_argument("dggs_type", type=str, choices=DGGAL_TYPES.keys(), help="DGGAL DGGS type")
    parser.add_argument("zone_id", nargs="+", help="ZoneIDs, e.g., dggal2geo isea3h A4-0-A A4-0-B")
    args = parser.parse_args()

    polys = dggal2geo(args.dggs_type, args.zone_id)
    return polys

def dggal2geojson(dggs_type: str, zone_ids: str, options: dict = {}):       
    """
    Convert DGGAL ZoneIDs to GeoJSON FeatureCollection.
    
    This function takes DGGAL ZoneIDs and converts them to a GeoJSON    
    FeatureCollection containing features with geometry and properties for each cell.
    """
    dggs_type = validate_dggal_type(dggs_type)    
    # Create the appropriate DGGS instance
    dggs_class_name = DGGAL_TYPES[dggs_type]["class_name"]
    dggrs = globals()[dggs_class_name]()
    
    if isinstance(zone_ids, str):
        zone_ids = [zone_ids]
    zone_features = []
    
    for zone_id in zone_ids:
        try:            
            zone = dggrs.getZoneFromTextID(zone_id)
            resolution = dggrs.getZoneLevel(zone)
            num_edges = dggrs.countZoneEdges(zone)
            cell_polygon = dggal_to_geo(dggs_type, zone_id, options)
            zone_feature = geodesic_dggs_to_feature(
                f"dggal_{dggs_type}", zone_id, resolution, cell_polygon, num_edges
            )   
            zone_features.append(zone_feature)
        except Exception:
            continue
    return {"type": "FeatureCollection", "features": zone_features}


def dggal2geojson_cli():
    """
    Command-line interface for converting DGGAL ZoneIDs to GeoJSON.
    
    This function provides a command-line interface that accepts multiple DGGAL
    ZoneIDs as command-line arguments and outputs the corresponding GeoJSON
    FeatureCollection as a JSON string to stdout.
    
    Usage:
        dggal2geojson isea3h A4-0-A A4-0-B
    
    Output:
        Prints a JSON string representing a GeoJSON FeatureCollection to stdout.
    
    Example:
        $ python -m vgrid.conversion.dggs2geo.dggal2geo isea3h A4-0-A
        {"type": "FeatureCollection", "features": [...]}
    
    Note:
        This function is designed to be called from the command line and will
        parse arguments using argparse. The GeoJSON output is formatted as a
        JSON string printed to stdout. Invalid cell IDs are silently skipped.
    """
    parser = argparse.ArgumentParser(
        description="Convert DGGAL ZoneID(s) to GeoJSON"
    )
    parser.add_argument(
        "dggs_type",
        type=str,
        choices=DGGAL_TYPES.keys(),
        help="DGGAL DGGS type"
    )
    parser.add_argument(
        "zone_id",
        nargs="+",
        help="Input DGGAL ZoneID(s), e.g., dggal2geojson isea3h A4-0-A A4-0-B",
    )
    args = parser.parse_args()
    geojson_data = json.dumps(dggal2geojson(args.dggs_type, args.zone_id))
    print(geojson_data) # print to stdout   

