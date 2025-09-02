"""
This module provides functions for generating statistics for Tilecode DGGS cells.
"""
import math
import pandas as pd
import numpy as np
import argparse
import geopandas as gpd
from vgrid.utils.constants import AUTHALIC_AREA, DGGS_TYPES, VMIN_QUAD, VMAX_QUAD, VCENTER_QUAD
from vgrid.generator.tilecodegrid import tilecodegrid
from vgrid.utils.geometry import check_crossing_geom, characteristic_length_scale
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colors import TwoSlopeNorm
min_res = DGGS_TYPES["tilecode"]["min_res"]
max_res = DGGS_TYPES["tilecode"]["max_res"]

def tilecode_metrics(res, unit: str = "km"):            
    """
    Calculate metrics for Tilecode DGGS cells.
    
    Args:
        res: Resolution level (0-30)
        unit: 'm' or 'km' for length; area will be 'm^2' or 'km^2'
    
    Returns:
        tuple: (num_cells, avg_edge_len_in_unit, avg_cell_area_in_unit_squared)
    """
    # normalize and validate unit
    unit = unit.strip().lower()
    if unit not in {"m", "km"}:
        raise ValueError("unit must be one of {'m','km'}")
    
    num_cells = 4 ** res
    
    # Calculate area in km² first
    avg_cell_area = AUTHALIC_AREA / num_cells
    avg_edge_len = math.sqrt(avg_cell_area)
    cls = characteristic_length_scale(avg_cell_area, unit=unit)
    # Convert to requested unit
    if unit == "m":
        avg_cell_area = avg_cell_area * (10**6)  # Convert km² to m²
        avg_edge_len = avg_edge_len * 1000  # Convert km to m
    
    return num_cells, avg_edge_len, avg_cell_area, cls


def tilecodestats(unit: str = "km"):
    """
    Generate statistics for Tilecode DGGS cells.
    
    Args:
        unit: 'm' or 'km' for length; area will be 'm^2' or 'km^2'
    
    Returns:
        pandas.DataFrame: DataFrame containing Tilecode DGGS statistics with columns:
            - resolution: Resolution level (0-30)
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
        num_cells, avg_edge_len, avg_cell_area, cls = tilecode_metrics(res, unit=unit)
        resolutions.append(res)
        num_cells_list.append(num_cells)
        avg_edge_lens.append(avg_edge_len)
        avg_cell_areas.append(avg_cell_area)
        cls_list.append(cls)
    # Create DataFrame
    # Build column labels with unit awareness (lower case)
    avg_edge_len = f"avg_edge_len_{unit}"
    unit_area_label = {"m": "m2", "km": "km2"}[unit]
    avg_cell_area = f"avg_cell_area_{unit_area_label}"
    cls_label = f"cls_{unit}"
    df = pd.DataFrame({
        'resolution': resolutions,
        'number_of_cells': num_cells_list,
        avg_edge_len: avg_edge_lens,
        avg_cell_area: avg_cell_areas,
        cls_label: cls_list
    })
    
    return df


def tilecodestats_cli():
    """
    Command-line interface for generating Tilecode DGGS statistics.

    CLI options:
      -unit, --unit {m,km}
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-unit', '--unit', dest='unit', choices=['m', 'km'], default="km")              
    args, _ = parser.parse_known_args()

    unit = args.unit if args.unit is not None else unit

    # Get the DataFrame
    df = tilecodestats(unit=unit)
    
    # Display the DataFrame
    print(df)

def tilecodeinspect(res):
    """
    Generate comprehensive inspection data for Tilecode DGGS cells at a given resolution.
    
    This function creates a detailed analysis of Tilecode cells including area variations,
    compactness measures, and dateline crossing detection.
    
    Args:
        res: Tilecode resolution level (0-29)
    
    Returns:
        geopandas.GeoDataFrame: DataFrame containing Tilecode cell inspection data with columns:
            - tilecode: Tilecode cell ID
            - resolution: Resolution level
            - geometry: Cell geometry
            - cell_area: Cell area in square meters
            - cell_perimeter: Cell perimeter in meters
            - crossed: Whether cell crosses the dateline
            - norm_area: Normalized area (cell_area / mean_area)
            - ipq: Isoperimetric Quotient compactness
            - zsc: Zonal Standardized Compactness
    """
    tilecode_gpd = tilecodegrid(res, output_format="gpd")
    tilecode_gpd['crossed'] = tilecode_gpd['geometry'].apply(check_crossing_geom)
    mean_area = tilecode_gpd['cell_area'].mean()
    # Calculate normalized area
    tilecode_gpd['norm_area'] = tilecode_gpd['cell_area'] / mean_area  
    # Calculate IPQ compactness using the standard formula: CI = 4πA/P²
    tilecode_gpd['ipq'] = 4 * np.pi * tilecode_gpd['cell_area'] / (tilecode_gpd['cell_perimeter'] ** 2)    
    # Calculate zonal standardized compactness
    tilecode_gpd['zsc'] = np.sqrt(4*np.pi*tilecode_gpd['cell_area'] - np.power(tilecode_gpd['cell_area'],2)/np.power(6378137,2))/tilecode_gpd['cell_perimeter']
    return tilecode_gpd

def tilecode_norm_area(tilecode_gpd):
    """
    Plot normalized area map for Tilecode cells.
    
    This function creates a visualization showing how Tilecode cell areas vary relative
    to the mean area across the globe, highlighting areas of distortion.
    
    Args:
        tilecode_gpd: GeoDataFrame from tilecodeinspect function
    """
    fig, ax = plt.subplots(figsize=(10,5))
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("bottom", size="5%", pad=0.1)
    vmin, vmax, vcenter = tilecode_gpd['norm_area'].min(), tilecode_gpd['norm_area'].max(), 1
    norm = TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
    tilecode_gpd = tilecode_gpd[~tilecode_gpd['crossed']] # remove cells that cross the dateline
    tilecode_gpd.to_crs('proj=moll').plot(column='norm_area', ax=ax, norm=norm, legend=True,cax=cax, cmap='RdYlBu_r', legend_kwds={'label': "cell area/mean cell area",'orientation': "horizontal"})
    world_countries = gpd.read_file('https://raw.githubusercontent.com/opengeoshub/vopendata/refs/heads/main/shape/world_countries.geojson')
    world_countries.boundary.to_crs('proj=moll').plot(color=None, edgecolor='black',linewidth = 0.2,ax=ax)
    ax.axis('off')
    cb_ax = fig.axes[1] 
    cb_ax.tick_params(labelsize=14)
    cb_ax.set_xlabel(xlabel= "Tilecode Normalized Area",fontsize=14)
    ax.margins(0)
    ax.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)
    plt.tight_layout()

def tilecode_compactness(tilecode_gpd):
    """
    Plot IPQ compactness map for Tilecode cells.
    
    This function creates a visualization showing the Isoperimetric Quotient (IPQ)
    compactness of Tilecode cells across the globe. IPQ measures how close each cell
    is to being circular, with values closer to 0.785 indicating more regular squares.
    
    Args:
        tilecode_gpd: GeoDataFrame from tilecodeinspect function
    """
    fig, ax = plt.subplots(figsize=(10,5))
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("bottom", size="5%", pad=0.1)
    # vmin, vmax, vcenter = tilecode_gpd['ipq'].min(), tilecode_gpd['ipq'].max(), np.mean([tilecode_gpd['ipq'].min(), tilecode_gpd['ipq'].max()])
    norm = TwoSlopeNorm(vmin=VMIN_QUAD, vcenter=VCENTER_QUAD, vmax=VMAX_QUAD)
    tilecode_gpd = tilecode_gpd[~tilecode_gpd['crossed']] # remove cells that cross the dateline
    tilecode_gpd.to_crs('proj=moll').plot(column='ipq', ax=ax, norm=norm, legend=True,cax=cax, cmap='viridis', legend_kwds={'orientation': "horizontal" }) 
    world_countries = gpd.read_file('https://raw.githubusercontent.com/opengeoshub/vopendata/refs/heads/main/shape/world_countries.geojson')
    world_countries.boundary.to_crs('proj=moll').plot(color=None, edgecolor='black',linewidth = 0.2,ax=ax)
    ax.axis('off')
    cb_ax = fig.axes[1] 
    cb_ax.tick_params(labelsize=14)
    cb_ax.set_xlabel(xlabel= "Tilecode IPQ Compactness",fontsize=14)
    ax.margins(0)
    ax.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)
    plt.tight_layout()

def tilecode_norm_area_hist(tilecode_gpd):
    """
    Plot histogram of normalized area for Tilecode cells.
    
    This function creates a histogram visualization showing the distribution
    of normalized areas for Tilecode cells, helping to understand area variations
    and identify patterns in area distortion.
    
    Args:
        tilecode_gpd: GeoDataFrame from tilecodeinspect function
    """
    # Filter out cells that cross the dateline
    tilecode_gpd_filtered = tilecode_gpd[~tilecode_gpd['crossed']]
    
    # Create the histogram with color ramp
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Get histogram data
    counts, bins, patches = ax.hist(tilecode_gpd_filtered['norm_area'], bins=50, alpha=0.7, edgecolor='black')
    
    # Create color ramp using the same normalization as the map function
    vmin, vmax, vcenter = tilecode_gpd_filtered['norm_area'].min(), tilecode_gpd_filtered['norm_area'].max(), 1
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
    stats_text = f'Mean: {tilecode_gpd_filtered["norm_area"].mean():.3f}\nStd: {tilecode_gpd_filtered["norm_area"].std():.3f}\nMin: {tilecode_gpd_filtered["norm_area"].min():.3f}\nMax: {tilecode_gpd_filtered["norm_area"].max():.3f}'
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=12, verticalalignment='top', 
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Customize the plot
    ax.set_xlabel('Tilecode normalized area', fontsize=14)
    ax.set_ylabel('Number of cells', fontsize=14)
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()

def tilecode_compactness_hist(tilecode_gpd):
    """
    Plot histogram of IPQ compactness for Tilecode cells.
    
    This function creates a histogram visualization showing the distribution
    of Isoperimetric Quotient (IPQ) compactness values for Tilecode cells, helping
    to understand how close cells are to being regular squares.
    
    Args:
        tilecode_gpd: GeoDataFrame from tilecodeinspect function
    """
    # Filter out cells that cross the dateline
    tilecode_gpd_filtered = tilecode_gpd[~tilecode_gpd['crossed']]
    
    # Create the histogram with color ramp
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Get histogram data
    counts, bins, patches = ax.hist(tilecode_gpd_filtered['ipq'], bins=50, alpha=0.7, edgecolor='black')
    
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
    stats_text = f'Mean: {tilecode_gpd_filtered["ipq"].mean():.3f}\nStd: {tilecode_gpd_filtered["ipq"].std():.3f}\nMin: {tilecode_gpd_filtered["ipq"].min():.3f}\nMax: {tilecode_gpd_filtered["ipq"].max():.3f}'
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=12, verticalalignment='top', 
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Customize the plot
    ax.set_xlabel('Tilecode IPQ Compactness', fontsize=14)
    ax.set_ylabel('Number of cells', fontsize=14)
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()

def tilecodeinspect_cli():
    """
    Command-line interface for Tilecode cell inspection.
    
    CLI options:
      -r, --resolution: Tilecode resolution level (0-30)
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-r', '--resolution', dest='resolution', type=int, default=None)
    args, _ = parser.parse_known_args()
    res = args.resolution if args.resolution is not None else 2
    print(tilecodeinspect(res))

if __name__ == "__main__":
    tilecodestats_cli()
