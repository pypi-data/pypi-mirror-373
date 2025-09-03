"""
DGGRID Statistics Module

This module provides functions to calculate and display statistics for DGGRID
Discrete Global Grid System (DGGS) types. It supports both command-line interface
and direct function calls.

Key Functions:
- dggrid_stats: Calculate and display statistics for a given DGGRID DGGS type and resolution
- dggridinspect: Generate detailed inspection data for a given DGGRID DGGS type and resolution
- main: Command-line interface for dggrid_stats
"""

import argparse
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colors import TwoSlopeNorm

from vgrid.utils.geometry import check_crossing_geom, geod, dggrid_intercell_distance
from vgrid.utils.constants import VMIN_QUAD, VMAX_QUAD, VCENTER_QUAD, VMIN_HEX, VMAX_HEX, VCENTER_HEX
from vgrid.generator.dggridgen import dggridgen
from dggrid4py import dggs_types
from pyproj import Geod
from vgrid.utils.io import  validate_dggrid_type, create_dggrid_instance
from vgrid.utils.constants import DGGRID_TYPES   
geod = Geod(ellps="WGS84")

def dggridstats(dggrid_instance, dggs_type: str, unit: str = "km") -> pd.DataFrame:      # length unit is km, area unit is km2
    """
    Return a DataFrame of DGGRID stats per resolution.

    unit: 'km' or 'm' for length columns; area is squared unit.
          DGGRID native output is km^2 for area and km for CLS.
    """
    dggs_type = validate_dggrid_type(dggs_type)
    unit_norm = unit.strip().lower()
    
    if unit_norm not in {"m", "km"}:
        raise ValueError("unit must be one of {'m','km'}")

    max_res = int(DGGRID_TYPES[dggs_type]["max_res"])

    dggrid_stats_table = dggrid_instance.grid_stats_table(dggs_type, max_res)
    # Characteristic Length Scale (CLS): the diameter of a spherical cap of the same area as a cell of the specified res
    if isinstance(dggrid_stats_table, pd.DataFrame):
        rename_map = {
            "Resolution": "resolution",
            "Cells": "number_of_cells",
            "Area (km^2)": "area_km2",
            "CLS (km)": "cls_km",
        }
        dggrid_stats = dggrid_stats_table.rename(columns=rename_map).copy()
    else:
        dggrid_stats = pd.DataFrame(
            dggrid_stats_table,
            columns=["resolution", "number_of_cells", "area_km2", "cls_km"],
        )

    # Add intercell distance in requested unit
    intercell_col = f"intercell_{unit_norm}"
    dggrid_stats[intercell_col] = dggrid_stats["resolution"].apply(
        lambda r: dggrid_intercell_distance(dggs_type, int(r), unit=unit_norm)          
    )

    if unit_norm == "m":
        dggrid_stats = dggrid_stats.rename(columns={"area_km2": "area_m2", "cls_km": "cls_m"})
        dggrid_stats["area_m2"] = dggrid_stats["area_m2"] * 1_000_000.0
        dggrid_stats["cls_m"] = dggrid_stats["cls_m"] * 1_000.0

    return dggrid_stats

def dggridstats_cli():
	"""
	Command-line interface for generating DGGAL DGGS statistics.

	CLI options:
	  -dggs, --dggs_type {gnosis, isea3h, isea9r, ivea3h, ivea9r, rtea3h, rtea9r, rhealpix}
	  -unit, --unit {m,km}
	  --minres, --maxres
	"""
	parser = argparse.ArgumentParser(add_help=False)
	parser.add_argument("-dggs", "--dggs_type", dest="dggs_type", choices=DGGRID_TYPES.keys())
	parser.add_argument("-unit", "--unit", dest="unit", choices=["m", "km"], default="km")
	args = parser.parse_args()

	dggs_type = args.dggs_type
	unit = args.unit

	dggrid_instance = create_dggrid_instance()
	result = dggridstats(dggrid_instance, dggs_type, unit)
	if result is not None:
		print(result)

def dggridinspect(dggrid_instance, dggs_type: str, resolution: int, crs: str | None = None) -> gpd.GeoDataFrame:
    """
    Generate detailed inspection data for a DGGRID DGGS type at a given resolution.

    Args:
        dggs_type: DGGS type supported by DGGRID (see dggs_types)
        res: Resolution level
        crs: Coordinate reference system (optional)

    Returns:
        geopandas.GeoDataFrame: DataFrame containing inspection data with columns:
          - name (cell identifier from DGGRID)
          - resolution
          - geometry
          - cell_area (m^2)
          - cell_perimeter (m)
          - crossed (bool)
          - norm_area (area/mean_area)
          - ipq (4πA/P²)
          - zsc (sqrt(4πA - A²/R²)/P), with R=WGS84 a
    """
            
    # Generate grid using dggridgen
    dggrid_gdf = dggridgen(dggrid_instance, dggs_type, resolution, output_format="gpd")
    
    # Remove cells with null or invalid geometry
    dggrid_gdf = dggrid_gdf.dropna(subset=['geometry'])
    dggrid_gdf = dggrid_gdf[dggrid_gdf.geometry.is_valid]
    
    # Add dggs_type column
    dggrid_gdf["dggs_type"] = f"dggrid_{dggs_type.lower()}"
    
    # Rename global_id to cell_id
    if 'global_id' in dggrid_gdf.columns:
        dggrid_gdf = dggrid_gdf.rename(columns={'global_id': 'cell_id'})

    # Determine whether current CRS is geographic; compute metrics accordingly
    if dggrid_gdf.crs.is_geographic:
        dggrid_gdf["cell_area"] = dggrid_gdf.geometry.apply(lambda g: abs(geod.geometry_area_perimeter(g)[0]))
        dggrid_gdf["cell_perimeter"] = dggrid_gdf.geometry.apply(lambda g: abs(geod.geometry_area_perimeter(g)[1]))
        dggrid_gdf["crossed"] = dggrid_gdf.geometry.apply(check_crossing_geom)
    else:
        dggrid_gdf["cell_area"] = dggrid_gdf.geometry.area
        dggrid_gdf["cell_perimeter"] = dggrid_gdf.geometry.length
        dggrid_gdf["crossed"] = False

    # Add resolution column
    dggrid_gdf["resolution"] = resolution
    

    # Calculate normalized area
    mean_area = dggrid_gdf["cell_area"].mean()
    dggrid_gdf["norm_area"] = dggrid_gdf["cell_area"] / mean_area if mean_area and mean_area != 0 else np.nan
    
    # Calculate compactness metrics (robust formulas avoiding division by zero)
    dggrid_gdf['ipq'] = 4 * np.pi * dggrid_gdf['cell_area'] / (dggrid_gdf['cell_perimeter'] ** 2)
    dggrid_gdf['zsc'] = np.sqrt(4*np.pi*dggrid_gdf['cell_area'] - np.power(dggrid_gdf['cell_area'],2)/np.power(6378137,2))/dggrid_gdf['cell_perimeter']
    
    return dggrid_gdf


def dggrid_norm_area(gdf, dggs_type="DGGRID", crs='proj=moll'):
    """
    Plot normalized area map for DGGRID cells.
    """
    fig, ax = plt.subplots(figsize=(10,5))
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("bottom", size="5%", pad=0.1)
    vmin, vmax, vcenter = gdf['norm_area'].min(), gdf['norm_area'].max(), 1
    norm = TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
    gdf = gdf[~gdf['crossed']] # remove cells that cross the dateline
    gdf.to_crs(crs).plot(column='norm_area', ax=ax, norm=norm, legend=True, cax=cax, cmap='RdYlBu_r', legend_kwds={'label': "cell area/mean cell area",'orientation': "horizontal"})
    world_countries = gpd.read_file('https://raw.githubusercontent.com/opengeoshub/vopendata/refs/heads/main/shape/world_countries.geojson')
    world_countries.boundary.to_crs(crs).plot(color=None, edgecolor='black', linewidth=0.2, ax=ax)
    ax.axis('off')
    cb_ax = fig.axes[1] 
    cb_ax.tick_params(labelsize=14)
    cb_ax.set_xlabel(xlabel=f"{dggs_type.upper()} Normalized Area", fontsize=14)
    ax.margins(0)
    ax.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)
    plt.tight_layout()


def dggrid_compactness(gdf: gpd.GeoDataFrame, dggs_type: str = "DGGRID", crs: str | None = 'proj=moll'):
    """
    Plot IPQ compactness map for DGGRID cells.
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("bottom", size="5%", pad=0.1)
    
    # Determine compactness bounds based on topology
    vmin, vmax, vcenter = VMIN_QUAD, VMAX_QUAD, VCENTER_QUAD
    
    dggs_type_norm = str(dggs_type).strip().lower()
    if any(hex_type in dggs_type_norm for hex_type in ["3h", "4h", "7h", "43h"]):
        vmin, vmax, vcenter = VMIN_HEX, VMAX_HEX, VCENTER_HEX
    
    norm = TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
    # Only filter out antimeridian-crossed cells when plotting in EPSG:4326
    gdf = gdf[~gdf['crossed']]
    gdf_plot = gdf.to_crs(crs) if crs else gdf
    gdf_plot.plot(column='ipq', ax=ax, norm=norm, legend=True, cax=cax,
                  cmap='viridis', legend_kwds={'orientation': "horizontal"})
    world_countries = gpd.read_file('https://raw.githubusercontent.com/opengeoshub/vopendata/refs/heads/main/shape/world_countries.geojson')
    wc_plot = world_countries.boundary.to_crs(crs)
    wc_plot.plot(color=None, edgecolor='black', linewidth=0.2, ax=ax)
    ax.axis('off')
    cb_ax = fig.axes[1]
    cb_ax.tick_params(labelsize=14)
    cb_ax.set_xlabel(xlabel=f"{dggs_type.upper()} IPQ Compactness", fontsize=14)
    ax.margins(0)
    ax.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)
    plt.tight_layout()


def dggrid_norm_area_hist(gdf, dggs_type="DGGRID"):
	"""
	Plot histogram of normalized area for DGGRID cells.
	
	This function creates a histogram visualization showing the distribution
	of normalized areas for DGGRID cells, helping to understand area variations
	and identify patterns in area distortion.
	
	Args:
		gdf: GeoDataFrame from dggridinspect function
		dggs_type: DGGS type name for labeling
	"""
	# Filter out cells that cross the dateline
	gdf_filtered = gdf[~gdf['crossed']]
	
	# Create the histogram with color ramp
	fig, ax = plt.subplots(figsize=(10, 6))
	
	# Get histogram data
	counts, bins, patches = ax.hist(gdf_filtered['norm_area'], bins=50, alpha=0.7, edgecolor='black')
	
	# Create color ramp using the same normalization as the map function
	vmin, vmax, vcenter = gdf_filtered['norm_area'].min(), gdf_filtered['norm_area'].max(), 1
	norm = TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
	
	# Apply colors to histogram bars using the same color mapping as the map
	for i, patch in enumerate(patches):
		# Use the center of each bin for color mapping
		bin_center = (bins[i] + bins[i+1]) / 2
		color = plt.cm.RdYlBu_r(norm(bin_center))
		patch.set_facecolor(color)
	
	# Add reference line at mean area (norm_area = 1)
	ax.axvline(x=1, color='red', linestyle='--', linewidth=2, label='Mean Area (norm_area = 1)')
	
	# Add statistics text box
	stats_text = f'Mean: {gdf_filtered["norm_area"].mean():.3f}\nStd: {gdf_filtered["norm_area"].std():.3f}\nMin: {gdf_filtered["norm_area"].min():.3f}\nMax: {gdf_filtered["norm_area"].max():.3f}'
	ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=12, verticalalignment='top', 
			 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
	
	# Customize the plot
	ax.set_xlabel(f'{dggs_type.upper()} normalized area', fontsize=14)
	ax.set_ylabel('Number of cells', fontsize=14)
	ax.legend(fontsize=12)
	ax.grid(True, alpha=0.3)
	
	plt.tight_layout()


def dggrid_compactness_hist(gdf, dggs_type="DGGRID"):
	"""
	Plot histogram of IPQ compactness for DGGRID cells.
	
	This function creates a histogram visualization showing the distribution
	of Isoperimetric Quotient (IPQ) compactness values for DGGRID cells, helping
	to understand how close cells are to being regular shapes.
	
	Args:
		gdf: GeoDataFrame from dggridinspect function
		dggs_type: DGGS type name for labeling and determining ideal IPQ values
	"""
	# Filter out cells that cross the dateline
	gdf_filtered = gdf[~gdf['crossed']]
	
	# Create the histogram with color ramp
	fig, ax = plt.subplots(figsize=(10, 6))
	
	# Get histogram data
	counts, bins, patches = ax.hist(gdf_filtered['ipq'], bins=50, alpha=0.7, edgecolor='black')
	
	# Create color ramp using the same normalization as the map function
	dggs_type_norm = str(dggs_type).strip().lower()
	if any(hex_type in dggs_type_norm for hex_type in ["3h", "4h", "7h", "43h"]):
		# Hexagonal cells
		norm = TwoSlopeNorm(vmin=VMIN_HEX, vcenter=VCENTER_HEX, vmax=VMAX_HEX)
		ideal_ipq = 0.907  # Ideal hexagon
		shape_name = "Hexagon"
	else:
		# Quadrilateral cells
		norm = TwoSlopeNorm(vmin=VMIN_QUAD, vcenter=VCENTER_QUAD, vmax=VMAX_QUAD)
		ideal_ipq = 0.785  # Ideal square (π/4)
		shape_name = "Square"
	
	# Apply colors to histogram bars using the same color mapping as the map
	for i, patch in enumerate(patches):
		# Use the center of each bin for color mapping
		bin_center = (bins[i] + bins[i+1]) / 2
		color = plt.cm.viridis(norm(bin_center))
		patch.set_facecolor(color)
	
	# Add reference line at ideal IPQ value
	ax.axvline(x=ideal_ipq, color='red', linestyle='--', linewidth=2, label=f'Ideal {shape_name} (IPQ = {ideal_ipq:.3f})')
	
	# Add statistics text box
	stats_text = f'Mean: {gdf_filtered["ipq"].mean():.3f}\nStd: {gdf_filtered["ipq"].std():.3f}\nMin: {gdf_filtered["ipq"].min():.3f}\nMax: {gdf_filtered["ipq"].max():.3f}'
	ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=12, verticalalignment='top', 
			 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
	
	# Customize the plot
	ax.set_xlabel(f'{dggs_type.upper()} IPQ Compactness', fontsize=14)
	ax.set_ylabel('Number of cells', fontsize=14)
	ax.legend(fontsize=12)
	ax.grid(True, alpha=0.3)
	
	plt.tight_layout()


def dggridinspect_cli():
    """
    Command-line interface for DGGRID cell inspection.

    CLI options:
      -t, --dggs_type: DGGS type from dggs_types
      -r, --resolution: Resolution level
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-dggs', '--dggs_type', dest='dggs_type', choices=dggs_types, required=True)
    parser.add_argument('-r', '--resolution', dest='resolution', type=int, default=None)
    parser.add_argument('-crs', dest='crs', type=str, default=None, help="CRS to pass to DGGRID; omit for WGS84")
    args, _ = parser.parse_known_args()
    res = args.resolution if args.resolution is not None else 0
    
    dggrid_instance = create_dggrid_instance()

    print(dggridinspect(dggrid_instance, args.dggs_type, res, crs=args.crs))


if __name__ == "__main__":
    dggridstats_cli()
