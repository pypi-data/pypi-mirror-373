"""
Raster to Quadkey DGGS Conversion Module

Converts raster data to Quadkey DGGS format with automatic resolution determination and multi-band support.

Key Functions:
- raster2quadkey(): Main conversion function with multiple output formats
- get_nearest_quadkey_resolution(): Automatically determines optimal Quadkey resolution
- raster2quadkey_cli(): Command-line interface for conversion process
"""

import os
import argparse
from tqdm import tqdm
from vgrid.dggs import tilecode, mercantile
from shapely.geometry import Polygon
from vgrid.stats.quadkeystats import quadkey_metrics
from math import cos, radians
from vgrid.utils.io import validate_quadkey_resolution, convert_to_output_format
from vgrid.utils.constants import OUTPUT_FORMATS, STRUCTURED_FORMATS, DGGS_TYPES, MIN_CELL_AREA
import geopandas as gpd
from pyproj import datadir
os.environ["PROJ_LIB"] = datadir.get_data_dir()
import rasterio
min_res = DGGS_TYPES["quadkey"]["min_res"]
max_res = DGGS_TYPES["quadkey"]["max_res"]

def get_nearest_quadkey_resolution(raster_path):
    with rasterio.open(raster_path) as src:
        transform = src.transform
        crs = src.crs
        pixel_width = transform.a
        pixel_height = -transform.e
        cell_size = pixel_width * pixel_height

        if crs.is_geographic:
            # Latitude of the raster center
            center_latitude = (src.bounds.top + src.bounds.bottom) / 2
            # Convert degrees to meters
            meter_per_degree_lat = 111_320  # Roughly 1 degree latitude in meters
            meter_per_degree_lon = meter_per_degree_lat * cos(radians(center_latitude))

            pixel_width_m = pixel_width * meter_per_degree_lon
            pixel_height_m = pixel_height * meter_per_degree_lat
            cell_size = pixel_width_m * pixel_height_m

    min_diff = float("inf")
    nearest_resolution = min_res

    for res in range(min_res, max_res + 1):
        _, _, avg_area, _ = quadkey_metrics(res)
        if avg_area < MIN_CELL_AREA:
            break       
        diff = abs(avg_area - cell_size)
        # If the difference is smaller than the current minimum, update the nearest resolution
        if diff < min_diff:
            min_diff = diff
            nearest_resolution = res

    return cell_size, nearest_resolution


def raster2quadkey(raster_path, resolution=None, output_format="gpd"):
    """Convert raster to quadkey output_format

    Args:
        raster_path (str): Path to input raster file
        resolution (int, optional): Quadkey resolution level [0-29]. If None, will be determined automatically
        output_format (str, optional): Output output_format, see supported formats

    Returns:
        Various formats based on output_format parameter
    """
    # Step 1: Determine the nearest quadkey resolution if none is provided
    if resolution is None:
        cell_size, resolution = get_nearest_quadkey_resolution(raster_path)
        print(f"Cell size: {cell_size} m2")
        print(f"Nearest Quadkey resolution determined: {resolution}")
    else:
        resolution = validate_quadkey_resolution(resolution)
    # Open the raster file to get metadata and data
    with rasterio.open(raster_path) as src:
        raster_data = src.read()  # Read all bands
        transform = src.transform
        width, height = src.width, src.height
        band_count = src.count  # Number of bands in the raster

    # Collect band values during the pixel scan, storing the first sample per Quadkey cell
    quadkey_band_values = {}
    for row in range(height):
        for col in range(width):
            lon, lat = transform * (col, row)
            quadkey_id = tilecode.latlon2quadkey(lat, lon, resolution)
            if quadkey_id not in quadkey_band_values:
                vals = raster_data[:, int(row), int(col)]
                quadkey_band_values[quadkey_id] = [
                    (v.item() if hasattr(v, "item") else v) for v in vals
                ]

    properties = []
    for quadkey_id, band_values in tqdm(quadkey_band_values.items(),
                                        desc="Converting raster to Quadkey", unit=" cells"):
        tile = mercantile.quadkey_to_tile(quadkey_id)
        z = tile.z
        x = tile.x
        y = tile.y
        bounds = mercantile.bounds(x, y, z)
        min_lat, min_lon = bounds.south, bounds.west
        max_lat, max_lon = bounds.north, bounds.east
        cell_polygon = Polygon([
            [min_lon, min_lat],
            [max_lon, min_lat],
            [max_lon, max_lat],
            [min_lon, max_lat],
            [min_lon, min_lat],
        ])
        base_props = {"quadkey": quadkey_id, "geometry": cell_polygon}
        band_props = {f"band_{i + 1}": band_values[i] for i in range(band_count)}
        base_props.update(band_props)
        properties.append(base_props)
    gdf = gpd.GeoDataFrame(properties, geometry="geometry", crs="EPSG:4326")

    # Use centralized output utility
    base_name = os.path.splitext(os.path.basename(raster_path))[0]
    output_name = f"{base_name}2quadkey" if output_format is not None else None
    return convert_to_output_format(gdf, output_format, output_name)


def raster2quadkey_cli():
    parser = argparse.ArgumentParser(
        description="Convert Raster in Geographic CRS to Quadkey DGGS"
    )
    parser.add_argument("-raster", type=str, required=True, help="Raster file path")

    parser.add_argument(
        "-r",
        "--resolution",
        type=int,
        required=False,
        default=None,
        help=f"Quadkey resolution [{min_res}..{max_res}]",
    )

    parser.add_argument(
        "-f",
        "--output_format",
        type=str,
        choices=OUTPUT_FORMATS,
        default="gpd",
    )

    args = parser.parse_args()
    raster = args.raster
    resolution = args.resolution
    output_format = args.output_format

    if not os.path.exists(raster):
        print(f"Error: The file {raster} does not exist.")
        return

    result = raster2quadkey(raster, resolution, output_format)
    if output_format in STRUCTURED_FORMATS:
        print(result)


if __name__ == "__main__":
    raster2quadkey_cli()
