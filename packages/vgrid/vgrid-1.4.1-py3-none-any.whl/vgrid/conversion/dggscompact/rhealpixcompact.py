"""
rhealpixcompact.py - rHEALPix Cell Compaction Utilities

This module provides functions and command-line interfaces for compacting and expanding rHEALPix cells.
It supports flexible input and output formats, including file paths (GeoJSON, Shapefile, CSV, Parquet),
GeoDataFrames, lists of cell IDs, and GeoJSON dictionaries. Outputs can be written to various formats or
returned as Python objects. The main functions are:

- rhealpixcompact: Compact a set of rHEALPix cells to their minimal covering set.
- rhealpixexpand: Expand (uncompact) a set of rHEALPix cells to a target resolution.
- rhealpixcompact_cli: Command-line interface for compaction.
- rhealpixexpand_cli: Command-line interface for expansion.

Dependencies: geopandas, pandas, shapely, rhealpixdggs, vgrid DGGS.
"""
import os
import argparse
import geopandas as gpd
from vgrid.dggs.rhealpixdggs.dggs import WGS84_003 as rhealpix_dggs    
from vgrid.utils.geometry import geodesic_dggs_to_geoseries, rhealpix_cell_to_polygon
from vgrid.utils.io import process_input_data_compact, convert_to_output_format,validate_rhealpix_resolution        
from vgrid.utils.constants import OUTPUT_FORMATS, STRUCTURED_FORMATS
from collections import defaultdict

def rhealpix_compact(rhealpix_ids):
    rhealpix_ids = set(rhealpix_ids)  # Remove duplicates

    # Main loop for compaction
    while True:
        grouped_rhealpix_ids = defaultdict(set)

        # Group cells by their parent
        for rhealpix_id in rhealpix_ids:
            if len(rhealpix_id) > 1:  # Ensure there's a valid parent
                parent = rhealpix_id[:-1]
                grouped_rhealpix_ids[parent].add(rhealpix_id)

        new_rhealpix_ids = set(rhealpix_ids)
        changed = False

        # Check if we can replace children with parent
        for parent, children in grouped_rhealpix_ids.items():
            parent_uids = (parent[0],) + tuple(
                map(int, parent[1:])
            )  # Assuming parent is a string like 'A0'
            parent_cell = rhealpix_dggs.cell(
                parent_uids
            )  # Retrieve the parent cell object

            # Generate the subcells for the parent at the next resolution
            subcells_at_next_res = set(
                str(subcell) for subcell in parent_cell.subcells()
            )  # Collect subcells as strings

            # Check if the current children match the subcells at the next resolution
            if children == subcells_at_next_res:    
                new_rhealpix_ids.difference_update(children)  # Remove children
                new_rhealpix_ids.add(parent)  # Add the parent
                changed = True  # A change occurred

        if not changed:
            break  # Stop if no more compaction is possible
        rhealpix_ids = new_rhealpix_ids  # Continue compacting

    return sorted(rhealpix_ids)  # Sorted for consistency

def rhealpix_expand(rhealpix_ids, resolution):
    expand_cells = []
    for rhealpix_id in rhealpix_ids:
        rhealpix_uids = (rhealpix_id[0],) + tuple(map(int, rhealpix_id[1:]))
        rhealpix_cell = rhealpix_dggs.cell(rhealpix_uids)
        cell_resolution = rhealpix_cell.resolution

        if cell_resolution >= resolution:
            expand_cells.append(rhealpix_cell)
        else:
            expand_cells.extend(
                rhealpix_cell.subcells(resolution)
            )  # Expand to the target level
    return expand_cells


def get_rhealpix_resolution(rhealpix_id):
    try:
        rhealpix_uids = (rhealpix_id[0],) + tuple(map(int, rhealpix_id[1:]))
        rhealpix_cell = rhealpix_dggs.cell(rhealpix_uids)
        return rhealpix_cell.resolution
    except Exception as e:
        raise ValueError(f"Invalid cell ID <{rhealpix_id}>: {e}")

def rhealpixcompact(
    input_data,
    rhealpix_id="rhealpix",
    output_format="gpd",
):
    gdf = process_input_data_compact(input_data, rhealpix_id)
    rhealpix_ids = gdf[rhealpix_id].drop_duplicates().tolist()
    if not rhealpix_ids:
        print(f"No rHEALPix tokens found in <{rhealpix_id}> field.")
        return
    try:
        rhealpix_tokens_compact = rhealpix_compact(rhealpix_ids)
    except Exception:
        raise Exception("Compact cells failed. Please check your rHEALPix ID field.")
    if not rhealpix_tokens_compact:
        return None
    rows = []
    for rhealpix_token_compact in rhealpix_tokens_compact:
        try:
            rhealpix_uids = (rhealpix_token_compact[0],) + tuple(map(int, rhealpix_token_compact[1:]))
            rhealpix_cell = rhealpix_dggs.cell(rhealpix_uids)
            cell_polygon = rhealpix_cell_to_polygon(rhealpix_cell)
            cell_resolution = rhealpix_cell.resolution
            num_edges = 4
            if rhealpix_cell.ellipsoidal_shape() == "dart":
                num_edges = 3
            row = geodesic_dggs_to_geoseries(
                "rhealpix", rhealpix_token_compact, cell_resolution, cell_polygon, num_edges
            )
            rows.append(row)
        except Exception:
            continue
    out_gdf = gpd.GeoDataFrame(rows, geometry="geometry",crs="EPSG:4326")
    output_name = None
    if output_format in OUTPUT_FORMATS:
        if isinstance(input_data, str):
            base = os.path.splitext(os.path.basename(input_data))[0]
            output_name = f"{base}_rhealpix_compacted"
        else:
            output_name = f"rhealpix_compacted"
    return convert_to_output_format(out_gdf, output_format, output_name)

def rhealpixcompact_cli():
    parser = argparse.ArgumentParser(description="rHEALPix Compact")
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="Input rHEALPix (GeoJSON, Shapefile, CSV, Parquet, or pickled GeoDataFrame .gpd/.geopandas)",
    )
    parser.add_argument("-cellid", "--cellid", type=str, help="rHEALPix ID field")
    parser.add_argument("-f", "--output_format", type=str, default="gpd", choices=OUTPUT_FORMATS, help="Output format")

    args = parser.parse_args()
    input_data = args.input
    cellid = args.cellid
    output_format = args.output_format
    result = rhealpixcompact(
        input_data,
        rhealpix_id=cellid,
        output_format=output_format,
    )
    if output_format in STRUCTURED_FORMATS:
        print(result)

def rhealpixexpand(
    input_data,
    resolution,
    rhealpix_id="rhealpix",
    output_format="gpd",
):
    resolution = validate_rhealpix_resolution(resolution)       
    gdf = process_input_data_compact(input_data, rhealpix_id)
    rhealpix_ids = gdf[rhealpix_id].drop_duplicates().tolist()
    if not rhealpix_ids:
        print(f"No rHEALPix tokens found in <{rhealpix_id}> field.")
        return
    try:
        # Get max resolution in input
        max_res = max(get_rhealpix_resolution(token) for token in rhealpix_ids)
        if resolution < max_res:
            print(f"Target expand resolution ({resolution}) must >= {max_res}.")
            return None
        expanded_cells = rhealpix_expand(rhealpix_ids, resolution)
        rhealpix_tokens_expand = [str(cell) for cell in expanded_cells]
    except Exception:
        raise Exception("Expand cells failed. Please check your rHEALPix ID field and resolution.")
    if not rhealpix_tokens_expand:
        return None
    rows = []
    for rhealpix_token_expand in rhealpix_tokens_expand:
        try:
            rhealpix_uids = (rhealpix_token_expand[0],) + tuple(map(int, rhealpix_token_expand[1:]))
            rhealpix_cell = rhealpix_dggs.cell(rhealpix_uids)
            cell_polygon = rhealpix_cell_to_polygon(rhealpix_cell)
            cell_resolution = resolution
            num_edges = 4
            if rhealpix_cell.ellipsoidal_shape() == "dart":
                num_edges = 3
            row = geodesic_dggs_to_geoseries(
                "rhealpix", rhealpix_token_expand, cell_resolution, cell_polygon, num_edges
            )
            rows.append(row)
        except Exception:
            continue
    out_gdf = gpd.GeoDataFrame(rows, geometry="geometry",crs="EPSG:4326")
    output_name = None
    if output_format in OUTPUT_FORMATS:
        if isinstance(input_data, str):
            base = os.path.splitext(os.path.basename(input_data))[0]
            output_name = f"{base}_rhealpix_expanded"
        else:
            output_name = f"rhealpix_expanded"
    return convert_to_output_format(out_gdf, output_format, output_name)

def rhealpixexpand_cli():
    parser = argparse.ArgumentParser(description="rHEALPix Expand (Uncompact)")
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="Input rHEALPix (GeoJSON, Shapefile, CSV, Parquet, or pickled GeoDataFrame .gpd/.geopandas)",
    )
    parser.add_argument(
        "-r",
        "--resolution",
        type=int,
        required=True,
        help="Target rHEALPix resolution to expand to (must be greater than input cells)",
    )
    parser.add_argument("-cellid", "--cellid", type=str, help="rHEALPix ID field")
    parser.add_argument("-f", "--output_format", type=str, default="gpd", choices=OUTPUT_FORMATS, help="Output format")

    args = parser.parse_args()
    input_data = args.input
    resolution = args.resolution
    cellid = args.cellid
    output_format = args.output_format
    result = rhealpixexpand(
        input_data,
        resolution,
        rhealpix_id=cellid,
        output_format=output_format,
    )
    if output_format in STRUCTURED_FORMATS:
        print(result)