# TACOTIFF Python Package

Python bindings for the TACOTIFF high-performance GeoTIFF driver.

## Installation

```bash
pip install tacotiff
```

## Prerequisites

- GDAL Python bindings (`pip install gdal`)
- TACOTIFF GDAL driver installed in system

## Usage

```python
import tacotiff

# Open TACOTIFF with JSON metadata
metadata = {
    "ImageWidth": 1024,
    "ImageLength": 1024,
    "TileWidth": 256,
    "TileLength": 256,
    # ... complete metadata
}

ds = tacotiff.open("data.tif", metadata_json=metadata, num_threads=4)
array = ds.ReadAsArray()
```

## API Reference

- `tacotiff.open(filename, metadata_json, num_threads=1)` - Open TACOTIFF file
- `tacotiff.metadata_from_tiff(filename)` - Extract metadata from TIFF
- `tacotiff.validate_metadata(metadata)` - Validate metadata schema
