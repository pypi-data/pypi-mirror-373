"""
This module provides lightweight wrappers for DGGAL using the external `dgg` CLI directly.

Per request, `dggalstats` simply returns the direct output from
`dgg <dggs_type> level` without computing any additional metrics.
"""

import argparse
import shutil
import subprocess
import sys
import numpy as np
import pandas as pd
import math
import geopandas as gpd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colors import TwoSlopeNorm

from vgrid.utils.geometry import check_crossing_geom, geod, characteristic_length_scale	
from vgrid.utils.constants import AUTHALIC_AREA, DGGAL_TYPES, VMIN_QUAD, VMAX_QUAD, VCENTER_QUAD, VMIN_HEX, VMAX_HEX, VCENTER_HEX
from vgrid.generator.dggalgen import dggalgrid                                  
from pyproj import Geod
from vgrid.utils.io import validate_dggal_resolution, validate_dggal_type       
from vgrid.utils.constants import DGGAL_TYPES		
# Import dggal library
from dggal import *
# Initialize dggal application
app = Application(appGlobals=globals())
pydggal_setup(app)

geod = Geod(ellps="WGS84")


def dggalinfo(dggs_type: str) -> str | None:
	"""
	Return the direct stdout from `dgg <dggs_type> level`.

	Args:
		dggs_type: DGGS type supported by DGGAL (see vgrid.utils.constants.dggs_type)

	Returns:
		stdout string on success; None on failure.
	"""
	dggs_type = validate_dggal_type(dggs_type)

	dgg_exe = shutil.which("dgg")
	if dgg_exe is None:
		print(
			"Error: `dgg` command not found. Please ensure the `dggal` package is installed and `dgg` is on PATH.",
			file=sys.stderr,
		)
		return None

	# Use the style: `dgg <dggs_type> level`
	cmd = [dgg_exe, dggs_type, "level"]

	try:
		completed = subprocess.run(
			cmd,
			check=True,
			capture_output=True,
			text=True,
			encoding="utf-8",
			errors="replace",
		)
		stdout = completed.stdout
	except Exception as exc:
		print(f"Failed to run {' '.join(cmd)}: {exc}", file=sys.stderr)
		return None
	# Return the textual table directly for display
	return stdout


def dggalinfo_cli():
	"""
	Command-line interface for generating DGGAL DGGS statistics.

	CLI options:
	  -dggs, --dggs_type {gnosis, isea3h, isea9r, ivea3h, ivea9r, rtea3h, rtea9r, rhealpix}
	  -unit, --unit {m,km}
	  --minres, --maxres
	"""
	parser = argparse.ArgumentParser(add_help=False)
	# Positional shorthand: dggalstats isea3h
	parser.add_argument("pos_dggs_type", nargs="?", choices=DGGAL_TYPES.keys())
	# Optional flag remains supported for type
	parser.add_argument("-dggs", "--dggs_type", dest="dggs_type", choices=DGGAL_TYPES.keys())
	args, _ = parser.parse_known_args()

	# Resolve parameters from positional or flagged inputs
	dggs_type = args.pos_dggs_type or args.dggs_type

	if dggs_type is None:
		raise SystemExit("Error: dggs_type is required. Usage: dggalstats <dggs_type> or with flag -t")

	result = dggalinfo(dggs_type)
	if result is not None:
		print(result)


def dggal_metrics(dggs_type: str, res: int, unit: str = "km"):					# length unit is km, area unit is km2
	"""
	Calculate metrics for DGGAL cells at a given resolution.
	
	Args:
		dggs_type: DGGS type supported by DGGAL (see vgrid.utils.constants.DGGAL_TYPES)
		res: Resolution level (0-29)
		unit: 'm' or 'km' for length; area will be 'm^2' or 'km^2'
	
	Returns:
		tuple: (num_cells, edge_length_in_unit, cell_area_in_unit_squared)
	"""

	dggs_type = validate_dggal_type(dggs_type)
	res = validate_dggal_resolution(dggs_type, int(res))

	unit_norm = unit.strip().lower()
	if unit_norm not in {"m", "km"}:
		raise ValueError("unit must be one of {'m','km'}")

	if dggs_type == "gnosis": 
		num_edges = 4  # Square cells
	elif dggs_type in ["isea9r", "ivea9r", "rtea9r"]:
		num_edges = 4  # Square cells
	elif dggs_type in ["isea3h", "ivea3h", "rtea3h"]:
		num_edges = 6  # Hexagonal cells
	elif dggs_type == "rhealpix":
		num_edges = 4  # Square cells
	else:
		num_edges = 4  # Default to square cells

	# Calculate number of cells using the original formulas
	if dggs_type == "gnosis": 
		num_cells = (16 * (4**res) + 8) // 3 
	elif dggs_type in ["isea9r", "ivea9r", "rtea9r"]:
		num_cells = 10*(9**res)
	elif dggs_type in ["isea3h", "ivea3h", "rtea3h"]:
		num_cells = 10*(3**res) + 2
	elif dggs_type == "rhealpix":
		num_cells = 6 * 9 ** (res)
	else:
		num_cells = 1

	avg_cell_area = AUTHALIC_AREA / num_cells
	cls = characteristic_length_scale(avg_cell_area, unit=unit)
	# Calculate average edge length based on the number of edges
	if num_edges == 6:  # Hexagonal cells
		avg_edge_len = math.sqrt((2 * avg_cell_area) / (3 * math.sqrt(3)))
	else:  # Square or other polygonal cells
		avg_edge_len = math.sqrt(avg_cell_area)
		
	# Convert to requested unit
	if unit_norm == "m":
		avg_edge_len = avg_edge_len * 1000
		avg_cell_area = avg_cell_area * (10**6)

	return num_cells, avg_edge_len, avg_cell_area, cls


def dggalstats(dggs_type: str, unit: str = "km") -> pd.DataFrame | None:			# length unit is km, area unit is km2
	"""	
	Compute and return a DataFrame of DGGAL metrics per resolution for the given type.

	Args:
		dggs_type: DGGS type supported by DGGAL (see vgrid.utils.constants.DGGAL_TYPES)
		unit: 'm' or 'km' for length; area columns will reflect the squared unit

	Returns:
		pandas DataFrame with columns for resolution, number of cells, average edge length,
		and average cell area in the requested units.
	"""
	dggs_type = validate_dggal_type(dggs_type)	
	min_res = int(DGGAL_TYPES[dggs_type]["min_res"])
	max_res = int(DGGAL_TYPES[dggs_type]["max_res"])
	
	# Initialize lists to store data
	resolutions = []
	num_cells_list = []
	avg_edge_lens = []
	avg_cell_areas = []
	cls_list = []
	for res in range(min_res, max_res + 1):
		num_cells, avg_edge_len, avg_cell_area, cls = dggal_metrics(dggs_type, res, unit=unit)       # length unit is km, area unit is km2
		resolutions.append(res)
		num_cells_list.append(num_cells)
		avg_edge_lens.append(avg_edge_len)
		avg_cell_areas.append(avg_cell_area)
		cls_list.append(cls)
	# Build column labels with unit awareness
	avg_edge_len_col = f"avg_edge_len_{unit}"
	unit_area_label = {"m": "m2", "km": "km2"}[unit]
	avg_cell_area_col = f"avg_cell_area_{unit_area_label}"
	cls_label = f"cls_{unit}"
	df = pd.DataFrame({
		"resolution": resolutions,
		"number_of_cells": num_cells_list,
		avg_edge_len_col: avg_edge_lens,
		avg_cell_area_col: avg_cell_areas,
		cls_label: cls_list
	})
	
	return df

def dggalstats_cli():
	"""
	Command-line interface for generating DGGAL DGGS statistics.

	CLI options:
	  -dggs, --dggs_type {gnosis, isea3h, isea9r, ivea3h, ivea9r, rtea3h, rtea9r, rhealpix}
	  -unit, --unit {m,km}
	  --minres, --maxres
	"""
	parser = argparse.ArgumentParser(add_help=False)
	parser.add_argument("-dggs", "--dggs_type", dest="dggs_type", choices=DGGAL_TYPES.keys())
	parser.add_argument("-unit", "--unit", dest="unit", choices=["m", "km"], default="km")
	args = parser.parse_args()

	dggs_type = args.dggs_type
	unit = args.unit

	result = dggalstats(dggs_type, unit)
	if result is not None:
		print(result)

def dggalinspect(dggs_type: str, res: int, crs: str | None = None) -> gpd.GeoDataFrame:
	"""
	Generate detailed inspection data for a DGGAL DGGS type at a given resolution.

	Columns:
	  - ZoneID (as provided by DGGAL output; no renaming is performed)
	  - resolution
	  - geometry
	  - cell_area (m^2)
	  - cell_perimeter (m)
	  - crossed (bool)
	  - norm_area (area/mean_area)
	  - ipq (4πA/P²)
	  - zsc (sqrt(4πA - A²/R²)/P), with R=WGS84 a
	"""
	dggal_gdf = dggalgrid(dggs_type, res, output_format="gpd", crs=crs)	

	# Determine whether current CRS is geographic; compute metrics accordingly
	if dggal_gdf.crs.is_geographic:
		dggal_gdf["cell_area"] = dggal_gdf.geometry.apply(lambda g: abs(geod.geometry_area_perimeter(g)[0]))
		dggal_gdf["cell_perimeter"] = dggal_gdf.geometry.apply(lambda g: abs(geod.geometry_area_perimeter(g)[1]))
		dggal_gdf["crossed"] = dggal_gdf.geometry.apply(check_crossing_geom)
	else:
		dggal_gdf["cell_area"] = dggal_gdf.geometry.area
		dggal_gdf["cell_perimeter"] = dggal_gdf.geometry.length
		dggal_gdf["crossed"] = False
	

	mean_area = dggal_gdf["cell_area"].mean()
	dggal_gdf["norm_area"] = dggal_gdf["cell_area"] / mean_area if mean_area and mean_area != 0 else np.nan
	# Robust formulas avoiding division by zero
	dggal_gdf['ipq'] = 4 * np.pi * dggal_gdf['cell_area'] / (dggal_gdf['cell_perimeter'] ** 2)	
	dggal_gdf['zsc'] = np.sqrt(4*np.pi*dggal_gdf['cell_area'] - np.power(dggal_gdf['cell_area'],2)/np.power(6378137,2))/dggal_gdf['cell_perimeter']
	return dggal_gdf

def dggal_norm_area(gdf, dggs_type="DGGAL", crs='proj=moll'):
    fig, ax = plt.subplots(figsize=(10,5))
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("bottom", size="5%", pad=0.1)
    vmin, vmax, vcenter = gdf['norm_area'].min(), gdf['norm_area'].max(), 1
    norm = TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
    gdf = gdf[~gdf['crossed']] # remove cells that cross the dateline
    gdf.to_crs(crs).plot(column='norm_area', ax=ax, norm=norm, legend=True,cax=cax, cmap='RdYlBu_r', legend_kwds={'label': "cell area/mean cell area",'orientation': "horizontal"})
    world_countries = gpd.read_file('https://raw.githubusercontent.com/opengeoshub/vopendata/refs/heads/main/shape/world_countries.geojson')
    world_countries.boundary.to_crs(crs).plot(color=None, edgecolor='black',linewidth = 0.2,ax=ax)
    ax.axis('off')
    cb_ax = fig.axes[1] 
    cb_ax.tick_params(labelsize=14)
    cb_ax.set_xlabel(xlabel= f"{dggs_type.upper()} Normalized Area",fontsize=14)
    ax.margins(0)
    ax.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)
    plt.tight_layout()


def dggal_compactness(gdf: gpd.GeoDataFrame, dggs_type: str = "DGGAL", crs: str | None = 'proj=moll'):
	"""
	Plot IPQ compactness map for DGGAL cells (generic visualization).
	"""
	fig, ax = plt.subplots(figsize=(10, 5))
	divider = make_axes_locatable(ax)
	cax = divider.append_axes("bottom", size="5%", pad=0.1)
	
	vmin, vmax, vcenter = VMIN_QUAD, VMAX_QUAD, VCENTER_QUAD
	
	dggs_type_norm = str(dggs_type).strip().lower()
	if dggs_type_norm in ["isea3h", "ivea3h", "rtea3h"]:
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


def dggal_norm_area_hist(gdf, dggs_type="DGGAL"):
	"""
	Plot histogram of normalized area for DGGAL cells.
	
	This function creates a histogram visualization showing the distribution
	of normalized areas for DGGAL cells, helping to understand area variations
	and identify patterns in area distortion.
	
	Args:
		gdf: GeoDataFrame from dggalinspect function
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


def dggal_compactness_hist(gdf, dggs_type="DGGAL"):
	"""
	Plot histogram of IPQ compactness for DGGAL cells.
	
	This function creates a histogram visualization showing the distribution
	of Isoperimetric Quotient (IPQ) compactness values for DGGAL cells, helping
	to understand how close cells are to being regular shapes.
	
	Args:
		gdf: GeoDataFrame from dggalinspect function
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
	if dggs_type_norm in ["isea3h", "ivea3h", "rtea3h"]:
		# Hexagonal cells
		norm = TwoSlopeNorm(vmin=VMIN_HEX, vcenter=VCENTER_HEX, vmax=VMAX_HEX)
		ideal_ipq = 0.907  # Ideal hexagon
		shape_name = "Hexagon"
	else:
		# Quadrilateral cells (gnosis, isea9r, ivea9r, rtea9r, rhealpix)
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


def dggalinspect_cli():
	"""
	Command-line interface for DGGAL cell inspection.

	CLI options:
	  -t, --dggs_type
	  -r, --resolution
	"""
	parser = argparse.ArgumentParser(add_help=False)
	parser.add_argument('-t', '--dggs_type', dest='dggs_type', choices=DGGAL_TYPES.keys(), required=True)
	parser.add_argument('-r', '--resolution', dest='resolution', type=int, default=None)
	parser.add_argument('-crs', dest='crs', type=str, default=None, help="CRS to pass to dgg CLI; omit for WGS84")
	args, _ = parser.parse_known_args()
	res = args.resolution if args.resolution is not None else 0
	print(dggalinspect(args.dggs_type, res, crs=args.crs))


if __name__ == "__main__":
	dggalstats_cli()


