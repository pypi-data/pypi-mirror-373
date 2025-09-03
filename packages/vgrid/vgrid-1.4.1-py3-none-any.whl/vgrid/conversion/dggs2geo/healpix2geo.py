"""
HEALPix to Geographic Coordinate Conversion Module

This module provides functionality to convert HEALPix (Hierarchical Equal Area 
isoLatitude Pixelization) cell IDs to geographic coordinates and various geometric 
representations. HEALPix is a spherical coordinate system commonly used in astronomy 
and cosmology for equal-area pixelization of the celestial sphere.

Key Functions:
    healpix2geo: Convert HEALPix cell IDs to Shapely Polygons
    healpix2geojson: Convert HEALPix cell IDs to GeoJSON FeatureCollection
    healpix2geo_cli: Command-line interface for polygon conversion
    healpix2geojson_cli: Command-line interface for GeoJSON conversion      

Note: This module is only supported on Linux systems due to healpy dependency.
"""

import json
import argparse
import platform  
from shapely.geometry import Polygon
from vgrid.utils.geometry import geodesic_dggs_to_feature

# Import healpy helper functions only on Linux
if platform.system() == "Linux":
    import healpy as hp
    from vgrid.dggs.healpy_helper import _cellid2boundaries
else:
    _cellid2boundaries = None

def healpix2geo(healpix_ids):
    """
    Convert a list of HEALPix cell IDs to Shapely geometry objects.
    Accepts a single healpix_id (int) or a list of healpix_ids.
    Skips invalid or error-prone cells.
    Returns a list of Shapely Polygon objects, or a single Polygon if only one input.
    
    Args:
        healpix_ids: HEALPix cell ID(s) as int or list of ints
    """
    if platform.system() != "Linux":
        raise RuntimeError("HEALPix is only supported on Linux systems")
    
    if _cellid2boundaries is None:
        raise RuntimeError("HEALPix helper functions not available")
    
    if isinstance(healpix_ids, int):
        healpix_ids = [healpix_ids]
    
    healpix_polygons = []
    for healpix_id in healpix_ids:
        try:
            # Calculate nside from the cell ID by finding the appropriate resolution
            # HEALPix has 12*4^resolution pixels total
            # We need to find the resolution where 12*4^resolution > healpix_id
            resolution = 0
            while 12 * (4 ** resolution) <= healpix_id:
                resolution += 1
                if resolution > 29:  # Maximum HEALPix resolution
                    raise ValueError(f"Cell ID {healpix_id} is too large for valid HEALPix resolution")
            
            nside = 2 ** resolution
            nside = hp.order2nside(resolution)
            # Validate that the cell ID is within the valid range for this nside
            max_pixels = 12 * (4 ** resolution)
            if healpix_id >= max_pixels:
                raise ValueError(f"Cell ID {healpix_id} is out of range for resolution {resolution} (max: {max_pixels-1})")
            
            # Get cell boundaries using healpy helper
            # _cellid2boundaries returns a list of boundary arrays, each with shape (4, 2)
            boundaries = _cellid2boundaries([healpix_id], nside, nest=True, as_geojson=False)
            # boundaries[0] is the boundary for our single cell - shape (4, 2) of (lon, lat)
            cell_polygon = Polygon(boundaries[0])
            healpix_polygons.append(cell_polygon)
        except Exception as e:
            print(f"Error processing cell {healpix_id}: {e}")
            continue
    
    if len(healpix_polygons) == 1:
        return healpix_polygons[0]
    return healpix_polygons
    

def healpix2geo_cli():
    """
    Command-line interface for healpix2geo supporting multiple HEALPix cell IDs.
    """
    parser = argparse.ArgumentParser(description="Convert HEALPix cell ID(s) to Shapely Polygons")
    parser.add_argument(
        "healpix",
        nargs="+",
        type=int,
        help="Input HEALPix cell ID(s), e.g., healpix2geo 12345 67890",
    )
    args = parser.parse_args()
    
    polys = healpix2geo(args.healpix)
    return polys

def healpix2geojson(healpix_ids):
    """
    Convert a list of HEALPix cell IDs to a GeoJSON FeatureCollection.
    Accepts a single healpix_id (int) or a list of healpix_ids.
    Skips invalid or error-prone cells.
    
    Args:
        healpix_ids: HEALPix cell ID(s) as int or list of ints
    """
    if platform.system() != "Linux":
        raise RuntimeError("HEALPix is only supported on Linux systems")
    
    if isinstance(healpix_ids, int):
        healpix_ids = [healpix_ids]
    
    healpix_features = []
    for healpix_id in healpix_ids:
        try:
            cell_polygon = healpix2geo(healpix_id)
            # HEALPix cells are always quadrilaterals (4 edges)
            num_edges = 4
            # Calculate resolution from the cell ID using the same logic as healpix2geo
            resolution = 0
            while 12 * (4 ** resolution) <= healpix_id:
                resolution += 1
                if resolution > 29:
                    raise ValueError(f"Cell ID {healpix_id} is too large for valid HEALPix resolution")
            healpix_feature = geodesic_dggs_to_feature(
                "healpix", str(healpix_id), resolution, cell_polygon, num_edges
            )
            healpix_features.append(healpix_feature)
        except Exception as e:
            print(f"Error processing cell {healpix_id}: {e}")
            continue
    
    return {"type": "FeatureCollection", "features": healpix_features}

def healpix2geojson_cli():
    """
    Command-line interface for healpix2geojson supporting multiple HEALPix cell IDs.
    """
    parser = argparse.ArgumentParser(description="Convert HEALPix cell ID(s) to GeoJSON")
    parser.add_argument(
        "healpix",
        nargs="+",
        type=int,
        help="Input HEALPix cell ID(s), e.g., healpix2geojson 12345 67890",
    )
    args = parser.parse_args()
    
    try:
        geojson_data = json.dumps(healpix2geojson(args.healpix))
        print(geojson_data)
    except RuntimeError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    healpix2geojson_cli()
