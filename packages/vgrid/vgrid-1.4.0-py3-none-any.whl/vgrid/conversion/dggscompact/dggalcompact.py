"""
dggalcompact.py - DGGAL Cell Compaction Utilities

This module provides functions and command-line interfaces for compacting and expanding DGGAL cells.
It supports flexible input and output formats, including file paths (GeoJSON, Shapefile, CSV, Parquet),
GeoDataFrames, lists of cell IDs, and GeoJSON dictionaries. Outputs can be written to various formats or
returned as Python objects. The main functions are:

- dggalcompact: Compact a set of DGGAL cells to their minimal covering set.
- dggalexpand: Expand (uncompact) a set of DGGAL cells to a target resolution.
- dggalcompact_cli: Command-line interface for compaction.
- dggalexpand_cli: Command-line interface for expansion.

Dependencies: geopandas, pandas, shapely, vgrid.dggs.dggal, vgrid DGGS.
"""
import os
import argparse
import geopandas as gpd
from collections import defaultdict
from vgrid.conversion.dggs2geo.dggal2geo import dggal2geo
from vgrid.utils.io import process_input_data_compact,validate_dggal_type, convert_to_output_format
from vgrid.utils.constants import OUTPUT_FORMATS, STRUCTURED_FORMATS, DGGAL_TYPES
from vgrid.utils.geometry import geodesic_dggs_to_geoseries     
from collections import defaultdict

from dggal import *
# Initialize dggal application
app = Application(appGlobals=globals())
pydggal_setup(app)
# --- DGGAL Compaction/Expansion Logic ---

def dggal_compact(dggs_type, zone_ids):
    """
    Compact a set of DGGAL cells to their minimal covering set using hierarchical compaction.
    
    This function implements a hierarchical compaction approach similar to rhealpix_compact,
    grouping cells by their parent and checking if all children of a parent are present
    to replace them with the parent.
    
    Args:
        dggs_type (str): DGGAL DGGS type
        zone_ids (list): List of DGGAL zone IDs to compact
        
    Returns:
        list: Sorted list of compacted DGGAL zone IDs
    """
    
    # Create the appropriate DGGS instance
    dggs_type = validate_dggal_type(dggs_type)
    dggs_class_name = DGGAL_TYPES[dggs_type]["class_name"]
    dggrs = getattr(dggal, dggs_class_name)()
    
    # Remove duplicates
    zone_ids = set(zone_ids) 
    
    while True:
        grouped_zone_ids = defaultdict(set)        
        # Group cells by their parent
        for zone_id in zone_ids:
            zone = dggrs.getZoneFromTextID(zone_id) 
            zone_level = dggrs.getZoneLevel(zone)
            if zone_level > 0:  # Ensure there's a valid parent
                # Get all parent zones
                parent_zones = dggrs.getZoneParents(zone)
                for parent_zone in parent_zones:
                    parent_zone_id = dggrs.getZoneTextID(parent_zone)                
                    grouped_zone_ids[parent_zone_id].add(zone_id)  

        new_zone_ids = set(zone_ids)
        changed = False

        # Check if we can replace children with parent
        for parent_zone_id, children in grouped_zone_ids.items():
            # Get parent zone object
            parent_zone = dggrs.getZoneFromTextID(parent_zone_id)
            # Get all subzones of the parent
            subzones = dggrs.getZoneChildren(parent_zone)
            subzone_ids = set()                
            for subzone in subzones:
                subzone_id = dggrs.getZoneTextID(subzone)
                subzone_ids.add(subzone_id)                   
            
            # Check if the current children match all subzones of the parent
            if children == subzone_ids:
                # Remove children and add parent
                new_zone_ids.difference_update(children)
                new_zone_ids.add(parent_zone_id)
                changed = True
        
        if not changed:
            break  # Stop if no more compaction is possible
            
        zone_ids = new_zone_ids  # Continue compacting
    
    return sorted(zone_ids)  # Sorted for consistency

def dggalcompact(
    dggs_type,
    input_data,
    zone_id=None,
    output_format="gpd",         
):
    dggs_type = validate_dggal_type(dggs_type)
    if not zone_id:
        zone_id = f"dggal_{dggs_type}"
    
    gdf = process_input_data_compact(input_data, zone_id)
    dggal_ids = gdf[zone_id].drop_duplicates().tolist()
    
    if not dggal_ids:
        print(f"No DGGAL IDs found in <{zone_id}> field.")
        return
    
    dggal_ids_compact = dggal_compact(dggs_type, dggal_ids)
  
    if not dggal_ids_compact:
        print("Warning: Compaction returned no results, returning original data")
        # Return the original data if compaction fails
        return convert_to_output_format(gdf, output_format, f"{dggs_type}_original")
    
    # Create the appropriate DGGS instance
    dggs_class_name = DGGAL_TYPES[dggs_type]["class_name"]
    dggrs = getattr(dggal, dggs_class_name)()
    
    rows = []
    for dggal_id_compact in dggal_ids_compact:
        try:
            # Get zone object to get resolution directly
            zone = dggrs.getZoneFromTextID(dggal_id_compact)
            cell_resolution = dggrs.getZoneLevel(zone)
            cell_polygon = dggal2geo(dggs_type, dggal_id_compact)
            num_edges = dggrs.countZoneEdges(zone)
            row = geodesic_dggs_to_geoseries(
                f"dggal_{dggs_type}", dggal_id_compact, cell_resolution, cell_polygon, num_edges
            )
            rows.append(row)
        except Exception:
            continue
    out_gdf = gpd.GeoDataFrame(rows, geometry="geometry",crs="EPSG:4326")

    output_name = None
    if output_format in OUTPUT_FORMATS:
        if isinstance(input_data, str):
            base = os.path.splitext(os.path.basename(input_data))[0]
            output_name = f"{base}_dggal_compacted"
        else:
            output_name = f"dggal_compacted"
    
    return convert_to_output_format(out_gdf, output_format, output_name)

def dggalcompact_cli():
    parser = argparse.ArgumentParser(description="DGGAL Compact")
    parser.add_argument(
        "-dggs",
        "--dggs_type",
        type=str,
        required=True,
        choices=DGGAL_TYPES.keys(),
        help="DGGAL DGGS type"
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="Input DGGAL (GeoJSON, Shapefile, CSV, Parquet, or pickled GeoDataFrame .gpd/.geopandas)",
    )
    parser.add_argument("-zoneid", "--zoneid", type=str, help="DGGAL ID field")
    parser.add_argument("-f", "--output_format", type=str, default="gpd", choices=OUTPUT_FORMATS, help="Output format")

    args = parser.parse_args()
    input_data = args.input
    dggs_type = args.dggs_type
    zoneid = args.zoneid
    output_format = args.output_format
    
    result = dggalcompact(
        dggs_type,
        input_data,
        zone_id=zoneid,
        output_format=output_format,
    )
    if output_format in STRUCTURED_FORMATS:
        print(result)

def dggal_expand(dggs_type, zone_ids, resolution): 
    """
    Expand a list of DGGAL cell IDs to the target resolution using dggrs methods.
    In DGGAL, higher resolution = lower level number (e.g., level 0 is coarser than level 1).
    Only returns children cells, not the parent cells themselves.
    """
    # Create the appropriate DGGS instance
    dggs_class_name = DGGAL_TYPES[dggs_type]["class_name"]
    dggrs = getattr(dggal, dggs_class_name)()
    
    expanded_cells = []
    for zone_id in zone_ids:
        try:
            zone = dggrs.getZoneFromTextID(zone_id)
            current_res = dggrs.getZoneLevel(zone)
            
            if resolution < current_res:
                print(f"Warning: Target resolution {resolution} is lower than current resolution {current_res} for zone {zone_id}")
                continue
                
            # If already at target resolution, keep the zone
            if resolution == current_res:
                expanded_cells.append(zone_id)
            else:
                # Get sub-zones at the target resolution
                depth = resolution - current_res
                sub_zones = dggrs.getSubZones(zone, depth)
                
                for sub_zone in sub_zones:
                    sub_zone_id = dggrs.getZoneTextID(sub_zone)
                    expanded_cells.append(sub_zone_id)
                
        except Exception as e:
            print(f"Warning: Could not expand zone {zone_id}: {e}")
            continue
            
    return expanded_cells


def dggalexpand(
    dggs_type,
    input_data,
    resolution,
    zone_id=None,
    output_format="gpd", 
):
    dggs_type = validate_dggal_type(dggs_type)
    if zone_id is None:
        zone_id = f"dggal_{dggs_type}"
    
    gdf = process_input_data_compact(input_data, zone_id)
    zone_ids = gdf[zone_id].drop_duplicates().tolist()
    
    if not zone_ids:
        print(f"No Zone IDs found in <{zone_id}> field.")
        return
    
    # Create the appropriate DGGS instance
    dggs_class_name = DGGAL_TYPES[dggs_type]["class_name"]
    dggrs = getattr(dggal, dggs_class_name)()
    
    try:
        # Get max resolution using zone objects
        max_res = 0
        for zone_id in zone_ids:
            try:
                zone = dggrs.getZoneFromTextID(zone_id)
                zone_res = dggrs.getZoneLevel(zone)
                max_res = max(max_res, zone_res)
            except Exception:
                continue
        
        if resolution < max_res:
            print(f"Target expand resolution ({resolution}) must >= {max_res}.")
            return None
        zone_ids_expand = dggal_expand(dggs_type, zone_ids, resolution)
    except Exception:
        raise Exception("Expand cells failed. Please check your Zone ID field and resolution.")
    if not zone_ids_expand:
        return None
    
    rows = []
    for zone_id_expand in zone_ids_expand:
        try:
            # Get zone object to get resolution directly
            zone = dggrs.getZoneFromTextID(zone_id_expand)
            cell_resolution = dggrs.getZoneLevel(zone)
            cell_polygon = dggal2geo(dggs_type, zone_id_expand)
            num_edges = dggrs.countZoneEdges(zone)
            row = geodesic_dggs_to_geoseries(
                f"dggal_{dggs_type}", zone_id_expand, cell_resolution, cell_polygon, num_edges
            )
            rows.append(row)
        except Exception:
            continue
    out_gdf = gpd.GeoDataFrame(rows, geometry="geometry",crs="EPSG:4326")

    # If output_format is file-based, set ouput_name as just the filename in current directory
    ouput_name = None
    if output_format in OUTPUT_FORMATS:
        if isinstance(input_data, str):
            base = os.path.splitext(os.path.basename(input_data))[0]
            ouput_name = f"{base}_dggal_expanded"
        else:
            ouput_name = f"dggal_expanded"

    return convert_to_output_format(out_gdf, output_format, ouput_name)

def dggalexpand_cli():
    parser = argparse.ArgumentParser(description="DGGAL Expand (Uncompact)")
    parser.add_argument(
        "-dggs",
        "--dggs_type",
        type=str,
        required=True,
        choices=DGGAL_TYPES.keys(),
        help="DGGAL DGGS type"
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="Input DGGAL (GeoJSON, Shapefile, CSV, Parquet, or pickled GeoDataFrame .gpd/.geopandas)",
    )
    parser.add_argument(
        "-r",
        "--resolution",
        type=int,
        required=True,
        help="Target DGGAL resolution to expand to (must be greater than input cells)",
    )
    
    parser.add_argument("-zoneid", "--zoneid", type=str, help="DGGAL ID field")
    parser.add_argument("-f", "--output_format", type=str, default="gpd", choices=OUTPUT_FORMATS, help="Output format")

    args = parser.parse_args()
    input_data = args.input
    resolution = args.resolution
    dggs_type = args.dggs_type
    zoneid = args.zoneid
    output_format = args.output_format
    
    result = dggalexpand(
        dggs_type,
        input_data,
        resolution,
        zone_id=zoneid,
        output_format=output_format,
    )
    if output_format in STRUCTURED_FORMATS:
        print(result)
