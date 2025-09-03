"""
s2compact.py - S2 Cell Compaction Utilities

This module provides functions and command-line interfaces for compacting S2 cells.
It supports flexible input and output formats, including file paths (GeoJSON, Shapefile, CSV, Parquet),
GeoDataFrames, lists of cell IDs, and GeoJSON dictionaries. Outputs can be written to various formats or
returned as Python objects. The main functions are:

- s2compact: Compact a set of S2 cells to their minimal covering set.
- s2compact_cli: Command-line interface for compaction.

Dependencies: geopandas, pandas, shapely, vgrid.dggs.s2, vgrid DGGS.
"""
import os
import argparse
import geopandas as gpd
from vgrid.dggs import s2
from vgrid.utils.geometry import geodesic_dggs_to_geoseries
from vgrid.utils.io import process_input_data_compact, convert_to_output_format, validate_s2_resolution                                 
from vgrid.utils.constants import OUTPUT_FORMATS, STRUCTURED_FORMATS
from vgrid.conversion.dggs2geo.s22geo import s22geo     

def s2compact(
    input_data,
    s2_token="s2",
    output_format="gpd",
):
    """
    Compact S2 cells. Flexible input/output format.
    input_data: file path, URL, dict, GeoDataFrame, or list of cell IDs
    output_format: None, 'csv', 'geojson', 'shapefile', 'gpd', 'geojson_dict', 'gpkg', 'geoparquet'
    Output is always written to the current directory if file-based.
    """
    gdf = process_input_data_compact(input_data, s2_token)
    s2_tokens = gdf[s2_token].drop_duplicates().tolist()
    if not s2_tokens:
        print(f"No S2 tokens found in <{s2_token}> field.")
        return
    try:
        s2_cells = [s2.CellId.from_token(token) for token in s2_tokens]
        s2_cells = list(set(s2_cells))
        if not s2_cells:
            print(f"No valid S2 tokens found in <{s2_token}> field.")
            return
        covering = s2.CellUnion(s2_cells)
        covering.normalize()
        s2_tokens_compact = [cell_id.to_token() for cell_id in covering.cell_ids()]
    except Exception:
        raise Exception("Compact cells failed. Please check your S2 ID field.")
    if not s2_tokens_compact:
        return None
    # Build output GeoDataFrame
    rows = []
    for s2_token_compact in s2_tokens_compact:
        try:
            cell_polygon = s22geo(s2_token_compact)
            cell_resolution = s2.CellId.from_token(s2_token_compact).level()
            num_edges = 4
            row = geodesic_dggs_to_geoseries(
                "s2", s2_token_compact, cell_resolution, cell_polygon, num_edges
            )
            rows.append(row)
        except Exception:
            continue
    out_gdf = gpd.GeoDataFrame(rows, geometry="geometry",crs="EPSG:4326")

    # If output_format is file-based, set output_name as just the filename in current directory
    output_name = None
    if output_format in OUTPUT_FORMATS:
        if isinstance(input_data, str):
            base = os.path.splitext(os.path.basename(input_data))[0]
            output_name = f"{base}_s2_compacted"
        else:
            output_name = f"s2_compacted"

    return convert_to_output_format(out_gdf, output_format, output_name)


def s2compact_cli():
    """
    Command-line interface for s2compact with flexible input/output.
    """
    parser = argparse.ArgumentParser(description="S2 Compact")
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="Input S2 (GeoJSON, Shapefile, CSV, Parquet, or pickled GeoDataFrame .gpd/.geopandas)",
    )
    parser.add_argument("-cellid", "--cellid", type=str, help="S2 ID field")
    parser.add_argument("-f", "--output_format", type=str, default="gpd", choices=OUTPUT_FORMATS, help="Output format")

    args = parser.parse_args()
    input_data = args.input
    cellid = args.cellid
    output_format = args.output_format

    result = s2compact(
        input_data,
        s2_token=cellid,
        output_format=output_format,
    )
    if output_format in STRUCTURED_FORMATS:
        print(result)


def s2expand(
    input_data,
    resolution,
    s2_token="s2",
    output_format="gpd",
):
    """
    Expand (uncompact) S2 cells to a target resolution. Flexible input/output format.
    input_data: file path, URL, dict, GeoDataFrame, or list of cell IDs
    resolution: target S2 resolution (int)
    output_format: None, 'csv', 'geojson', 'shapefile', 'gpd', 'geojson_dict', 'gpkg', 'parquet', 'geoparquet'
    Output is always written to the current directory if file-based.
    """
    resolution = validate_s2_resolution(resolution)     
    gdf = process_input_data_compact(input_data, s2_token)
    s2_tokens = gdf[s2_token].drop_duplicates().tolist()
    if not s2_tokens:
        print(f"No S2 tokens found in <{s2_token}> field.")
        return
    try:
        s2_cells = [s2.CellId.from_token(token) for token in s2_tokens]
        s2_cells = list(set(s2_cells))
        if not s2_cells:
            print(f"No valid S2 tokens found in <{s2_token}> field.")
            return
        max_res = max(cell.level() for cell in s2_cells)
        if resolution < max_res:
            print(f"Target expand resolution ({resolution}) must >= {max_res}.")
            return None
        # Expand each cell to the target resolution
        expanded_cells = []
        for cell in s2_cells:
            if cell.level() >= resolution:
                expanded_cells.append(cell)
            else:
                expanded_cells.extend(cell.children(resolution))
        s2_tokens_expand = [cell_id.to_token() for cell_id in expanded_cells]
    except Exception:
        raise Exception("Expand cells failed. Please check your S2 ID field and resolution.")
    if not s2_tokens_expand:
        return None
    # Build output GeoDataFrame
    rows = []
    for s2_token_expand in s2_tokens_expand:
        try:
            cell_polygon = s22geo(s2_token_expand)
            cell_resolution = resolution
            num_edges = 4
            row = geodesic_dggs_to_geoseries(
                "s2", s2_token_expand, cell_resolution, cell_polygon, num_edges
            )
            rows.append(row)
        except Exception:
            continue
    out_gdf = gpd.GeoDataFrame(rows, geometry="geometry",crs="EPSG:4326")

    # If output_format is file-based, set output_name as just the filename in current directory
    output_name = None
    if output_format in OUTPUT_FORMATS:
        if isinstance(input_data, str):
            base = os.path.splitext(os.path.basename(input_data))[0]
            output_name = f"{base}_s2_expanded"
        else:
            output_name = f"s2_expanded"

    return convert_to_output_format(out_gdf, output_format, output_name)

def s2expand_cli():
    """
    Command-line interface for s2expand with flexible input/output.
    """
    parser = argparse.ArgumentParser(description="S2 Expand (Uncompact)")
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="Input S2 (GeoJSON, Shapefile, CSV, Parquet, or pickled GeoDataFrame .gpd/.geopandas)",
    )
    parser.add_argument(
        "-r",
        "--resolution",
        type=int,
        required=True,
        help="Target S2 resolution to expand to (must be greater than input cells)",
    )
    parser.add_argument("-cellid", "--cellid", type=str, help="S2 Token field")
    parser.add_argument("-f", "--output_format", type=str, default="gpd", choices=OUTPUT_FORMATS, help="Output format")

    args = parser.parse_args()
    input_data = args.input
    resolution = args.resolution
    cellid = args.cellid
    output_format = args.output_format

    result = s2expand(
        input_data,
        resolution,
        s2_token=cellid,
        output_format=output_format,
    )
    if output_format in STRUCTURED_FORMATS:
        print(result)