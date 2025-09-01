import json
import numpy as np
try:
    from osgeo import gdal
    gdal.UseExceptions()
except ImportError:
    raise ImportError("GDAL Python bindings are required for tacotiff")

def open(filename: str, metadata_json: str | None = None, num_threads: int = 1):
    """
    Open a TACOTIFF file with JSON metadata bypass
    
    Args:
        filename: Path to the TACOTIFF file
        metadata_json: JSON metadata string or dict containing tile information
        num_threads: Number of threads for parallel processing
    
    Returns:
        GDAL Dataset object
        
    Example:
        >>> import tacotiff
        >>> ds = tacotiff.open("data.tif", metadata_json=metadata, num_threads=4)
        >>> array = ds.ReadAsArray()
    """
    if metadata_json is None:
        metadata_json = metadata_from_tiff(filename)
    
    # Convert dict to JSON string if needed
    if isinstance(metadata_json, dict):
        metadata_json = json.dumps(metadata_json)
    
    # Prepare open options
    open_options = [
        f"METADATA_JSON={metadata_json}",
        f"NUM_THREADS={num_threads}"
    ]
    
    # Open with TACOTIFF driver
    ds = gdal.OpenEx(
        filename,
        gdal.GA_ReadOnly,
        allowed_drivers=["TACOTIFF"],
        open_options=open_options
    )
    
    if ds is None:
        raise RuntimeError(f"Failed to open {filename} with TACOTIFF driver")
    
    return ds

def metadata_from_tiff(filename: str) -> dict:
    """
    Extract metadata from existing TIFF file for use with TACOTIFF
    
    Args:
        filename: Path to TIFF file
        
    Returns:
        Dictionary containing tile metadata
    """
    try:
        import tifffile
    except ImportError:
        raise ImportError("tifffile is required for metadata extraction. Install with: pip install tifffile")
    
    with tifffile.TiffFile(filename) as tif:
        page = tif.pages[0]
        
        # Check if tiled
        if not page.is_tiled:
            raise ValueError("TACOTIFF only supports tiled TIFF files")
        
        tags = page.tags
        
        # Get basic info
        def get_tag_value(tag_name):
            tag = tags.get(tag_name)
            if tag is None:
                raise ValueError(f"Required tag {tag_name} not found in TIFF")
            value = tag.value
            return value[0] if isinstance(value, (tuple, list)) else value
        
        # Extract metadata
        tile_offsets = list(tags['TileOffsets'].value)
        tile_byte_counts = list(tags['TileByteCounts'].value)
        
        # CRITICAL: tifffile returns tiles in logical order, 
        # but TACOTIFF needs them in physical file order
        indexed_offsets = [(offset, i) for i, offset in enumerate(tile_offsets)]
        indexed_offsets.sort(key=lambda x: x[0])  # Sort by physical offset
        
        # Reorder to match physical file order
        physical_order = [pair[1] for pair in indexed_offsets]
        tile_offsets_physical = [tile_offsets[i] for i in physical_order]
        tile_byte_counts_physical = [tile_byte_counts[i] for i in physical_order]
        
        metadata = {
            "ImageWidth": int(page.imagewidth),
            "ImageLength": int(page.imagelength), 
            "TileWidth": int(page.tilewidth),
            "TileLength": int(page.tilelength),
            "SamplesPerPixel": int(page.samplesperpixel),
            "BitsPerSample": int(get_tag_value('BitsPerSample')),
            "SampleFormat": int(get_tag_value('SampleFormat')),
            "Predictor": int(get_tag_value('Predictor')),
            "Compression": int(get_tag_value('Compression')),
            "TileOffsets": tile_offsets_physical,
            "TileByteCounts": tile_byte_counts_physical
        }
        
        return metadata

def validate_metadata(metadata: str | dict[str, int | str | list[int]]) -> bool:
    """
    Validate JSON metadata schema for TACOTIFF compatibility
    
    Args:
        metadata: Metadata dictionary to validate
        
    Returns:
        True if valid, raises exception if invalid
    """
    # Mandatory fields
    required_fields = [
        "ImageWidth", "ImageLength", "TileWidth", "TileLength",
        "SamplesPerPixel", "BitsPerSample", "SampleFormat", "Predictor", 
        "TileOffsets", "TileByteCounts"
    ]

    if isinstance(metadata, str):
        metadata = json.loads(metadata)
    
    for field in required_fields:
        if field not in metadata:
            raise ValueError(f"Missing required field: {field}")
    
    return True


def is_tacotiff(filename: str) -> bool:
    """
    Check if a file is a TACOTIFF by inspecting its properties
    
    Args:
        filename: Path to the file to check
        
    Returns:
        True if file is TACOTIFF, False otherwise
    """
    try:
        import tifffile
    except ImportError:
        raise ImportError("is_tacotiff requires tifffile. Install with: pip install tifffile")
    
    try:
        with tifffile.TiffFile(filename) as tif:
            # Must be BigTIFF
            if not tif.is_bigtiff:
                return False
            
            page = tif.pages[0]
            tags = page.tags
            
            # Must be tiled
            if not page.is_tiled:
                return False
            
            # No overviews (only main page)
            if len(tif.pages) > 1:
                return False
            
            # Check compression = 50000 (TACOTIFF)
            compression_tag = tags.get('Compression')
            if compression_tag is None or int(compression_tag.value) != 50000:
                return False
            
            # Check predictor = 1 or 2
            predictor_tag = tags.get('Predictor')
            if predictor_tag is not None:
                predictor = int(predictor_tag.value)
                if isinstance(predictor, (tuple, list)):
                    predictor = predictor[0]
                if predictor not in [1, 2]:
                    return False
            
            # Check total of tiles
            total_tiles = int(np.ceil(page.imagewidth / page.tilewidth))**2 * page.samplesperpixel
            if total_tiles != len(tags['TileOffsets'].value):
                return False
            
            # Calculate tile layout
            tiles_across = int(np.ceil(page.imagewidth / page.tilewidth))
            tiles_down = int(np.ceil(page.imagelength / page.tilelength))
            spatial_blocks = tiles_across * tiles_down
            num_bands = page.samplesperpixel
            expected_tiles = spatial_blocks * num_bands
            
            tile_offsets = list(tags['TileOffsets'].value)
            if len(tile_offsets) != expected_tiles:
                return False
            
            return True
    except Exception:
        return False