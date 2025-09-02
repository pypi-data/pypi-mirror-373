import logging
from pathlib import Path
from typing import Optional, Dict, Any

import pygadm
from ..mcp import gis_mcp

logger = logging.getLogger(__name__)

DEFAULT_PATH = Path(__file__).resolve().parent / "administrative_boundaries"

ALIASES = {
    "USA": "United States",
    "UK": "United Kingdom",
    "IR": "Iran",
}

try:
    import pygadm
    _pygadm_available = True
except ImportError:
    pygadm = None
    _pygadm_available = False

@gis_mcp.resource("gis://operations/administrative_boundaries")
def get_administrative_boundaries_operations() -> dict:
    return {"operations": ["download_boundaries"]}

@gis_mcp.tool()
def download_boundaries(region: str, level: int = 1, path: Optional[str] = None) -> Dict[str, Any]:
    """
    Download GADM administrative boundaries and save as GeoJSON.

    Args:
        region: e.g. "USA" or "United States"
        level: 0=country, 1=state, 2=county, ...
        path: custom output folder

    Returns:
        {"status": "success", "file_path": "..."} or {"status": "error", "message": "..."}
    """
    try:
        if not _pygadm_available:
            raise ImportError("pygadm is not installed. Please install with 'pip install gis-mcp[administrative-boundaries]'.")
        region = ALIASES.get(region.upper(), region)  
        out_dir = Path(path) if path else DEFAULT_PATH
        out_dir.mkdir(parents=True, exist_ok=True)

        # new pygadm API
        gdf = pygadm.AdmItems(name=region, content_level=level)

        file_name = f"{region.replace(' ', '_')}_adm{level}.geojson"
        file_path = out_dir / file_name
        gdf.to_file(file_path, driver="GeoJSON")

        logger.info("Saved %s level %s to %s", region, level, file_path)
        return {"status": "success", "file_path": str(file_path)}

    except Exception as e:
        logger.exception("Failed to download boundaries")
        return {"status": "error", "message": str(e)}
