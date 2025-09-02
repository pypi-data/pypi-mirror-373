"""
This module provides functions for generating statistics for GEOREF DGGS cells.
"""
import math
import pandas as pd
import numpy as np
import argparse
import geopandas as gpd
from vgrid.utils.constants import GEOREF_RESOLUTION_DEGREES, AUTHALIC_AREA, DGGS_TYPES, VMIN_QUAD, VMAX_QUAD, VCENTER_QUAD
from vgrid.generator.georefgrid import georefgrid
from vgrid.utils.geometry import check_crossing_geom, characteristic_length_scale
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colors import TwoSlopeNorm
min_res = DGGS_TYPES["georef"]["min_res"]
max_res = DGGS_TYPES["georef"]["max_res"]

def georef_metrics(res: int, unit: str = "km"):
    """
    Calculate metrics for GEOREF DGGS cells.
    
    Args:
        res: Resolution level (0-7)
        unit: 'm' or 'km' for length; area will be 'm^2' or 'km^2'
    
    Returns:
        tuple: (num_cells, avg_edge_len_in_unit, avg_cell_area_in_unit_squared)
    """
    # normalize and validate unit
    unit = unit.strip().lower()
    if unit not in {"m", "km"}:
        raise ValueError("unit must be one of {'m','km'}")  

    # Compute grid size in degrees per your formula
    grid_size_deg = GEOREF_RESOLUTION_DEGREES.get(res)

    # Number of cells across longitude and latitude
    num_lon = int(round(360.0 / grid_size_deg))
    num_lat = int(round(180.0 / grid_size_deg))
    num_cells = num_lon * num_lat

    # Calculate area in km² first
    avg_cell_area = AUTHALIC_AREA / num_cells
    avg_edge_len = math.sqrt(avg_cell_area)
    cls = characteristic_length_scale(avg_cell_area, unit=unit)
    # Convert to requested unit
    if unit == "m":
        avg_cell_area = avg_cell_area * (10**6)  # Convert km² to m²
        avg_edge_len = avg_edge_len * 1000  # Convert km to m

    return num_cells, avg_edge_len, avg_cell_area, cls


def georefstats(unit: str = "km"):
    """
    Generate statistics for GEOREF DGGS cells.
    
    Args:
        unit: 'm' or 'km' for length; area will be 'm^2' or 'km^2'
    
    Returns:
        pandas.DataFrame: DataFrame containing GEOREF DGGS statistics with columns:
            - resolution: Resolution level (0-7)
            - number_of_cells: Number of cells at each resolution
            - avg_edge_len_{unit}: Average edge length in the given unit
            - avg_cell_area_{unit}2: Average cell area in the squared unit
    """
    # normalize and validate unit
    unit = unit.strip().lower()
    if unit not in {"m", "km"}:
        raise ValueError("unit must be one of {'m','km'}")
    
   # Initialize lists to store data
    resolutions = []
    num_cells_list = []
    avg_edge_lens = []
    avg_cell_areas = []
    cls_list = []
    for res in range(min_res, max_res + 1):
        num_cells, avg_edge_len, avg_cell_area, cls = georef_metrics(res, unit=unit)
        resolutions.append(res)
        num_cells_list.append(num_cells)
        avg_edge_lens.append(avg_edge_len)
        avg_cell_areas.append(avg_cell_area)
        cls_list.append(cls)
    # Create DataFrame
    # Build column labels with unit awareness (lower case)
    length_col = f"avg_edge_len_{unit}"
    unit_area_label = {"m": "m2", "km": "km2"}[unit]
    area_col = f"avg_cell_area_{unit_area_label}"
    cls_label = f"cls_{unit}"
    df = pd.DataFrame({
        'resolution': resolutions,
        'number_of_cells': num_cells_list,
        length_col: avg_edge_lens,
        area_col: avg_cell_areas,
        cls_label: cls_list
    })
    
    return df


def georefstats_cli(unit: str = "km"):
    """
    Command-line interface for generating GEOREF DGGS statistics.

    CLI options:
      -unit, --unit {m,km}
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-unit', '--unit', dest='unit', choices=['m', 'km'], default="km")              
    args, _ = parser.parse_known_args()

    unit = args.unit if args.unit is not None else unit

    # Get the DataFrame
    df = georefstats(unit=unit)
    
    # Display the DataFrame
    print(df)    


def georefinspect(res):
    """
    Generate comprehensive inspection data for GEOREF DGGS cells at a given resolution.
    
    This function creates a detailed analysis of GEOREF cells including area variations,
    compactness measures, and dateline crossing detection.
    
    Args:
        res: GEOREF resolution level (0-10)
    
    Returns:
        geopandas.GeoDataFrame: DataFrame containing GEOREF cell inspection data with columns:
            - georef: GEOREF cell ID
            - resolution: Resolution level
            - geometry: Cell geometry
            - cell_area: Cell area in square meters
            - cell_perimeter: Cell perimeter in meters
            - crossed: Whether cell crosses the dateline
            - norm_area: Normalized area (cell_area / mean_area)
            - ipq: Isoperimetric Quotient compactness
            - zsc: Zonal Standardized Compactness
    """
    georef_gpd = georefgrid(res, output_format="gpd")
    georef_gpd['crossed'] = georef_gpd['geometry'].apply(check_crossing_geom)
    mean_area = georef_gpd['cell_area'].mean()
    # Calculate normalized area
    georef_gpd['norm_area'] = georef_gpd['cell_area'] / mean_area  
    # Calculate IPQ compactness using the standard formula: CI = 4πA/P²
    georef_gpd['ipq'] = 4 * np.pi * georef_gpd['cell_area'] / (georef_gpd['cell_perimeter'] ** 2)    
    # Calculate zonal standardized compactness
    georef_gpd['zsc'] = np.sqrt(4*np.pi*georef_gpd['cell_area'] - np.power(georef_gpd['cell_area'],2)/np.power(6378137,2))/georef_gpd['cell_perimeter']
    return georef_gpd

def georef_norm_area(georef_gpd):
    """
    Plot normalized area map for GEOREF cells.
    
    This function creates a visualization showing how GEOREF cell areas vary relative
    to the mean area across the globe, highlighting areas of distortion.
    
    Args:
        georef_gpd: GeoDataFrame from georefinspect function
    """
    fig, ax = plt.subplots(figsize=(10,5))
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("bottom", size="5%", pad=0.1)
    vmin, vmax, vcenter = georef_gpd['norm_area'].min(), georef_gpd['norm_area'].max(), 1
    norm = TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
    georef_gpd = georef_gpd[~georef_gpd['crossed']] # remove cells that cross the dateline
    georef_gpd.to_crs('proj=moll').plot(column='norm_area', ax=ax, norm=norm, legend=True,cax=cax, cmap='RdYlBu_r', legend_kwds={'label': "cell area/mean cell area",'orientation': "horizontal"})
    world_countries = gpd.read_file('https://raw.githubusercontent.com/opengeoshub/vopendata/refs/heads/main/shape/world_countries.geojson')
    world_countries.boundary.to_crs('proj=moll').plot(color=None, edgecolor='black',linewidth = 0.2,ax=ax)
    ax.axis('off')
    cb_ax = fig.axes[1] 
    cb_ax.tick_params(labelsize=14)
    cb_ax.set_xlabel(xlabel= "GEOREF Normalized Area",fontsize=14)
    ax.margins(0)
    ax.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)
    plt.tight_layout()

def georef_compactness(georef_gpd):
    """
    Plot IPQ compactness map for GEOREF cells.
    
    This function creates a visualization showing the Isoperimetric Quotient (IPQ)
    compactness of GEOREF cells across the globe. IPQ measures how close each cell
    is to being circular, with values closer to 0.785 indicating more regular squares.
    
    Args:
        georef_gpd: GeoDataFrame from georefinspect function
    """
    fig, ax = plt.subplots(figsize=(10,5))
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("bottom", size="5%", pad=0.1)
    # vmin, vmax, vcenter = georef_gpd['ipq'].min(), georef_gpd['ipq'].max(), np.mean([georef_gpd['ipq'].min(), georef_gpd['ipq'].max()])
    norm = TwoSlopeNorm(vmin=VMIN_QUAD, vcenter=VCENTER_QUAD, vmax=VMAX_QUAD)
    georef_gpd = georef_gpd[~georef_gpd['crossed']] # remove cells that cross the dateline
    georef_gpd.to_crs('proj=moll').plot(column='ipq', ax=ax, norm=norm, legend=True,cax=cax, cmap='viridis', legend_kwds={'orientation': "horizontal" }) 
    world_countries = gpd.read_file('https://raw.githubusercontent.com/opengeoshub/vopendata/refs/heads/main/shape/world_countries.geojson')
    world_countries.boundary.to_crs('proj=moll').plot(color=None, edgecolor='black',linewidth = 0.2,ax=ax)
    ax.axis('off')
    cb_ax = fig.axes[1] 
    cb_ax.tick_params(labelsize=14)
    cb_ax.set_xlabel(xlabel= "GEOREF IPQ Compactness",fontsize=14)
    ax.margins(0)
    ax.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)
    plt.tight_layout()

def georef_norm_area_hist(georef_gpd):
    """
    Plot histogram of normalized area for GEOREF cells.
    
    This function creates a histogram visualization showing the distribution
    of normalized areas for GEOREF cells, helping to understand area variations
    and identify patterns in area distortion.
    
    Args:
        georef_gpd: GeoDataFrame from georefinspect function
    """
    # Filter out cells that cross the dateline
    georef_gpd_filtered = georef_gpd[~georef_gpd['crossed']]
    
    # Create the histogram with color ramp
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Get histogram data
    counts, bins, patches = ax.hist(georef_gpd_filtered['norm_area'], bins=50, alpha=0.7, edgecolor='black')
    
    # Create color ramp using the same normalization as the map function
    vmin, vmax, vcenter = georef_gpd_filtered['norm_area'].min(), georef_gpd_filtered['norm_area'].max(), 1
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
    stats_text = f'Mean: {georef_gpd_filtered["norm_area"].mean():.3f}\nStd: {georef_gpd_filtered["norm_area"].std():.3f}\nMin: {georef_gpd_filtered["norm_area"].min():.3f}\nMax: {georef_gpd_filtered["norm_area"].max():.3f}'
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=12, verticalalignment='top', 
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Customize the plot
    ax.set_xlabel('GEOREF normalized area', fontsize=14)
    ax.set_ylabel('Number of cells', fontsize=14)
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()

def georef_compactness_hist(georef_gpd):
    """
    Plot histogram of IPQ compactness for GEOREF cells.
    
    This function creates a histogram visualization showing the distribution
    of Isoperimetric Quotient (IPQ) compactness values for GEOREF cells, helping
    to understand how close cells are to being regular squares.
    
    Args:
        georef_gpd: GeoDataFrame from georefinspect function
    """
    # Filter out cells that cross the dateline
    georef_gpd_filtered = georef_gpd[~georef_gpd['crossed']]
    
    # Create the histogram with color ramp
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Get histogram data
    counts, bins, patches = ax.hist(georef_gpd_filtered['ipq'], bins=50, alpha=0.7, edgecolor='black')
    
    # Create color ramp using the same normalization as the map function
    norm = TwoSlopeNorm(vmin=VMIN_QUAD, vcenter=VCENTER_QUAD, vmax=VMAX_QUAD)
    
    # Apply colors to histogram bars using the same color mapping as the map
    for i, patch in enumerate(patches):
        # Use the center of each bin for color mapping
        bin_center = (bins[i] + bins[i+1]) / 2
        color = plt.cm.viridis(norm(bin_center))
        patch.set_facecolor(color)
    
    # Add reference line at ideal square IPQ value (0.785)
    ax.axvline(x=0.785, color='red', linestyle='--', linewidth=2, label='Ideal Square (IPQ = 0.785)')
    
    # Add statistics text box
    stats_text = f'Mean: {georef_gpd_filtered["ipq"].mean():.3f}\nStd: {georef_gpd_filtered["ipq"].std():.3f}\nMin: {georef_gpd_filtered["ipq"].min():.3f}\nMax: {georef_gpd_filtered["ipq"].max():.3f}'
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=12, verticalalignment='top', 
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Customize the plot
    ax.set_xlabel('GEOREF IPQ Compactness', fontsize=14)
    ax.set_ylabel('Number of cells', fontsize=14)
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()

def georefinspect_cli():
    """
    Command-line interface for GEOREF cell inspection.
    
    CLI options:
      -r, --resolution: GEOREF resolution level (0-10)
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-r', '--resolution', dest='resolution', type=int, default=None)
    args, _ = parser.parse_known_args()
    res = args.resolution if args.resolution is not None else 2
    print(georefinspect(res))


if __name__ == "__main__":
    georefstats_cli()
