import warnings
import geopandas as gpd
import pandas as pd
import json
import os
import zipfile
import tarfile
import requests
from urllib.parse import urlparse
from vgrid.utils.constants import DGGS_TYPES, DGGAL_TYPES, DGGRID_TYPES
from dggrid4py import DGGRIDv7, tool

# Suppress pyogrio RuntimeWarnings
warnings.filterwarnings("ignore", message="driver ESRI Shapefile does not support open option DRIVER", category=RuntimeWarning)
warnings.filterwarnings("ignore", message="Several features with id = .* have been found. Altering it to be unique. This warning will not be emitted anymore for this layer", category=RuntimeWarning)

def process_input_data_compact(input_data, id_field=None, crs="EPSG:4326"):
    """
    Convert various inputs into a GeoDataFrame with 'id_field' and None geometry.
    Supports:
    - List of Cell IDs
    - GeoJSON dictionary (FeatureCollection with id_field in properties)
    - Local or remote files (GeoJSON, Shapefile, GPKG, etc.) using gpd.read_file
    - CSV and Parquet files (local or remote) with id_field column
    """
    if id_field is None:
        id_field = f"cellid"

    # 1. GeoDataFrame or DataFrame
    if isinstance(input_data, gpd.GeoDataFrame) or isinstance(input_data, pd.DataFrame):
        if id_field not in input_data.columns:
            raise ValueError(f"Missing '{id_field}' in GeoDataFrame")
        df = input_data[[id_field]].copy()
        df["geometry"] = None
        return gpd.GeoDataFrame(df, geometry="geometry", crs=crs)

    # 2. GeoJSON dictionary
    if isinstance(input_data, dict) and "features" in input_data:
        ids = []
        for feature in input_data["features"]:
            props = feature.get("properties", {})
            if id_field not in props:
                raise ValueError(f"Feature missing '{id_field}' in properties")
            ids.append(props[id_field])
        df = pd.DataFrame({id_field: ids})
        df["geometry"] = None
        return gpd.GeoDataFrame(df, geometry="geometry", crs=crs)

    # 3. List of IDs
    if isinstance(input_data, list):
        df = pd.DataFrame({id_field: [str(i) for i in input_data]})
        df["geometry"] = None
        return gpd.GeoDataFrame(df, geometry="geometry", crs=crs)

    # 4. File path or URL
    if isinstance(input_data, str):
        try:
            if input_data.endswith(".csv"):
                df = pd.read_csv(input_data)
            elif input_data.endswith(".parquet"):
                df = pd.read_parquet(input_data)
            else:
                df = gpd.read_file(input_data)
            if id_field not in df.columns:
                raise ValueError(f"Missing '{id_field}' in file/URL: {input_data}")
            df = df[[id_field]].copy()
            df["geometry"] = None
            return gpd.GeoDataFrame(df, geometry="geometry", crs=crs)
        except Exception as e:
            raise ValueError(f"Failed to read from '{input_data}': {e}")
    raise ValueError("Unsupported input type")


def process_input_data_bin(data, lat_col="lat", lon_col="lon", delimiter=None, **kwargs):
    if isinstance(data, gpd.GeoDataFrame):
        return data
    elif isinstance(data, pd.DataFrame):
        if "geometry" in data.columns:
            return gpd.GeoDataFrame(data, geometry="geometry", crs="EPSG:4326")
        elif lat_col in data.columns and lon_col in data.columns:
            gdf = gpd.GeoDataFrame(
                data.copy(),
                geometry=gpd.points_from_xy(data[lon_col], data[lat_col]),
                crs="EPSG:4326",
            )
            return gdf
        else:
            raise ValueError(f"DataFrame must have either a 'geometry' column or '{lat_col}' and '{lon_col}' columns.")
    elif isinstance(data, list):
        gdf = gpd.GeoDataFrame.from_features(data)
        gdf.set_crs(epsg=4326, inplace=True)
        return gdf
    elif isinstance(data, dict) and "type" in data:
        if data["type"] == "FeatureCollection":
            gdf = gpd.GeoDataFrame.from_features(data["features"])
            gdf.set_crs(epsg=4326, inplace=True)
            return gdf
        elif data["type"] == "Feature":
            gdf = gpd.GeoDataFrame.from_features([data])
            gdf.set_crs(epsg=4326, inplace=True)
            return gdf
        else:
            raise ValueError(f"Unsupported GeoJSON type: {data['type']}")
    elif isinstance(data, str):
        ext = os.path.splitext(data)[1].lower()
        if ext in [".csv", ".txt", ".tsv"]:
            if delimiter is None:
                if ext == ".tsv":
                    delimiter = "\t"
                else:
                    delimiter = ","
            df = pd.read_csv(data, delimiter=delimiter, **kwargs)
            if lat_col in df.columns and lon_col in df.columns:
                gdf = gpd.GeoDataFrame(
                    df.copy(),
                    geometry=gpd.points_from_xy(df[lon_col], df[lat_col]),
                    crs="EPSG:4326",
                )
                return gdf
            else:
                raise ValueError(f"Tabular file must have columns '{lat_col}' and '{lon_col}'")
        else:
            gdf = gpd.read_file(data, **kwargs)
            return process_input_data_bin(gdf, lat_col=lat_col, lon_col=lon_col)
    else:
        raise ValueError(f"Unsupported input type: {type(data)}")


def process_input_data_vector(input_data, crs="EPSG:4326", **kwargs):
    """
    Convert various vector inputs into a GeoDataFrame with geometry column preserved.
    Supports:
    - GeoDataFrame (returns as is)
    - DataFrame with geometry column
    - GeoJSON dictionary (FeatureCollection)
    - File path or URL (GeoJSON, Shapefile, GPKG, etc.) using gpd.read_file
    - List of GeoJSON features
    """
    # 1. GeoDataFrame
    if isinstance(input_data, gpd.GeoDataFrame):
        if input_data.crs is None:
            input_data = input_data.set_crs(crs)
        elif input_data.crs != crs:
            # Reproject to target CRS if different
            input_data = input_data.to_crs(crs)
        return input_data
    # 2. DataFrame with geometry column
    if isinstance(input_data, pd.DataFrame):
        if "geometry" in input_data.columns:
            gdf = gpd.GeoDataFrame(input_data, geometry="geometry", crs=crs)
            if gdf.crs is None:
                gdf = gdf.set_crs(crs)
            return gdf
        else:
            raise ValueError("DataFrame must have a 'geometry' column.")
    # 3. GeoJSON dictionary
    if isinstance(input_data, dict) and "features" in input_data:
        gdf = gpd.GeoDataFrame.from_features(input_data["features"])
        if gdf.crs is None:
            gdf = gdf.set_crs(crs)
        elif gdf.crs != crs:
            # Reproject to target CRS if different
            gdf = gdf.to_crs(crs)
        return gdf
    # 4. List of GeoJSON features
    if isinstance(input_data, list) and len(input_data) > 0 and isinstance(input_data[0], dict):
        gdf = gpd.GeoDataFrame.from_features(input_data)
        if gdf.crs is None:
            gdf = gdf.set_crs(crs)
        elif gdf.crs != crs:
            # Reproject to target CRS if different
            gdf = gdf.to_crs(crs)
        return gdf
    # 5. File path or URL
    if isinstance(input_data, str):
        gdf = gpd.read_file(input_data, **kwargs)
        if gdf.crs is None:
            gdf = gdf.set_crs(crs)
        elif gdf.crs != crs:
            # Reproject to target CRS if different
            gdf = gdf.to_crs(crs)
        return gdf
    raise ValueError(f"Unsupported input type for vector data: {type(input_data)}")


def convert_to_output_format(gdf, output_format=None, output_name=None):
    """
    Utility to output a GeoDataFrame in various formats.
    output_format: None, 'csv','geojson', 'shapefile'/'shp', 'gpd'/'geopandas'/'gdf'/'geodataframe',
                   'geojson_dict'/'json_dict', 'gpkg'/'geopackage', 'geoparquet'/'parquet'
    output_name: base name or full filename; if provided without extension, an appropriate extension is appended.
    """
    if output_format is None:
        return gdf.to_dict(orient="records")
    elif output_format in ["gpd", "geopandas","gdf","geodataframe"]:
        if gdf.crs is None:
            gdf.set_crs("EPSG:4326", inplace=True)
        return gdf
    elif output_format == "csv":
        if output_name:
            # Append extension only if missing
            if not output_name.lower().endswith(".csv"):
                output_name = f"{output_name}.csv"
            output_name = os.path.join(os.getcwd(), output_name)
            gdf.to_csv(output_name, index=False)
            print(f"Output file saved as: {output_name}")
            return output_name
        else:
            return gdf.to_csv(index=False)
    elif output_format in ["geojson_dict", "json_dict"]:
        return gdf.__geo_interface__
    elif output_format in ["geojson", "json"]:
        geojson = gdf.__geo_interface__
        if output_name:
            if not output_name.lower().endswith(".geojson"):
                output_name = f"{output_name}.geojson"
            output_name = os.path.join(os.getcwd(), output_name)
            with open(output_name, "w", encoding="utf-8") as f:
                json.dump(geojson, f, indent=2)
            print(f"Output file saved as: {output_name}")
            return output_name
        else:
            return geojson
    elif output_format in ["shapefile", "shp"]:
        if not output_name:
            output_name = os.path.join(os.getcwd(), "output.shp")
        else:
            if not output_name.lower().endswith(".shp"):
                output_name = f"{output_name}.shp"
            output_name = os.path.join(os.getcwd(), output_name)
        if gdf.crs is None:
            gdf.set_crs("EPSG:4326", inplace=True)
        gdf.to_file(output_name, driver="ESRI Shapefile")
        print(f"Output file saved as: {output_name}")
        return output_name
    elif output_format in ["gpkg", "geopackage"]:
        if not output_name:
            output_name = os.path.join(os.getcwd(), "output.gpkg")
        else:
            if not output_name.lower().endswith(".gpkg"):
                output_name = f"{output_name}.gpkg"
            output_name = os.path.join(os.getcwd(), output_name)
        if gdf.crs is None:
            gdf.set_crs("EPSG:4326", inplace=True)
        gdf.to_file(output_name, driver="GPKG")
        print(f"Output file saved as: {output_name}")
        return output_name
    elif output_format in ["geoparquet", "parquet"]:
        if not output_name:
            output_name = os.path.join(os.getcwd(), "output.parquet")
        else:
            if not output_name.lower().endswith(".parquet"):
                output_name = f"{output_name}.parquet"
            output_name = os.path.join(os.getcwd(), output_name)
        if gdf.crs is None:
            gdf.set_crs("EPSG:4326", inplace=True)
        gdf.to_parquet(output_name)
        print(f"Output file saved as: {output_name}")
        return output_name
    else:
        raise ValueError(f"Unsupported output_format: {output_format}")

def dggal_convert_to_output_format(gdf, output_format=None, crs=None, output_name=None):
    """
    Utility to output a GeoDataFrame in various formats.
    output_format: None, 'csv','geojson', 'shapefile'/'shp', 'gpd'/'geopandas'/'gdf'/'geodataframe',
                   'geojson_dict'/'json_dict', 'gpkg'/'geopackage', 'geoparquet'/'parquet'
    output_name: base name or full filename; if provided without extension, an appropriate extension is appended.
    """
    if crs:
        gdf.set_crs(f"proj={crs}", inplace=True)
    else:
        gdf.set_crs("EPSG:4326", inplace=True)

    if output_format is None:
        return gdf.to_dict(orient="records")

    elif output_format in ["gpd", "geopandas","gdf","geodataframe"]:
        return gdf
    elif output_format == "csv":
        if output_name:
            # Append extension only if missing
            if not output_name.lower().endswith(".csv"):
                output_name = f"{output_name}.csv"
            output_name = os.path.join(os.getcwd(), output_name)
            gdf.to_csv(output_name, index=False)
            print(f"Output file saved as: {output_name}")
            return output_name
        else:
            return gdf.to_csv(index=False)
    elif output_format in ["geojson_dict", "json_dict"]:
        return gdf.__geo_interface__
    elif output_format in ["geojson", "json"]:
        geojson = gdf.__geo_interface__
        if output_name:
            if not output_name.lower().endswith(".geojson"):
                output_name = f"{output_name}.geojson"
            output_name = os.path.join(os.getcwd(), output_name)
            with open(output_name, "w", encoding="utf-8") as f:
                json.dump(geojson, f, indent=2)
            print(f"Output file saved as: {output_name}")
            return output_name
        else:
            return geojson
    elif output_format in ["shapefile", "shp"]:
        if not output_name:
            output_name = os.path.join(os.getcwd(), "output.shp")
        else:
            if not output_name.lower().endswith(".shp"):
                output_name = f"{output_name}.shp"
            output_name = os.path.join(os.getcwd(), output_name)

        gdf.to_file(output_name, driver="ESRI Shapefile")
        print(f"Output file saved as: {output_name}")
        return output_name
    elif output_format in ["gpkg", "geopackage"]:
        if not output_name:
            output_name = os.path.join(os.getcwd(), "output.gpkg")
        else:
            if not output_name.lower().endswith(".gpkg"):
                output_name = f"{output_name}.gpkg"
            output_name = os.path.join(os.getcwd(), output_name)

        gdf.to_file(output_name, driver="GPKG")
        print(f"Output file saved as: {output_name}")
        return output_name
    elif output_format in ["geoparquet", "parquet"]:
        if not output_name:
            output_name = os.path.join(os.getcwd(), "output.parquet")
        else:
            if not output_name.lower().endswith(".parquet"):
                output_name = f"{output_name}.parquet"
            output_name = os.path.join(os.getcwd(), output_name)

        gdf.to_parquet(output_name)
        print(f"Output file saved as: {output_name}")
        return output_name
    else:
        raise ValueError(f"Unsupported output_format: {output_format}")


def convert_numpy_types(obj):
    """Recursively convert NumPy types to native Python types"""
    if isinstance(obj, np.generic):
        return obj.item()  # Convert numpy types like np.uint8 to native Python int
    elif isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(v) for v in obj]
    else:
        return obj


def create_dggrid_instance(executable=None, **kwargs):
    """
    Create a DGGRIDv7 instance with proper configuration.
    
    Args:
        executable: Path to DGGRID executable (optional)
        **kwargs: Additional parameters to override defaults
        
    Returns:
        DGGRIDv7 instance with proper configuration
    """
   
    if executable is None:
        executable = tool.get_portable_executable(".")
    
    dggrid_instance = DGGRIDv7(executable=executable, working_dir='.', capture_logs=True, silent=True, 
                            has_gdal=False, tmp_geo_out_legacy=True, debug=False)
    return dggrid_instance


# =============================
# Resolution Validators
# =============================
def validate_dggs_type(dggs_type: str): 
    dggs_type = dggs_type.strip().lower()   
    available_types = list(DGGS_TYPES.keys())
    if dggs_type not in available_types:
        raise ValueError(f"Invalid DGGS type '{dggs_type}'. Valid types are: {available_types}")
    return dggs_type

def validate_dggs_resolution(dggs_type: str, resolution: int) -> int:
    """
    Validate resolution for a DGGS type using DGGS_TYPES uniform (min, max) bounds.

    Args:
        dggs_type: DGGS name present in DGGS_TYPES
        resolution: integer resolution value

    Returns:
        int: Validated resolution

    Raises:
        ValueError: If DGGS type unknown or resolution out of bounds
        TypeError: If inputs are of incorrect types
    """        
    dggs_type = validate_dggs_type(dggs_type)
    min_res = int(DGGS_TYPES[dggs_type]["min_res"])
    max_res = int(DGGS_TYPES[dggs_type]["max_res"])
    
    if resolution is None or resolution < min_res or resolution > max_res:
        raise ValueError(
            f"Resolution for '{dggs_type}' must be in range [{min_res}..{max_res}], got {resolution}"
        )
    return resolution

def validate_h3_resolution(resolution: int) -> int:
    return validate_dggs_resolution("h3", resolution)

def validate_s2_resolution(resolution: int) -> int:
    return validate_dggs_resolution("s2", resolution)

def validate_a5_resolution(resolution: int) -> int:
    return validate_dggs_resolution("a5", resolution)

def validate_healpix_resolution(resolution: int) -> int:
    return validate_dggs_resolution("healpix", resolution)

def validate_rhealpix_resolution(resolution: int) -> int:
    return validate_dggs_resolution("rhealpix", resolution)

def validate_isea3h_resolution(resolution: int) -> int:
    return validate_dggs_resolution("isea3h", resolution)

def validate_isea4t_resolution(resolution: int) -> int:
    return validate_dggs_resolution("isea4t", resolution)

def validate_qtm_resolution(resolution: int) -> int:
    return validate_dggs_resolution("qtm", resolution)

def validate_ease_resolution(resolution: int) -> int:
    return validate_dggs_resolution("ease", resolution)

def validate_geohash_resolution(resolution: int) -> int:
    return validate_dggs_resolution("geohash", resolution)

def validate_georef_resolution(resolution: int) -> int:
    return validate_dggs_resolution("georef", resolution)

def validate_mgrs_resolution(resolution: int) -> int:
    return validate_dggs_resolution("mgrs", resolution)

def validate_tilecode_resolution(resolution: int) -> int:
    return validate_dggs_resolution("tilecode", resolution)

def validate_quadkey_resolution(resolution: int) -> int:
    return validate_dggs_resolution("quadkey", resolution)

def validate_gars_resolution(resolution: int) -> int:
    return validate_dggs_resolution("gars", resolution)

def validate_maidenhead_resolution(resolution: int) -> int:
    return validate_dggs_resolution("maidenhead", resolution)

def validate_olc_resolution(resolution: int) -> int:
    """
    Validate that OLC resolution is in the valid range [2,4,6,8,10,11,12,13,14,15].
    Args:
        resolution (int): Resolution value to validate
    Returns:
        int: Validated resolution value
    Raises:
        ValueError: If resolution is not in range [2,4,6,8,10,11,12,13,14,15]
        TypeError: If resolution is not an integer
    """
    if not isinstance(resolution, int):
        raise TypeError(
            f"Resolution must be an integer, got {type(resolution).__name__}"
        )
    if resolution not in [2, 4, 6, 8, 10, 11, 12, 13, 14, 15]:
        raise ValueError(
            f"Resolution must be in [2,4,6,8,10,11,12,13,14,15], got {resolution}"
        )
    return resolution


def validate_vgrid_resolution(resolution: int) -> int:
    """
    Validate VGRID resolution is within valid bounds.
    
    Args:
        resolution (int): Resolution value to validate
        
    Returns:
        int: Validated resolution value
        
    Raises:
        ValueError: If resolution is out of bounds [-31, 31]
        TypeError: If resolution is not an integer
    """
    if not isinstance(resolution, int):
        raise TypeError(
            f"Resolution must be an integer, got {type(resolution).__name__}"
        )
    if resolution < -31:  # -MAX_HIERARCHY_LEVEL for VGRID
        raise ValueError(f"Resolution must be >= -31, got {resolution}")
    if resolution > 31:  # MAX_HIERARCHY_LEVEL for VGRID
        raise ValueError(f"Resolution must be <= 31, got {resolution}")
    return resolution


def validate_dggal_type(dggs_type: str): 
    dggs_type = dggs_type.strip().lower()   
    available_types = list(DGGAL_TYPES.keys())
    if dggs_type not in available_types:
        raise ValueError(f"Invalid DGGAL type '{dggs_type}'. Valid types are: {available_types}")
    return dggs_type

def validate_dggal_resolution(dggs_type: str, resolution: int) -> int: 
    dggs_type = validate_dggal_type(dggs_type)
    
    min_res = int(DGGAL_TYPES[dggs_type]["min_res"])    
    max_res = int(DGGAL_TYPES[dggs_type]["max_res"])    
    if resolution is None or resolution < min_res or resolution > max_res:
        raise ValueError(
            f"Resolution for '{dggs_type}' must be in range [{min_res}..{max_res}], got {resolution}"
        )
    return resolution

def validate_dggrid_type(dggrid_type: str): 
    dggrid_type = dggrid_type.strip().upper()   
    available_types = list(DGGRID_TYPES.keys())
    if dggrid_type not in available_types:
        raise ValueError(f"Invalid DGGRID type '{dggrid_type}'. Valid types are: {available_types}")
    return dggrid_type

def validate_dggrid_resolution(dggrid_type: str, resolution: int) -> int: 
    dggrid_type = validate_dggrid_type(dggrid_type)    
    min_res = int(DGGRID_TYPES[dggrid_type]["min_res"])    
    max_res = int(DGGRID_TYPES[dggrid_type]["max_res"])  
    
    if resolution is None or resolution < min_res or resolution > max_res:
        raise ValueError(
            f"Resolution for '{dggrid_type}' must be in range [{min_res}..{max_res}], got {resolution}"
        )
    return resolution

def gars_num_cells(resolution: int) -> int:
    """
    Return the total number of GARS cells at a given resolution.

    Resolution levels:
    1 = 30' × 30' cell
    2 = 15' × 15' quadrant
    3 = 5' × 5' area (keypad)
    4 = 1' × 1' sub-cell (optional extension)
    """
    resolution = validate_gars_resolution(resolution)         
    # Base 30' × 30' cells
    lon_bands = 720
    lat_bands = 360
    base_cells = lon_bands * lat_bands

    # Multipliers for each resolution
    multipliers = {
        1: 1,
        2: 4,
        3: 4 * 9,
        4: 4 * 9 * 25
    }

    return base_cells * multipliers[resolution]

def is_url(path):
    """Check if the given path is a URL."""
    try:
        result = urlparse(path)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def read_geojson_file(geojson_path):
    """Read GeoJSON from either a local file or URL."""
    if is_url(geojson_path):
        try:
            response = requests.get(geojson_path)
            response.raise_for_status()
            return json.loads(response.text)
        except requests.RequestException as e:
            print(
                f"Error: Failed to download GeoJSON from URL {geojson_path}: {str(e)}"
            )
            return None
    else:
        if not os.path.exists(geojson_path):
            print(f"Error: The file {geojson_path} does not exist.")
            return None
        try:
            with open(geojson_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading GeoJSON file: {e}")
            return None

def github_raw_url(url):
    """Get the raw URL for a GitHub file.

    Args:
        url (str): The GitHub URL.
    Returns:
        str: The raw URL.
    """
    if isinstance(url, str) and url.startswith("https://github.com/") and "blob" in url:
        url = url.replace("github.com", "raw.githubusercontent.com").replace(
            "blob/", ""
        )
    return url

def install_package(package):
    """Install a Python package.

    Args:
        package (str | list): The package name or a GitHub URL or a list of package names or GitHub URLs.
    """
    import subprocess

    if isinstance(package, str):
        packages = [package]
    elif isinstance(package, list):
        packages = package

    for package in packages:
        if package.startswith("https"):
            package = f"git+{package}"

        # Execute pip install command and show output in real-time
        command = f"pip install {package}"
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)

        # Print output in real-time
        while True:
            output = process.stdout.readline()
            if output == b"" and process.poll() is not None:
                break
            if output:
                print(output.decode("utf-8").strip())

        # Wait for process to complete
        process.wait()

def extract_archive(archive, outdir=None, **kwargs) -> None:
    """
    Extracts a multipart archive.

    This function uses the patoolib library to extract a multipart archive.
    If the patoolib library is not installed, it attempts to install it.
    If the archive does not end with ".zip", it appends ".zip" to the archive name.
    If the extraction fails (for example, if the files already exist), it skips the extraction.

    Args:
        archive (str): The path to the archive file.
        outdir (str): The directory where the archive should be extracted.
        **kwargs: Arbitrary keyword arguments for the patoolib.extract_archive function.

    Returns:
        None

    Raises:
        Exception: An exception is raised if the extraction fails for reasons other than the files already existing.

    Example:

        files = ["sam_hq_vit_tiny.zip", "sam_hq_vit_tiny.z01", "sam_hq_vit_tiny.z02", "sam_hq_vit_tiny.z03"]
        base_url = "https://github.com/opengeos/datasets/releases/download/models/"
        urls = [base_url + f for f in files]
        vgrid.utils.io.download_files(urls, out_dir="models", multi_part=True)

    """
    try:
        import patoolib
    except ImportError:
        install_package("patool")
        import patoolib

    if not archive.endswith(".zip"):
        archive = archive + ".zip"

    if outdir is None:
        outdir = os.path.dirname(archive)

    try:
        patoolib.extract_archive(archive, outdir=outdir, **kwargs)
    except Exception:
        print("The unzipped files might already exist. Skipping extraction.")
        return

def download_file(
    url=None,
    output=None,
    quiet=False,
    proxy=None,
    speed=None,
    use_cookies=True,
    verify=True,
    id=None,
    fuzzy=False,
    resume=False,
    unzip=True,
    overwrite=False,
    subfolder=False,
):
    """Download a file from URL, including Google Drive shared URL.

    Args:
        url (str, optional): Google Drive URL is also supported. Defaults to None.
        output (str, optional): Output filename. Default is basename of URL.
        quiet (bool, optional): Suppress terminal output. Default is False.
        proxy (str, optional): Proxy. Defaults to None.
        speed (float, optional): Download byte size per second (e.g., 256KB/s = 256 * 1024). Defaults to None.
        use_cookies (bool, optional): Flag to use cookies. Defaults to True.
        verify (bool | str, optional): Either a bool, in which case it controls whether the server's TLS certificate is verified, or a string,
            in which case it must be a path to a CA bundle to use. Default is True.. Defaults to True.
        id (str, optional): Google Drive's file ID. Defaults to None.
        fuzzy (bool, optional): Fuzzy extraction of Google Drive's file Id. Defaults to False.
        resume (bool, optional): Resume the download from existing tmp file if possible. Defaults to False.
        unzip (bool, optional): Unzip the file. Defaults to True.
        overwrite (bool, optional): Overwrite the file if it already exists. Defaults to False.
        subfolder (bool, optional): Create a subfolder with the same name as the file. Defaults to False.

    Returns:
        str: The output file path.
    """
    try:
        import gdown
    except ImportError:
        print(
            "The gdown package is required for this function. Use `pip install gdown` to install it."
        )
        return

    if output is None:
        if isinstance(url, str) and url.startswith("http"):
            output = os.path.basename(url)

    out_dir = os.path.abspath(os.path.dirname(output))
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    if isinstance(url, str):
        if os.path.exists(os.path.abspath(output)) and (not overwrite):
            print(
                f"{output} already exists. Skip downloading. Set overwrite=True to overwrite."
            )
            return os.path.abspath(output)
        else:
            url = github_raw_url(url)

    if "https://drive.google.com/file/d/" in url:
        fuzzy = True

    output = gdown.download(
        url, output, quiet, proxy, speed, use_cookies, verify, id, fuzzy, resume
    )

    if unzip:
        if output.endswith(".zip"):
            with zipfile.ZipFile(output, "r") as zip_ref:
                if not quiet:
                    print("Extracting files...")
                if subfolder:
                    basename = os.path.splitext(os.path.basename(output))[0]

                    output = os.path.join(out_dir, basename)
                    if not os.path.exists(output):
                        os.makedirs(output)
                    zip_ref.extractall(output)
                else:
                    zip_ref.extractall(os.path.dirname(output))
        elif output.endswith(".tar.gz") or output.endswith(".tar"):
            if output.endswith(".tar.gz"):
                mode = "r:gz"
            else:
                mode = "r"

            with tarfile.open(output, mode) as tar_ref:
                if not quiet:
                    print("Extracting files...")
                if subfolder:
                    basename = os.path.splitext(os.path.basename(output))[0]
                    output = os.path.join(out_dir, basename)
                    if not os.path.exists(output):
                        os.makedirs(output)
                    tar_ref.extractall(output)
                else:
                    tar_ref.extractall(os.path.dirname(output))

    return os.path.abspath(output)

def download_files(
    urls,
    out_dir=None,
    filenames=None,
    quiet=False,
    proxy=None,
    speed=None,
    use_cookies=True,
    verify=True,
    id=None,
    fuzzy=False,
    resume=False,
    unzip=True,
    overwrite=False,
    subfolder=False,
    multi_part=False,
):
    """Download files from URLs, including Google Drive shared URL.

    Args:
        urls (list): The list of urls to download. Google Drive URL is also supported.
        out_dir (str, optional): The output directory. Defaults to None.
        filenames (list, optional): Output filename. Default is basename of URL.
        quiet (bool, optional): Suppress terminal output. Default is False.
        proxy (str, optional): Proxy. Defaults to None.
        speed (float, optional): Download byte size per second (e.g., 256KB/s = 256 * 1024). Defaults to None.
        use_cookies (bool, optional): Flag to use cookies. Defaults to True.
        verify (bool | str, optional): Either a bool, in which case it controls whether the server's TLS certificate is verified, or a string, in which case it must be a path to a CA bundle to use. Default is True.. Defaults to True.
        id (str, optional): Google Drive's file ID. Defaults to None.
        fuzzy (bool, optional): Fuzzy extraction of Google Drive's file Id. Defaults to False.
        resume (bool, optional): Resume the download from existing tmp file if possible. Defaults to False.
        unzip (bool, optional): Unzip the file. Defaults to True.
        overwrite (bool, optional): Overwrite the file if it already exists. Defaults to False.
        subfolder (bool, optional): Create a subfolder with the same name as the file. Defaults to False.
        multi_part (bool, optional): If the file is a multi-part file. Defaults to False.

    Examples:

        files = ["sam_hq_vit_tiny.zip", "sam_hq_vit_tiny.z01", "sam_hq_vit_tiny.z02", "sam_hq_vit_tiny.z03"]
        base_url = "https://github.com/opengeos/datasets/releases/download/models/"
        urls = [base_url + f for f in files]
        vgrid.utils.io.download_files(urls, out_dir="models", multi_part=True)
    """

    if out_dir is None:
        out_dir = os.getcwd()

    if filenames is None:
        filenames = [None] * len(urls)

    filepaths = []
    for url, output in zip(urls, filenames):
        if output is None:
            filename = os.path.join(out_dir, os.path.basename(url))
        else:
            filename = os.path.join(out_dir, output)

        filepaths.append(filename)
        if multi_part:
            unzip = False

        download_file(
            url,
            filename,
            quiet,
            proxy,
            speed,
            use_cookies,
            verify,
            id,
            fuzzy,
            resume,
            unzip,
            overwrite,
            subfolder,
        )

    if multi_part:
        archive = os.path.splitext(filename)[0] + ".zip"
        out_dir = os.path.dirname(filename)
        extract_archive(archive, out_dir)

        for file in filepaths:
            os.remove(file)


def download_folder(
    url=None,
    id=None,
    output=None,
    quiet=False,
    proxy=None,
    speed=None,
    use_cookies=True,
    remaining_ok=False,
):
    """Downloads the entire folder from URL.

    Args:
        url (str, optional): URL of the Google Drive folder. Must be of the format 'https://drive.google.com/drive/folders/{url}'. Defaults to None.
        id (str, optional): Google Drive's folder ID. Defaults to None.
        output (str, optional):  String containing the path of the output folder. Defaults to current working directory.
        quiet (bool, optional): Suppress terminal output. Defaults to False.
        proxy (str, optional): Proxy. Defaults to None.
        speed (float, optional): Download byte size per second (e.g., 256KB/s = 256 * 1024). Defaults to None.
        use_cookies (bool, optional): Flag to use cookies. Defaults to True.
        resume (bool, optional): Resume the download from existing tmp file if possible. Defaults to False.

    Returns:
        list: List of files downloaded, or None if failed.
    """

    try:
        import gdown
    except ImportError:
        print(
            "The gdown package is required for this function. Use `pip install gdown` to install it."
        )
        return

    files = gdown.download_folder(
        url, id, output, quiet, proxy, speed, use_cookies, remaining_ok
    )
    return files


