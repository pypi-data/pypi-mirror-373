"""
TACOTIFF - AI-Optimized GeoTIFF reading with JSON metadata bypass

High-performance GeoTIFF driver that bypasses TIFF header parsing
using external JSON metadata for maximum speed.
"""

import os
from pathlib import Path

# Auto-configure GDAL to find the TACOTIFF driver
def _setup_driver_path():
    """Automatically configure GDAL_DRIVER_PATH to find TACOTIFF driver"""
    driver_dir = Path(__file__).parent / "drivers"
    if driver_dir.exists():
        existing_path = os.environ.get("GDAL_DRIVER_PATH", "")
        new_path = f"{existing_path}:{driver_dir}" if existing_path else str(driver_dir)
        os.environ["GDAL_DRIVER_PATH"] = new_path

# Setup driver path on import
_setup_driver_path()

from .core import open, metadata_from_tiff, validate_metadata, is_tacotiff, parse_binary_metadata
from .version import __version__

__author__ = "Cesar Aybar"
__author_email__ = "cesar.aybar@uv.es"
__description__ = "TACOTIFF - AI-Optimized GeoTIFF reading with JSON metadata bypass"
__url__ = "https://github.com/tacofoundation/tacotiff"
__license__ = "MIT"

__all__ = ["open", "metadata_from_tiff", "validate_metadata", "is_tacotiff", "parse_binary_metadata"]
