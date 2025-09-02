import logging
from pathlib import Path
from typing import Optional, Dict, Any
import cdsapi

from ..mcp import gis_mcp

logger = logging.getLogger(__name__)

DEFAULT_PATH = Path(__file__).resolve().parent / "climate_data"

@gis_mcp.resource("gis://operations/climate")
def get_climate_operations() -> dict:
    """List available climate operations."""
    return {"operations": ["download_climate_data"]}


@gis_mcp.tool()
def download_climate_data(
    variable: str,
    year: str,
    month: str,
    day: str,
    time: str = "12:00",
    dataset: str = "reanalysis-era5-single-levels",
    format: str = "netcdf",
    path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Download climate data (ERA5 or other CDS datasets).

    Args:
        variable: e.g. "2m_temperature", "total_precipitation"
        year: e.g. "2024"
        month: "01".."12"
        day: "01".."31"
        time: Time of day (default: "12:00")
        dataset: CDS dataset name (default: "reanalysis-era5-single-levels")
        format: File format ("netcdf" or "grib")
        path: custom output folder (default: ./data/climate_data)

    Returns:
        {"status": "success", "file_path": "..."} or {"status": "error", "message": "..."}
    """
    try:
        out_dir = Path(path) if path else DEFAULT_PATH
        out_dir.mkdir(parents=True, exist_ok=True)

        client = cdsapi.Client()

        file_path = out_dir / f"{dataset}_{variable}_{year}{month}{day}.{ 'nc' if format == 'netcdf' else 'grib'}"

        client.retrieve(
            dataset,
            {
                "variable": variable,
                "year": year,
                "month": month,
                "day": day,
                "time": time,
                "format": format,
            },
            str(file_path),
        )

        logger.info("Saved climate data %s for %s-%s-%s to %s",
                    variable, year, month, day, file_path)

        return {"status": "success", "file_path": str(file_path)}

    except Exception as e:
        logger.exception("Failed to download climate data")
        return {"status": "error", "message": str(e)}
