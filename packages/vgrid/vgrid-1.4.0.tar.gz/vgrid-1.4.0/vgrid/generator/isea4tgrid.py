"""
ISEA4T Grid Generator Module

Generates ISEA4T DGGS grids for specified resolutions with automatic cell generation and validation using hierarchical triangular grid system.

Key Functions:
- isea4t_grid(): Main grid generation function for whole world
- isea4t_grid_within_bbox(): Grid generation within bounding box
- isea4tgrid(): User-facing function with multiple output formats
- isea4tgrid_cli(): Command-line interface for grid generation
"""

import argparse
from shapely.ops import unary_union
from tqdm import tqdm
from shapely.geometry import box, shape
import geopandas as gpd
import platform
if platform.system() == "Windows":
    from vgrid.dggs.eaggr.eaggr import Eaggr
    from vgrid.dggs.eaggr.shapes.dggs_cell import DggsCell
    from vgrid.dggs.eaggr.enums.model import Model
    from vgrid.dggs.eaggr.enums.shape_string_format import ShapeStringFormat
    from vgrid.utils.constants import ISEA4T_RES_ACCURACY_DICT
    isea4t_dggs = Eaggr(Model.ISEA4T)

from vgrid.utils.constants import MAX_CELLS, ISEA4T_BASE_CELLS, OUTPUT_FORMATS, STRUCTURED_FORMATS
from vgrid.conversion.dggs2geo.isea4t2geo import isea4t2geo
from vgrid.utils.geometry import  geodesic_dggs_to_geoseries, isea4t_cell_to_polygon
from vgrid.utils.io import validate_isea4t_resolution, convert_to_output_format

def get_isea4t_children_cells(base_cells, target_resolution):
    """
    Recursively generate DGGS cells for the desired resolution.
    """
    current_cells = base_cells
    for res in range(target_resolution):
        next_cells = []
        for cell in current_cells:
            children = isea4t_dggs.get_dggs_cell_children(DggsCell(cell))
            next_cells.extend([child._cell_id for child in children])
        current_cells = next_cells
    return current_cells


def get_isea4t_children_cells_within_bbox(
    bounding_cell, bbox, target_resolution
):
    current_cells = [
        bounding_cell
    ]  # Start with a list containing the single bounding cell
    bounding_resolution = len(bounding_cell) - 2

    for res in range(bounding_resolution, target_resolution):
        next_cells = []
        for cell in current_cells:
            # Get the child cells for the current cell
            children = isea4t_dggs.get_dggs_cell_children(DggsCell(cell))
            for child in children:
                # Convert child cell to geometry
                child_shape = isea4t_cell_to_polygon(child)
                if child_shape.intersects(bbox):
                    # Add the child cell ID to the next_cells list
                    next_cells.append(child._cell_id)
        if not next_cells:  # Break early if no cells remain
            break
        current_cells = (
            next_cells  # Update current_cells to process the next level of children
        )

    return current_cells


def isea4t_grid(resolution):
    resolution = validate_isea4t_resolution(resolution) 
    children = get_isea4t_children_cells(ISEA4T_BASE_CELLS, resolution)
    isea4t_rows = []
    for child in tqdm(children, desc="Generating ISEA4T DGGS", unit=" cells"):
        isea4t_cell = DggsCell(child)        
        isea4t_id = isea4t_cell.get_cell_id()
        cell_polygon = isea4t2geo(isea4t_id)
        num_edges = 3
        row = geodesic_dggs_to_geoseries(
            "isea4t", isea4t_id, resolution, cell_polygon, num_edges
        )
        isea4t_rows.append(row)
    return gpd.GeoDataFrame(isea4t_rows, geometry="geometry", crs="EPSG:4326")


def isea4t_grid_within_bbox(resolution, bbox):
    resolution = validate_isea4t_resolution(resolution)
    accuracy = ISEA4T_RES_ACCURACY_DICT.get(resolution)
    bounding_box = box(*bbox)
    bounding_box_wkt = bounding_box.wkt  # Create a bounding box polygon
    isea4t_shapes = isea4t_dggs.convert_shape_string_to_dggs_shapes(
        bounding_box_wkt, ShapeStringFormat.WKT, accuracy
    )
    isea4t_shape = isea4t_shapes[0]
    bbox_cells = isea4t_shape.get_shape().get_outer_ring().get_cells()
    bounding_cell = isea4t_dggs.get_bounding_dggs_cell(bbox_cells)
    bounding_children = get_isea4t_children_cells_within_bbox(
        bounding_cell.get_cell_id(), bounding_box, resolution
    )
    isea4t_rows = []
    for child in tqdm(bounding_children, desc="Generating ISEA4T DGGS", unit=" cells"):
        isea4t_cell = DggsCell(child)
        isea4t_id = isea4t_cell.get_cell_id()
        cell_polygon = isea4t2geo(isea4t_id)
        num_edges = 3
        row = geodesic_dggs_to_geoseries(
            "isea4t", isea4t_id, resolution, cell_polygon, num_edges
        )
        isea4t_rows.append(row)
    return gpd.GeoDataFrame(isea4t_rows, geometry="geometry", crs="EPSG:4326")


def isea4t_grid_ids(resolution):
    """
    Return a list of ISEA4T cell IDs for the whole world at a given resolution.
    """
    resolution = validate_isea4t_resolution(resolution)
    children = get_isea4t_children_cells(ISEA4T_BASE_CELLS, resolution)
    return [str(cid) for cid in children]


def isea4t_grid_within_bbox_ids(resolution, bbox):
    """
    Return a list of ISEA4T cell IDs intersecting the given bounding box at a given resolution.
    """
    resolution = validate_isea4t_resolution(resolution)
    accuracy = ISEA4T_RES_ACCURACY_DICT.get(resolution)
    bounding_box = box(*bbox)
    bounding_box_wkt = bounding_box.wkt
    isea4t_shapes = isea4t_dggs.convert_shape_string_to_dggs_shapes(
        bounding_box_wkt, ShapeStringFormat.WKT, accuracy
    )
    isea4t_shape = isea4t_shapes[0]
    bbox_cells = isea4t_shape.get_shape().get_outer_ring().get_cells()
    bounding_cell = isea4t_dggs.get_bounding_dggs_cell(bbox_cells)
    bounding_children = get_isea4t_children_cells_within_bbox(
        bounding_cell.get_cell_id(), bounding_box, resolution
    )
    return list(bounding_children or [])


def isea4t_grid_resample(resolution, geojson_features):
    resolution = validate_isea4t_resolution(resolution)
    accuracy = ISEA4T_RES_ACCURACY_DICT.get(resolution)
    geometries = [
        shape(feature["geometry"]) for feature in geojson_features["features"]
    ]
    unified_geom = unary_union(geometries)
    unified_geom_wkt = unified_geom.wkt
    isea4t_shapes = isea4t_dggs.convert_shape_string_to_dggs_shapes(
        unified_geom_wkt, ShapeStringFormat.WKT, accuracy
    )
    isea4t_shape = isea4t_shapes[0]
    bbox_cells = isea4t_shape.get_shape().get_outer_ring().get_cells()
    bounding_cell = isea4t_dggs.get_bounding_dggs_cell(bbox_cells)
    bounding_children = get_isea4t_children_cells_within_bbox(
        bounding_cell.get_cell_id(), unified_geom, resolution
    )
    isea4t_rows = []
    for child in tqdm(bounding_children, desc="Generating ISEA4T DGGS", unit=" cells"):
        isea4t_cell = DggsCell(child)
        isea4t_id = isea4t_cell.get_cell_id()
        cell_polygon = isea4t2geo(isea4t_id)
        num_edges = 3
        if not cell_polygon.intersects(unified_geom):
            continue
        row = geodesic_dggs_to_geoseries(
            "isea4t", isea4t_id, resolution, cell_polygon, num_edges
        )
        isea4t_rows.append(row)
    return gpd.GeoDataFrame(isea4t_rows, geometry="geometry", crs="EPSG:4326")


def isea4tgrid(resolution, bbox=None, output_format="gpd"):
    # Allow running on all platforms
    
    if bbox is None:
        bbox = [-180, -90, 180, 90]
        total_cells = 20 * (4 ** resolution)
        if total_cells > MAX_CELLS:
            raise ValueError(
                f"Resolution {resolution} will generate {total_cells} cells which exceeds the limit of {MAX_CELLS}"
            )
        gdf = isea4t_grid(resolution)
    else:
        gdf = isea4t_grid_within_bbox(resolution, bbox)
    output_name = f"isea4t_grid_{resolution}"
    return convert_to_output_format(gdf, output_format, output_name)


def isea4tgrid_cli():
    parser = argparse.ArgumentParser(description="Generate Open-Eaggr ISEA4T DGGS.")
    parser.add_argument(
        "-r", "--resolution", type=int, required=True, help="Resolution [0..39]"
    )
    parser.add_argument(
        "-b",
        "--bbox",
        type=float,
        nargs=4,
        help="Bounding box in the output_format: min_lon min_lat max_lon max_lat (default is the whole world)",
    )
    parser.add_argument(
        "-f",
        "--output_format",
        type=str,
        choices=OUTPUT_FORMATS,
        default="gpd",
    )
    args = parser.parse_args()
    resolution = args.resolution
    bbox = args.bbox if args.bbox else [-180, -90, 180, 90]
    if platform.system() == "Windows":
        try:
            result = isea4tgrid(resolution, bbox, args.output_format)
            if args.output_format in STRUCTURED_FORMATS:
                print(result)
        except ValueError as e:
            print(f"Error: {str(e)}")
            return
    else:
        print("ISEA4T is only supported on Windows systems")

if __name__ == "__main__":
    isea4tgrid_cli()
