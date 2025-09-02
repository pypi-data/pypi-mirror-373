"""
DGGRID Grid Generator Module

Generates DGGRID grids for multiple grid types with automatic cell generation and validation using the DGGRID library.

Key Functions:
- generate_grid(): Core grid generation function with DGGRID instance
- dggridgen(): User-facing function with multiple output formats
- dggridgen_cli(): Command-line interface for grid generation
"""

from shapely.geometry import box
import argparse

from dggrid4py import dggs_types
from dggrid4py.dggrid_runner import output_address_types
from vgrid.utils.io import convert_to_output_format, create_dggrid_instance
from vgrid.utils.io import validate_dggrid_type, validate_dggrid_resolution
from vgrid.utils.constants import   OUTPUT_FORMATS, STRUCTURED_FORMATS          

def generate_grid(dggrid_instance, dggs_type, resolution, bbox, output_address_type):
    dggs_type = validate_dggrid_type(dggs_type)
    resolution = validate_dggrid_resolution(dggs_type, resolution) 
    
    ### considering using dggrid_instance.grid_cellids_for_extent('ISEA4T', 10, output_address_type='SEQNUM')
    if bbox:        
        bounding_box = box(*bbox)
        dggrid_gdf = dggrid_instance.grid_cell_polygons_for_extent(
            dggs_type,
            resolution,
            clip_geom=bounding_box,
            split_dateline=True,
            output_address_type=output_address_type
        )
       
    else:
        dggrid_gdf = dggrid_instance.grid_cell_polygons_for_extent(
            dggs_type, resolution, split_dateline=True, output_address_type=output_address_type
        )
         

    return dggrid_gdf   


def dggridgen(dggrid_instance, dggs_type, resolution, bbox=None, output_address_type=None, output_format="gpd"):
    """
    Generate DGGRID grid for pure Python usage.

    Args:
        dggs_type (str): DGGS type from dggs_types
        resolution (int): Resolution level
        bbox (list, optional): Bounding box [min_lat, min_lon, max_lat, max_lon]. Defaults to None (whole world).
        output_address_type (str, optional): Address type for output. Defaults to None.
        output_format (str, optional): Output format handled entirely by convert_to_output_format

    Returns:
        Delegated to convert_to_output_format
    """
    gdf = generate_grid(dggrid_instance, dggs_type, resolution, bbox, output_address_type)  
    output_name = f"dggrid_{dggs_type}_{resolution}"
    return convert_to_output_format(gdf, output_format, output_name)


def dggridgen_cli():
    parser = argparse.ArgumentParser(description="Generate DGGRID.")
    parser.add_argument(
        "-dggs",
        "--dggs_type",
        choices=dggs_types,
        help="Select a DGGS type from the available options.",
    )
    parser.add_argument(
        "-r", "--resolution", type=int, required=True, help="resolution"
    )
    parser.add_argument(
        "-b",
        "--bbox",
        type=float,
        nargs=4,
        help="Bounding box in the format: min_lon min_lat max_lon max_lat (default is the whole world)",
    )
    parser.add_argument(
        "-a",
        "--output_address_type",
        choices=output_address_types,
        default=None,
        help="Select an output address type.",
    )
    parser.add_argument(
        "-f",
        "--output_format",
        type=str,
        choices=OUTPUT_FORMATS,
        default="gpd",
        help="Select an output format.",
    )
    args = parser.parse_args()

    dggrid_instance = create_dggrid_instance()
    
    resolution = args.resolution
    dggs_type = args.dggs_type
    bbox = args.bbox
    output_address_type = args.output_address_type
    
    try:
        result = dggridgen(dggrid_instance, dggs_type, resolution, bbox, output_address_type, args.output_format)   
        if args.output_format in STRUCTURED_FORMATS:
            print(result)
    except ValueError as e:
        print(f"Error: {str(e)}")
        return 

    
   
if __name__ == "__main__":
    dggridgen_cli()
