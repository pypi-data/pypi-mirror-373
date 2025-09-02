"""
Raster to ISEA4T DGGS Conversion Module

Converts raster data to ISEA4T DGGS format with automatic resolution determination and multi-band support.

Key Functions:
- raster2isea4t(): Main conversion function with multiple output formats
- get_nearest_isea4t_resolution(): Automatically determines optimal ISEA4T resolution
- raster2isea4t_cli(): Command-line interface for conversion process
"""

import os
import argparse
from math import cos, radians
from tqdm import tqdm

from vgrid.stats.isea4tstats import isea4t_metrics
from vgrid.utils.constants import ISEA4T_RES_ACCURACY_DICT
from vgrid.utils.geometry import geodesic_dggs_metrics  
from vgrid.conversion.dggs2geo.isea4t2geo import isea4t2geo

from vgrid.utils.io import validate_isea4t_resolution, convert_to_output_format
from vgrid.utils.constants import OUTPUT_FORMATS, STRUCTURED_FORMATS, DGGS_TYPES, MIN_CELL_AREA
from pyproj import datadir
os.environ["PROJ_LIB"] = datadir.get_data_dir()
import rasterio
min_res = DGGS_TYPES["isea4t"]["min_res"]
max_res = DGGS_TYPES["isea4t"]["max_res"]
import platform
if platform.system() == "Windows":
    from vgrid.dggs.eaggr.eaggr import Eaggr
    from vgrid.dggs.eaggr.shapes.dggs_cell import DggsCell
    from vgrid.dggs.eaggr.enums.model import Model
    from vgrid.dggs.eaggr.shapes.lat_long_point import LatLongPoint
    isea4t_dggs = Eaggr(Model.ISEA4T)

# Optional imports for additional output formats
import geopandas as gpd


def get_nearest_isea4t_resolution(raster_path):
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
            meter_per_degree_lon = meter_per_degree_lat * cos(
                radians(center_latitude)
            )

            pixel_width_m = pixel_width * meter_per_degree_lon
            pixel_height_m = pixel_height * meter_per_degree_lat
            cell_size = pixel_width_m * pixel_height_m

    min_diff = float("inf")
    nearest_resolution = min_res

    for res in range(min_res, max_res + 1):
        _, _, avg_area, _ = isea4t_metrics(res)
        if avg_area < MIN_CELL_AREA:
            break       
        diff = abs(avg_area - cell_size)
        # If the difference is smaller than the current minimum, update the nearest resolution
        if diff < min_diff:
            min_diff = diff
            nearest_resolution = res

    return cell_size, nearest_resolution


def raster2isea4t(raster_path, resolution=None, output_format="gpd"):
    # Step 1: Determine the nearest isea4t resolution if none is provided
    if resolution is None:
        cell_size, resolution = get_nearest_isea4t_resolution(raster_path)
        print(f"Cell size: {cell_size} m2")
        print(f"Nearest ISEA4T resolution determined: {resolution}")
    else:   
        resolution = validate_isea4t_resolution(resolution)         
    # Open the raster file to get metadata and data
    with rasterio.open(raster_path) as src:
        raster_data = src.read()  # Read all bands
        transform = src.transform
        width, height = src.width, src.height
        band_count = src.count  # Number of bands in the raster

    # Collect band values during the pixel scan, storing the first sample per ISEA4T cell
    isea4t_ids_band_values = {}
    for row in range(height):
        for col in range(width):
            lon, lat = transform * (col, row)
            max_accuracy = ISEA4T_RES_ACCURACY_DICT[39]
            lat_long_point = LatLongPoint(lat, lon, max_accuracy)
            isea4t_cell_max_accuracy = isea4t_dggs.convert_point_to_dggs_cell(lat_long_point)
            cell_id_len = resolution + 2
            isea4t_cell = DggsCell(isea4t_cell_max_accuracy._cell_id[:cell_id_len])
            isea4t_id = isea4t_cell._cell_id
            if isea4t_id not in isea4t_ids_band_values:
                vals = raster_data[:, int(row), int(col)]
                isea4t_ids_band_values[isea4t_id] = [
                    (v.item() if hasattr(v, "item") else v) for v in vals
                ]

    properties = []
    for isea4t_id, band_values in tqdm(isea4t_ids_band_values.items(), desc="Converting raster to ISEA4T", unit=" cells"):
        cell_polygon = isea4t2geo(isea4t_id)
        num_edges = 3
        centroid_lat, centroid_lon, avg_edge_len, cell_area, cell_perimeter = geodesic_dggs_metrics(
            cell_polygon, num_edges
        )
        base_props = {
            "isea4t": isea4t_id,
            "resolution": resolution,
            "center_lat": centroid_lat,
            "center_lon": centroid_lon,
            "avg_edge_len": avg_edge_len,
            "cell_area": cell_area,
            "cell_perimeter": cell_perimeter,
            "geometry": cell_polygon,
        }
        band_properties = {f"band_{i + 1}": band_values[i] for i in range(band_count)}
        base_props.update(band_properties)
        properties.append(base_props)
    gdf = gpd.GeoDataFrame(properties, geometry="geometry", crs="EPSG:4326")

    # Use centralized output utility
    base_name = os.path.splitext(os.path.basename(raster_path))[0]
    output_name = f"{base_name}2isea4t" if output_format is not None else None
    return convert_to_output_format(gdf, output_format, output_name)


def raster2isea4t_cli():
    parser = argparse.ArgumentParser(
        description="Convert Raster in Geographic CRS to Open-Eaggr ISEA4T DGGS"
    )
    parser.add_argument("-raster", type=str, required=True, help="Raster file path")

    parser.add_argument(
        "-r",
        "--resolution",
        type=int,
        required=False,
        default=None,
        help=f"ISEA4T resolution [{min_res}..{max_res}]",
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

    if platform.system() == "Windows":
        result = raster2isea4t(raster, resolution, output_format)
        if output_format in STRUCTURED_FORMATS:
            print(result)
    else:
        print("ISEA4T is only supported on Windows systems")

if __name__ == "__main__":
    raster2isea4t_cli()
