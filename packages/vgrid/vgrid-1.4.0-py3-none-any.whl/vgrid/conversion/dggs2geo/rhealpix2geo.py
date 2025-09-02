"""
RHEALPix to Geographic Coordinate Conversion Module

This module provides functionality to convert RHEALPix (Rectified HEALPix) cell IDs 
to geographic coordinates and various geometric representations. RHEALPix is a 
discrete global grid system that provides equal-area cells on the Earth's surface 
with improved geometric properties compared to the original HEALPix system.

Key Functions:
    rhealpix2geo: Convert RHEALPix cell IDs to Shapely Polygons
    rhealpix2geojson: Convert RHEALPix cell IDs to GeoJSON FeatureCollection
    rhealpix2geo_cli: Command-line interface for polygon conversion
    rhealpix2geojson_cli: Command-line interface for GeoJSON conversion
"""

import json
import argparse
from vgrid.dggs.rhealpixdggs.dggs import RHEALPixDGGS         
from vgrid.dggs.rhealpixdggs.ellipsoids import WGS84_ELLIPSOID
from vgrid.utils.geometry import geodesic_dggs_to_feature, rhealpix_cell_to_polygon
from pyproj import Geod

geod = Geod(ellps="WGS84")
E = WGS84_ELLIPSOID
rhealpix_dggs = RHEALPixDGGS(ellipsoid=E, north_square=1, south_square=3, N_side=3)

def rhealpix2geo(rhealpix_ids):
    """
    Convert RHEALPix cell IDs to Shapely geometry objects.
    
    This function takes RHEALPix cell identifiers and converts them to Shapely
    Polygon objects representing the geographic boundaries of each cell.
    
    Args:
        rhealpix_ids (str or list): A single RHEALPix cell ID (string) or a list
                                   of RHEALPix cell IDs. Each ID should be a string
                                   starting with 'R' followed by numeric digits.
    
    Returns:
        list: A list of Shapely Polygon objects representing the converted cells.
              Invalid or error-prone cells are skipped and not included in the result.
    
    Example:
        >>> rhealpix2geo("R31260335553825")
        [<shapely.geometry.polygon.Polygon object at 0x...>]
        
        >>> rhealpix2geo(["R31260335553825", "R31260335553826"])
        [<shapely.geometry.polygon.Polygon object at 0x...>, 
         <shapely.geometry.polygon.Polygon object at 0x...>]
    
    Note:
        - Invalid cell IDs are silently skipped
        - The function uses WGS84 ellipsoid with north_square=1, south_square=3, N_side=3
        - Each RHEALPix ID is parsed by taking the first character as a string
          and converting the remaining characters to integers
    """
    if isinstance(rhealpix_ids, str):
        rhealpix_ids = [rhealpix_ids]
    rhealpix_polygons = []
    for rhealpix_id in rhealpix_ids:
        try:
            rhealpix_uids = (rhealpix_id[0],) + tuple(map(int, rhealpix_id[1:]))            
            rhealpix_cell = rhealpix_dggs.cell(rhealpix_uids)
            cell_polygon = rhealpix_cell_to_polygon(rhealpix_cell)
            rhealpix_polygons.append(cell_polygon)
        except Exception:
            continue
    if len(rhealpix_polygons) == 1:
        return rhealpix_polygons[0]
    return rhealpix_polygons


def rhealpix2geo_cli():
    """
    Command-line interface for converting RHEALPix cell IDs to Shapely Polygons.
    
    This function provides a command-line interface that accepts multiple RHEALPix
    cell IDs as command-line arguments and returns the corresponding Shapely
    Polygon objects.
    
    Returns:
        list: A list of Shapely Polygon objects representing the converted cells.
    
    Usage:
        rhealpix2geo R31260335553825 R31260335553826
    
    Note:
        This function is designed to be called from the command line and will
        parse arguments using argparse. Invalid cell IDs are silently skipped.
    """
    parser = argparse.ArgumentParser(
        description="Convert Rhealpix cell ID(s) to Shapely Polygons"
    )
    parser.add_argument(
        "rhealpix",
        nargs="+",
        help="Input Rhealpix cell ID(s), e.g., rhealpix2geo R31260335553825 R31260335553826",
    )
    args = parser.parse_args()
    polys = rhealpix2geo(args.rhealpix)
    return polys


def rhealpix2geojson(rhealpix_ids):
    """
    Convert RHEALPix cell IDs to GeoJSON FeatureCollection.
    
    This function takes RHEALPix cell identifiers and converts them to a GeoJSON
    FeatureCollection containing features with geometry and properties for each cell.
    
    Args:
        rhealpix_ids (str or list): A single RHEALPix cell ID (string) or a list
                                   of RHEALPix cell IDs. Each ID should be a string
                                   starting with 'R' followed by numeric digits.
    
    Returns:
        dict: A GeoJSON FeatureCollection dictionary with the following structure:
              {
                  "type": "FeatureCollection",
                  "features": [
                      {
                          "type": "Feature",
                          "geometry": {...},
                          "properties": {
                              "dggs_type": "rhealpix",
                              "cell_id": "R31260335553825",
                              "resolution": 12,
                              "num_edges": 4
                          }
                      },
                      ...
                  ]
              }
    
    Example:
        >>> result = rhealpix2geojson("R31260335553825")
        >>> print(result["type"])
        FeatureCollection
        >>> print(len(result["features"]))
        1
        
        >>> result = rhealpix2geojson(["R31260335553825", "R31260335553826"])
        >>> print(len(result["features"]))
        2
    
    Note:
        - Invalid cell IDs are silently skipped
        - Each feature includes metadata about the cell (type, ID, resolution, edges)
        - The number of edges is determined by the cell shape (4 for square, 3 for dart)
        - The function creates a new RHEALPixDGGS instance for each conversion
    """
    if isinstance(rhealpix_ids, str):
        rhealpix_ids = [rhealpix_ids]
    rhealpix_features = []
    for rhealpix_id in rhealpix_ids:
        try:            
            rhealpix_uids = (rhealpix_id[0],) + tuple(map(int, rhealpix_id[1:]))
            rhealpix_cell = rhealpix_dggs.cell(rhealpix_uids)
            resolution = rhealpix_cell.resolution
            cell_polygon = rhealpix_cell_to_polygon(rhealpix_cell)
            num_edges = 4
            if rhealpix_cell.ellipsoidal_shape() == "dart":
                num_edges = 3
            rhealpix_feature = geodesic_dggs_to_feature(
                "rhealpix", rhealpix_id, resolution, cell_polygon, num_edges
            )
            rhealpix_features.append(rhealpix_feature)
        except Exception:
            continue
    return {"type": "FeatureCollection", "features": rhealpix_features}


def rhealpix2geojson_cli():
    """
    Command-line interface for converting RHEALPix cell IDs to GeoJSON.
    
    This function provides a command-line interface that accepts multiple RHEALPix
    cell IDs as command-line arguments and outputs the corresponding GeoJSON
    FeatureCollection as a JSON string to stdout.
    
    Usage:
        rhealpix2geojson R31260335553825 R31260335553826
    
    Output:
        Prints a JSON string representing a GeoJSON FeatureCollection to stdout.
    
    Example:
        $ python -m vgrid.conversion.dggs2geo.rhealpix2geo R31260335553825
        {"type": "FeatureCollection", "features": [...]}
    
    Note:
        This function is designed to be called from the command line and will
        parse arguments using argparse. The GeoJSON output is formatted as a
        JSON string printed to stdout. Invalid cell IDs are silently skipped.
    """
    parser = argparse.ArgumentParser(
        description="Convert Rhealpix cell ID(s) to GeoJSON"
    )
    parser.add_argument(
        "rhealpix",
        nargs="+",
        help="Input Rhealpix cell ID(s), e.g., rhealpix2geojson R31260335553825 R31260335553826",
    )
    args = parser.parse_args()
    geojson_data = json.dumps(rhealpix2geojson(args.rhealpix))
    print(geojson_data)