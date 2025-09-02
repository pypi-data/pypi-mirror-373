
"""
DGGRID to Geographic Coordinate Conversion Module

This module provides functionality to convert DGGRID cell IDs to geographic coordinates
and various geometric representations. DGGRID is a Discrete Global Grid System
implementation that supports multiple DGGS types.

Key Functions:
    dggrid2geo: Convert DGGRID cell IDs to Shapely Polygons
    dggrid2geojson: Convert DGGRID cell IDs to GeoJSON FeatureCollection
    dggrid2geo_cli: Command-line interface for polygon conversion
    dggrid2geojson_cli: Command-line interface for GeoJSON conversion
"""

import json
import argparse

from dggrid4py import dggs_types
from dggrid4py.dggrid_runner import output_address_types     
from vgrid.utils.io import validate_dggrid_type, validate_dggrid_resolution, create_dggrid_instance

def dggrid2geo(dggrid_instance, dggs_type, dggrid_ids, resolution=None, input_address_type="SEQNUM"):
    """
    Convert a list of DGGRID cell IDs to Shapely geometry objects.
    Accepts a single dggrid_id (string/int) or a list of dggrid_ids.
    Skips invalid or error-prone cells.
    Returns a list of Shapely Polygon objects, or a single Polygon if only one input.
    """
    dggs_type = validate_dggrid_type(dggs_type) 
    resolution = validate_dggrid_resolution(dggs_type, resolution)       
    if isinstance(dggrid_ids, (str, int)):
        dggrid_ids = [dggrid_ids]
    
    # Convert from input_address_type to SEQNUM if needed
    if input_address_type and input_address_type != "SEQNUM":
        address_type_transform = dggrid_instance.address_transform(
            dggrid_ids,
            dggs_type=dggs_type,
            resolution=resolution,
            mixed_aperture_level=None,
            input_address_type=input_address_type,
            output_address_type="SEQNUM",
        )
        # Extract all SEQNUM values, not just the first one
        dggrid_ids = address_type_transform["SEQNUM"].tolist()

    
    dggrid_cells = dggrid_instance.grid_cell_polygons_from_cellids(
                dggrid_ids, dggs_type, resolution, split_dateline=True
            )    
    
    # Convert global_id back to input_address_type if needed
    if input_address_type and input_address_type != "SEQNUM":
        # Get the SEQNUM values from global_id column
        seqnum_values = dggrid_cells['global_id'].tolist()
        
        # Transform back to input_address_type
        reverse_transform = dggrid_instance.address_transform(
            seqnum_values,
            dggs_type=dggs_type,
            resolution=resolution,
            mixed_aperture_level=None,
            input_address_type="SEQNUM",
            output_address_type=input_address_type,
        )
        
        # Replace global_id values with the original input_address_type values
        dggrid_cells['global_id'] = reverse_transform[input_address_type].values
    
    # Rename global_id column to dggrid_{dggs_type.lower()}
    dggrid_cells = dggrid_cells.rename(columns={'global_id': f"dggrid_{dggs_type.lower()}"})
    # Add resolution property
    dggrid_cells['resolution'] = resolution
    
    return dggrid_cells

def dggrid2geo_cli():
    """
    Command-line interface for dggrid2geo supporting multiple DGGRID cell IDs.
    """
    parser = argparse.ArgumentParser(
        description="Convert DGGRID cell ID(s) to Shapely Polygons. \
                                     Usage: dggrid2geo <cell_ids> <dggs_type> <res> [input_address_type]. \
                                     Ex: dggrid2geo 783229476878 ISEA7H 13 SEQNUM"
    )
    parser.add_argument(
        "dggs_type",
        choices=dggs_types,
        help="Select a DGGS type from the available options.",
    )
    
    parser.add_argument(
        "dggrid_ids",
        nargs="+",
        help="Input DGGRID cell ID(s)"
    )

    parser.add_argument("resolution", type=int, help="resolution")
    parser.add_argument(
        "input_address_type",
        choices=output_address_types,
        default="SEQNUM",
        nargs="?",  # This makes the argument optional
        help="Select an input address type from the available options.",
    )

    args = parser.parse_args()
    dggrid_instance = create_dggrid_instance()
    polys = dggrid2geo(dggrid_instance, args.dggs_type, args.dggrid_ids, args.resolution, args.input_address_type)
    return polys

def dggrid2geojson(dggrid_instance, dggs_type, dggrid_ids, resolution, input_address_type="SEQNUM"):
    """
    Convert a list of DGGRID cell IDs to a GeoJSON FeatureCollection.
    Accepts a single dggrid_id (string/int) or a list of dggrid_ids.
    Skips invalid or error-prone cells.
    """
    if isinstance(dggrid_ids, (str, int)):
        dggrid_ids = [dggrid_ids]
    
    # Get the GeoDataFrame from dggrid2geo
    gdf = dggrid2geo(dggrid_instance, dggs_type, dggrid_ids, resolution, input_address_type)    
    # Ensure the geometry column is set as active
    if 'geometry' in gdf.columns:
        gdf = gdf.set_geometry('geometry')
    
    # Convert GeoDataFrame to GeoJSON dictionary
    geojson_dict = json.loads(gdf.to_json())
    
    return geojson_dict


def dggrid2geojson_cli():
    """
    Command-line interface for dggrid2geojson supporting multiple DGGRID cell IDs.
    """
    parser = argparse.ArgumentParser(
        description="Convert DGGRID cell ID(s) to GeoJSON. \
                                     Usage: dggrid2geojson <cell_ids> <dggs_type> <res> [input_address_type]. \
                                     Ex: dggrid2geojson 783229476878 ISEA7H 13 SEQNUM"
    )
  
    parser.add_argument(
        "dggs_type",
        choices=dggs_types,
        help="Select a DGGS type from the available options.",
    )
    parser.add_argument(
        "dggrid_ids",
        nargs="+",
        help="Input DGGRID cell ID(s)"
    )
    parser.add_argument("resolution", type=int, help="resolution")
    parser.add_argument(
        "input_address_type",
        choices=output_address_types,   
        default="SEQNUM",
        nargs="?",  # This makes the argument optional
        help="Select an input address type from the available options.",
    )

    args = parser.parse_args()
    dggrid_instance = create_dggrid_instance()
    geojson_data = json.dumps(dggrid2geojson(dggrid_instance, args.dggs_type, args.dggrid_ids, args.resolution, args.input_address_type))
    print(geojson_data)

if __name__ == "__main__":
    dggrid2geojson_cli()