"""
A5 Grid Binning Module

Bins point data into A5 (Adaptive 5) grid cells and computes various statistics using hierarchical geospatial indexing.

Key Functions:
- a5_bin(): Core binning function with spatial joins and aggregation
- a5bin(): Main user-facing function with multiple input/output formats
- a5bin_cli(): Command-line interface for binning functionality
"""

import os
import argparse
import geopandas as gpd
from vgrid.generator.a5grid import a5_grid
from vgrid.utils.io import (
    process_input_data_bin,
    convert_to_output_format,
    validate_a5_resolution,
)
from vgrid.utils.constants import STATS_OPTIONS, OUTPUT_FORMATS, STRUCTURED_FORMATS

def a5_bin(
    data,
    resolution,
    stats="count",
    category=None,
    numeric_field=None,
    lat_col="lat",
    lon_col="lon",
    **kwargs,
):
    """
    Bin point data into A5 grid cells and compute statistics using a single
    grid generation + spatial join, followed by pandas groupby aggregation.

    Returns a GeoDataFrame with A5 cell stats and geometry.
    """
    resolution = validate_a5_resolution(int(resolution))

    if stats != "count" and not numeric_field:
        raise ValueError("A numeric_field is required for statistics other than 'count'")

    # 1) Normalize input to GeoDataFrame of points
    points_gdf = process_input_data_bin(data, lat_col=lat_col, lon_col=lon_col, **kwargs)
    # Keep only points and multipoints; ignore others
    if not points_gdf.empty:
        points_gdf = points_gdf[points_gdf.geometry.geom_type.isin(["Point", "MultiPoint"])].copy()
        if "MultiPoint" in set(points_gdf.geometry.geom_type.unique()):
            points_gdf = points_gdf.explode(index_parts=False, ignore_index=True)

    # 2) Generate A5 grid covering the points' bounding box
    minx, miny, maxx, maxy = points_gdf.total_bounds  # lon/lat order
    id_col = "a5"
    grid_gdf = a5_grid(resolution=resolution, bbox=(minx, miny, maxx, maxy))

    # 3) Spatial join points -> cells with only needed columns
    join_cols = []
    if category and category in points_gdf.columns:
        join_cols.append(category)
    if stats != "count" and numeric_field:
        if numeric_field not in points_gdf.columns:
            raise ValueError(f"numeric_field '{numeric_field}' not found in input data")
        join_cols.append(numeric_field)
    left = points_gdf[[c for c in ["geometry", *join_cols] if c is not None]]
    joined = gpd.sjoin(left, grid_gdf[[id_col, "geometry"]], how="inner", predicate="within")

    # 4) Aggregate
    special_stats = {"range", "minority", "majority", "variety"}
    if stats in special_stats:
        value_field = numeric_field if numeric_field else category
        if not value_field:
            raise ValueError(
                f"'{stats}' requires either numeric_field or category to be provided"
            )

        if category:
            group_cols = [id_col, category]
            if stats == "variety":
                ser = joined.groupby(group_cols)[value_field].nunique()
                grouped = ser.unstack(fill_value=0)
                grouped.columns = [f"{cat}_variety" for cat in grouped.columns]
            elif stats == "range":
                ser = joined.groupby(group_cols)[value_field].agg(lambda s: (s.max() - s.min()) if len(s) else 0)
                grouped = ser.unstack(fill_value=0)
                grouped.columns = [f"{cat}_range" for cat in grouped.columns]
            elif stats in {"minority", "majority"}:
                def pick_value(s, pick):
                    vc = s.value_counts()
                    if vc.empty:
                        return None
                    if pick == "minority":
                        vc = vc.sort_values(ascending=True)
                    else:
                        vc = vc.sort_values(ascending=False)
                    return vc.index[0]
                ser = joined.groupby(group_cols)[value_field].apply(lambda s: pick_value(s, stats))
                grouped = ser.unstack()
                grouped.columns = [f"{cat}_{stats}" for cat in grouped.columns]
        else:
            if stats == "variety":
                grouped = joined.groupby(id_col)[value_field].nunique().to_frame("variety")
            elif stats == "range":
                grouped = joined.groupby(id_col)[value_field].agg(lambda s: (s.max() - s.min()) if len(s) else 0).to_frame("range")
            elif stats in {"minority", "majority"}:
                def pick_value(s, pick):
                    vc = s.value_counts()
                    if vc.empty:
                        return None
                    if pick == "minority":
                        vc = vc.sort_values(ascending=True)
                    else:
                        vc = vc.sort_values(ascending=False)
                    return vc.index[0]
                grouped = joined.groupby(id_col)[value_field].apply(lambda s: pick_value(s, stats)).to_frame(stats)
    else:
        if category:
            if stats == "count":
                grouped = joined.groupby([id_col, category]).size().unstack(fill_value=0)
                grouped.columns = [f"{cat}_count" for cat in grouped.columns]
            else:
                grouped = joined.groupby([id_col, category])[numeric_field].agg(stats).unstack()
                grouped.columns = [f"{cat}_{stats}" for cat in grouped.columns]
        else:
            if stats == "count":
                grouped = joined.groupby(id_col).size().to_frame("count")
            else:
                grouped = joined.groupby(id_col)[numeric_field].agg(stats).to_frame(stats)
    grouped = grouped.reset_index()

    # 5) Join back to grid and return GeoDataFrame
    out = grid_gdf[[id_col, "geometry"]].merge(grouped, on=id_col, how="inner")
    out["resolution"] = resolution
    result_gdf = gpd.GeoDataFrame(out, geometry="geometry", crs="EPSG:4326")
    return result_gdf

def a5bin(
    data,
    resolution,
    stats="count",
    category=None,
    numeric_field=None,
    output_format="gpd",
    **kwargs,
):
    """
    Bin point data into A5 grid cells and compute statistics from various input formats.

    This is the main function that handles binning of point data to A5 grid cells.
    It supports multiple input formats including file paths, URLs, DataFrames, GeoDataFrames,
    GeoJSON dictionaries, and lists of features.

    Args:
        data: Input data in one of the following formats:
            - File path (str): Path to vector file (shapefile, GeoJSON, etc.)
            - URL (str): URL to vector data
            - pandas.DataFrame: DataFrame with lat/lon columns
            - geopandas.GeoDataFrame: GeoDataFrame with point geometries
            - dict: GeoJSON dictionary
            - list: List of GeoJSON feature dictionaries
        resolution (int): A5 resolution level [0..29] (0=coarsest, 29=finest)
        stats (str): Statistic to compute:      
            - 'count': Count of points in each cell
            - 'sum': Sum of field values
            - 'min': Minimum field value
            - 'max': Maximum field value
            - 'mean': Mean field value
            - 'median': Median field value
            - 'std': Standard deviation of field values
            - 'var': Variance of field values
            - 'range': Range of field values
            - 'minority': Least frequent value
            - 'majority': Most frequent value
            - 'variety': Number of unique values
        category (str, optional): Category field for grouping statistics. When provided,
            statistics are computed separately for each category value.
        numeric_field (str, optional): Numeric field to compute statistics (required if stats != 'count')
        output_format (str, optional): Output format. Options include:
            - 'gpd', 'geopandas', 'gdf', 'geodataframe': Return GeoDataFrame
            - 'geojson_dict', 'json_dict': Return GeoJSON dictionary
            - 'geojson', 'json': Save as GeoJSON file or return string
            - 'csv': Save as CSV file or return string
            - 'shp', 'shapefile': Save as shapefile
            - 'gpkg', 'geopackage': Save as GeoPackage
            - 'parquet', 'geoparquet': Save as Parquet file
            - None: Return list of dictionaries
        **kwargs: Additional arguments passed to geopandas read functions (e.g., lat_col, lon_col)

    Returns:
        Various types depending on output_format:
        - GeoDataFrame: When output_format is 'gpd', 'geopandas', 'gdf', 'geodataframe'
        - dict: When output_format is 'geojson_dict', 'json_dict', or None
        - str: When output_format is 'geojson', 'json', or 'csv' (returns data as string)
        - str: File path when output_format is a file-based format (geojson, csv, shp, gpkg, parquet)

    Raises:
        ValueError: If input data type is not supported, conversion fails, or required parameters are missing
        TypeError: If resolution is not an integer

    Example:
        >>> # Bin from file with count statistics
        >>> result = a5bin("cities.shp", 10, "count")
        
        >>> # Bin from GeoDataFrame with mean statistics
        >>> import geopandas as gpd
        >>> gdf = gpd.read_file("cities.shp")
        >>> result = a5bin(gdf, 10, "mean", numeric_field="population")
        
        >>> # Bin from GeoJSON dict with category grouping
        >>> geojson = {"type": "FeatureCollection", "features": [...]}
        >>> result = a5bin(geojson, 10, "sum", numeric_field="value", category="type")
        
        >>> # Save output as GeoJSON file
        >>> result = a5bin("points.csv", 8, "count", output_format="geojson")
        >>> print(f"Output saved to: {result}")
    """

    if stats != "count" and not numeric_field:
        raise ValueError("A numeric_field is required for statistics other than 'count'")

    # Process input data and bin
    result_gdf = a5_bin(data, resolution, stats, category, numeric_field, **kwargs)
    
    # Convert to output output_format if specified
    output_name = None
    if output_format in OUTPUT_FORMATS:
        if isinstance(data, str):
            base = os.path.splitext(os.path.basename(data))[0]
            output_name = f"{base}_a5bin_{resolution}"
        else:
            output_name = f"a5bin_{resolution}"
    return convert_to_output_format(result_gdf, output_format, output_name)


def a5bin_cli():
    """
    Command-line interface for a5bin conversion.

    This function provides a command-line interface for binning point data to A5 grid cells.
    It parses command-line arguments and calls the main a5bin function.

    Usage:
        python a5bin.py -i input.shp -r 10 -stats count -f geojson -o output.geojson

    Arguments:
        -i, --input: Input file path, URL, or other vector file formats
        -r, --resolution: A5 resolution [0..29]
        -stats, --statistics: Statistic to compute (count, min, max, sum, mean, median, std, var, range, minority, majority, variety)
        -category, --category: Optional category field for grouping
        -field, --field: Numeric field to compute statistics (required if stats != 'count')
        -o, --output: Output file path (optional, will auto-generate if not provided)
        -f, --output_format: Output output_format (geojson, gpkg, parquet, csv, shapefile)

    Example:
        >>> # Bin shapefile to A5 cells at resolution 10 with count statistics
        >>> # python a5bin.py -i cities.shp -r 10 -stats count -f geojson
    """
    parser = argparse.ArgumentParser(description="Binning point data to A5 DGGS")
    parser.add_argument(
        "-i", "--input",
        type=str,
        required=True,
        help="Input data: GeoJSON file path, URL, or other vector file formats",
    )
    parser.add_argument(
        "-r",
        "--resolution",
        type=int,
        default=13,
        help="Resolution of the grid [0..29]",
    )
    parser.add_argument(
        "-stats",
        "--statistics",
        choices=STATS_OPTIONS,
        default="count",
        help="Statistic option",
    )

    parser.add_argument(
        "-category",
        "--category",
        required=False,
        help="Optional category field for grouping",
    )
    parser.add_argument(
        "-field", "--field", dest="numeric_field", required=False, help="Numeric field to compute statistics (required if stats != 'count')"
    )
    # Removed -o/--output; output is saved in CWD with predefined name
    parser.add_argument(
        "-f", "--output_format",
        required=False,
        default="gpd",
        choices=OUTPUT_FORMATS,
    )

    args = parser.parse_args()

    try:
        # Use the a5bin function
        result = a5bin(
            data=args.input,
            resolution=args.resolution,
            stats=args.statistics,
            category=args.category,
            numeric_field=args.numeric_field,
            output_format=args.output_format,            
        )
        if args.output_format in STRUCTURED_FORMATS:
            print(result)        
        # Print notification is now handled in convert_to_output_format
    except Exception as e:
        print(f"Error: {str(e)}")
        return


if __name__ == "__main__":
    a5bin_cli() 