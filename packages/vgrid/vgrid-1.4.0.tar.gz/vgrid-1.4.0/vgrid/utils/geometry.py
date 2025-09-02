import re
from vgrid.utils.constants import DGGAL_TYPES      
from vgrid.utils.io import validate_dggal_type, validate_dggrid_type  
import shapely.geometry
import geopandas as gpd
import shapely
from pyproj import Geod
from shapely.geometry import LineString, Point, Polygon,mapping
from shapely.wkt import loads
from vgrid.dggs.rhealpixdggs.utils import my_round
from vgrid.dggs import s2
from vgrid.dggs.eaggr.enums.shape_string_format import ShapeStringFormat
from vgrid.dggs.eaggr.eaggr import Eaggr
from vgrid.dggs.eaggr.enums.model import Model
from vgrid.utils.antimeridian import fix_polygon
from vgrid.utils.constants import AUTHALIC_RADIUS, ICOSA_EDGE_KM  
import platform
import math
if platform.system() == "Windows":  
    from vgrid.dggs.eaggr.eaggr import Eaggr
    from vgrid.dggs.eaggr.enums.model import Model
    isea4t_dggs = Eaggr(Model.ISEA4T)
    isea3h_dggs = Eaggr(Model.ISEA3H)


from dggal import *
app = Application(appGlobals=globals())
pydggal_setup(app)

# Initialize Geod with WGS84 ellipsoid
geod = Geod(ellps="WGS84")
# geod = Geod(a=6371007.181, f=0)  # sphere

def fix_h3_antimeridian_cells(hex_boundary, threshold=-128):
    if any(lon < threshold for _, lon in hex_boundary):
        # Adjust all longitudes accordingly
        return [(lat, lon - 360 if lon > 0 else lon) for lat, lon in hex_boundary]
    return hex_boundary

def fix_rhealpix_antimeridian_cells(boundary, threshold=-128):
    if any(lon < threshold for lon, _ in boundary):
        return [(lon - 360 if lon > 0 else lon, lat) for lon, lat in boundary]
    return boundary

def rhealpix_cell_to_polygon(cell):
    vertices = [
        tuple(my_round(coord, 14) for coord in vertex)
        for vertex in cell.vertices(plane=False)
    ]
    if vertices[0] != vertices[-1]:
        vertices.append(vertices[0])
    vertices = fix_rhealpix_antimeridian_cells(vertices)
    return Polygon(vertices)


def fix_isea4t_wkt(isea4t_wkt):
    coords_section = isea4t_wkt[isea4t_wkt.index("((") + 2 : isea4t_wkt.index("))")]
    coords = coords_section.split(",")
    if coords[0] != coords[-1]:
        coords.append(coords[0])
    fixed_coords = ", ".join(coords)
    return f"POLYGON (({fixed_coords}))"


def fix_isea4t_antimeridian_cells(isea4t_boundary, threshold=-100):
    lon_lat = [(float(lon), float(lat)) for lon, lat in isea4t_boundary.exterior.coords]
    if any(lon < threshold for lon, _ in lon_lat):
        adjusted_coords = [(lon - 360 if lon > 0 else lon, lat) for lon, lat in lon_lat]
    else:
        adjusted_coords = lon_lat
    return Polygon(adjusted_coords)


def isea4t_cell_to_polygon(isea4t_cell):
    cell_to_shp = isea4t_dggs.convert_dggs_cell_outline_to_shape_string(
        isea4t_cell, ShapeStringFormat.WKT
    )
    cell_to_shp_fixed = fix_isea4t_wkt(cell_to_shp)
    cell_polygon = loads(cell_to_shp_fixed)
    return cell_polygon

def get_ease_resolution(ease_id):
    """Get the resolution level of an EASE cell ID."""
    try:
        match = re.match(r"L(\d+)\.(.+)", ease_id)
        if not match:
            raise ValueError(f"Invalid EASE ID format: {ease_id}")
        return int(match.group(1))
    except Exception as e:
        raise ValueError(f"Invalid EASE ID <{ease_id}> : {e}")


def isea3h_cell_to_polygon(isea3h_cell):
    cell_to_shape = isea3h_dggs.convert_dggs_cell_outline_to_shape_string(
        isea3h_cell, ShapeStringFormat.WKT
    )
    cell_to_shp_fixed = fix_isea4t_wkt(cell_to_shape)
    cell_polygon = loads(cell_to_shp_fixed)
    fixed_polygon = fix_polygon(cell_polygon)
    return fixed_polygon


def s2_cell_to_polygon(s2_id):
    """ 
    Convert an S2 cell ID to a Shapely Polygon.
    """
    cell = s2.Cell(s2_id)
    vertices = []
    for i in range(4):
        vertex = s2.LatLng.from_point(cell.get_vertex(i))
        vertices.append((vertex.lng().degrees, vertex.lat().degrees))

    vertices.append(vertices[0])  # Close the polygon

    # Create a Shapely Polygon
    polygon = Polygon(vertices)
    #  Fix Antimerididan:
    fixed_polygon = fix_polygon(polygon)
    return fixed_polygon


def fix_eaggr_wkt(eaggr_wkt):
    coords_section = eaggr_wkt[eaggr_wkt.index("((") + 2 : eaggr_wkt.index("))")]
    coords = coords_section.split(",")
    if coords[0] != coords[-1]:
        coords.append(coords[0])
    fixed_coords = ", ".join(coords)
    return f"POLYGON (({fixed_coords}))"


def graticule_dggs_metrics(cell_polygon):    
    min_lon, min_lat, max_lon, max_lat = cell_polygon.bounds
    center_lat = round((min_lat + max_lat) / 2, 7)
    center_lon = round((min_lon + max_lon) / 2, 7)
    cell_width = round(geod.line_length([min_lon, max_lon], [min_lat, min_lat]), 3)
    cell_height = round(geod.line_length([min_lon, min_lon], [min_lat, max_lat]), 3)
    cell_area = round(abs(geod.geometry_area_perimeter(cell_polygon)[0]), 3)
    cell_perimeter = round(abs(geod.geometry_area_perimeter(cell_polygon)[1]), 3)
    return center_lat, center_lon, cell_width, cell_height, cell_area, cell_perimeter


def geodesic_dggs_metrics(cell_polygon, num_edges):
    cell_centroid = cell_polygon.centroid
    center_lat = round(cell_centroid.y, 7)
    center_lon = round(cell_centroid.x, 7)
    cell_area = round(
        abs(geod.geometry_area_perimeter(cell_polygon)[0]), 3
    )
    cell_perimeter = round(abs(geod.geometry_area_perimeter(cell_polygon)[1]), 3)       
    avg_edge_len = round(cell_perimeter / num_edges, 3)
    return center_lat, center_lon, avg_edge_len, cell_area, cell_perimeter


def graticule_dggs_to_feature(dggs_name, cell_id, resolution, cell_polygon):
    center_lat, center_lon, cell_width, cell_height, cell_area, cell_perimeter = graticule_dggs_metrics(
        cell_polygon
    )
    feature = {
        "type": "Feature",
        "geometry": mapping(cell_polygon),
        "properties": {
            f"{dggs_name}": str(cell_id),
            "resolution": resolution,
            "center_lat": center_lat,
            "center_lon": center_lon,
            "cell_width": cell_width,
            "cell_height": cell_height,
            "cell_area": cell_area,
            "cell_perimeter": cell_perimeter,
        },
    }
    return feature


def geodesic_dggs_to_feature(dggs_name, cell_id, resolution, cell_polygon, num_edges):
    center_lat, center_lon, avg_edge_len, cell_area, cell_perimeter = geodesic_dggs_metrics(
        cell_polygon, num_edges
    )
    feature = {
        "type": "Feature",
        "geometry": mapping(cell_polygon),
        "properties": {
            f"{dggs_name}": str(cell_id),
            "resolution": resolution,
            "center_lat": center_lat,
            "center_lon": center_lon,
            "avg_edge_len": avg_edge_len,
            "cell_area": cell_area,
            "cell_perimeter": cell_perimeter,
        },
    }
    return feature


def graticule_dggs_to_geoseries(dggs_name, cell_id, resolution, cell_polygon):
    center_lat, center_lon, cell_width, cell_height, cell_area, cell_perimeter = graticule_dggs_metrics(
        cell_polygon
    )
    return {
        f"{dggs_name}": str(cell_id),
        "resolution": resolution,
        "center_lat": center_lat,
        "center_lon": center_lon,
        "cell_width": cell_width,
        "cell_height": cell_height,
        "cell_area": cell_area,
        "cell_perimeter": cell_perimeter,
        "geometry": cell_polygon,
    }


def geodesic_dggs_to_geoseries(dggs_name, cell_id, resolution, cell_polygon, num_edges):
    center_lat, center_lon, avg_edge_len, cell_area, cell_perimeter = geodesic_dggs_metrics(
        cell_polygon, num_edges
    )
    return {
        f"{dggs_name}": str(cell_id),
        "resolution": resolution,
        "center_lat": center_lat,
        "center_lon": center_lon,
        "avg_edge_len": avg_edge_len,
        "cell_area": cell_area,
        "cell_perimeter": cell_perimeter,
        "geometry": cell_polygon,
    }

def shortest_point_distance(points):
    """
    Calculate distances between points in a Shapely geometry.
    If there's only one point, return 0.
    If there are multiple points, calculate Delaunay triangulation and return distances.

    Args:
        points: Shapely Point or MultiPoint geometry

    Returns:
        tuple: shortest_distance
    """
    # Handle single Point
    if isinstance(points, Point):
        return 0  # Single point has no distance to other points

    # Handle MultiPoint with single point
    if len(points.geoms) == 1:
        return 0

    # Generate Delaunay triangulation
    delaunay = shapely.delaunay_triangles(points, only_edges=True)

    # Find the shortest edge
    shortest_distance = float("inf")

    for line in delaunay.geoms:
        # Get the coordinates of the line endpoints
        coords = list(line.coords)
        lon1, lat1 = coords[0]
        lon2, lat2 = coords[1]

        # Calculate the distance in meters using pyproj Geod
        distance = geod.inv(lon1, lat1, lon2, lat2)[2]  # [2] gives the distance in meters
        if distance < shortest_distance:
            shortest_distance = distance

    return shortest_distance if shortest_distance != float("inf") else 0


def shortest_polyline_distance(polylines):
    """
    Calculate the shortest distance between polylines using GeoPandas shortest_line() method.
    If there's only one polyline, return 0.
    If there are multiple polylines, use shortest_line() and return the shortest distance in meters.

    Args:
        polylines: Shapely LineString or MultiLineString geometry, or GeoSeries of LineStrings
        
    Returns:
        float: shortest_distance between polylines in meters
    """
    # Handle single LineString
    if isinstance(polylines, LineString):
        return 0  # Single polyline has no distance to other polylines
    
    # Handle MultiLineString with single line
    if hasattr(polylines, 'geoms') and len(polylines.geoms) == 1:
        return 0
    
    # Handle GeoSeries
    if hasattr(polylines, 'iloc'):
        # Already a GeoSeries
        line_list = list(polylines.geometry)
        gs = polylines
    else:
        # Handle MultiLineString or list
        line_list = list(polylines.geoms) if hasattr(polylines, 'geoms') else [polylines]
        gs = gpd.GeoSeries(line_list)
    
    if len(line_list) < 2:
        return 0
    
    # Calculate shortest distance between all pairs of polylines using shortest_line()
    shortest_distance = float("inf")
    
    for i in range(len(line_list)):
        for j in range(i+1, len(line_list)):
            line1 = line_list[i]
            line2 = line_list[j]
            
            # Check if polylines are disjoint
            if line1.disjoint(line2):
                try:
                    # Create GeoSeries for shortest_line calculation
                    gs1 = gpd.GeoSeries([line1])
                    gs2 = gpd.GeoSeries([line2])
                    
                    # Get shortest line using GeoPandas method
                    shortest_line = gs1.shortest_line(gs2, align=False).iloc[0]
                    
                    if shortest_line and shortest_line.length > 0:
                            # Get the endpoints of the shortest line
                            coords = list(shortest_line.coords)
                            if len(coords) >= 2:
                                lon1, lat1 = coords[0]
                                lon2, lat2 = coords[1]
                                
                                # Calculate geodesic distance in meters
                                distance = geod.inv(lon1, lat1, lon2, lat2)[2]  # [2] gives distance in meters
                                
                                if distance < shortest_distance:
                                    shortest_distance = distance
                except Exception as e:
                    print(f"Error calculating distance between polylines {i} and {j}: {e}")
                    continue
    
    return shortest_distance if shortest_distance != float("inf") else 0 


def shortest_polygon_distance(polygons):
    """
    Calculate the shortest distance between polygons using GeoPandas shortest_line() method.
    If there's only one polygon, return 0.
    If there are multiple polygons, use shortest_line() and return the shortest distance in meters.

    Args:
        polygons: Shapely Polygon or MultiPolygon geometry, or GeoSeries of Polygons
        
    Returns:
        float: shortest_distance between polygons in meters
    """
    # Handle single Polygon
    if isinstance(polygons, Polygon):
        return 0  # Single polygon has no distance to other polygons
    
    # Handle MultiPolygon with single polygon
    if hasattr(polygons, 'geoms') and len(polygons.geoms) == 1:
        return 0
    
    # Handle GeoSeries
    if hasattr(polygons, 'iloc'):
        # Already a GeoSeries
        polygon_list = list(polygons.geometry)
        gs = polygons
    else:
        # Handle MultiPolygon or list
        polygon_list = list(polygons.geoms) if hasattr(polygons, 'geoms') else [polygons]
        gs = gpd.GeoSeries(polygon_list)
    
    if len(polygon_list) < 2:
        return 0
    
    # Calculate shortest distance between all pairs of polygons using shortest_line()
    shortest_distance = float("inf")
    
    for i in range(len(polygon_list)):
        for j in range(i+1, len(polygon_list)):
            polygon1 = polygon_list[i]
            polygon2 = polygon_list[j]
            
            # Check if polygons are disjoint
            if polygon1.disjoint(polygon2):
                try:
                    # Create GeoSeries for shortest_line calculation
                    gs1 = gpd.GeoSeries([polygon1])
                    gs2 = gpd.GeoSeries([polygon2])
                    
                    # Get shortest line using GeoPandas method
                    shortest_line = gs1.shortest_line(gs2, align=False).iloc[0]
                    
                    if shortest_line and shortest_line.length > 0:
                            # Get the endpoints of the shortest line
                            coords = list(shortest_line.coords)
                            if len(coords) >= 2:
                                lon1, lat1 = coords[0]
                                lon2, lat2 = coords[1]
                                
                                # Calculate geodesic distance in meters
                                distance = geod.inv(lon1, lat1, lon2, lat2)[2]  # [2] gives distance in meters
                                
                                if distance < shortest_distance:
                                    shortest_distance = distance
                except Exception as e:
                    print(f"Error calculating distance between polygons {i} and {j}: {e}")
                    continue
    
    return shortest_distance if shortest_distance != float("inf") else 0


def geodesic_distance(
    lat: float, lon: float, length_meter: float
) -> tuple[float, float]:
    """
    Convert meters to approximate degree offsets at a given location.

    Parameters:
        lat (float): Latitude of the reference point
        lon (float): Longitude of the reference point
        length_meter (float): Distance in meters

    Returns:
        (delta_lat_deg, delta_lon_deg): Tuple of degree offsets in latitude and longitude
    """
    # Move north for latitude delta
    lon_north, lat_north, _ = geod.fwd(lon, lat, 0, length_meter)
    delta_lat = lat_north - lat

    # Move east for longitude delta
    lon_east, lat_east, _ = geod.fwd(lon, lat, 90, length_meter)
    delta_lon = lon_east - lon

    return delta_lat, delta_lon


def geodesic_buffer(polygon, distance):
    """
    Create a geodesic buffer around a polygon using pyproj Geod.

    Args:
        polygon: Shapely Polygon geometry
        distance: Buffer distance in meters

    Returns:
        Shapely Polygon: Buffered polygon
    """
    buffered_coords = []
    for lon, lat in polygon.exterior.coords:
        # Generate points around the current vertex to approximate a circle
        circle_coords = [
            geod.fwd(lon, lat, azimuth, distance)[
                :2
            ]  # Forward calculation: returns (lon, lat, back_azimuth)
            for azimuth in range(0, 360, 10)  # Generate points every 10 degrees
        ]
        buffered_coords.append(circle_coords)

    # Flatten the list of buffered points and form a Polygon
    all_coords = [coord for circle in buffered_coords for coord in circle]
    return Polygon(all_coords).convex_hull


def check_predicate(cell_polygon, input_geometry, predicate=None):
    """
    Determine whether to keep an H3 cell based on its relationship with the input geometry.

    Args:
        cell_polygon: Shapely Polygon representing the H3 cell
        input_geometry: Shapely geometry (Polygon, LineString, etc.)
        predicate (str or int): Spatial predicate to apply:
            String values:
                None or "intersects": intersects (default)
                "within": within
                "centroid_within": centroid_within
                "largest_overlap": intersection >= 50% of cell area
            Integer values (for backward compatibility):
                None or 0: intersects (default)
                1: within
                2: centroid_within
                3: intersection >= 50% of cell area

    Returns:
        bool: True if cell should be kept, False otherwise
    """
    # Handle string predicates
    if isinstance(predicate, str):
        predicate_lower = predicate.lower()
        if predicate_lower in ["intersects", "intersect"]:
            return cell_polygon.intersects(input_geometry)
        elif predicate_lower == "within":
            return cell_polygon.within(input_geometry)
        elif predicate_lower in ["centroid_within", "centroid"]:
            return cell_polygon.centroid.within(input_geometry)
        elif predicate_lower in ["largest_overlap", "overlap", "majority"]:
            # intersection >= 50% of cell area
            if cell_polygon.intersects(input_geometry):
                intersection_geom = cell_polygon.intersection(input_geometry)
                if intersection_geom and intersection_geom.area > 0:
                    intersection_area = intersection_geom.area
                    cell_area = cell_polygon.area
                    return (intersection_area / cell_area) >= 0.5
            return False
        else:
            # Unknown string predicate, default to intersects
            return cell_polygon.intersects(input_geometry)

    # Handle integer predicates (backward compatibility)
    elif isinstance(predicate, int):
        if predicate == 0:
            # Default: intersects
            return cell_polygon.intersects(input_geometry)
        elif predicate == 1:
            # within
            return cell_polygon.within(input_geometry)
        elif predicate == 2:
            # centroid_within
            return cell_polygon.centroid.within(input_geometry)
        elif predicate == 3:
            # intersection >= 50% of cell area
            if cell_polygon.intersects(input_geometry):
                intersection_geom = cell_polygon.intersection(input_geometry)
                if intersection_geom and intersection_geom.area > 0:
                    intersection_area = intersection_geom.area
                    cell_area = cell_polygon.area
                    return (intersection_area / cell_area) >= 0.5
            return False
        else:
            # Unknown predicate, default to intersects
            return cell_polygon.intersects(input_geometry)

    else:
        # None or other types, default to intersects
        return cell_polygon.intersects(input_geometry)


def check_crossing(lon1: float, lon2: float, validate: bool = True):
    """
    Assuming a minimum travel distance between two provided longitude coordinates,
    checks if the 180th meridian (antimeridian) is crossed.
    """
    if validate and any(abs(x) > 180.0 for x in [lon1, lon2]):
        raise ValueError("longitudes must be in degrees [-180.0, 180.0]")
    return abs(lon2 - lon1) > 180.0


def check_crossing_geom(geom):
    """
    Check if a geometry crosses the antimeridian (180th meridian).
    
    Args:
        geom: Shapely geometry (Polygon, MultiPolygon)
    
    Returns:
        bool: True if any part of the geometry crosses the antimeridian, False otherwise
    """
    crossed = False
    try:
        # Handle None or empty geometries
        if geom is None or geom.is_empty:
            return False
        
        # Handle multi-geometries
        if hasattr(geom, 'geoms'):
            # MultiPolygon
            for sub_geom in geom.geoms:
                if check_crossing_geom(sub_geom):
                    crossed = True
                    break
            return crossed
        
        # Handle single Polygon
        if geom.geom_type == 'Polygon':
            # Check if exterior has coordinates
            if geom.exterior is None or len(geom.exterior.coords) == 0:
                return False
            
            # Check exterior ring only
            p_init = geom.exterior.coords[0]
            for p in range(1, len(geom.exterior.coords)):
                px = geom.exterior.coords[p]
                try:
                    if check_crossing(p_init[0], px[0]):
                        crossed = True
                        break
                except ValueError:
                    crossed = True
                    break
                p_init = px
    except Exception as e:
        return False
    
    return crossed

def dggal_to_geo(dggs_type: str, zone_id: str, options: dict = {}):
    """
    Convert a DGGAL ZoneID to a Shapely Polygon.
    
    Args:
        dggs_type (str): The DGGS type (e.g., 'isea3h', 'isea9r', 'ivea3h', 'ivea9r', 'rtea3h', 'rtea9r', 'gnosis', 'rhealpix')
        zone_id (str): The zone identifier
        options (dict): Options for geometry generation
            - 'crs' (str | None): "5x6" or "isea" to select alternate CRS; default WGS84
        
    Returns:
        shapely.geometry.Polygon: Shapely Polygon or None if invalid zone
    """
    # Validate DGGS type
    dggs_type = validate_dggal_type(dggs_type)    
    # Create the appropriate DGGS instance
    dggs_class_name = DGGAL_TYPES[dggs_type]["class_name"]
    dggrs = globals()[dggs_class_name]()
    
    # Get zone
    zone = dggrs.getZoneFromTextID(zone_id)
    
    if zone == nullZone:
        return None
    
    # Get CRS option
    crsOption = options.get('crs') if options else None
    crs = 0

    if crsOption:
        if crsOption == "5x6":    crs = CRS(ogc, 153456)
        elif crsOption == "isea": crs = CRS(ogc, 1534)

    # Get vertices based on CRS
    if not crs or crs == CRS(ogc, 84) or crs == CRS(epsg, 4326):
        vertices = dggrs.getZoneRefinedWGS84Vertices(zone, 0)
        if vertices and vertices.count:
            count = vertices.count
            # Create list of (lon, lat) coordinates
            coords = [(float(vertices[i].lon), float(vertices[i].lat)) for i in range(count)]
            # Close the polygon by adding the first point at the end
            coords.append(coords[0])
            return shapely.geometry.Polygon(coords)
    else:
        vertices = dggrs.getZoneRefinedCRSVertices(zone, crs, 0)
        if vertices and vertices.count:
            count = vertices.count
            # Create list of (x, y) coordinates
            coords = [(float(vertices[i].x), float(vertices[i].y)) for i in range(count)]
            # Close the polygon by adding the first point at the end
            coords.append(coords[0])
            return shapely.geometry.Polygon(coords)
    
    # Return None if no valid vertices found
    return None


def characteristic_length_scale(cell_area, unit="m"):
    """
    Compute the Characteristic Length Scale (CLS) from the cell area.
    
    Parameters
    ----------
    cell_area : float
        Cell area in the specified unit.
    unit : str, optional
        Unit for the output. Must be either "m" (meters) or "km" (kilometers).
        Default is "m".
    
    Returns
    -------
    float
        Characteristic length scale in the specified unit
    
    Raises
    ------
    ValueError
        If unit is not "m" or "km".
    """
    # Validate unit parameter
    if unit not in ["m", "km"]:
        raise ValueError("unit must be 'm' or 'km', got '{}'".format(unit))
    
    # average cell area (always in km²)
    # cell_area = 4 * math.pi * AUTHALIC_RADIUS**2 / (N_cells)    
    term = math.sqrt(cell_area / math.pi) / (2.0 * AUTHALIC_RADIUS)
    
    # Handle case where term > 1 (can happen with very small cell areas)
    # This indicates the cell is smaller than what can be represented on the sphere
    if term > 1:
        # Return a very small value as the characteristic length scale
        # This is the maximum possible CLS (half the circumference of the Earth)
        cls = 2.0 * math.pi * AUTHALIC_RADIUS * (1 if unit == "km" else 1000)
    else:
        cls = 4.0 * AUTHALIC_RADIUS * math.asin(term) * (1 if unit == "km" else 1000)
    
    return cls

def characteristic_length_scale_from_num_cells(N_cells, unit="m"):
    """
    Compute the Characteristic Length Scale (CLS) from the number of cells.
    
    Parameters
    ----------
    N_cells : int
        Number of cells at the given resolution.
    unit : str, optional
        Unit for the output. Must be either "m" (meters) or "km" (kilometers).
        Default is "m".
    
    Returns
    -------
    float
        Characteristic length scale in the specified unit
    
    Raises
    ------
    ValueError
        If unit is not "m" or "km".
    """
    # Validate unit parameter
    if unit not in ["m", "km"]:
        raise ValueError("unit must be 'm' or 'km', got '{}'".format(unit))
    
    # average cell area (always in km²)
    cell_area = 4 * math.pi * AUTHALIC_RADIUS**2 / (N_cells)    
    term = math.sqrt(cell_area / math.pi) / (2.0 * AUTHALIC_RADIUS)
    
    # Handle case where term > 1 (can happen with very large numbers of cells)
    # This indicates the cell is smaller than what can be represented on the sphere
    if term > 1:
        # Return a very small value as the characteristic length scale
        # This is the maximum possible CLS (half the circumference of the Earth)
        cls = 2.0 * math.pi * AUTHALIC_RADIUS * (1 if unit == "km" else 1000)
    else:
        cls = 4.0 * AUTHALIC_RADIUS * math.asin(term) * (1 if unit == "km" else 1000)
    
    return cls

def dggrid_intercell_distance(dggs_type: str, resolution: int, unit="m"):
    """
    Compute the intercell distance for a given DGGRID type and resolution.
    """
    dggs_type = validate_dggrid_type(dggs_type)
    tmp_len = ICOSA_EDGE_KM     
    aperture = 4
    if dggs_type in ["ISEA4T", "FULLER4T"]:
        tmp_len /= math.sqrt(3)
    elif dggs_type in ["ISEA3H", "FULLER3H"]:
        aperture = 3
    elif dggs_type in ["ISEA4T", "ISEA4D","ISEA4H", "FULLER4T", "FULLER4D","FULLER4H"]:
        aperture = 4
    elif dggs_type in ["ISEA7H", "FULLER7H", "IGEO7", "PLANETRISK"]:
        aperture = 7
    elif dggs_type in ["PLANETRISK"]: # Resolution pattern: _43334777777777777777777
        if resolution == 1 or resolution == 5: 
            aperture = 4
        elif resolution >1 and resolution <5:
            aperture = 3
        else: aperture = 7        
    else:
        return None
    
    tmp_len /= pow(math.sqrt(aperture), resolution)
    return tmp_len * (1 if unit == "km" else 1000)