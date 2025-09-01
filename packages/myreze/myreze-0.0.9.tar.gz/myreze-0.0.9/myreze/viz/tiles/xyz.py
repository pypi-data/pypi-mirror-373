"""
XYZ tile rendering for MyrezeDataPackage.

This module provides on-demand tile generation for web map tile services
following the XYZ/Slippy Map tile convention used by OpenStreetMap, Google Maps, etc.
"""

import math
import numpy as np
from typing import Dict, Any, Optional, Tuple, Union
from PIL import Image
import io
import base64
import warnings

try:
    import rasterio
    from rasterio.warp import reproject, Resampling, calculate_default_transform
    from rasterio.transform import from_bounds
    from rasterio.crs import CRS

    HAS_RASTERIO = True
except ImportError:
    HAS_RASTERIO = False
    warnings.warn("rasterio not available. Map tile functionality will be limited.")

# Web Mercator constants
EARTH_RADIUS = 6378137.0  # meters
EARTH_CIRCUMFERENCE = 2 * math.pi * EARTH_RADIUS
WEB_MERCATOR_CRS = "EPSG:3857"
WGS84_CRS = "EPSG:4326"


def xyz_tile_bounds(x: int, y: int, z: int) -> Tuple[float, float, float, float]:
    """
    Calculate Web Mercator bounds for an XYZ tile.

    Args:
        x: Tile X coordinate
        y: Tile Y coordinate
        z: Zoom level

    Returns:
        Tuple of (minx, miny, maxx, maxy) in Web Mercator meters
    """
    if z < 0:
        raise ValueError(f"Zoom level must be >= 0, got {z}")

    # Calculate tile size at this zoom level
    n = 2**z
    tile_size_meters = EARTH_CIRCUMFERENCE / n

    # Calculate bounds
    minx = -EARTH_CIRCUMFERENCE / 2 + x * tile_size_meters
    maxx = minx + tile_size_meters
    miny = EARTH_CIRCUMFERENCE / 2 - (y + 1) * tile_size_meters
    maxy = miny + tile_size_meters

    return (minx, miny, maxx, maxy)


def deg_to_web_mercator(lon: float, lat: float) -> Tuple[float, float]:
    """Convert longitude/latitude to Web Mercator coordinates."""
    # Clamp latitude to avoid infinity
    lat = max(-85.0511, min(85.0511, lat))

    x = lon * EARTH_RADIUS * math.pi / 180.0
    y = math.log(math.tan((90 + lat) * math.pi / 360.0)) * EARTH_RADIUS

    return (x, y)


def web_mercator_to_deg(x: float, y: float) -> Tuple[float, float]:
    """Convert Web Mercator coordinates to longitude/latitude."""
    lon = x / EARTH_RADIUS * 180.0 / math.pi
    lat = (2 * math.atan(math.exp(y / EARTH_RADIUS)) - math.pi / 2) * 180.0 / math.pi

    return (lon, lat)


def bounds_to_web_mercator(
    bounds: Tuple[float, float, float, float], source_crs: str = WGS84_CRS
) -> Tuple[float, float, float, float]:
    """Convert bounds from source CRS to Web Mercator."""
    if source_crs.upper() in [WEB_MERCATOR_CRS, "EPSG:3857"]:
        return bounds
    elif source_crs.upper() in [WGS84_CRS, "EPSG:4326"]:
        west, south, east, north = bounds
        minx, miny = deg_to_web_mercator(west, south)
        maxx, maxy = deg_to_web_mercator(east, north)
        return (minx, miny, maxx, maxy)
    else:
        raise ValueError(f"Unsupported CRS: {source_crs}")


def apply_colormap(
    data: np.ndarray,
    colormap: str = "viridis",
    vmin: Optional[float] = None,
    vmax: Optional[float] = None,
    nodata: Optional[float] = None,
) -> np.ndarray:
    """
    Apply colormap to scalar data to create RGBA array.

    Args:
        data: 2D numpy array of scalar values
        colormap: Colormap name (viridis, plasma, inferno, magma, etc.)
        vmin: Minimum value for colormap scaling
        vmax: Maximum value for colormap scaling
        nodata: Value to treat as transparent

    Returns:
        RGBA array with shape (H, W, 4)
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.cm as cm
    except ImportError:
        # Fallback to simple grayscale
        warnings.warn("matplotlib not available, using grayscale colormap")
        if vmin is None:
            vmin = np.nanmin(data)
        if vmax is None:
            vmax = np.nanmax(data)

        # Normalize to 0-255
        normalized = np.clip((data - vmin) / (vmax - vmin) * 255, 0, 255).astype(
            np.uint8
        )
        rgba = np.stack(
            [normalized, normalized, normalized, np.full_like(normalized, 255)], axis=-1
        )

        # Handle nodata
        if nodata is not None:
            mask = np.isclose(data, nodata)
            rgba[mask, 3] = 0  # Set alpha to 0 for nodata

        return rgba

    # Use matplotlib colormap
    if vmin is None:
        vmin = np.nanmin(data)
    if vmax is None:
        vmax = np.nanmax(data)

    # Normalize data
    normalized = (data - vmin) / (vmax - vmin)
    normalized = np.clip(normalized, 0, 1)

    # Apply colormap
    try:
        # New matplotlib API (3.7+)
        cmap = plt.colormaps[colormap]
    except (KeyError, AttributeError):
        try:
            # Fallback for older matplotlib versions
            cmap = cm.get_cmap(colormap)
        except (KeyError, ValueError):
            # Invalid colormap name - fallback to viridis
            warnings.warn(f"Unknown colormap '{colormap}', falling back to 'viridis'")
            try:
                cmap = plt.colormaps["viridis"]
            except (KeyError, AttributeError):
                cmap = cm.get_cmap("viridis")
    rgba = cmap(normalized)  # Returns RGBA in [0,1]
    rgba = (rgba * 255).astype(np.uint8)

    # Handle nodata
    if nodata is not None:
        mask = np.isclose(data, nodata)
        rgba[mask, 3] = 0  # Set alpha to 0 for nodata

    return rgba


def render_xyz_tile(
    data: Dict[str, Any],
    metadata: Dict[str, Any],
    x: int,
    y: int,
    z: int,
    tile_size: int = 256,
    style: Optional[Dict[str, Any]] = None,
) -> np.ndarray:
    """
    Render a 256x256 RGBA tile for the given XYZ coordinates.

    Args:
        data: Data dictionary from MyrezeDataPackage
        metadata: Metadata dictionary from MyrezeDataPackage
        x: Tile X coordinate
        y: Tile Y coordinate
        z: Zoom level (clamped to 1-18)
        tile_size: Output tile size in pixels (default 256)
        style: Optional styling parameters

    Returns:
        RGBA numpy array with shape (tile_size, tile_size, 4)
    """
    # Clamp zoom level
    z = max(1, min(18, z))

    if style is None:
        style = {}

    # Get tile bounds in Web Mercator
    tile_minx, tile_miny, tile_maxx, tile_maxy = xyz_tile_bounds(x, y, z)

    # Get source data bounds and CRS
    source_bounds = metadata.get("bounds")
    if not source_bounds:
        raise ValueError("No 'bounds' found in metadata")

    source_crs = metadata.get("crs", WGS84_CRS)

    # Convert source bounds to Web Mercator
    try:
        source_bounds_mercator = bounds_to_web_mercator(source_bounds, source_crs)
    except ValueError as e:
        raise ValueError(f"Failed to convert bounds: {e}")

    src_minx, src_miny, src_maxx, src_maxy = source_bounds_mercator

    # Check for overlap
    if (
        tile_maxx <= src_minx
        or tile_minx >= src_maxx
        or tile_maxy <= src_miny
        or tile_miny >= src_maxy
    ):
        # No overlap - return transparent tile
        return np.zeros((tile_size, tile_size, 4), dtype=np.uint8)

    # Handle different data types
    if "grid" in data:
        # Numeric grid data
        grid = np.array(data["grid"])
        if grid.ndim != 2:
            raise ValueError(f"Grid must be 2D, got shape {grid.shape}")

        # Create source transform
        src_height, src_width = grid.shape
        src_transform = from_bounds(*source_bounds_mercator, src_width, src_height)

        # Create destination transform
        dst_transform = from_bounds(
            tile_minx, tile_miny, tile_maxx, tile_maxy, tile_size, tile_size
        )

        # Prepare output array
        dst_array = np.zeros((tile_size, tile_size), dtype=grid.dtype)

        if HAS_RASTERIO:
            # Use rasterio for reprojection
            reproject(
                source=grid,
                destination=dst_array,
                src_transform=src_transform,
                dst_transform=dst_transform,
                src_crs=WEB_MERCATOR_CRS,
                dst_crs=WEB_MERCATOR_CRS,
                resampling=Resampling.bilinear,
            )
        else:
            # Simple nearest neighbor fallback
            warnings.warn(
                "Using simple nearest neighbor resampling. Install rasterio for better quality."
            )

            # Calculate sampling coordinates
            for dst_row in range(tile_size):
                for dst_col in range(tile_size):
                    # Convert destination pixel to world coordinates
                    dst_x = (
                        tile_minx
                        + (dst_col + 0.5) * (tile_maxx - tile_minx) / tile_size
                    )
                    dst_y = (
                        tile_maxy
                        - (dst_row + 0.5) * (tile_maxy - tile_miny) / tile_size
                    )

                    # Convert to source pixel coordinates
                    src_col = (dst_x - src_minx) / (src_maxx - src_minx) * src_width
                    src_row = (src_maxy - dst_y) / (src_maxy - src_miny) * src_height

                    # Nearest neighbor sampling
                    src_col_int = int(round(src_col))
                    src_row_int = int(round(src_row))

                    if 0 <= src_row_int < src_height and 0 <= src_col_int < src_width:
                        dst_array[dst_row, dst_col] = grid[src_row_int, src_col_int]

        # Convert to RGBA
        colormap = style.get("colormap", metadata.get("colormap", "viridis"))
        vmin = style.get("vmin", metadata.get("min_value"))
        vmax = style.get("vmax", metadata.get("max_value"))
        nodata = style.get("nodata", metadata.get("nodata"))

        rgba_tile = apply_colormap(dst_array, colormap, vmin, vmax, nodata)

    elif "png_bytes" in data:
        # PNG data
        png_data = data["png_bytes"]

        if isinstance(png_data, str):
            # Base64 encoded
            png_bytes = base64.b64decode(png_data)
        elif isinstance(png_data, bytes):
            png_bytes = png_data
        else:
            raise ValueError(f"png_bytes must be string or bytes, got {type(png_data)}")

        # Load PNG
        img = Image.open(io.BytesIO(png_bytes))
        img_array = np.array(img)

        # Handle different image formats and convert to RGBA
        if img_array.ndim == 2:
            # Single-channel grayscale - treat as scalar data for colormap application
            # Check if we should apply colormap or use as grayscale
            colormap = style.get("colormap", metadata.get("colormap"))
            if colormap and colormap.lower() != "grayscale":
                # Apply colormap to single-channel data
                vmin = style.get("vmin", metadata.get("min_value"))
                vmax = style.get("vmax", metadata.get("max_value"))
                nodata = style.get("nodata", metadata.get("nodata"))
                img_array = apply_colormap(img_array, colormap, vmin, vmax, nodata)
            else:
                # Use as grayscale (RGB with alpha)
                img_array = np.stack(
                    [img_array, img_array, img_array, np.full_like(img_array, 255)],
                    axis=-1,
                )
        elif img_array.ndim == 3 and img_array.shape[2] == 1:
            # Single-channel with explicit channel dimension
            single_channel = img_array[:, :, 0]
            colormap = style.get("colormap", metadata.get("colormap"))
            if colormap and colormap.lower() != "grayscale":
                # Apply colormap to single-channel data
                vmin = style.get("vmin", metadata.get("min_value"))
                vmax = style.get("vmax", metadata.get("max_value"))
                nodata = style.get("nodata", metadata.get("nodata"))
                img_array = apply_colormap(single_channel, colormap, vmin, vmax, nodata)
            else:
                # Use as grayscale (RGB with alpha)
                img_array = np.stack(
                    [
                        single_channel,
                        single_channel,
                        single_channel,
                        np.full_like(single_channel, 255),
                    ],
                    axis=-1,
                )
        elif img_array.ndim == 3 and img_array.shape[2] == 3:
            # RGB - add alpha channel
            alpha = np.full(
                (img_array.shape[0], img_array.shape[1], 1), 255, dtype=img_array.dtype
            )
            img_array = np.concatenate([img_array, alpha], axis=-1)
        elif img_array.ndim == 3 and img_array.shape[2] == 4:
            # Already RGBA - use as is
            pass
        else:
            raise ValueError(
                f"Unsupported image format: shape {img_array.shape}, "
                f"expected 2D grayscale, 3D with 1/3/4 channels"
            )

        # Simple resampling for PNG (could be improved with proper reprojection)
        src_height, src_width = img_array.shape[:2]

        # Calculate overlap region
        overlap_minx = max(tile_minx, src_minx)
        overlap_miny = max(tile_miny, src_miny)
        overlap_maxx = min(tile_maxx, src_maxx)
        overlap_maxy = min(tile_maxy, src_maxy)

        if overlap_minx >= overlap_maxx or overlap_miny >= overlap_maxy:
            return np.zeros((tile_size, tile_size, 4), dtype=np.uint8)

        # Map to tile coordinates
        tile_start_x = int(
            (overlap_minx - tile_minx) / (tile_maxx - tile_minx) * tile_size
        )
        tile_end_x = int(
            (overlap_maxx - tile_minx) / (tile_maxx - tile_minx) * tile_size
        )
        tile_start_y = int(
            (tile_maxy - overlap_maxy) / (tile_maxy - tile_miny) * tile_size
        )
        tile_end_y = int(
            (tile_maxy - overlap_miny) / (tile_maxy - tile_miny) * tile_size
        )

        # Map to source coordinates
        src_start_x = int((overlap_minx - src_minx) / (src_maxx - src_minx) * src_width)
        src_end_x = int((overlap_maxx - src_minx) / (src_maxx - src_minx) * src_width)
        src_start_y = int(
            (src_maxy - overlap_maxy) / (src_maxy - src_miny) * src_height
        )
        src_end_y = int((src_maxy - overlap_miny) / (src_maxy - src_miny) * src_height)

        # Create output tile
        rgba_tile = np.zeros((tile_size, tile_size, 4), dtype=np.uint8)

        # Simple nearest neighbor copy (could be improved)
        if (
            tile_end_x > tile_start_x
            and tile_end_y > tile_start_y
            and src_end_x > src_start_x
            and src_end_y > src_start_y
        ):

            # Resize source region to tile region
            src_region = img_array[src_start_y:src_end_y, src_start_x:src_end_x]
            if src_region.size > 0:
                src_img = Image.fromarray(src_region)
                tile_width = tile_end_x - tile_start_x
                tile_height = tile_end_y - tile_start_y

                if tile_width > 0 and tile_height > 0:
                    resized = src_img.resize((tile_width, tile_height), Image.LANCZOS)
                    resized_array = np.array(resized)

                    rgba_tile[tile_start_y:tile_end_y, tile_start_x:tile_end_x] = (
                        resized_array
                    )

    else:
        raise ValueError("Data must contain either 'grid' or 'png_bytes'")

    return rgba_tile


def encode_tile_png(
    rgba_array: np.ndarray, return_format: str = "bytes"
) -> Union[bytes, str, Image.Image]:
    """
    Encode RGBA array as PNG in the requested format.

    Args:
        rgba_array: RGBA array with shape (H, W, 4)
        return_format: "bytes", "base64", or "image"

    Returns:
        PNG data in requested format
    """
    if rgba_array.shape[2] != 4:
        raise ValueError(f"Expected RGBA array, got shape {rgba_array.shape}")

    img = Image.fromarray(rgba_array, mode="RGBA")

    if return_format == "image":
        return img
    elif return_format == "base64":
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        png_bytes = buffer.getvalue()
        return base64.b64encode(png_bytes).decode("utf-8")
    else:  # bytes
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()
