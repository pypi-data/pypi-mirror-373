"""
Raster to H3 DGGS Conversion Module

Converts raster data to H3 (Hierarchical Hexagonal Grid) DGGS format with automatic resolution determination and multi-band support.

Key Functions:
- raster2h3(): Main conversion function with multiple output formats
- get_nearest_h3_resolution(): Automatically determines optimal H3 resolution
- raster2h3_cli(): Command-line interface for conversion process
"""

import os
import argparse
from math import cos, radians
from tqdm import tqdm
import h3
from vgrid.utils.geometry import geodesic_dggs_to_geoseries
from vgrid.utils.io import validate_h3_resolution, convert_to_output_format
from vgrid.utils.constants import OUTPUT_FORMATS, STRUCTURED_FORMATS, DGGS_TYPES, MIN_CELL_AREA
from vgrid.conversion.dggs2geo.h32geo import h32geo
import geopandas as gpd
import os
from pyproj import datadir
os.environ["PROJ_LIB"] = datadir.get_data_dir()
import rasterio
min_res = DGGS_TYPES["h3"]["min_res"]
max_res = DGGS_TYPES["h3"]["max_res"]

def get_nearest_h3_resolution(raster_path):
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
    # Check resolutions from 0 to 15
    nearest_resolution = min_res

    for res in range(min_res, max_res + 1):
        avg_area = h3.average_hexagon_area(res, unit="m^2")
        if avg_area < MIN_CELL_AREA:
            break
        diff = abs(avg_area - cell_size)
        # If the difference is smaller than the current minimum, update the nearest resolution
        if diff < min_diff:
            min_diff = diff
            nearest_resolution = res

    return cell_size, nearest_resolution


def raster2h3(raster_path, resolution=None, output_format="gpd"):
    """
    Convert raster data to H3 DGGS format.
    
    Args:
        raster_path (str): Path to the raster file
        resolution (int, optional): H3 resolution [0..15]. If None, automatically determined
        output_format (str, optional): Output format. Options:
            - None: Returns GeoPandas GeoDataFrame (default)
            - "gpd": Returns GeoPandas GeoDataFrame
            - "csv": Returns CSV file path
            - "geojson": Returns GeoJSON file path
            - "geojson_dict": Returns GeoJSON FeatureCollection as Python dict
            - "parquet": Returns Parquet file path
            - "shapefile"/"shp": Returns Shapefile file path
            - "gpkg"/"geopackage": Returns GeoPackage file path
    Returns:
        Various formats based on output_format parameter
    Raises:
        ValueError: If resolution is not in valid range [0..15]
        ImportError: If required dependencies are not available for specific formats
    """
    # Step 1: Determine the nearest H3 resolution if none is provided
    if resolution is None:
        cell_size, resolution = get_nearest_h3_resolution(raster_path)
        print(f"Cell size: {cell_size} m2")
        print(f"Nearest H3 resolution determined: {resolution}")
    else:
        resolution = validate_h3_resolution(resolution)

    # Open the raster file to get metadata and data
    with rasterio.open(raster_path) as src:
        raster_data = src.read()  # Read all bands
        transform = src.transform
        width, height = src.width, src.height
        band_count = src.count  # Number of bands in the raster

    # Collect band values during the pixel scan, storing the first sample per H3 cell
    h3_ids_band_values = {}
    for row in range(height):
        for col in range(width):
            lon, lat = transform * (col, row)
            h3_id = h3.latlng_to_cell(lat, lon, resolution)
            if h3_id not in h3_ids_band_values:
                vals = raster_data[:, int(row), int(col)]
                # Convert NumPy scalars to native Python types
                h3_ids_band_values[h3_id] = [
                    (v.item() if hasattr(v, "item") else v) for v in vals
                ]

    properties = []
    for h3_id, band_values in tqdm(h3_ids_band_values.items(), desc="Converting raster to H3", unit=" cells"):
        cell_polygon = h32geo(h3_id)
        num_edges = 6
        if h3.is_pentagon(h3_id):
            num_edges = 5
        base_props = geodesic_dggs_to_geoseries(
            "h3", h3_id, resolution, cell_polygon, num_edges
        )
        band_properties = {
            f"band_{i + 1}": band_values[i]
            for i in range(band_count)
        }
        base_props.update(band_properties)
        properties.append(base_props)
        
  
    gdf = gpd.GeoDataFrame(properties, geometry="geometry", crs="EPSG:4326")

    base_name = os.path.splitext(os.path.basename(raster_path))[0]
    output_name = f"{base_name}2h3" if output_format is not None else None
    return convert_to_output_format(gdf, output_format, output_name)


def raster2h3_cli():
    parser = argparse.ArgumentParser(
        description="Convert Raster in Geographic CRS to H3 DGGS"
    )
    parser.add_argument("-raster", type=str, required=True, help="Raster file path")

    parser.add_argument(
        "-r",
        "--resolution",
        type=int,
        required=False,
        default=None,
        help=f"H3 resolution [{min_res}..{max_res}]",
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
    
    result = raster2h3(raster, resolution, output_format)
    if output_format in STRUCTURED_FORMATS:
        print(result)
if __name__ == "__main__":
    raster2h3_cli()
