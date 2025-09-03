"""
Raster to DGGAL DGGS Conversion Module

Converts raster data to DGGAL (Discrete Global Grids with Adaptive Localization) DGGS format with automatic resolution determination and multi-band support.

Key Functions:
- raster2dggal(): Main conversion function with multiple output formats
- get_nearest_dggal_resolution(): Automatically determines optimal DGGAL resolution
- raster2dggal_cli(): Command-line interface for conversion process
"""

import os
import argparse
from tqdm import tqdm       
from vgrid.utils.io import convert_to_output_format
from vgrid.utils.constants import OUTPUT_FORMATS, STRUCTURED_FORMATS, DGGAL_TYPES, MIN_CELL_AREA
import geopandas as gpd
from vgrid.utils.io import validate_dggal_resolution, validate_dggal_type       
from vgrid.stats.dggalstats import dggal_metrics
from vgrid.conversion.latlon2dggs import latlon2dggal
from vgrid.conversion.dggs2geo.dggal2geo import dggal2geo   
from vgrid.utils.geometry import geodesic_dggs_metrics
from pyproj import datadir
os.environ["PROJ_LIB"] = datadir.get_data_dir()
import rasterio
import math
from dggal import *
app = Application(appGlobals=globals())
pydggal_setup(app)
    

def get_nearest_dggal_resolution (dggs_type,raster_path):       
    """
    Determine the nearest DGGAL resolution based on the raster cell size.
    """
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
            meter_per_degree_lon = meter_per_degree_lat * math.cos(math.radians(center_latitude))

            pixel_width_m = pixel_width * meter_per_degree_lon
            pixel_height_m = pixel_height * meter_per_degree_lat
            cell_size = pixel_width_m * pixel_height_m

    min_diff = float("inf")
    min_res = int(DGGAL_TYPES[dggs_type]["min_res"])
    max_res = int(DGGAL_TYPES[dggs_type]["max_res"])
    nearest_resolution = min_res
    for res in range(min_res, max_res + 1):
        _, _, avg_area, _ = dggal_metrics(dggs_type, res)
        if avg_area < MIN_CELL_AREA:
            break
        diff = math.fabs(avg_area - cell_size)  
        # If the difference is smaller than the current minimum, update the nearest resolution
        if diff < min_diff:
            min_diff = diff
            nearest_resolution = res

    return cell_size, nearest_resolution


def raster2dggal(dggs_type: str, raster_path, resolution: int | None = None, output_format: str = "gpd"):   
    """
    Convert raster data to DGGAL grid cells for a given type and resolution.

    - raster_path: path to raster in geographic CRS (EPSG:4326)
    - dggs_type: one of DGGAL_TYPES
    - resolution: integer resolution understood by the `dgg` CLI for the chosen type. If None, auto-selected
    - output_format: see OUTPUT_FORMATS
    """
    dggs_type = validate_dggal_type(dggs_type)
    # Auto-select resolution if not provided
    if resolution is None:
        cell_size, resolution = get_nearest_dggal_resolution(dggs_type, raster_path)    
        print(f"Cell size: {cell_size} m2")
        print(f"Nearest {dggs_type.upper()} resolution determined: {resolution}")
    else:
        resolution = validate_dggal_resolution(dggs_type, resolution)

    # Open the raster file to get metadata and data
    with rasterio.open(raster_path) as src:
        raster_data = src.read()  # Read all bands
        transform = src.transform
        width, height = src.width, src.height
        band_count = src.count  # Number of bands in the raster

    # Collect band values during the pixel scan, storing the first sample per DGGAL cell
    zone_ids_band_values = {}
    for row in range(height):
        for col in range(width):
            lon, lat = transform * (col, row)
            try:
                zone_id = latlon2dggal(dggs_type, lat, lon, resolution)
                if zone_id not in zone_ids_band_values:
                    vals = raster_data[:, int(row), int(col)]
                    zone_ids_band_values[zone_id] = [
                        (v.item() if hasattr(v, "item") else v) for v in vals
                    ]
            except Exception:
                continue
    # Build GeoDataFrame as the base
    properties = []
    for zone_id, band_values in tqdm(zone_ids_band_values.items(), desc="Converting raster to DGGAL", unit=" cells"):
        try:
            # Get zone object to get resolution and edge count
            dggs_class_name = DGGAL_TYPES[dggs_type]["class_name"]
            dggrs = globals()[dggs_class_name]()
            zone = dggrs.getZoneFromTextID(zone_id)
            num_edges = dggrs.countZoneEdges(zone)
            
            # Convert zone to geometry using dggal2geo
            cell_polygon = dggal2geo(dggs_type, zone_id)
            
            centroid_lat, centroid_lon, avg_edge_len, cell_area, cell_perimeter = geodesic_dggs_metrics(cell_polygon, num_edges)
            base_props = {
                f"dggal_{dggs_type}": zone_id,
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
        except Exception:
            continue
    
    # Build GeoDataFrame
    gdf = gpd.GeoDataFrame(properties, geometry="geometry", crs="EPSG:4326")
    
    # Use centralized output utility
    base_name = os.path.splitext(os.path.basename(raster_path))[0]
    output_name = f"{base_name}2dggal" if output_format is not None else None
    return convert_to_output_format(gdf, output_format, output_name)


def raster2dggal_cli():
    parser = argparse.ArgumentParser(
        description="Convert Raster in Geographic CRS to DGGAL DGGS"
    )
    parser.add_argument("-raster", type=str, required=True, help="Raster file path")
    parser.add_argument(
        "-dggs",
        "--dggs_type",
        type=str,
        required=True,
        choices=DGGAL_TYPES.keys(),
        help="DGGAL type"
    )
    parser.add_argument(
        "-r",
        "--resolution",
        type=int,
        required=False,
        default=None,
        help="Resolution (integer). If omitted, auto-selected",
    )
    parser.add_argument(
        "-f",
        "--output_format",
        type=str,
        choices=OUTPUT_FORMATS,
        default="gpd",
    )    
    # No compact option for raster2dggal

    args = parser.parse_args()
    raster = args.raster
    dggs_type = args.dggs_type
    resolution = args.resolution
    output_format = args.output_format

    if not os.path.exists(raster):
        print(f"Error: The file {raster} does not exist.")
        return

    result = raster2dggal(dggs_type, raster, resolution, output_format)
    if output_format in STRUCTURED_FORMATS:
        print(result)
    

if __name__ == "__main__":
    raster2dggal_cli()
