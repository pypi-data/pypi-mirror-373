import base64
import math
import struct
try:
    from osgeo import gdal
    gdal.UseExceptions()
except ImportError:
    raise ImportError("GDAL Python bindings are required for tacotiff")

# TacoHeader binary format constants
TACO_MAGIC = 0x45564F4C  # "LOVE" ❤️
TACO_VERSION = 1
HEADER_SIZE = 35  # Fixed header size without tile_byte_counts array

# ============================================================================
# BINARY SERIALIZATION CORE
# ============================================================================

def _serialize_to_binary(
    image_width: int,
    image_length: int,
    tile_width: int,
    tile_length: int,
    samples_per_pixel: int,
    bits_per_sample: int,
    sample_format: int,
    predictor: int,
    base_tiles_offset: int,
    tile_byte_counts: list
) -> bytes:
    """Serialize metadata to TacoTIFF binary format"""
    
    tile_count = len(tile_byte_counts)
    
    # Pack fixed header (35 bytes) - clean, no wasted bytes
    header_data = struct.pack(
        '<IHIIHHHBBBQI',               # Clean format - no useless reserved byte
        TACO_MAGIC,                    # magic (4 bytes) ❤️
        TACO_VERSION,                  # version (2 bytes)
        image_width,                   # image_width (4 bytes)
        image_length,                  # image_length (4 bytes)
        tile_width,                    # tile_width (2 bytes)
        tile_length,                   # tile_length (2 bytes)
        samples_per_pixel,             # samples_per_pixel (2 bytes)
        bits_per_sample,               # bits_per_sample (1 byte)
        sample_format,                 # sample_format (1 byte)
        predictor,                     # predictor (1 byte)
        base_tiles_offset,             # base_tiles_offset (8 bytes)
        tile_count                     # tile_count (4 bytes)
    )
    
    # Pack tile_byte_counts array
    tile_counts_data = struct.pack(f'<{tile_count}I', *tile_byte_counts)
    
    return header_data + tile_counts_data


def parse_binary_metadata(data: bytes) -> dict:
    """
    Parse TacoTIFF binary format back to metadata dictionary
    
    Args:
        data: Binary data in TacoHeader format
        
    Returns:
        Dictionary containing TIFF metadata
    """
    if len(data) < HEADER_SIZE:
        raise ValueError("Binary data too short for TacoHeader")
    
    # Unpack fixed header - clean, no wasted bytes
    header_values = struct.unpack('<IHIIHHHBBBQI', data[:HEADER_SIZE])
    
    magic, version, image_width, image_length, tile_width, tile_length, \
    samples_per_pixel, bits_per_sample, sample_format, predictor, \
    base_tiles_offset, tile_count = header_values
    
    # Validate magic number
    if magic != TACO_MAGIC:
        raise ValueError(f"Invalid TacoTIFF magic number: 0x{magic:08x} (expected LOVE)")
    
    # Unpack tile_byte_counts array
    counts_offset = HEADER_SIZE        
    tile_byte_counts = list(struct.unpack(f'<{tile_count}I', data[counts_offset:]))
    
    # Calculate tile_offsets from base_tiles_offset and tile_byte_counts
    tile_offsets = []
    current_offset = base_tiles_offset
    for byte_count in tile_byte_counts:
        tile_offsets.append(current_offset)
        # https://gdal.org/en/stable/drivers/raster/cog.html#tile-data-leader-and-trailer
        current_offset += byte_count + 8
    
    return {
        "ImageWidth": image_width,
        "ImageLength": image_length,
        "TileWidth": tile_width,
        "TileLength": tile_length,
        "SamplesPerPixel": samples_per_pixel,
        "BitsPerSample": bits_per_sample,
        "SampleFormat": sample_format,
        "Predictor": predictor,
        "TileOffsets": tile_offsets,
        "TileByteCounts": tile_byte_counts
    }

# ============================================================================
# MAIN API FUNCTIONS
# ============================================================================

def open(filename: str, metadata_bytes: bytes = None, num_threads: int = 1):
    """
    Open a TACOTIFF file with binary metadata
    
    Args:
        filename: Path to the TACOTIFF file
        metadata_bytes: Binary metadata bytes (TacoHeader format). If None, will extract from TIFF
        num_threads: Number of threads for parallel processing
    
    Returns:
        GDAL Dataset object
        
    Example:
        >>> import tacotiff
        >>> # With metadata bytes
        >>> metadata_bytes = get_metadata_from_somewhere(file_id)  # From Parquet/DB/whatever
        >>> ds = tacotiff.open("data.tif", metadata_bytes, num_threads=4)
        >>> 
        >>> # Without metadata bytes (auto-extract)
        >>> ds = tacotiff.open("data.tif", num_threads=4)
        >>> array = ds.ReadAsArray()
    """
    # If no metadata provided, extract from TIFF
    if metadata_bytes is None:
        metadata_bytes = metadata_from_tiff(filename)
    
    # Prepare open options for GDAL    
    open_options = [
        f"METADATA_BINARY={base64.b64encode(metadata_bytes).decode()}",
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


def metadata_from_tiff(filename: str) -> bytes:
    """
    Extract metadata from existing TIFF file and return as TacoTIFF binary format
    
    Args:
        filename: Path to TIFF file
        
    Returns:
        Binary data in TacoHeader format (ready to write to .tacoheader file)
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
        tile_byte_counts_physical = [tile_byte_counts[i] for i in physical_order]

        # Serialize directly to binary
        return _serialize_to_binary(
            image_width=int(page.imagewidth),
            image_length=int(page.imagelength), 
            tile_width=int(page.tilewidth),
            tile_length=int(page.tilelength),
            samples_per_pixel=int(page.samplesperpixel),
            bits_per_sample=int(get_tag_value('BitsPerSample')),
            sample_format=int(get_tag_value('SampleFormat')),
            predictor=int(get_tag_value('Predictor')),
            base_tiles_offset=min(tile_offsets),
            tile_byte_counts=tile_byte_counts_physical
        )

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_metadata(data: bytes) -> bool:
    """
    Validate binary metadata format
    
    Args:
        data: Binary data to validate
        
    Returns:
        True if valid, raises exception if invalid
    """
    try:
        metadata = parse_binary_metadata(data)
        
        # Check required fields are present and reasonable
        required_fields = [
            "ImageWidth", "ImageLength", "TileWidth", "TileLength",
            "SamplesPerPixel", "BitsPerSample", "SampleFormat", "Predictor", 
            "TileOffsets", "TileByteCounts"
        ]
        
        for field in required_fields:
            if field not in metadata:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate field values are reasonable
        if metadata["ImageWidth"] <= 0 or metadata["ImageLength"] <= 0:
            raise ValueError("Image dimensions must be positive")
        
        if metadata["TileWidth"] <= 0 or metadata["TileLength"] <= 0:
            raise ValueError("Tile dimensions must be positive")
        
        if metadata["SamplesPerPixel"] <= 0 or metadata["SamplesPerPixel"] > 16:
            raise ValueError("SamplesPerPixel must be between 1-16")
        
        if metadata["BitsPerSample"] not in [8, 16, 32, 64]:
            raise ValueError("BitsPerSample must be 8, 16, 32, or 64")
        
        # Validate arrays have same length
        tile_offsets = metadata["TileOffsets"]
        tile_byte_counts = metadata["TileByteCounts"]
        
        if len(tile_offsets) != len(tile_byte_counts):
            raise ValueError("TileOffsets and TileByteCounts must have same length")
        
        if len(tile_offsets) == 0:
            raise ValueError("No tiles found")
        
        # Validate offsets are increasing (physical order)
        for i in range(1, len(tile_offsets)):
            if tile_offsets[i] <= tile_offsets[i-1]:
                raise ValueError("TileOffsets must be in increasing order")
        
        # Validate byte counts are positive
        for count in tile_byte_counts:
            if count <= 0:
                raise ValueError("All tile byte counts must be positive")
        
        return True
        
    except Exception as e:
        raise ValueError(f"Invalid binary metadata: {e}")


def is_tacotiff(filename: str) -> bool:
    """
    Check if a TIFF is a TACOTIFF by inspecting its properties
    
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
            
            # Calculate tile layout - FIXED: removed duplicate/incorrect calculation
            tiles_across = int(math.ceil(page.imagewidth / page.tilewidth))
            tiles_down = int(math.ceil(page.imagelength / page.tilelength))
            spatial_blocks = tiles_across * tiles_down
            num_bands = page.samplesperpixel
            expected_tiles = spatial_blocks * num_bands
            
            tile_offsets = list(tags['TileOffsets'].value)
            if len(tile_offsets) != expected_tiles:
                return False
            
            return True
    except Exception:
        return False