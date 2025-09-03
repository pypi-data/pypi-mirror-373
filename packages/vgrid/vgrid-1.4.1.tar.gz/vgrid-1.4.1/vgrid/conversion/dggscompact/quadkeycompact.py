"""
quadkeycompact.py - Quadkey Cell Compaction Utilities

This module provides functions and command-line interfaces for compacting and expanding Quadkey cells.
It supports flexible input and output formats, including file paths (GeoJSON, Shapefile, CSV, Parquet),
GeoDataFrames, lists of cell IDs, and GeoJSON dictionaries. Outputs can be written to various formats or
returned as Python objects. The main functions are:

- quadkeycompact: Compact a set of Quadkey cells to their minimal covering set.
- quadkeyexpand: Expand (uncompact) a set of Quadkey cells to a target resolution.
- quadkeycompact_cli: Command-line interface for compaction.
- quadkeyexpand_cli: Command-line interface for expansion.

Dependencies: geopandas, pandas, shapely, vgrid.dggs.tilecode, mercantile, vgrid DGGS.
"""
import os
import argparse
import geopandas as gpd
from collections import defaultdict

from vgrid.utils.geometry import graticule_dggs_to_geoseries
from vgrid.utils.io import process_input_data_compact, convert_to_output_format
from vgrid.utils.constants import OUTPUT_FORMATS, STRUCTURED_FORMATS
from vgrid.dggs import mercantile, tilecode
from vgrid.dggs.tilecode import quadkey_resolution
from vgrid.conversion.dggs2geo.quadkey2geo import quadkey2geo   

def quadkey_compact(quadkey_ids):   
    """Compact a list of Quadkey cell IDs to their minimal covering set."""
    quadkey_ids = set(quadkey_ids)  # Remove duplicates
    
    # Main loop for compaction
    while True:
        grouped_quadkey_ids = defaultdict(set)
        
        # Group cells by their parent
        for quadkey_id in quadkey_ids:
            parent = tilecode.quadkey_parent(quadkey_id)
            grouped_quadkey_ids[parent].add(quadkey_id)

        new_quadkey_ids = set(quadkey_ids)
        changed = False

        # Check if we can replace children with parent
        for parent, children in grouped_quadkey_ids.items():
            parent_resolution = mercantile.quadkey_to_tile(parent).z

            # Generate the subcells for the parent at the next resolution
            childcells_at_next_res = set(
                childcell
                for childcell in tilecode.quadkey_children(
                    parent, parent_resolution + 1
                )
            )

            # Check if the current children match the subcells at the next resolution
            if children == childcells_at_next_res:
                new_quadkey_ids.difference_update(children)  # Remove children
                new_quadkey_ids.add(parent)  # Add the parent
                changed = True  # A change occurred

        if not changed:
            break  # Stop if no more compaction is possible
        quadkey_ids = new_quadkey_ids  # Continue compacting

    return sorted(quadkey_ids)  # Sorted for consistency

def quadkeycompact(
    input_data,
    quadkey_id="quadkey",
    output_format="gpd",
):
    """Compact Quadkey cells from input data."""
    
    gdf = process_input_data_compact(input_data, quadkey_id)
    quadkey_ids = gdf[quadkey_id].drop_duplicates().tolist()
    
    if not quadkey_ids:
        print(f"No Quadkey IDs found in <{quadkey_id}> field.")
        return
    
    try:
        quadkey_ids_compact = quadkey_compact(quadkey_ids)
    except Exception:
        raise Exception("Compact cells failed. Please check your Quadkey ID field.")
    
    if not quadkey_ids_compact:
        return None
    
    rows = []
    for quadkey_id_compact in quadkey_ids_compact:
        try:
            cell_polygon = quadkey2geo(quadkey_id_compact)
            cell_resolution = quadkey_resolution(quadkey_id_compact)
            row = graticule_dggs_to_geoseries(
                "quadkey", quadkey_id_compact, cell_resolution, cell_polygon
            )
            rows.append(row)
        except Exception:
            continue
    
    out_gdf = gpd.GeoDataFrame(rows, geometry="geometry",crs="EPSG:4326")
    
    output_name = None
    if output_format in OUTPUT_FORMATS:
        if isinstance(input_data, str):
            base = os.path.splitext(os.path.basename(input_data))[0]
            output_name = f"{base}_quadkey_compacted"
        else:
            output_name = f"quadkey_compacted"
    
    return convert_to_output_format(out_gdf, output_format, output_name)

def quadkeycompact_cli():
    """Command-line interface for Quadkey compaction."""
    parser = argparse.ArgumentParser(description="Quadkey Compact")
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="Input Quadkey (GeoJSON, Shapefile, CSV, Parquet, or pickled GeoDataFrame .gpd/.geopandas)",
    )
    parser.add_argument("-cellid", "--cellid", type=str, help="Quadkey ID field")
    parser.add_argument("-f", "--output_format", type=str, default="gpd", choices=OUTPUT_FORMATS, help="Output format")

    args = parser.parse_args()
    input_data = args.input
    cellid = args.cellid
    output_format = args.output_format
    
    result = quadkeycompact(
        input_data,
        quadkey_id=cellid,
        output_format=output_format,
    )
    
    if output_format in STRUCTURED_FORMATS:
        print(result)

def quadkey_expand(quadkey_ids, resolution):
    """Expands a list of Quadkey cells to the target resolution."""
    expand_cells = []
    for quadkey_id in quadkey_ids:
        cell_resolution = len(quadkey_id)
        if cell_resolution >= resolution:
            expand_cells.append(quadkey_id)
        else:
            expand_cells.extend(
                tilecode.quadkey_children(quadkey_id, resolution)
            )  # Expand to the target level
    return expand_cells

def quadkeyexpand(
    input_data,
    resolution,
    quadkey_id="quadkey",
    output_format="gpd",
):
    """Expand Quadkey cells to a target resolution."""
    
    gdf = process_input_data_compact(input_data, quadkey_id)
    quadkey_ids = gdf[quadkey_id].drop_duplicates().tolist()
    
    if not quadkey_ids:
        print(f"No Quadkey IDs found in <{quadkey_id}> field.")
        return
    
    try:
        max_res = max(len(quadkey_id) for quadkey_id in quadkey_ids)
        if resolution < max_res:
            print(f"Target expand resolution ({resolution}) must >= {max_res}.")
            return None
        
        quadkey_ids_expand = quadkey_expand(quadkey_ids, resolution)
    except Exception:
        raise Exception("Expand cells failed. Please check your Quadkey ID field and resolution.")
    
    if not quadkey_ids_expand:
        return None
    
    rows = []
    for quadkey_id_expand in quadkey_ids_expand:
        try:
            cell_polygon = quadkey2geo(quadkey_id_expand)
            cell_resolution = resolution
            row = graticule_dggs_to_geoseries(
                "quadkey", quadkey_id_expand, cell_resolution, cell_polygon
            )
            rows.append(row)
        except Exception:
            continue
    
    out_gdf = gpd.GeoDataFrame(rows, geometry="geometry",crs="EPSG:4326")
    
    output_name = None
    if output_format in OUTPUT_FORMATS:
        if isinstance(input_data, str):
            base = os.path.splitext(os.path.basename(input_data))[0]
            output_name = f"{base}_quadkey_expanded"
        else:
            output_name = f"quadkey_expanded"
    
    return convert_to_output_format(out_gdf, output_format, output_name)

def quadkeyexpand_cli():
    """Command-line interface for Quadkey expansion."""
    parser = argparse.ArgumentParser(description="Quadkey Expand (Uncompact)")
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="Input Quadkey (GeoJSON, Shapefile, CSV, Parquet, or pickled GeoDataFrame .gpd/.geopandas)",
    )
    parser.add_argument(
        "-r",
        "--resolution",
        type=int,
        required=True,
        help="Target Quadkey resolution to expand to (must be greater than input cells)",
    )
    parser.add_argument("-cellid", "--cellid", type=str, help="Quadkey ID field")
    parser.add_argument("-f", "--output_format", type=str, default="gpd", choices=OUTPUT_FORMATS, help="Output format")

    args = parser.parse_args()
    input_data = args.input
    resolution = args.resolution
    cellid = args.cellid
    output_format = args.output_format
    
    result = quadkeyexpand(
        input_data,
        resolution,
        quadkey_id=cellid,
        output_format=output_format,
    )
    
    if output_format in STRUCTURED_FORMATS:
        print(result)