"""Rasterio-related MCP tool functions and resource listings."""
import os
import logging
from typing import Any, Dict, List, Optional
from .mcp import gis_mcp

# Configure logging
logger = logging.getLogger(__name__)

@gis_mcp.resource("gis://operation/rasterio")
def get_rasterio_operations() -> Dict[str, List[str]]:
    """List available rasterio operations."""
    return {
        "operations": [
            "metadata_raster",
            "get_raster_crs",
            "clip_raster_with_shapefile",
            "resample_raster",
            "reproject_raster",
            "weighted_band_sum",
            "concat_bands",
            "raster_algebra",
            "compute_ndvi",
            "raster_histogram",
            "tile_raster",
            "raster_band_statistics",
            "extract_band",
            "zonal_statistics",
            "reclassify_raster",
            "focal_statistics",
            "hillshade",
            "write_raster"
        ]
    }

@gis_mcp.tool()
def zonal_statistics(raster_path: str, vector_path: str, stats: list = None) -> Dict[str, Any]:
    """
    Calculate statistics of raster values within polygons (zonal statistics).
    Args:
        raster_path: Path to the raster file.
        vector_path: Path to the vector file (polygons).
        stats: List of statistics to compute (e.g., ["mean", "min", "max", "std"]).
    Returns:
        Dictionary with status, message, and statistics per polygon.
    """
    try:
        import rasterio
        import rasterio.mask
        import geopandas as gpd
        import numpy as np
        if stats is None:
            stats = ["mean", "min", "max", "std"]
        gdf = gpd.read_file(vector_path)
        with rasterio.open(raster_path) as src:
            results = []
            for idx, row in gdf.iterrows():
                geom = [row["geometry"]]
                out_image, out_transform = rasterio.mask.mask(src, geom, crop=True, filled=True)
                data = out_image[0]
                data = data[data != src.nodata] if src.nodata is not None else data
                stat_result = {"index": idx}
                if data.size == 0:
                    for s in stats:
                        stat_result[s] = None
                else:
                    if "mean" in stats:
                        stat_result["mean"] = float(np.mean(data))
                    if "min" in stats:
                        stat_result["min"] = float(np.min(data))
                    if "max" in stats:
                        stat_result["max"] = float(np.max(data))
                    if "std" in stats:
                        stat_result["std"] = float(np.std(data))
                results.append(stat_result)
        return {
            "status": "success",
            "message": "Zonal statistics computed successfully.",
            "results": results
        }
    except Exception as e:
        logger.error(f"Error in zonal_statistics: {str(e)}")
        return {"status": "error", "message": str(e)}

@gis_mcp.tool()
def reclassify_raster(raster_path: str, reclass_map: dict, output_path: str) -> Dict[str, Any]:
    """
    Reclassify raster values using a mapping dictionary.
    Args:
        raster_path: Path to the input raster.
        reclass_map: Dictionary mapping old values to new values (e.g., {1: 10, 2: 20}).
        output_path: Path to save the reclassified raster.
    Returns:
        Dictionary with status and message.
    """
    try:
        import rasterio
        import numpy as np
        with rasterio.open(raster_path) as src:
            data = src.read(1)
            profile = src.profile.copy()
            reclass_data = np.copy(data)
            for old, new in reclass_map.items():
                reclass_data[data == old] = new
        with rasterio.open(output_path, "w", **profile) as dst:
            dst.write(reclass_data, 1)
        return {
            "status": "success",
            "message": f"Raster reclassified and saved to '{output_path}'.",
            "output_path": output_path
        }
    except Exception as e:
        logger.error(f"Error in reclassify_raster: {str(e)}")
        return {"status": "error", "message": str(e)}

@gis_mcp.tool()
def focal_statistics(raster_path: str, statistic: str, size: int = 3, output_path: str = None) -> Dict[str, Any]:
    """
    Compute focal (moving window) statistics on a raster.
    Args:
        raster_path: Path to the input raster.
        statistic: Statistic to compute ('mean', 'min', 'max', 'std').
        size: Window size (odd integer).
        output_path: Optional path to save the result.
    Returns:
        Dictionary with status, message, and output path if saved.
    """
    try:
        import rasterio
        import numpy as np
        from scipy.ndimage import generic_filter
        with rasterio.open(raster_path) as src:
            data = src.read(1)
            profile = src.profile.copy()
            func = None
            if statistic == "mean":
                func = np.mean
            elif statistic == "min":
                func = np.min
            elif statistic == "max":
                func = np.max
            elif statistic == "std":
                func = np.std
            else:
                raise ValueError(f"Unsupported statistic: {statistic}")
            filtered = generic_filter(data, func, size=size, mode='nearest')
        if output_path:
            with rasterio.open(output_path, "w", **profile) as dst:
                dst.write(filtered, 1)
        return {
            "status": "success",
            "message": f"Focal {statistic} computed successfully.",
            "output_path": output_path
        }
    except Exception as e:
        logger.error(f"Error in focal_statistics: {str(e)}")
        return {"status": "error", "message": str(e)}

@gis_mcp.tool()
def hillshade(raster_path: str, azimuth: float = 315, angle_altitude: float = 45, output_path: str = None) -> Dict[str, Any]:
    """
    Generate hillshade from a DEM raster.
    Args:
        raster_path: Path to the DEM raster.
        azimuth: Sun azimuth angle in degrees.
        angle_altitude: Sun altitude angle in degrees.
        output_path: Optional path to save the hillshade raster.
    Returns:
        Dictionary with status, message, and output path if saved.
    """
    try:
        import rasterio
        import numpy as np
        with rasterio.open(raster_path) as src:
            elevation = src.read(1).astype('float32')
            profile = src.profile.copy()
            x, y = np.gradient(elevation, src.res[0], src.res[1])
            slope = np.pi/2 - np.arctan(np.sqrt(x*x + y*y))
            aspect = np.arctan2(-x, y)
            az = np.deg2rad(azimuth)
            alt = np.deg2rad(angle_altitude)
            shaded = np.sin(alt) * np.sin(slope) + np.cos(alt) * np.cos(slope) * np.cos(az - aspect)
            hillshade = np.clip(255 * shaded, 0, 255).astype('uint8')
        if output_path:
            profile.update(dtype='uint8', count=1)
            with rasterio.open(output_path, "w", **profile) as dst:
                dst.write(hillshade, 1)
        return {
            "status": "success",
            "message": "Hillshade generated successfully.",
            "output_path": output_path
        }
    except Exception as e:
        logger.error(f"Error in hillshade: {str(e)}")
        return {"status": "error", "message": str(e)}

@gis_mcp.tool()
def write_raster(array: list, reference_raster: str, output_path: str, dtype: str = None) -> Dict[str, Any]:
    """
    Write a numpy array to a raster file using metadata from a reference raster.
    Args:
        array: 2D or 3D list (or numpy array) of raster values.
        reference_raster: Path to a raster whose metadata will be copied.
        output_path: Path to save the new raster.
        dtype: Optional data type (e.g., 'float32', 'uint8').
    Returns:
        Dictionary with status and message.
    """
    try:
        import rasterio
        import numpy as np
        arr = np.array(array)
        with rasterio.open(reference_raster) as src:
            profile = src.profile.copy()
            if dtype:
                profile.update(dtype=dtype)
            if arr.ndim == 2:
                profile.update(count=1)
            elif arr.ndim == 3:
                profile.update(count=arr.shape[0])
            else:
                raise ValueError("Array must be 2D or 3D.")
        with rasterio.open(output_path, "w", **profile) as dst:
            dst.write(arr)
        return {
            "status": "success",
            "message": f"Raster written to '{output_path}' successfully.",
            "output_path": output_path
        }
    except Exception as e:
        logger.error(f"Error in write_raster: {str(e)}")
        return {"status": "error", "message": str(e)}



@gis_mcp.tool()
def metadata_raster(path_or_url: str) -> Dict[str, Any]:
    """
    Open a raster dataset in read-only mode and return metadata.
    
    This tool supports two modes based on the provided string:
    1. A local filesystem path (e.g., "D:\\Data\\my_raster.tif").
    2. An HTTPS URL (e.g., "https://example.com/my_raster.tif").
    
    The input must be a single string that is either a valid file path
    on the local machine or a valid HTTPS URL pointing to a raster.
    """
    try:
        # Import numpy first to ensure NumPy's C-API is initialized
        import numpy as np
        import rasterio

        # Remove any backticks (`) if the client wrapped the path_or_url in them
        cleaned = path_or_url.replace("`", "")

        # Determine if the string is an HTTPS URL or a local file path
        if cleaned.lower().startswith("https://"):
            # For HTTPS URLs, let Rasterio/GDAL handle remote access directly
            dataset = rasterio.open(cleaned)
        else:
            # Treat as local filesystem path
            local_path = os.path.expanduser(cleaned)

            # Verify that the file exists on disk
            if not os.path.isfile(local_path):
                raise FileNotFoundError(f"Raster file not found at '{local_path}'.")

            # Open the local file in read-only mode
            dataset = rasterio.open(local_path)

        # Build a mapping from band index to its data type (dtype)
        band_dtypes = {i: dtype for i, dtype in zip(dataset.indexes, dataset.dtypes)}

        # Collect core metadata fields in simple Python types
        meta: Dict[str, Any] = {
            "name": dataset.name,                                       # Full URI or filesystem path
            "mode": dataset.mode,                                       # Mode should be 'r' for read                                 
            "driver": dataset.driver,                                   # GDAL driver, e.g. "GTiff"
            "width": dataset.width,                                     # Number of columns
            "height": dataset.height,                                   # Number of rows
            "count": dataset.count,                                     # Number of bands
            "bounds": dataset.bounds,                                   # Show bounding box
            "band_dtypes": band_dtypes,                                 # { band_index: dtype_string }
            "no_data": dataset.nodatavals,                              # Number of NoData values in each band
            "crs": dataset.crs.to_string() if dataset.crs else None,    # CRS as EPSG string or None
            "transform": list(dataset.transform),                       # Affine transform coefficients (6 floats)
        }

        # Return a success status along with metadata
        return {
            "status": "success",
            "metadata": meta,
            "message": f"Raster dataset opened successfully from '{cleaned}'."
        }

    except Exception as e:
        # Log the error for debugging purposes, then raise ValueError so MCP can relay it
        logger.error(f"Error opening raster '{path_or_url}': {str(e)}")
        raise ValueError(f"Failed to open raster '{path_or_url}': {str(e)}")

@gis_mcp.tool()
def get_raster_crs(path_or_url: str) -> Dict[str, Any]:
    """
    Retrieve the Coordinate Reference System (CRS) of a raster dataset.
    
    Opens the raster (local path or HTTPS URL), reads its DatasetReader.crs
    attribute as a PROJ.4-style dict, and also returns the WKT representation.
    """
    try:
        import numpy as np
        import rasterio

        # Strip backticks if the client wrapped the input in them
        cleaned = path_or_url.replace("`", "")

        # Open remote or local dataset
        if cleaned.lower().startswith("https://"):
            src = rasterio.open(cleaned)
        else:
            local_path = os.path.expanduser(cleaned)
            if not os.path.isfile(local_path):
                raise FileNotFoundError(f"Raster file not found at '{local_path}'.")
            src = rasterio.open(local_path)

        # Access the CRS object on the opened dataset
        crs_obj = src.crs
        src.close()

        if crs_obj is None:
            raise ValueError("No CRS defined for this dataset.")

        # Convert CRS to PROJ.4‐style dict and WKT string
        proj4_dict = crs_obj.to_dict()    # e.g., {'init': 'epsg:32618'}
        wkt_str    = crs_obj.to_wkt()     # full WKT representation

        return {
            "status":      "success",
            "proj4":       proj4_dict,
            "wkt":         wkt_str,
            "message":     "CRS retrieved successfully"
        }

    except Exception as e:
        # Log and re-raise as ValueError for MCP error propagation
        logger.error(f"Error retrieving CRS for '{path_or_url}': {e}")
        raise ValueError(f"Failed to retrieve CRS: {e}")

@gis_mcp.tool()
def clip_raster_with_shapefile(
    raster_path_or_url: str,
    shapefile_path: str,
    destination: str
) -> Dict[str, Any]:
    """
    Clip a raster dataset using polygons from a shapefile and write the result.
    Converts the shapefile's CRS to match the raster's CRS if they are different.
    
    Parameters:
    - raster_path_or_url: local path or HTTPS URL of the source raster.
    - shapefile_path:     local filesystem path to a .shp file containing polygons.
    - destination:        local path where the masked raster will be written.
    """
    try:
        import numpy as np
        import rasterio
        import rasterio.mask
        from rasterio.warp import transform_geom
        import pyproj
        import fiona

        # Clean paths
        raster_clean = raster_path_or_url.replace("`", "")
        shp_clean = shapefile_path.replace("`", "")
        dst_clean = destination.replace("`", "")

        # Verify shapefile exists
        shp_path = os.path.expanduser(shp_clean)
        if not os.path.isfile(shp_path):
            raise FileNotFoundError(f"Shapefile not found at '{shp_path}'.")

        # Open the raster
        if raster_clean.lower().startswith("https://"):
            src = rasterio.open(raster_clean)
        else:
            src_path = os.path.expanduser(raster_clean)
            if not os.path.isfile(src_path):
                raise FileNotFoundError(f"Raster not found at '{src_path}'.")
            src = rasterio.open(src_path)

        raster_crs = src.crs  # Get raster CRS

        # Read geometries from shapefile and check CRS
        with fiona.open(shp_path, "r") as shp:
            shapefile_crs = pyproj.CRS(shp.crs)  # Get shapefile CRS
            shapes: List[Dict[str, Any]] = [feat["geometry"] for feat in shp]

            # Convert geometries to raster CRS if necessary
            if shapefile_crs != raster_crs:
                shapes = [transform_geom(str(shapefile_crs), str(raster_crs), shape) for shape in shapes]

        # Apply mask: crop to shapes and set outside pixels to zero
        out_image, out_transform = rasterio.mask.mask(src, shapes, crop=True)
        out_meta = src.meta.copy()
        src.close()

        # Update metadata for the masked output
        out_meta.update({
            "driver": "GTiff",
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform
        })

        # Ensure destination directory exists
        dst_path = os.path.expanduser(dst_clean)
        os.makedirs(os.path.dirname(dst_path) or ".", exist_ok=True)

        # Write the masked raster
        with rasterio.open(dst_path, "w", **out_meta) as dst:
            dst.write(out_image)

        return {
            "status": "success",
            "destination": dst_path,
            "message": f"Raster masked and saved to '{dst_path}'."
        }

    except Exception as e:
        print(f"Error: {e}")
        raise ValueError(f"Failed to mask raster: {e}")

@gis_mcp.tool()
def resample_raster(
    source: str,
    scale_factor: float,
    resampling: str,
    destination: str
) -> Dict[str, Any]:
    """
    Resample a raster dataset by a scale factor and save the result.
    
    Parameters:
    - source:       local path or HTTPS URL of the source raster.
    - scale_factor: multiplicative factor for width/height 
                    (e.g., 0.5 to halve resolution, 2.0 to double).
    - resampling:   resampling method name: "nearest", "bilinear", "cubic", etc.
    - destination:  local filesystem path for the resampled raster.
    """
    try:
        import numpy as np
        import rasterio
        from rasterio.enums import Resampling
        from rasterio.transform import Affine

        # Strip backticks if present
        src_clean = source.replace("`", "")
        dst_clean = destination.replace("`", "")

        # Open source (remote or local)
        if src_clean.lower().startswith("https://"):
            src = rasterio.open(src_clean)
        else:
            src_path = os.path.expanduser(src_clean)
            if not os.path.isfile(src_path):
                raise FileNotFoundError(f"Source raster not found at '{src_path}'.")
            src = rasterio.open(src_path)

        # Validate scale factor
        if scale_factor <= 0:
            raise ValueError("Scale factor must be positive.")

        # Compute new dimensions
        new_width  = int(src.width  * scale_factor)
        new_height = int(src.height * scale_factor)

        if new_width == 0 or new_height == 0:
            raise ValueError("Resulting raster dimensions are zero. Check scale_factor.")

        # Map resampling method string to Resampling enum
        resampling_enum = getattr(Resampling, resampling.lower(), Resampling.nearest)

        # Read and resample all bands
        data = src.read(
            out_shape=(src.count, new_height, new_width),
            resampling=resampling_enum
        )

        # Validate resampled data
        if data is None or data.size == 0:
            raise ValueError("No data was resampled.")

        # Calculate the new transform to reflect the resampling
        new_transform = src.transform * Affine.scale(
            (src.width  / new_width),
            (src.height / new_height)
        )

        # Update profile
        profile = src.profile.copy()
        profile.update({
            "height":    new_height,
            "width":     new_width,
            "transform": new_transform
        })
        src.close()

        # Ensure destination directory exists
        dst_path = os.path.expanduser(dst_clean)
        os.makedirs(os.path.dirname(dst_path) or ".", exist_ok=True)

        # Write the resampled raster
        with rasterio.open(dst_path, "w", **profile) as dst:
            dst.write(data)

        return {
            "status":      "success",
            "destination": dst_path,
            "message":     f"Raster resampled by factor {scale_factor} using '{resampling}' and saved to '{dst_path}'."
        }

    except Exception as e:
        # Log error and raise for MCP to report
        logger.error(f"Error resampling raster '{source}': {e}")
        raise ValueError(f"Failed to resample raster: {e}")

@gis_mcp.tool()
def reproject_raster(
    source: str,
    target_crs: str,
    destination: str,
    resampling: str = "nearest"
) -> Dict[str, Any]:
    """
    Reproject a raster dataset to a new CRS and save the result.
    
    Parameters:
    - source:      local path or HTTPS URL of the source raster.
    - target_crs:  target CRS string (e.g., "EPSG:4326").
    - destination: local filesystem path for the reprojected raster.
    - resampling:  resampling method: "nearest", "bilinear", "cubic", etc.
    """
    try:
        import numpy as np
        import rasterio
        from rasterio.warp import calculate_default_transform, reproject, Resampling

        # Strip backticks if present
        src_clean = source.replace("`", "")
        dst_clean = destination.replace("`", "")

        # Open source (remote or local)
        if src_clean.lower().startswith("https://"):
            src = rasterio.open(src_clean)
        else:
            src_path = os.path.expanduser(src_clean)
            if not os.path.isfile(src_path):
                raise FileNotFoundError(f"Source raster not found at '{src_path}'.")
            src = rasterio.open(src_path)

        # Calculate transform and dimensions for the target CRS
        transform, width, height = calculate_default_transform(
            src.crs, target_crs, src.width, src.height, *src.bounds
        )

        # Update profile for output
        profile = src.profile.copy()
        profile.update({
            "crs": target_crs,
            "transform": transform,
            "width": width,
            "height": height
        })
        src.close()

        # Map resampling method string to Resampling enum
        resampling_enum = getattr(Resampling, resampling.lower(), Resampling.nearest)

        # Ensure destination directory exists
        dst_path = os.path.expanduser(dst_clean)
        os.makedirs(os.path.dirname(dst_path) or ".", exist_ok=True)

        # Perform reprojection and write output
        with rasterio.open(dst_path, "w", **profile) as dst:
            for i in range(1, profile["count"] + 1):
                reproject(
                    source=rasterio.open(src_clean).read(i),
                    destination=rasterio.band(dst, i),
                    src_transform=profile["transform"],  # placeholder, will be overwritten
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=target_crs,
                    resampling=resampling_enum
                )

        return {
            "status":      "success",
            "destination": dst_path,
            "message":     f"Raster reprojected to '{target_crs}' and saved to '{dst_path}'."
        }

    except Exception as e:
        logger.error(f"Error reprojecting raster '{source}' to '{target_crs}': {e}")
        raise ValueError(f"Failed to reproject raster: {e}")

@gis_mcp.tool()
def extract_band(
    source: str,
    band_index: int,
    destination: str
) -> Dict[str, Any]:
    """
    Extract a specific band from a multi-band raster and save it as a single-band GeoTIFF.

    Parameters:
    - source:      path or URL of the input raster.
    - band_index:  index of the band to extract (1-based).
    - destination: path to save the extracted band raster.
    """
    try:
        import rasterio

        src_path = os.path.expanduser(source.replace("`", ""))
        dst_path = os.path.expanduser(destination.replace("`", ""))

        with rasterio.open(src_path) as src:
            if band_index < 1 or band_index > src.count:
                raise ValueError(f"Band index {band_index} is out of range. This raster has {src.count} bands.")

            band = src.read(band_index)
            profile = src.profile.copy()
            profile.update({
                "count": 1
            })

        os.makedirs(os.path.dirname(dst_path) or ".", exist_ok=True)

        with rasterio.open(dst_path, "w", **profile) as dst:
            dst.write(band, 1)

        return {
            "status": "success",
            "destination": dst_path,
            "message": f"Band {band_index} extracted and saved to '{dst_path}'."
        }

    except Exception as e:
        raise ValueError(f"Failed to extract band: {e}")

@gis_mcp.tool()
def raster_band_statistics(
    source: str
) -> Dict[str, Any]:
    """
    Calculate min, max, mean, and std for each band of a raster.

    Parameters:
    - source: path to input raster (local or URL).
    """
    try:
        import numpy as np
        import rasterio

        src_path = os.path.expanduser(source.replace("`", ""))
        stats = {}

        with rasterio.open(src_path) as src:
            for i in range(1, src.count + 1):
                band = src.read(i, masked=True)  # masked array handles NoData
                stats[f"Band {i}"] = {
                    "min": float(band.min()),
                    "max": float(band.max()),
                    "mean": float(band.mean()),
                    "std": float(band.std())
                }

        return {
            "status": "success",
            "statistics": stats,
            "message": f"Band-wise statistics computed successfully."
        }

    except Exception as e:
        raise ValueError(f"Failed to compute statistics: {e}")

@gis_mcp.tool()
def tile_raster(
    source: str,
    tile_size: int,
    destination_dir: str
) -> Dict[str, Any]:
    """
    Split a raster into square tiles of a given size and save them individually.

    Parameters:
    - source:         input raster path.
    - tile_size:      size of each tile (e.g., 256 or 512).
    - destination_dir: directory to store the tiles.
    """
    try:
        import os
        import rasterio
        from rasterio.windows import Window

        src_path = os.path.expanduser(source.replace("`", ""))
        dst_dir = os.path.expanduser(destination_dir.replace("`", ""))
        os.makedirs(dst_dir, exist_ok=True)

        tile_count = 0

        with rasterio.open(src_path) as src:
            profile = src.profile.copy()
            for i in range(0, src.height, tile_size):
                for j in range(0, src.width, tile_size):
                    window = Window(j, i, tile_size, tile_size)
                    transform = src.window_transform(window)
                    data = src.read(window=window)

                    out_profile = profile.copy()
                    out_profile.update({
                        "height": data.shape[1],
                        "width": data.shape[2],
                        "transform": transform
                    })

                    tile_path = os.path.join(dst_dir, f"tile_{i}_{j}.tif")
                    with rasterio.open(tile_path, "w", **out_profile) as dst:
                        dst.write(data)

                    tile_count += 1

        return {
            "status": "success",
            "tiles_created": tile_count,
            "message": f"{tile_count} tiles created and saved in '{dst_dir}'."
        }

    except Exception as e:
        raise ValueError(f"Failed to tile raster: {e}")

@gis_mcp.tool()
def raster_histogram(
    source: str,
    bins: int = 256
) -> Dict[str, Any]:
    """
    Compute histogram of pixel values for each band.

    Parameters:
    - source: path to input raster.
    - bins:   number of histogram bins.
    """
    try:
        import rasterio
        import numpy as np
        import os

        src_path = os.path.expanduser(source.replace("`", ""))
        histograms = {}

        with rasterio.open(src_path) as src:
            for i in range(1, src.count + 1):
                band = src.read(i, masked=True)
                hist, bin_edges = np.histogram(band.compressed(), bins=bins)
                histograms[f"Band {i}"] = {
                    "histogram": hist.tolist(),
                    "bin_edges": bin_edges.tolist()
                }

        return {
            "status": "success",
            "histograms": histograms,
            "message": f"Histogram computed for all bands."
        }

    except Exception as e:
        raise ValueError(f"Failed to compute histogram: {e}")

@gis_mcp.tool()
def compute_ndvi(
    source: str,
    red_band_index: int,
    nir_band_index: int,
    destination: str
) -> Dict[str, Any]:
    """
    Compute NDVI (Normalized Difference Vegetation Index) and save to GeoTIFF.

    Parameters:
    - source:            input raster path.
    - red_band_index:    index of red band (1-based).
    - nir_band_index:    index of near-infrared band (1-based).
    - destination:       output NDVI raster path.
    """
    try:
        import rasterio
        import numpy as np

        src_path = os.path.expanduser(source.replace("`", ""))
        dst_path = os.path.expanduser(destination.replace("`", ""))

        with rasterio.open(src_path) as src:
            red = src.read(red_band_index).astype("float32")
            nir = src.read(nir_band_index).astype("float32")
            ndvi = (nir - red) / (nir + red + 1e-6)  # avoid division by zero

            profile = src.profile.copy()
            profile.update(dtype="float32", count=1)

        os.makedirs(os.path.dirname(dst_path) or ".", exist_ok=True)

        with rasterio.open(dst_path, "w", **profile) as dst:
            dst.write(ndvi, 1)

        return {
            "status": "success",
            "destination": dst_path,
            "message": f"NDVI calculated and saved to '{dst_path}'."
        }

    except Exception as e:
        raise ValueError(f"Failed to compute NDVI: {e}")

@gis_mcp.tool()
def raster_algebra(
    raster1: str,
    raster2: str,
    band_index: int,
    operation: str,  # User selects "add" or "subtract"
    destination: str
) -> Dict[str, Any]:
    """
    Perform algebraic operations (addition or subtraction) on two raster bands, 
    handling alignment issues automatically.

    Parameters:
    - raster1:     Path to the first raster (.tif).
    - raster2:     Path to the second raster (.tif).
    - band_index:  Index of the band to process (1-based index).
    - operation:   Either "add" or "subtract" to specify the calculation.
    - destination: Path to save the result as a new raster.

    The function aligns rasters if needed, applies the selected operation, and saves the result.
    """
    try:
        import rasterio
        import numpy as np
        from rasterio.warp import reproject, calculate_default_transform, Resampling

        # Expand file paths
        r1 = os.path.expanduser(raster1.replace("`", ""))
        r2 = os.path.expanduser(raster2.replace("`", ""))
        dst = os.path.expanduser(destination.replace("`", ""))

        # Open the raster files
        with rasterio.open(r1) as src1, rasterio.open(r2) as src2:
            # Ensure alignment of rasters
            if src1.crs != src2.crs or src1.transform != src2.transform or src1.shape != src2.shape:
                transform, width, height = calculate_default_transform(
                    src2.crs, src1.crs, src2.width, src2.height, *src2.bounds
                )
                aligned_data = np.zeros((height, width), dtype="float32")
                reproject(
                    source=src2.read(band_index),
                    destination=aligned_data,
                    src_transform=src2.transform,
                    src_crs=src2.crs,
                    dst_transform=transform,
                    dst_crs=src1.crs,
                    resampling=Resampling.bilinear
                )
                band2 = aligned_data
            else:
                band2 = src2.read(band_index).astype("float32")

            band1 = src1.read(band_index).astype("float32")

            # Perform the selected operation
            if operation.lower() == "add":
                result = band1 + band2
            elif operation.lower() == "subtract":
                result = band1 - band2
            else:
                raise ValueError("Invalid operation. Use 'add' or 'subtract'.")

            # Prepare output raster metadata
            profile = src1.profile.copy()
            profile.update(dtype="float32", count=1)

        # Ensure the output directory exists
        os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)

        # Save the result to a new raster file
        with rasterio.open(dst, "w", **profile) as dstfile:
            dstfile.write(result, 1)

        return {
            "status": "success",
            "destination": dst,
            "message": f"Raster operation '{operation}' completed and saved."
        }

    except Exception as e:
        raise ValueError(f"Failed to perform raster operation: {e}")

@gis_mcp.tool()
def concat_bands(
    folder_path: str,
    destination: str
) -> Dict[str, Any]:
    """
    Concatenate multiple single-band raster files into one multi-band raster, 
    handling alignment issues automatically.

    Parameters:
    - folder_path:   Path to folder containing input raster files (e.g. GeoTIFFs).
    - destination:   Path to output multi-band raster file.

    Notes:
    - Files are read in sorted order by filename.
    - If rasters have mismatched CRS, resolution, or dimensions, they are aligned automatically.
    """
    try:
        import rasterio
        import numpy as np
        from rasterio.warp import reproject, calculate_default_transform, Resampling
        from glob import glob

        folder_path = os.path.expanduser(folder_path.replace("`", ""))
        dst_path = os.path.expanduser(destination.replace("`", ""))

        # Collect single-band TIFF files in folder
        files = sorted(glob(os.path.join(folder_path, "*.tif")))

        if len(files) == 0:
            raise ValueError("No .tif files found in folder.")

        # Read properties of the first file for reference
        with rasterio.open(files[0]) as ref:
            meta = ref.meta.copy()
            height, width = ref.height, ref.width
            crs = ref.crs
            transform = ref.transform
            dtype = ref.dtypes[0]

        meta.update(count=len(files), dtype=dtype)

        os.makedirs(os.path.dirname(dst_path) or ".", exist_ok=True)

        with rasterio.open(dst_path, "w", **meta) as dst:
            for idx, fp in enumerate(files, start=1):
                with rasterio.open(fp) as src:
                    band = src.read(1)

                    # Auto-align raster if size or CRS mismatch occurs
                    if src.height != height or src.width != width or src.crs != crs or src.transform != transform:
                        new_transform, new_width, new_height = calculate_default_transform(
                            src.crs, crs, src.width, src.height, *src.bounds
                        )
                        aligned_band = np.zeros((new_height, new_width), dtype=dtype)
                        reproject(
                            source=band,
                            destination=aligned_band,
                            src_transform=src.transform,
                            src_crs=src.crs,
                            dst_transform=new_transform,
                            dst_crs=crs,
                            resampling=Resampling.bilinear
                        )
                        band = aligned_band

                    dst.write(band, idx)

        return {
            "status": "success",
            "destination": dst_path,
            "message": f"{len(files)} single-band rasters concatenated into '{dst_path}'."
        }

    except Exception as e:
        raise ValueError(f"Failed to concatenate rasters: {e}")

@gis_mcp.tool()
def weighted_band_sum(
    source: str,
    weights: List[float],
    destination: str
) -> Dict[str, Any]:
    """
    Compute a weighted sum of all bands in a raster using specified weights.

    Parameters:
    - source:      Path to the input multi-band raster file.
    - weights:     List of weights (must match number of bands and sum to 1).
    - destination: Path to save the output single-band raster.
    """
    try:
        import os
        import numpy as np
        import rasterio

        src_path = os.path.expanduser(source.replace("`", ""))
        dst_path = os.path.expanduser(destination.replace("`", ""))

        with rasterio.open(src_path) as src:
            count = src.count
            if len(weights) != count:
                raise ValueError(f"Number of weights ({len(weights)}) does not match number of bands ({count}).")

            if not np.isclose(sum(weights), 1.0, atol=1e-6):
                raise ValueError("Sum of weights must be 1.0.")

            weighted = np.zeros((src.height, src.width), dtype="float32")

            for i in range(1, count + 1):
                band = src.read(i).astype("float32")
                weighted += weights[i - 1] * band

            profile = src.profile.copy()
            profile.update(dtype="float32", count=1)

        os.makedirs(os.path.dirname(dst_path) or ".", exist_ok=True)

        with rasterio.open(dst_path, "w", **profile) as dst:
            dst.write(weighted, 1)

        return {
            "status": "success",
            "destination": dst_path,
            "message": f"Weighted band sum computed and saved to '{dst_path}'."
        }

    except Exception as e:
        raise ValueError(f"Failed to compute weighted sum: {e}")
