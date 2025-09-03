"""
Polygon Binning Module

Bins point data into custom polygon geometries and computes various statistics using pre-defined polygon features like administrative boundaries.

Key Functions:
- polygon_bin(): Core binning function with spatial joins and aggregation
- polygonbin(): Main user-facing function with multiple input/output formats
- polygonbin_cli(): Command-line interface for binning functionality
"""

import argparse
import geopandas as gpd
from vgrid.utils.io import process_input_data_bin, convert_to_output_format
from vgrid.utils.constants import STATS_OPTIONS, OUTPUT_FORMATS, STRUCTURED_FORMATS     

def polygon_bin(polygon_data, point_data, stats="count", category=None, numeric_field=None, lat_col="lat", lon_col="lon", **kwargs):
    """
    Bin points into provided polygons using spatial join + pandas groupby aggregation.
    No grid generation is performed; the input polygons are used directly.
    """
    # Read inputs
    polygon_gdf = process_input_data_bin(polygon_data, lat_col=lat_col, lon_col=lon_col, **kwargs)
    point_gdf = process_input_data_bin(point_data, lat_col=lat_col, lon_col=lon_col, **kwargs)

    # Ensure valid polygons only
    polygon_gdf = polygon_gdf[polygon_gdf.geometry.notnull()]
    polygon_gdf = polygon_gdf[polygon_gdf.geometry.is_valid]

    # Keep Points/MultiPoints for points and explode MultiPoints
    if not point_gdf.empty:
        point_gdf = point_gdf[point_gdf.geometry.geom_type.isin(["Point", "MultiPoint"])].copy()
        if "MultiPoint" in set(point_gdf.geometry.geom_type.unique()):
            point_gdf = point_gdf.explode(index_parts=False, ignore_index=True)

    # Create a stable polygon id for join/merge
    polygon_gdf = polygon_gdf.reset_index(drop=True).copy()
    id_col = "poly_id"
    polygon_gdf[id_col] = polygon_gdf.index

    # Select required columns from points for join and aggregation
    join_cols = []
    if category and category in point_gdf.columns:
        join_cols.append(category)
    if stats != "count" and numeric_field:
        if numeric_field not in point_gdf.columns:
            raise ValueError(f"numeric_field '{numeric_field}' not found in point data")
        join_cols.append(numeric_field)
    left = point_gdf[[c for c in ["geometry", *join_cols] if c is not None]]

    # Spatial join: assign each point to a polygon
    joined = gpd.sjoin(left, polygon_gdf[[id_col, "geometry"]], how="inner", predicate="within")

    # Aggregate per polygon (and optional category)
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

    # Merge aggregates back to polygons; keep original polygon attributes
    out = polygon_gdf.merge(grouped, on=id_col, how="left")
    out = out.drop(columns=[id_col])
    result_gdf = gpd.GeoDataFrame(out, geometry="geometry", crs="EPSG:4326")
    return result_gdf

def polygonbin(
    polygon_data,
    point_data,
    stats="count",
    category=None,
    numeric_field=None,
    output_format="gpd",
    **kwargs,
):
    if stats not in STATS_OPTIONS:
        raise ValueError(f"Unsupported statistic: {stats}")
    if stats != "count" and not numeric_field:
        raise ValueError("A numeric_field is required for statistics other than 'count'")
    result_gdf = polygon_bin(polygon_data, point_data, stats, category, numeric_field, **kwargs)
    output_name = None
    if output_format in OUTPUT_FORMATS:
        import os
        ext_map = {
            "csv": ".csv",
            "geojson": ".geojson",
            "shapefile": ".shp",
            "gpkg": ".gpkg",
            "parquet": ".parquet",
        }
        ext = ext_map.get(output_format, "")
        if isinstance(point_data, str):
            base = os.path.splitext(os.path.basename(point_data))[0]
            output_name = f"{base}_polygonbin_{stats}{ext}"
        else:
            output_name = f"polygonbin_{stats}{ext}"
    return convert_to_output_format(result_gdf, output_format, output_name)

def polygonbin_cli():
    parser = argparse.ArgumentParser(description="Bin points into polygons and compute statistics")
    parser.add_argument(
        "-i", "--input",
        type=str,
        required=True,
        help="Input point data: GeoJSON file path, URL, or other vector file formats",
    )
    parser.add_argument(
        "-p", "--polygon",
        type=str,
        required=True,
        help="Input polygon data: GeoJSON file path, URL, or other vector file formats",
    )
    parser.add_argument(
        "-stats",
        "--statistic",
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
    # Removed -o/--output; output saved in CWD with predefined name
    parser.add_argument(
        "-f", "--output_format",
        required=False,
        default="gpd",
        choices=OUTPUT_FORMATS,
    )
    args = parser.parse_args()
    try:
        result = polygonbin(
            polygon_data=args.polygon,
            point_data=args.input,
            stats=args.statistic,
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
    polygonbin_cli()
