"""
Raster to OLC DGGS Conversion Module

Converts raster data to OLC (Open Location Code) DGGS format with automatic resolution determination and multi-band support.

Key Functions:
- raster2olc(): Main conversion function with multiple output formats
- get_nearest_olc_resolution(): Automatically determines optimal OLC resolution
- raster2olc_cli(): Command-line interface for conversion process
"""

import os
import argparse
from tqdm import tqdm
from shapely.geometry import Polygon
from vgrid.stats.olcstats import olc_metrics
from math import cos, radians
from vgrid.conversion.latlon2dggs import latlon2olc
from vgrid.utils.io import validate_olc_resolution, convert_to_output_format
from vgrid.conversion.dggs2geo.olc2geo import olc2geo
from vgrid.utils.constants import OUTPUT_FORMATS, STRUCTURED_FORMATS, MIN_CELL_AREA, DGGS_TYPES
import geopandas as gpd
from pyproj import datadir
os.environ["PROJ_LIB"] = datadir.get_data_dir()
import rasterio 
olc_res = [2, 4, 6, 8, 10, 11, 12, 13, 14, 15]

def get_nearest_olc_resolution(raster_path):
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

    # Find the nearest s2 resolution by comparing the pixel size to the s2 edge lengths
    nearest_resolution = None
    min_diff = float("inf")

    for res in olc_res:
        _, _, avg_area, _ = olc_metrics(res)
        if avg_area < MIN_CELL_AREA:
            break
        diff = abs(avg_area - cell_size)
        # If the difference is smaller than the current minimum, update the nearest resolution
        if diff < min_diff:
            min_diff = diff
            nearest_resolution = res

    return cell_size, nearest_resolution



def raster2olc(raster_path, resolution=None, output_format="gpd"):
    # Step 1: Determine the nearest olc resolution if none is provided
    if resolution is None:
        cell_size, resolution = get_nearest_olc_resolution(raster_path)
        print(f"Cell size: {cell_size} m2")
        print(f"Nearest OLC resolution determined: {resolution}")
    else:
        resolution = validate_olc_resolution(resolution)
    # Open the raster file to get metadata and data
    with rasterio.open(raster_path) as src:
        raster_data = src.read()  # Read all bands
        transform = src.transform
        width, height = src.width, src.height
        band_count = src.count  # Number of bands in the raster

    # Collect band values during the pixel scan, storing the first sample per OLC cell
    olc_band_values = {}
    for row in range(height):
        for col in range(width):
            lon, lat = transform * (col, row)
            olc_id = latlon2olc(lat, lon, resolution)
            if olc_id not in olc_band_values:
                vals = raster_data[:, int(row), int(col)]
                olc_band_values[olc_id] = [
                    (v.item() if hasattr(v, "item") else v) for v in vals
                ]

    properties = []
    for olc_id, band_values in tqdm(olc_band_values.items(), desc="Converting raster to OLC", unit=" cells"):
        cell_polygon = olc2geo(olc_id)
        min_lon, min_lat, max_lon, max_lat = cell_polygon.bounds
        cell_polygon = Polygon([
            [min_lon, min_lat],
            [max_lon, min_lat],
            [max_lon, max_lat],
            [min_lon, max_lat],
            [min_lon, min_lat],
        ])
        base_props = {"olc": olc_id, "geometry": cell_polygon}
        band_props = {f"band_{i + 1}": band_values[i] for i in range(band_count)}
        base_props.update(band_props)
        properties.append(base_props)
    gdf = gpd.GeoDataFrame(properties, geometry="geometry", crs="EPSG:4326")

    # Use centralized output utility
    base_name = os.path.splitext(os.path.basename(raster_path))[0]
    output_name = f"{base_name}2olc" if output_format is not None else None
    return convert_to_output_format(gdf, output_format, output_name)


def raster2olc_cli():
    """Command line interface for raster to OLC conversion"""
    parser = argparse.ArgumentParser(
        description="Convert Raster in Geographic CRS to OLC/ Google Plus Code DGGS"
    )
    parser.add_argument("-raster", type=str, required=True, help="Raster file path")

    parser.add_argument(
        "-r",
        "--resolution",
        type=int,
        required=False,
        choices=olc_res,    
        default=None,
        help=f"OLC resolution",
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

    result = raster2olc(raster, resolution, output_format)
    if output_format in STRUCTURED_FORMATS:
        print(result)


if __name__ == "__main__":
    raster2olc_cli()