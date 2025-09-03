"""
easecompact.py - EASE Cell Compaction Utilities

This module provides functions and command-line interfaces for compacting and expanding EASE cells.
It supports flexible input and output formats, including file paths (GeoJSON, Shapefile, CSV, Parquet),
GeoDataFrames, lists of cell IDs, and GeoJSON dictionaries. Outputs can be written to various formats or
returned as Python objects. The main functions are:

- easecompact: Compact a set of EASE cells to their minimal covering set.
- easeexpand: Expand (uncompact) a set of EASE cells to a target resolution.
- easecompact_cli: Command-line interface for compaction.
- easeexpand_cli: Command-line interface for expansion.

Dependencies: geopandas, pandas, shapely, ease_dggs, vgrid DGGS.
"""
import os
import argparse
import geopandas as gpd
from collections import defaultdict
import re
from vgrid.conversion.dggs2geo.ease2geo import ease2geo
from vgrid.utils.geometry import geodesic_dggs_to_geoseries, get_ease_resolution
from vgrid.utils.io import process_input_data_compact, convert_to_output_format
from vgrid.utils.constants import OUTPUT_FORMATS, STRUCTURED_FORMATS        
from ease_dggs.dggs.hierarchy import _parent_to_children

# --- EASE Compaction/Expansion Logic ---

def ease_compact(ease_ids):
    """Compact a list of EASE cell IDs to their minimal covering set."""
    ease_ids = set(ease_ids)  # Remove duplicates

    while True:
        grouped_ease_ids = defaultdict(set)

        # Group cells by their parent
        for ease_id in ease_ids:
            match = re.match(r"L(\d+)\.(.+)", ease_id)  # Extract resolution level & ID
            if not match:
                continue  # Skip invalid IDs

            resolution = int(match.group(1))
            base_id = match.group(2)

            if resolution == 0:
                continue  # L0 has no parent

            # Determine the parent by removing the last section
            parent = f"L{resolution - 1}." + ".".join(base_id.split(".")[:-1])
            grouped_ease_ids[parent].add(ease_id)

        new_ease_ids = set(ease_ids)
        changed = False

        # Check if we can replace children with their parent
        for parent, children in grouped_ease_ids.items():
            match = re.match(r"L(\d+)\..+", parent)
            if not match:
                continue  # Skip invalid parents

            resolution = int(match.group(1))
            children_at_next_res = set(
                _parent_to_children(parent, resolution + 1)
            )  # Ensure correct format
            
            # If all expected children are present, replace them with the parent
            if children == children_at_next_res:
                new_ease_ids.difference_update(children)
                new_ease_ids.add(parent)
                changed = True  # A change occurred

        if not changed:
            break  # Stop if no more compaction is possible
        ease_ids = new_ease_ids  # Continue compacting

    return sorted(ease_ids)  # Sorted for consistency

def easecompact(
    input_data,
    ease_id=None,
    output_format="gpd",    
):
    """Compact EASE cells from input data."""
    if not ease_id:
        ease_id = "ease"
    
    gdf = process_input_data_compact(input_data, ease_id)
    ease_ids = gdf[ease_id].drop_duplicates().tolist()
    
    if not ease_ids:
        print(f"No EASE IDs found in <{ease_id}> field.")
        return
    
    try:
        ease_ids_compact = ease_compact(ease_ids)
    except Exception:
        raise Exception("Compact cells failed. Please check your EASE ID field.")
    
    if not ease_ids_compact:
        return None
    
    rows = []
    for ease_id_compact in ease_ids_compact:
        try:
            cell_polygon = ease2geo(ease_id_compact)
            cell_resolution = get_ease_resolution(ease_id_compact)
            num_edges = 4  # EASE cells are rectangular
            row = geodesic_dggs_to_geoseries(
                "ease", ease_id_compact, cell_resolution, cell_polygon, num_edges
            )
            rows.append(row)
        except Exception:
            continue
    
    out_gdf = gpd.GeoDataFrame(rows, geometry="geometry",crs="EPSG:4326")
    
    output_name = None
    if output_format in OUTPUT_FORMATS:
        if isinstance(input_data, str):
            base = os.path.splitext(os.path.basename(input_data))[0]
            output_name = f"{base}_ease_compacted"
        else:
            output_name = f"ease_compacted"
    
    return convert_to_output_format(out_gdf, output_format, output_name)

def easecompact_cli():
    """Command-line interface for EASE compaction."""
    parser = argparse.ArgumentParser(description="EASE Compact")
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="Input EASE (GeoJSON, Shapefile, CSV, Parquet, or pickled GeoDataFrame .gpd/.geopandas)",
    )
    parser.add_argument("-cellid", "--cellid", type=str, help="EASE ID field")
    parser.add_argument("-f", "--output_format", type=str, default="gpd", choices=OUTPUT_FORMATS, help="Output format")

    args = parser.parse_args()
    input_data = args.input
    cellid = args.cellid
    output_format = args.output_format
    
    result = easecompact(
        input_data,
        ease_id=cellid,
        output_format=output_format,
    )
    
    if output_format in STRUCTURED_FORMATS:
        print(result)

def ease_expand(ease_ids, resolution):
    """Expands a list of EASE cells to the target resolution."""
    uncompacted_cells = []
    for ease_id in ease_ids:
        ease_resolution = int(ease_id[1])
        if ease_resolution >= resolution:
            uncompacted_cells.append(ease_id)
        else:
            uncompacted_cells.extend(
                _parent_to_children(ease_id, ease_resolution + 1)
            )  # Expand to the target level

    return uncompacted_cells

def easeexpand(
    input_data,
    resolution,
    ease_id=None,
    output_format="gpd", 
):
    """Expand EASE cells to a target resolution."""
    if ease_id is None:
        ease_id = "ease"
    
    gdf = process_input_data_compact(input_data, ease_id)
    ease_ids = gdf[ease_id].drop_duplicates().tolist()
    
    if not ease_ids:
        print(f"No EASE IDs found in <{ease_id}> field.")
        return
    
    try:
        max_res = max(int(ease_id[1]) for ease_id in ease_ids)
        if resolution < max_res:
            print(f"Target expand resolution ({resolution}) must >= {max_res}.")
            return None
        
        ease_ids_expand = ease_expand(ease_ids, resolution)
    except Exception:
        raise Exception("Expand cells failed. Please check your EASE ID field and resolution.")
    
    if not ease_ids_expand:
        return None
    
    rows = []
    for ease_id_expand in ease_ids_expand:
        try:
            cell_polygon = ease2geo(ease_id_expand)
            cell_resolution = resolution
            num_edges = 4  # EASE cells are rectangular
            row = geodesic_dggs_to_geoseries(
                "ease", ease_id_expand, cell_resolution, cell_polygon, num_edges
            )
            rows.append(row)
        except Exception:
            continue
    
    out_gdf = gpd.GeoDataFrame(rows, geometry="geometry",crs="EPSG:4326")
    
    output_name = None
    if output_format in OUTPUT_FORMATS:
        if isinstance(input_data, str):
            base = os.path.splitext(os.path.basename(input_data))[0]
            output_name = f"{base}_ease_expanded"
        else:
            output_name = f"ease_expanded"
    
    return convert_to_output_format(out_gdf, output_format, output_name)

def easeexpand_cli():
    """Command-line interface for EASE expansion."""
    parser = argparse.ArgumentParser(description="EASE Expand (Uncompact)")
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="Input EASE (GeoJSON, Shapefile, CSV, Parquet, or pickled GeoDataFrame .gpd/.geopandas)",
    )
    parser.add_argument(
        "-r",
        "--resolution",
        type=int,
        required=True,
        help="Target EASE resolution to expand to (must be greater than input cells)",
    )
    parser.add_argument("-cellid", "--cellid", type=str, help="EASE ID field")
    parser.add_argument("-f", "--output_format", type=str, default="gpd", choices=OUTPUT_FORMATS, help="Output format")

    args = parser.parse_args()
    input_data = args.input
    resolution = args.resolution
    cellid = args.cellid
    output_format = args.output_format
    
    result = easeexpand(
        input_data,
        resolution,
        ease_id=cellid,
        output_format=output_format,
    )
    
    if output_format in STRUCTURED_FORMATS:
        print(result)