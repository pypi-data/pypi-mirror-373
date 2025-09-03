"""
Quadkey Grid Binning Module

Bins point data into Quadkey grid cells and computes various statistics using hierarchical geospatial indexing system used by mapping services.

Key Functions:
- quadkey_bin(): Core binning function with spatial joins and aggregation
- quadkeybin(): Main user-facing function with multiple input/output formats
- quadkeybin_cli(): Command-line interface for binning functionality
"""

import argparse
import geopandas as gpd
from vgrid.utils.io import process_input_data_bin, convert_to_output_format, validate_quadkey_resolution
from vgrid.utils.constants import STATS_OPTIONS, OUTPUT_FORMATS, STRUCTURED_FORMATS

def quadkey_bin(data, resolution, stats="count", category=None, numeric_field=None, lat_col="lat", lon_col="lon", **kwargs):
    resolution = validate_quadkey_resolution(resolution)
    points_gdf = process_input_data_bin(data, lat_col=lat_col, lon_col=lon_col, **kwargs)
    # Keep only points and multipoints; ignore others
    if not points_gdf.empty:
        points_gdf = points_gdf[points_gdf.geometry.geom_type.isin(["Point", "MultiPoint"])].copy()
        if "MultiPoint" in set(points_gdf.geometry.geom_type.unique()):
            points_gdf = points_gdf.explode(index_parts=False, ignore_index=True)

    # Generate Quadkey grid covering the points' bbox
    minx, miny, maxx, maxy = points_gdf.total_bounds
    id_col = "quadkey"
    from vgrid.generator.quadkeygrid import quadkey_grid
    grid_gdf = quadkey_grid(resolution=resolution, bbox=(minx, miny, maxx, maxy))

    # Spatial join
    join_cols = []
    if category and category in points_gdf.columns:
        join_cols.append(category)
    if stats != "count" and numeric_field:
        if numeric_field not in points_gdf.columns:
            raise ValueError(f"numeric_field '{numeric_field}' not found in input data")
        join_cols.append(numeric_field)
    left = points_gdf[[c for c in ["geometry", *join_cols] if c is not None]]
    joined = gpd.sjoin(left, grid_gdf[[id_col, "geometry"]], how="inner", predicate="within")

    # Aggregate
    special_stats = {"range", "minority", "majority", "variety"}
    if stats in special_stats:
        value_field = numeric_field if numeric_field else category
        if not value_field:
            raise ValueError(f"'{stats}' requires either numeric_field or category to be provided")

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

    # Merge back to grid for geometry
    out = grid_gdf[[id_col, "geometry"]].merge(grouped, on=id_col, how="inner")
    out["resolution"] = resolution
    result_gdf = gpd.GeoDataFrame(out, geometry="geometry", crs="EPSG:4326")
    return result_gdf

def quadkeybin(
    data,
    resolution,
    stats="count",
    category=None,
    numeric_field=None,
    output_format="gpd",
    **kwargs,
):
    resolution = validate_quadkey_resolution(resolution)
    if stats != "count" and not numeric_field:
        raise ValueError("A numeric_field is required for statistics other than 'count'")
    result_gdf = quadkey_bin(data, resolution, stats, category, numeric_field, **kwargs)
    output_name = None
    if output_format in OUTPUT_FORMATS:
        import os
        if isinstance(data, str):
            base = os.path.splitext(os.path.basename(data))[0]
            output_name = f"{base}_quadkeybin_{resolution}"
        else:
            output_name = f"quadkeybin_{resolution}"
    return convert_to_output_format(result_gdf, output_format, output_name)

def quadkeybin_cli():
    parser = argparse.ArgumentParser(description="Binning point data to Quadkey DGGS")
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
        default=15,
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
        result = quadkeybin(
            data=args.input,
            resolution=args.resolution,
            stats=args.statistics,
            category=args.category,
            numeric_field=args.numeric_field,
            output_format=args.output_format            
        )
        if args.output_format in STRUCTURED_FORMATS:
            print(result)
    except Exception as e:
        print(f"Error: {str(e)}")
        return

if __name__ == "__main__":
    quadkeybin_cli()
