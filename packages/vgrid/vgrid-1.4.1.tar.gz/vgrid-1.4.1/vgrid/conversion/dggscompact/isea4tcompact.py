"""
isea4tcompact.py - ISEA4T Cell Compaction Utilities

This module provides functions and command-line interfaces for compacting and expanding ISEA4T cells.
It supports flexible input and output formats, including file paths (GeoJSON, Shapefile, CSV, Parquet),
GeoDataFrames, lists of cell IDs, and GeoJSON dictionaries. Outputs can be written to various formats or
returned as Python objects. The main functions are:

- isea4tcompact: Compact a set of ISEA4T cells to their minimal covering set.
- isea4texpand: Expand (uncompact) a set of ISEA4T cells to a target resolution.
- isea4tcompact_cli: Command-line interface for compaction.
- isea4texpand_cli: Command-line interface for expansion.

Dependencies: geopandas, pandas, shapely, vgrid.dggs.eaggr, vgrid DGGS.
"""
import os
import argparse
import geopandas as gpd
import platform
if platform.system() == "Windows":
    from vgrid.dggs.eaggr.eaggr import Eaggr
    from vgrid.dggs.eaggr.shapes.dggs_cell import DggsCell
    from vgrid.dggs.eaggr.enums.model import Model
    isea4t_dggs = Eaggr(Model.ISEA4T)

from vgrid.conversion.dggs2geo.isea4t2geo import isea4t2geo
from vgrid.utils.geometry import geodesic_dggs_to_geoseries
from vgrid.utils.io import process_input_data_compact, convert_to_output_format
from vgrid.utils.constants import OUTPUT_FORMATS, STRUCTURED_FORMATS

# --- ISEA4T Compaction/Expansion Logic ---
def get_isea4t_resolution(isea4t_id):
    return len(isea4t_id) - 2

def get_isea4t_cell_children(isea4t_cell, resolution):
    """Recursively expands a DGGS cell until all children reach the desired resolution."""
    cell_id = isea4t_cell.get_cell_id()
    cell_resolution = len(cell_id) - 2

    if cell_resolution >= resolution:
        return [
            isea4t_cell
        ]  # Base case: return the cell if it meets/exceeds resolution

    expanded_cells = []
    children = isea4t_dggs.get_dggs_cell_children(isea4t_cell)

    for child in children:
        expanded_cells.extend(
            get_isea4t_cell_children(child, resolution)
        )

    return expanded_cells

def isea4t_compact(isea4t_ids):
    isea4t_ids = set(isea4t_ids)
    while True:
        grouped_isea4t_ids = {}
        for isea4t_id in isea4t_ids:
            if len(isea4t_id) > 2:
                parent = isea4t_id[:-1]
                grouped_isea4t_ids.setdefault(parent, set()).add(isea4t_id)
        new_isea4t_ids = set(isea4t_ids)
        changed = False
        for parent, children in grouped_isea4t_ids.items():
            parent_cell = DggsCell(parent)
            children_at_next_res = set(
                child.get_cell_id() for child in isea4t_dggs.get_dggs_cell_children(parent_cell)
            )
            if children == children_at_next_res:
                new_isea4t_ids.difference_update(children)
                new_isea4t_ids.add(parent)
                changed = True
        if not changed:
            break
        isea4t_ids = new_isea4t_ids
    return sorted(isea4t_ids)

def isea4t_expand(isea4t_ids, resolution):
    """Expands a list of DGGS cells to the target resolution."""
    expand_cells = []
    for isea4t_id in isea4t_ids:
        isea4t_cell = DggsCell(isea4t_id)
        expand_cells.extend(
            get_isea4t_cell_children(isea4t_cell, resolution)
        )
    return expand_cells


def isea4tcompact(
    input_data,
    isea4t_id=None,
    output_format="gpd",         
):
    if not isea4t_id:
        isea4t_id = "isea4t"
    gdf = process_input_data_compact(input_data, isea4t_id)
    isea4t_ids = gdf[isea4t_id].drop_duplicates().tolist()
    if not isea4t_ids:
        print(f"No ISEA4T isea4t_ids found in <{isea4t_id}> field.")
        return
    try:
        isea4t_ids_compact = isea4t_compact(isea4t_ids)
    except Exception:
        raise Exception("Compact cells failed. Please check your ISEA4T ID field.")
    if not isea4t_ids_compact:
        return None
    rows = []
    for isea4t_id_compact in isea4t_ids_compact:
        try:
            cell_polygon = isea4t2geo(isea4t_id_compact)
            cell_resolution = get_isea4t_resolution(isea4t_id_compact)
            num_edges = 3          
            row = geodesic_dggs_to_geoseries(
                "isea4t", isea4t_id_compact, cell_resolution, cell_polygon, num_edges
            )
            rows.append(row)
        except Exception:
            continue
    out_gdf = gpd.GeoDataFrame(rows, geometry="geometry",crs="EPSG:4326")
    ouput_name = None
    if output_format in OUTPUT_FORMATS:
        if isinstance(input_data, str):
            base = os.path.splitext(os.path.basename(input_data))[0]
            ouput_name = f"{base}_isea4t_compacted"
        else:
            ouput_name = f"isea4t_compacted"
    return convert_to_output_format(out_gdf, output_format, ouput_name)

def isea4tcompact_cli():
    parser = argparse.ArgumentParser(description="ISEA4T Compact")
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="Input ISEA4T (GeoJSON, Shapefile, CSV, Parquet, or pickled GeoDataFrame .gpd/.geopandas)",
    )
    parser.add_argument("-cellid", "--cellid", type=str, help="ISEA4T ID field")
    parser.add_argument("-f", "--output_format", type=str, default="gpd", choices=OUTPUT_FORMATS, help="Output format")

    args = parser.parse_args()
    input_data = args.input
    cellid = args.cellid
    output_format = args.output_format
    result = isea4tcompact(
        input_data,
        isea4t_id=cellid,
        output_format=output_format,
    )
    if output_format in STRUCTURED_FORMATS:
        print(result)

def isea4texpand(
    input_data,
    resolution,
    isea4t_id=None,
    output_format="gpd", 
):
    if isea4t_id is None:
        isea4t_id = "isea4t"
    gdf = process_input_data_compact(input_data, isea4t_id)
    isea4t_ids = gdf[isea4t_id].drop_duplicates().tolist()
    if not isea4t_ids:
        print(f"No ISEA4T IDs found in <{isea4t_id}> field.")
        return
    try:
        max_res = max(get_isea4t_resolution(isea4t_id) for isea4t_id in isea4t_ids)
        if resolution < max_res:
            print(f"Target expand resolution ({resolution}) must >= {max_res}.")
            return None
        expanded_cells = []
        for isea4t_id in isea4t_ids:
            cell = DggsCell(isea4t_id)
            cell_res = get_isea4t_resolution(isea4t_id)
            if cell_res >= resolution:
                expanded_cells.append(cell)
            else:
                expanded_cells.extend(isea4t_dggs.get_dggs_cell_children(cell))
        isea4t_ids_expand = [c.get_cell_id() for c in expanded_cells]
    except Exception:
        raise Exception("Expand cells failed. Please check your ISEA4T ID field and resolution.")
    if not isea4t_ids_expand:
        return None
    rows = []
    for isea4t_id_expand in isea4t_ids_expand:
        try:
            cell_polygon = isea4t2geo(isea4t_id_expand)
            cell_resolution = resolution
            num_edges = 3
            row = geodesic_dggs_to_geoseries(
                "isea4t", isea4t_id_expand, cell_resolution, cell_polygon, num_edges
            )
            rows.append(row)
        except Exception:
            continue
    out_gdf = gpd.GeoDataFrame(rows, geometry="geometry",crs="EPSG:4326")
    ouput_name = None
    if output_format in OUTPUT_FORMATS:
        if isinstance(input_data, str):
            base = os.path.splitext(os.path.basename(input_data))[0]
            ouput_name = f"{base}_isea4t_expanded"
        else:
            ouput_name = f"isea4t_expanded"
    return convert_to_output_format(out_gdf, output_format, ouput_name)

def isea4texpand_cli():
    parser = argparse.ArgumentParser(description="ISEA4T Expand (Uncompact)")
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="Input ISEA4T (GeoJSON, Shapefile, CSV, Parquet, or pickled GeoDataFrame .gpd/.geopandas)",
    )
    parser.add_argument(
        "-r",
        "--resolution",
        type=int,
        required=True,
        help="Target ISEA4T resolution to expand to (must be greater than input cells)",
    )
    parser.add_argument("-cellid", "--cellid", type=str, help="ISEA4T ID field")
    parser.add_argument("-f", "--output_format", type=str, default="gpd", choices=OUTPUT_FORMATS, help="Output format")

    args = parser.parse_args()
    input_data = args.input
    resolution = args.resolution
    cellid = args.cellid
    output_format = args.output_format
    if platform.system() == "Windows":
        result = isea4texpand(
            input_data,
            resolution,
            isea4t_id=cellid,
            output_format=output_format,
        )
        if output_format in STRUCTURED_FORMATS:
            print(result)
    else:
        print("ISEA4T is only supported on Windows systems")