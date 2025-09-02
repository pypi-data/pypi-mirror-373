# PIP

### Install via pip (with uv)

This video teaches you the installation of GIS MCP Server on your windows and Claude Desktop:

<iframe width="560" height="315" src="https://www.youtube.com/embed/1u_ra1Wp4es" frameborder="0" allowfullscreen></iframe>

1. Install uv and create a virtual environment (Python 3.10+):

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

### Client configuration for pip installs

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

Notes:

- Replace `YourUsername` with your actual user name
- Restart your IDE after adding configuration
