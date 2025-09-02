# Reference: https://observablehq.com/@claude-ducharme/h3-map
# https://h3-snow.streamlit.app/

import argparse
from shapely.geometry import box, shape
from shapely.ops import unary_union
from tqdm import tqdm
from pyproj import Geod
import geopandas as gpd
import h3
from vgrid.utils.constants import OUTPUT_FORMATS, STRUCTURED_FORMATS, MAX_CELLS
from vgrid.utils.geometry import (
    geodesic_buffer,
    geodesic_dggs_to_geoseries,
)
from vgrid.utils.io import validate_h3_resolution, convert_to_output_format
from vgrid.conversion.dggs2geo.h32geo import h32geo 
geod = Geod(ellps="WGS84")      

def h3_grid(resolution):
    resolution = validate_h3_resolution(resolution)
    total_cells = h3.get_num_cells(resolution)
    if total_cells > MAX_CELLS:
        raise ValueError(
            f"Resolution {resolution} will generate {total_cells} cells which exceeds the limit of {MAX_CELLS}"
        )
    else:
        base_cells = h3.get_res0_cells()
        h3_records = []
        # Progress bar for base cells
        with tqdm(
            total=total_cells, desc="Generating H3 DGGS", unit=" cells"
        ) as pbar:
            for cell in base_cells:
                child_cells = h3.cell_to_children(cell, resolution)
                # Progress bar for child cells
                for child_cell in child_cells:
                    cell_polygon = h32geo(child_cell)
                    h3_id = str(child_cell)
                    num_edges = 6
                    if h3.is_pentagon(h3_id):
                        num_edges = 5
                    record = geodesic_dggs_to_geoseries(
                        "h3", h3_id, resolution, cell_polygon, num_edges
                    )
                    h3_records.append(record)
                    pbar.update(1)

        return gpd.GeoDataFrame(h3_records, geometry="geometry", crs="EPSG:4326")


def h3_grid_within_bbox(resolution, bbox):
    resolution = validate_h3_resolution(resolution)
    bbox_polygon = box(*bbox)  # Create a bounding box polygon
    distance = h3.average_hexagon_edge_length(resolution, unit="m") * 2
    bbox_buffer = geodesic_buffer(bbox_polygon, distance)
    bbox_buffer_cells = h3.geo_to_cells(bbox_buffer, resolution)
    total_cells = len(bbox_buffer_cells)
    if total_cells > MAX_CELLS:
        raise ValueError(
            f"Resolution {resolution} within bounding box {bbox} will generate {total_cells} cells which exceeds the limit of {MAX_CELLS}"
        )
    else:
        h3_records = []
        for bbox_buffer_cell in tqdm(bbox_buffer_cells, desc="Generating H3 DGGS"):
            cell_polygon = h32geo(bbox_buffer_cell)
            if cell_polygon.intersects(bbox_polygon):
                h3_id = str(bbox_buffer_cell)
                num_edges = 6
                if h3.is_pentagon(h3_id):
                    num_edges = 5
                record = geodesic_dggs_to_geoseries(
                    "h3", h3_id, resolution, cell_polygon, num_edges
                )
                h3_records.append(record)

        return gpd.GeoDataFrame(h3_records, geometry="geometry", crs="EPSG:4326")


def h3_grid_ids(resolution):
    """
    Generate a list of H3 cell IDs for the whole world at a given resolution.

    Args:
        resolution (int): H3 resolution [0..15]

    Returns:
        list[str]: List of H3 cell IDs as strings
    """
    resolution = validate_h3_resolution(resolution)
    total_cells = h3.get_num_cells(resolution)
    base_cells = h3.get_res0_cells()
    h3_ids = []
    with tqdm(total=total_cells, desc="Generating H3 IDs", unit=" cells") as pbar:
        for cell in base_cells:
            child_cells = h3.cell_to_children(cell, resolution)
            for child_cell in child_cells:
                h3_ids.append(str(child_cell))
                pbar.update(1)

    return h3_ids


def h3_grid_within_bbox_ids(resolution, bbox):
    """
    Generate a list of H3 cell IDs that intersect a bounding box.

    Args:
        resolution (int): H3 resolution [0..15]
        bbox (list[float]): [min_lon, min_lat, max_lon, max_lat]

    Returns:
        list[str]: List of H3 cell IDs as strings that intersect the bbox
    """
    resolution = validate_h3_resolution(resolution)
    bbox_polygon = box(*bbox)
    distance = h3.average_hexagon_edge_length(resolution, unit="m") * 2
    bbox_buffer = geodesic_buffer(bbox_polygon, distance)
    bbox_buffer_cells = h3.geo_to_cells(bbox_buffer, resolution)
    total_cells = len(bbox_buffer_cells)    
    h3_ids = []
    for bbox_buffer_cell in tqdm(bbox_buffer_cells, total=total_cells, desc="Generating H3 IDs"):
        cell_polygon = h32geo(bbox_buffer_cell)
        if cell_polygon.intersects(bbox_polygon):
            h3_ids.append(str(bbox_buffer_cell))

    return h3_ids


def h3_grid_resample(
    resolution, geojson_features, output_format="geojson"
):
    resolution = validate_h3_resolution(resolution)
    geometries = [
        shape(feature["geometry"]) for feature in geojson_features["features"]
    ]
    unified_geom = unary_union(geometries)
    distance = h3.average_hexagon_edge_length(resolution, unit="m") * 2
    buffered_geom = geodesic_buffer(unified_geom, distance)
    h3_cells = h3.geo_to_cells(buffered_geom, resolution)
    h3_records = []
    for h3_cell in tqdm(h3_cells, desc="Generating H3 DGGS", unit=" cells"):
        cell_polygon = h32geo(h3_cell)
        if cell_polygon.intersects(unified_geom):
            h3_id = str(h3_cell)
            num_edges = 6 if not h3.is_pentagon(h3_id) else 5
            record = geodesic_dggs_to_geoseries(
                "h3", h3_id, resolution, cell_polygon, num_edges
            )
            h3_records.append(record)

    gdf = gpd.GeoDataFrame(h3_records, geometry="geometry", crs="EPSG:4326")
    output_name = f"h3_grid_{resolution}"
    return convert_to_output_format(gdf, output_format, output_name)


def h3grid(resolution, bbox=None, output_format="gpd"):
    """
    Generate H3 grid for pure Python usage.

    Args:
        resolution (int): H3 resolution [0..15]
        bbox (list, optional): Bounding box [min_lon, min_lat, max_lon, max_lat]. Defaults to None (whole world).
        output_format (str, optional): Output format handled entirely by convert_to_output_format

    Returns:
        Delegated to convert_to_output_format
    """
    if bbox is None:
        h3_gdf = h3_grid(resolution)
    else:
        h3_gdf = h3_grid_within_bbox(resolution, bbox)
    output_name = f"h3_grid_{resolution}"
    return convert_to_output_format(h3_gdf, output_format, output_name)


def h3grid_cli():
    """CLI interface for generating H3 grid."""
    parser = argparse.ArgumentParser(description="Generate H3 DGGS.")
    parser.add_argument(
        "-r", "--resolution", type=int, required=True, help="Resolution [0..15]"
    )
    parser.add_argument(
        "-b",
        "--bbox",
        type=float,
        nargs=4,
        help="Bounding box: <min_lon> <min_lat> <max_lon> <max_lat> (default is the whole world)",
    )
    parser.add_argument(
        "-f",
        "--output_format",
        type=str,
        choices= OUTPUT_FORMATS,
        default="gpd"
    )
    args = parser.parse_args()
    try:
        result = h3grid(args.resolution, args.bbox, args.output_format)
        if args.output_format in STRUCTURED_FORMATS:
            print(result)
    except ValueError as e:
        print(f"Error: {str(e)}")
        return
