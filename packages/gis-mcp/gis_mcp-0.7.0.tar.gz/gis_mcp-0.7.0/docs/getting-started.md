# Getting Started

This guide helps you install and run the GIS MCP Server quickly using pip (with uv) and shows how to connect it to your IDE/client.

### Prerequisites

- Python 3.10+
- Internet access to install packages

### Install via pip (with uv)

1. Create a virtual environment:

```bash
pip install uv
uv venv --python=3.10
```

2. Install the package:

```bash
uv pip install gis-mcp
```

3. Run the server:

```bash
gis-mcp
```

### Connect to an MCP client (optional)

Claude Desktop (Windows):

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

Claude Desktop (Linux/Mac):

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

Cursor IDE (Windows) – `.cursor/mcp.json`:

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

Cursor IDE (Linux/Mac) – `.cursor/mcp.json`:

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

This video teaches you the installation of GIS MCP Server on your windows and Claude Desktop:

<iframe width="560" height="315" src="https://www.youtube.com/embed/1u_ra1Wp4es" frameborder="0" allowfullscreen></iframe>

Notes

- Replace `YourUsername` with your actual username
- Restart your IDE after adding configuration

### Next steps

- Explore the API Reference in the sidebar (Shapely, PyProj, GeoPandas, Rasterio, PySAL)
- Check Installations → Developers for editable installs
