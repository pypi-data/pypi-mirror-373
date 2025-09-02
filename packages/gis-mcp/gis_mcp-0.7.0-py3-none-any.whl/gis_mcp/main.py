""" GIS MCP Server - Main entry point

This module implements an MCP server that connects LLMs to GIS operations using
Shapely and PyProj libraries, enabling AI assistants to perform geospatial operations
and transformations.
"""

import json
import logging
import argparse
import sys
from typing import Any, Dict, List, Optional, Union
from .mcp import gis_mcp
try:
    from .data import administrative_boundaries
except ImportError as e:
    administrative_boundaries = None
    import logging
    logging.warning(f"administrative_boundaries module could not be imported: {e}. Install with 'pip install gis-mcp[administrative-boundaries]' if you need this feature.")
try:
    from .data import climate
except ImportError as e:
    climate = None
    import logging
    logging.warning(f"climate module could not be imported: {e}. Install with 'pip install gis-mcp[climate]' if you need this feature.")
try:
    from .data import ecology
except ImportError as e:
    ecology = None
    import logging
    logging.warning(f"ecology module could not be imported: {e}. Install with 'pip install gis-mcp[ecology]' if you need this feature.")
try:
    from .data import movement
except ImportError as e:
    movement = None
    import logging
    logging.warning(f"movement module could not be imported: {e}. Install with 'pip install gis-mcp[movement]' if you need this feature.")



import warnings
warnings.filterwarnings('ignore')  # Suppress warnings for cleaner output

# Import library-specific functions
from .geopandas_functions import (
    read_file_gpd, append_gpd, merge_gpd, overlay_gpd, dissolve_gpd, 
    explode_gpd, clip_vector, sjoin_gpd, sjoin_nearest_gpd, 
    point_in_polygon, write_file_gpd
)
from .shapely_functions import (
    buffer, intersection, union, difference, symmetric_difference,
    convex_hull, envelope, minimum_rotated_rectangle, get_centroid,
    get_bounds, get_coordinates, get_geometry_type, rotate_geometry,
    scale_geometry, translate_geometry, triangulate_geometry, voronoi,
    unary_union_geometries, get_length, get_area, is_valid, make_valid,
    simplify, snap_geometry, nearest_point_on_geometry, normalize_geometry,
    geometry_to_geojson, geojson_to_geometry
)
from .rasterio_functions import (
    metadata_raster, get_raster_crs, clip_raster_with_shapefile,
    resample_raster, reproject_raster, weighted_band_sum, concat_bands,
    raster_algebra, compute_ndvi, raster_histogram, tile_raster,
    raster_band_statistics, extract_band, zonal_statistics,
    reclassify_raster, focal_statistics, hillshade, write_raster
)
from .pyproj_functions import (
    transform_coordinates, project_geometry, get_crs_info,
    get_available_crs, get_utm_zone, get_utm_crs, get_geocentric_crs,
    get_geod_info, calculate_geodetic_distance, calculate_geodetic_point,
    calculate_geodetic_area
)
from .pysal_functions import (
    getis_ord_g, morans_i, gearys_c, gamma_statistic, moran_local,
    getis_ord_g_local, join_counts, join_counts_local, adbscan,
    weights_from_shapefile, distance_band_weights, knn_weights,
    build_transform_and_save_weights, ols_with_spatial_diagnostics_safe,
    build_and_transform_weights
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("gis-mcp")

# Create FastMCP instance

def main():
    """Main entry point for the GIS MCP server."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="GIS MCP Server")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    
    # Set logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    try:
        # Start the MCP server
        print("Starting GIS MCP server...")
        gis_mcp.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 

