"""
GEOREF Grid Generator Module

Generates GEOREF DGGS grids for specified resolutions with automatic cell generation and validation using World Geographic Reference System.

Key Functions:
- georef_grid(): Main grid generation function with bounding box support
- georef_grid_ids(): Returns list of GEOREF IDs for given bbox and resolution
- georefgrid(): User-facing function with multiple output formats
- georefgrid_cli(): Command-line interface for grid generation
"""
import json
import argparse
from tqdm import tqdm
from shapely.geometry import Polygon, box
import numpy as np
from vgrid.dggs import georef
from vgrid.utils.constants import MAX_CELLS, OUTPUT_FORMATS, STRUCTURED_FORMATS
from vgrid.utils.geometry import graticule_dggs_to_geoseries
import geopandas as gpd
from vgrid.utils.io import validate_georef_resolution, convert_to_output_format
from vgrid.utils.constants import GEOREF_RESOLUTION_DEGREES

def georef_grid(bbox, resolution):
    resolution = validate_georef_resolution(resolution) # 0..4
    lon_min, lat_min, lon_max, lat_max = bbox
    resolution_degrees = GEOREF_RESOLUTION_DEGREES.get(resolution)
    longitudes = np.arange(lon_min, lon_max, resolution_degrees)
    latitudes = np.arange(lat_min, lat_max, resolution_degrees) 
    num_cells = len(longitudes) * len(latitudes)

    if num_cells > MAX_CELLS:
        print(f"Resolution {resolution} will generate {num_cells} cells which exceeds the limit of {MAX_CELLS}.")
        print("Please select a smaller resolution and try again.")
        return
    georef_records = []

    with tqdm(total=num_cells, desc="Generating GEOREF DGGS", unit=" cells") as pbar:
        for lon in longitudes:
            for lat in latitudes:
                cell_polygon = Polygon(
                    box(lon, lat, lon + resolution_degrees, lat + resolution_degrees)
                )
                georef_id = georef.encode(lat, lon, resolution)
                georef_record = graticule_dggs_to_geoseries(
                    "georef", georef_id, resolution, cell_polygon
                )
                georef_records.append(georef_record)
                pbar.update(1)

    return gpd.GeoDataFrame(georef_records, geometry="geometry", crs="EPSG:4326")


def georef_grid_ids(bbox, resolution):
    """
    Return a list of GEOREF IDs for a given bounding box at the specified resolution.

    Args:
        bbox (list[float]): [min_lon, min_lat, max_lon, max_lat]
        resolution (int): GEOREF resolution [0..4]

    Returns:
        list[str]: List of GEOREF IDs
    """
    resolution = validate_georef_resolution(resolution)  # 0..4
    lon_min, lat_min, lon_max, lat_max = bbox
    resolution_degrees = GEOREF_RESOLUTION_DEGREES.get(resolution)
    longitudes = np.arange(lon_min, lon_max, resolution_degrees)
    latitudes = np.arange(lat_min, lat_max, resolution_degrees)

    num_cells = len(longitudes) * len(latitudes)
    ids = []
    with tqdm(total=num_cells, desc="Generating GEOREF IDs", unit=" cells") as pbar:
        for lon in longitudes:
            for lat in latitudes:
                georef_id = georef.encode(lat, lon, resolution)
                ids.append(georef_id)
                pbar.update(1)

    return ids


def georefgrid(resolution, bbox=None, output_format="gpd"):
    """
    Generate GEOREF grid for pure Python usage.

    Args:
        resolution (int): GEOREF resolution [0..4]
        bbox (list, optional): Bounding box [min_lon, min_lat, max_lon, max_lat]. Defaults to None (whole world).
        output_format (str, optional): Output format ('geojson', 'csv', 'geo', 'gpd', 'shapefile', 'gpkg', 'parquet', or None for list of GEOREF IDs).

    Returns:
        dict, list, or str: Output in the requested format or file path.
    """
    if bbox is None:
        bbox = [-180, -90, 180, 90]
    gdf = georef_grid(bbox, resolution)
    output_name = f"georef_grid_{resolution}"
    return convert_to_output_format(gdf, output_format, output_name)


def georefgrid_cli():
    parser = argparse.ArgumentParser(description="Generate GEOREF DGGS")
    parser.add_argument(
        "-r", "--resolution", type=int, required=True, help="Resolution [0..4]"
    )
    parser.add_argument(
        "-b",
        "--bbox",
        type=float,
        nargs=4,
        help="Bounding box in the format: min_lon min_lat max_lon max_lat (default is the whole world)",
    )
    parser.add_argument(
        "-f",
        "--output_format",
        type=str,
        choices=OUTPUT_FORMATS,
        default="gpd",
    )
    args = parser.parse_args()
    try:
        result = georefgrid(args.resolution, args.bbox, args.output_format)
        if args.output_format in STRUCTURED_FORMATS:
            print(result)
    except ValueError as e:
        print(f"Error: {str(e)}")
        return


if __name__ == "__main__":
    georefgrid_cli()
