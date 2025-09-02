# GIS MCP Server

<div align="center">
  <h3>✨ Want to perform accurate geospatial analysis in your chatbot? ✨</h3>
  <p><strong>Install GIS-MCP and transform your AI's spatial capabilities!</strong></p>
  <br/>
  <img src="docs/Logo.png" alt="GIS MCP Server Logo" width="300"/>
  <br/>
  <br/>
</div>

A Model Context Protocol (MCP) server implementation that connects Large Language Models (LLMs) to GIS operations using GIS libraries, enabling AI assistants to perform geospatial operations and transformations.

🌐 **Website:** [gis-mcp.com](https://gis-mcp.com)

> Current version is 0.7.0
>
> Version 0.8.0 (Beta) is under active development. We welcome contributions and developers to join us in building this project.

## 🎥 Demo

<div align="center">
  <img src="docs/demo.gif" alt="GIS MCP Server Demo" width="800"/>
</div>

### Rasterio Demo

<div align="center">
  <a href="https://www.veed.io/view/95ff85f4-efbb-4154-9a04-d966c6ae1737?panel=share">
    <br/>
    <em>Click to watch the Rasterio demo video or go to docs folder</em>
  </a>
</div>

## 📋 Table of Contents

- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
  - [Installing via Smithery](#-installing-via-smithery)
  - [pip Installation](#-pip-installation)
  - [Development Installation](#-development-installation)
- [Available Functions](#-available-functions)
  - [Shapely Functions](#-shapely-functions-29-total)
  - [PyProj Functions](#-pyproj-functions-11-total)
  - [GeoPandas Functions](#-geopandas-functions-11-total)
  - [Rasterio Functions](#-rasterio-functions-18-total)
  - [PySAL Functions](#-pysal-functions-15-total)
  - [Administrative Boundaries Functions](#-administrative-boundaries-functions)
  - [Climate Data Functions](#-climate-data-functions)
  - [Ecology Data Functions](#-ecology-data-functions)
  - [Movement Data Functions](#-movement-data-functions)
- [Client Development](#-client-development)
- [Planned Features](#-planned-features)
- [Contributing](#-contributing)
- [License](#-license)
- [Related Projects](#-related-projects)
- [Support](#-support)
- [Badges](#-badges)

## 🚀 Features

GIS MCP Server empowers AI assistants with advanced geospatial intelligence. Key features include:

- 🔹 **Comprehensive Geometry Operations** – Perform intersection, union, buffer, difference, and other geometric transformations with ease.
- 🔹 **Advanced Coordinate Transformations** – Effortlessly reproject and transform geometries between coordinate reference systems.
- 🔹 **Accurate Measurements** – Compute distances, areas, lengths, and centroids precisely.
- 🔹 **Spatial Analysis & Validation** – Validate geometries, run proximity checks, and perform spatial overlays or joins.
- 🔹 **Raster & Vector Support** – Process raster layers, compute indices like NDVI, clip, resample, and merge with vector data.
- 🔹 **Spatial Statistics & Modeling** – Leverage PySAL for spatial autocorrelation, clustering, and neighborhood analysis.
- 🔹 **Easy Integration** – Connect seamlessly with MCP-compatible clients like Claude Desktop or Cursor IDE.
- 🔹 **Flexible & Extensible** – Supports Python-based GIS libraries and is ready for custom tools or workflow extensions.

> 🌟 **Tip:** With GIS MCP Server, your AI can now “think spatially,” unlocking new capabilities for environmental analysis, mapping, and location intelligence.

---

## 📋 Prerequisites

- Python 3.10 or higher
- MCP-compatible client (like Claude Desktop or Cursor)
- Internet connection for package installation

## 🛠 Installation

Choose the installation method that best suits your needs:

### 🛠 Installing via Smithery

To install GIS MCP Server for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@mahdin75/gis-mcp):

```bash
npx -y @smithery/cli install @mahdin75/gis-mcp --client claude
```

### 📦 pip Installation

The pip installation is recommended for most users:

1. Install uv package manager:

```bash
pip install uv
```

2. Create the Virtual Environment (Python 3.10+):

```bash
uv venv --python=3.10
```

3. Install the package:

```bash
uv pip install gis-mcp
```

4. Start the server:

```bash
gis-mcp
```

#### pip Configuration

To use the pip installation with Claude or Cursor, add the following configuration:

**Claude Desktop:**

**Windows:**

```json
{
  "mcpServers": {
    "gis-mcp": {
      "command": "C:\\Users\\YourUsername\\.venv\\Scripts\\gis-mcp",
      "args": []
    }
  }
}
```

**Linux/Mac:**

```json
{
  "mcpServers": {
    "gis-mcp": {
      "command": "/home/YourUsername/.venv/bin/gis-mcp",
      "args": []
    }
  }
}
```

**Cursor IDE** (create `.cursor/mcp.json`):

**Windows:**

```json
{
  "mcpServers": {
    "gis-mcp": {
      "command": "C:\\Users\\YourUsername\\.venv\\Scripts\\gis-mcp",
      "args": []
    }
  }
}
```

**Linux/Mac:**

```json
{
  "mcpServers": {
    "gis-mcp": {
      "command": "/home/YourUsername/.venv/bin/gis-mcp",
      "args": []
    }
  }
}
```

After configuration:

1. Make sure to replace `YourUsername` with your actual username
2. For development installation, replace `/path/to/gis-mcp` with the actual path to your project
3. Restart your IDE to apply the changes
4. You can now use all GIS operations through Claude or Cursor!

### 🛠 Development Installation

For contributors and developers:

1. Install uv package manager:

```bash
pip install uv
```

2. Create the Virtual Environment:

```bash
uv venv --python=3.10
```

3. Install the package in development mode:

```bash
uv pip install -e .
```

4. Start the server:

```bash
python -m gis_mcp
```

#### Development Configuration

To use the development installation with Claude or Cursor, add the following configuration:

**Claude Desktop:**

**Windows:**

```json
{
  "mcpServers": {
    "gis-mcp": {
      "command": "C:\\path\\to\\gis-mcp\\.venv\\Scripts\\python",
      "args": ["-m", "gis_mcp"]
    }
  }
}
```

**Linux/Mac:**

```json
{
  "mcpServers": {
    "gis-mcp": {
      "command": "/path/to/gis-mcp/.venv/bin/python",
      "args": ["-m", "gis_mcp"]
    }
  }
}
```

**Cursor IDE** (create `.cursor/mcp.json`):

**Windows:**

```json
{
  "mcpServers": {
    "gis-mcp": {
      "command": "C:\\path\\to\\gis-mcp\\.venv\\Scripts\\python",
      "args": ["-m", "gis_mcp"]
    }
  }
}
```

**Linux/Mac:**

```json
{
  "mcpServers": {
    "gis-mcp": {
      "command": "/path/to/gis-mcp/.venv/bin/python",
      "args": ["-m", "gis_mcp"]
    }
  }
}
```

After configuration:

1. Make sure to replace `YourUsername` with your actual username
2. For development installation, replace `/path/to/gis-mcp` with the actual path to your project
3. Restart your IDE to apply the changes
4. You can now use all GIS operations through Claude or Cursor!

## 📚 Available Functions

This section provides a comprehensive list of all available functions organized by library.

### 🔷 Shapely Functions (29 total)

**Basic Geometric Operations:**

- `buffer` - Create buffer around geometry
- `intersection` - Find intersection of two geometries
- `union` - Combine two geometries
- `difference` - Find difference between geometries
- `symmetric_difference` - Find symmetric difference

**Geometric Properties:**

- `convex_hull` - Calculate convex hull
- `envelope` - Get bounding box
- `minimum_rotated_rectangle` - Get minimum rotated rectangle
- `get_centroid` - Get centroid point
- `get_bounds` - Get geometry bounds
- `get_coordinates` - Extract coordinate array
- `get_geometry_type` - Get geometry type name

**Transformations:**

- `rotate_geometry` - Rotate geometry by angle
- `scale_geometry` - Scale geometry by factors
- `translate_geometry` - Move geometry by offset

**Advanced Operations:**

- `triangulate_geometry` - Create triangulation
- `voronoi` - Create Voronoi diagram
- `unary_union_geometries` - Union multiple geometries

**Measurements:**

- `get_length` - Calculate geometry length
- `get_area` - Calculate geometry area

**Validation & Utilities:**

- `is_valid` - Check geometry validity
- `make_valid` - Fix invalid geometry
- `simplify` - Simplify geometry
- `snap_geometry` - Snap to reference geometry
- `nearest_point_on_geometry` - Find nearest point
- `normalize_geometry` - Normalize orientation
- `geometry_to_geojson` - Convert to GeoJSON
- `geojson_to_geometry` - Convert from GeoJSON

### 🔷 PyProj Functions (11 total)

**Coordinate Transformations:**

- `transform_coordinates` - Transform point coordinates
- `project_geometry` - Project geometry between CRS

**CRS Information:**

- `get_crs_info` - Get detailed CRS information
- `get_available_crs` - List available CRS systems
- `get_utm_zone` - Get UTM zone for coordinates
- `get_utm_crs` - Get UTM CRS for coordinates
- `get_geocentric_crs` - Get geocentric CRS

**Geodetic Calculations:**

- `get_geod_info` - Get ellipsoid information
- `calculate_geodetic_distance` - Calculate distance on ellipsoid
- `calculate_geodetic_point` - Calculate point at distance/azimuth
- `calculate_geodetic_area` - Calculate area on ellipsoid

### 🔷 GeoPandas Functions (11 total)

**I/O Operations:**

- `read_file_gpd` - Read geospatial file with preview
- `write_file_gpd` - Export GeoDataFrame to file

**Join & Merge Operations:**

- `append_gpd` - Concatenate GeoDataFrames vertically
- `merge_gpd` - Database-style attribute joins
- `overlay_gpd` - Spatial overlay operations
- `dissolve_gpd` - Dissolve by attribute
- `explode_gpd` - Split multi-part geometries

**Spatial Operations:**

- `clip_vector` - Clip geometries
- `sjoin_gpd` - Spatial joins
- `sjoin_nearest_gpd` - Nearest neighbor spatial joins
- `point_in_polygon` - Point-in-polygon tests

### 🔷 Rasterio Functions (18 total)

**Basic Raster Operations:**

- `metadata_raster` - Get raster metadata
- `get_raster_crs` - Get raster CRS
- `extract_band` - Extract single band
- `raster_band_statistics` - Calculate band statistics
- `raster_histogram` - Compute pixel histograms

**Raster Processing:**

- `clip_raster_with_shapefile` - Clip raster with polygons
- `resample_raster` - Resample by scale factor
- `reproject_raster` - Reproject to new CRS
- `tile_raster` - Split into tiles

**Raster Analysis:**

- `compute_ndvi` - Calculate vegetation index
- `raster_algebra` - Mathematical operations on bands
- `concat_bands` - Combine single-band rasters
- `weighted_band_sum` - Weighted band combination

**Advanced Analysis:**

- `zonal_statistics` - Statistics within polygons
- `reclassify_raster` - Reclassify pixel values
- `focal_statistics` - Moving window statistics
- `hillshade` - Generate hillshade from DEM
- `write_raster` - Write array to raster file

### 🔷 PySAL Functions (15 total)

**Spatial Autocorrelation:**

- `morans_i` - Global Moran's I statistic
- `gearys_c` - Global Geary's C statistic
- `gamma_statistic` - Gamma index
- `getis_ord_g` - Global Getis-Ord G statistic

**Local Statistics:**

- `moran_local` - Local Moran's I
- `getis_ord_g_local` - Local Getis-Ord G\*
- `join_counts_local` - Local join counts

**Global Statistics:**

- `join_counts` - Binary join counts test
- `adbscan` - Adaptive density-based clustering

**Spatial Weights:**

- `weights_from_shapefile` - Create weights from shapefile
- `distance_band_weights` - Distance-based weights
- `knn_weights` - K-nearest neighbors weights
- `build_transform_and_save_weights` - Build, transform, and save weights
- `ols_with_spatial_diagnostics_safe` - OLS regression with spatial diagnostics
- `build_and_transform_weights` - Build and transform weights

### 🔷 Administrative Boundaries Functions

**Boundary Download:**

- `download_boundaries` - Download GADM administrative boundaries and save as GeoJSON

### 🔷 Climate Data Functions

**Climate Data Download:**

- `download_climate_data` - Download climate data (ERA5 or other CDS datasets)

### 🔷 Ecology Data Functions

**Ecology Data Download and Info:**

- `get_species_info` – Retrieve taxonomic information for a given species name
- `download_species_occurrences` – Download occurrence records for a given species and save as JSON

### 🔷 Movement Data Functions

**Movement Data Download and Routing (via [OSMnx](https://osmnx.readthedocs.io/en/stable/)):**

- `download_street_network` – Download a street network for a given place and save as GraphML
- `calculate_shortest_path` – Calculate the shortest path between two points using a saved street network

**Total Functions Available: 86**

## 🛠 Client Development

Example usage of the tools:

### Buffer Operation

```python
Tool: buffer
Parameters: {
    "geometry": "POINT(0 0)",
    "distance": 10,
    "resolution": 16,
    "join_style": 1,
    "mitre_limit": 5.0,
    "single_sided": false
}
```

### Coordinate Transformation

```python
Tool: transform_coordinates
Parameters: {
    "coordinates": [0, 0],
    "source_crs": "EPSG:4326",
    "target_crs": "EPSG:3857"
}
```

### Geodetic Distance

```python
Tool: calculate_geodetic_distance
Parameters: {
    "point1": [0, 0],
    "point2": [10, 10],
    "ellps": "WGS84"
}
```

## 🔮 Planned Features

- Implement advanced spatial indexing
- Implement network analysis capabilities
- Add support for 3D geometries
- Implement performance optimizations
- Add support for more GIS libraries

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please ensure your PR description clearly describes the problem and solution. Include the relevant issue number if applicable.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Related Projects

- [Model Context Protocol](https://github.com/anthropics/model-context-protocol) - The core MCP implementation
- [Shapely](https://github.com/shapely/shapely) - Python package for manipulation and analysis of geometric objects
- [PyProj](https://github.com/pyproj4/pyproj) - Python interface to PROJ library
- [GeoPandas](https://github.com/geopandas/geopandas) - Python package for working with geospatial data
- [Rasterio](https://github.com/rasterio/rasterio) - Python package for reading and writing geospatial raster data
- [PySAL](https://github.com/pysal/pysal) - PySAL, the Python spatial analysis library for geospatial data science with an emphasis on geospatial vector data written in Python.
- [cdsapi](https://github.com/ecmwf/cdsapi) - Python API to access the Copernicus Climate Data Store (CDS).
- [pygadm](https://github.com/12rambau/pygadm) - Easy access to administrative boundary defined by GADM from Python scripts
- [pygbif](https://github.com/gbif/pygbif) - Python client for the GBIF API (ecology and biodiversity data)
- [OSMnx](https://osmnx.readthedocs.io/en/stable/) - Python package for downloading, modeling, and analyzing street networks and urban features from OpenStreetMap

## 📞 Support

For support, please open an issue in the GitHub repository.

## 💬 Community

Join our Discord community for discussions, updates, and support:

[![Join our Discord](https://img.shields.io/badge/Discord-Join%20our%20community-7289DA?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/dzkXZsZK)

## 👥 Contributors

<a href="https://github.com/mahdin75/gis-mcp/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=mahdin75/gis-mcp" />
</a>

Made with [contrib.rocks](https://contrib.rocks).

<br/>

## 🏆 Badges

<div align="center">

[![Trust Score](https://archestra.ai/mcp-catalog/api/badge/quality/mahdin75/gis-mcp)](https://archestra.ai/mcp-catalog/mahdin75__gis-mcp)
<br/></br>

  <a href="https://glama.ai/mcp/servers/@mahdin75/gis-mcp">
    <img width="380" height="200" src="https://glama.ai/mcp/servers/@mahdin75/gis-mcp/badge" alt="GIS Server MCP server" />
  </a>
  <br/><br/><br/>
  
  <a href="https://mcp.so/server/gis-mcp-server/mahdin75">
    <img src="https://mcp.so/logo.png" alt="MCP.so Badge" width="150"/>
  </a>
</div>
