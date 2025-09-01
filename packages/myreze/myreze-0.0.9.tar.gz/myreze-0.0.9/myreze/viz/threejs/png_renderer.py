from myreze.viz.threejs.threejs import ThreeJSRenderer
from typing import Dict, Any, Optional, List, Union
import base64
import io
import numpy as np
from PIL import Image


@ThreeJSRenderer.register
class THREEPNGRenderer(ThreeJSRenderer):
    """Render PNG bytes for Three.js visualization.

    This renderer now accepts native resolution PNG data and interpolates it to the
    desired output resolution (default 2048x2048). This allows high-resolution
    datasets to be passed as MyrezeDataPackages and interpolated on-demand.
    """

    def render(
        self, data: Dict[str, Any], params: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        Render the data package as PNG bytes with interpolation.

        Args:
            data: Data dictionary containing base64-encoded PNG data
            params: Optional rendering parameters:
                - size: Output resolution as (width, height) tuple or int (default: 2048)
                - interpolation: Interpolation method - "bilinear", "nearest", "bicubic" (default: "bilinear")
                - format: Output format - "PNG", "JPEG" (default: "PNG")
                - quality: JPEG quality 1-100 (default: 95, only for JPEG)

        Returns:
            PNG image as bytes (interpolated to target resolution)
        """
        if params is None:
            params = {}

        # Extract base64-encoded PNG data from the data dictionary
        png_bytes_b64 = data.get("png_bytes")
        if png_bytes_b64 is None:
            raise ValueError("No 'png_bytes' data found in data dictionary")

        # Handle both single PNG and lists of PNGs
        if isinstance(png_bytes_b64, list):
            # For now, use the first PNG in the series
            # TODO: Could be extended to create animated PNG or multiple PNGs
            if len(png_bytes_b64) == 0:
                raise ValueError("Empty png_bytes list")
            png_data = png_bytes_b64[0]
        elif isinstance(png_bytes_b64, str):
            png_data = png_bytes_b64
        elif isinstance(png_bytes_b64, bytes):
            # Handle bytes for backwards compatibility - encode to base64 first
            png_data = base64.b64encode(png_bytes_b64).decode("utf-8")
        else:
            raise ValueError(
                f"png_bytes must be base64 string, bytes, or list, "
                f"got {type(png_bytes_b64)}"
            )

        # Decode base64 to bytes
        if isinstance(png_data, str):
            png_bytes = base64.b64decode(png_data)
        else:
            png_bytes = png_data

        # Get target size from parameters
        target_size = params.get("size", 2048)
        if isinstance(target_size, int):
            target_size = (target_size, target_size)  # Square output
        elif isinstance(target_size, (list, tuple)) and len(target_size) == 2:
            target_size = tuple(target_size)
        else:
            raise ValueError(
                f"Invalid size parameter: {target_size}. Expected int or (width, height) tuple."
            )

        target_width, target_height = target_size

        # Get interpolation method
        interpolation_method = params.get("interpolation", "bilinear")

        # Map interpolation methods to PIL resampling
        interpolation_map = {
            "nearest": Image.NEAREST,
            "bilinear": Image.BILINEAR,
            "bicubic": Image.BICUBIC,
            "lanczos": Image.LANCZOS,
        }

        if interpolation_method not in interpolation_map:
            raise ValueError(
                f"Unsupported interpolation method: {interpolation_method}. "
                f"Supported methods: {list(interpolation_map.keys())}"
            )

        pil_resample = interpolation_map[interpolation_method]

        # Get output format
        output_format = params.get("format", "PNG").upper()
        if output_format not in ["PNG", "JPEG", "JPG"]:
            raise ValueError(
                f"Unsupported output format: {output_format}. Supported: PNG, JPEG"
            )

        if output_format == "JPG":
            output_format = "JPEG"

        # Load the PNG image
        try:
            original_image = Image.open(io.BytesIO(png_bytes))
        except Exception as e:
            raise ValueError(f"Failed to load PNG image: {e}")

        # Get current dimensions
        current_width, current_height = original_image.size

        # Skip interpolation if already at target size
        if current_width == target_width and current_height == target_height:
            # Still need to re-encode in case format changed
            if output_format == "PNG":
                # Return original bytes if PNG and no size change
                return png_bytes
            else:
                # Convert to JPEG
                if original_image.mode in ("RGBA", "LA", "P"):
                    # Convert transparency to white background for JPEG
                    rgb_image = Image.new("RGB", original_image.size, (255, 255, 255))
                    if original_image.mode == "P":
                        original_image = original_image.convert("RGBA")
                    rgb_image.paste(
                        original_image,
                        mask=(
                            original_image.split()[-1]
                            if original_image.mode in ("RGBA", "LA")
                            else None
                        ),
                    )
                    original_image = rgb_image

                buffer = io.BytesIO()
                quality = params.get("quality", 95)
                original_image.save(buffer, format=output_format, quality=quality)
                return buffer.getvalue()

        # Perform interpolation
        interpolated_image = original_image.resize(
            (target_width, target_height), resample=pil_resample
        )

        # Handle format conversion
        if output_format == "JPEG" and interpolated_image.mode in ("RGBA", "LA", "P"):
            # Convert transparency to white background for JPEG
            rgb_image = Image.new("RGB", interpolated_image.size, (255, 255, 255))
            if interpolated_image.mode == "P":
                interpolated_image = interpolated_image.convert("RGBA")
            if interpolated_image.mode in ("RGBA", "LA"):
                rgb_image.paste(interpolated_image, mask=interpolated_image.split()[-1])
            else:
                rgb_image.paste(interpolated_image)
            interpolated_image = rgb_image

        # Encode the result
        buffer = io.BytesIO()
        if output_format == "PNG":
            interpolated_image.save(buffer, format="PNG")
        else:  # JPEG
            quality = params.get("quality", 95)
            interpolated_image.save(buffer, format="JPEG", quality=quality)

        return buffer.getvalue()


@ThreeJSRenderer.register
class THREEAnimatedPNGRenderer(ThreeJSRenderer):
    """
    Render a sequence of PNG images for Three.js visualization.

    This renderer handles animated data by processing a list of base64-encoded
    PNG images and returning them as a list of bytes objects, suitable for
    creating animations, time series visualizations, or multi-frame displays.

    ## Creating a Product with THREEAnimatedPNGRenderer

    To create a product that uses this renderer, you need to:

    1. **Prepare your data**: Convert your time series images to base64-encoded
       PNG format
    2. **Create the data package**: Structure your data with a 'png_bytes' key
       containing a list
    3. **Set up the renderer**: Use THREEAnimatedPNGRenderer in your
       MyrezeDataPackage
    4. **Configure visualization**: Set appropriate visualization_type and
       metadata

    ### Example Usage:

    ```python
    import base64
    from myreze.data import MyrezeDataPackage, Time
    from myreze.viz.threejs.png_renderer import THREEAnimatedPNGRenderer

    # Step 1: Prepare your PNG data (example with PIL)
    from PIL import Image
    import io

    def image_to_base64(image_array):
        # Convert numpy array or PIL image to base64 PNG
        if hasattr(image_array, 'shape'):  # numpy array
            image = Image.fromarray(image_array)
        else:
            image = image_array  # Already PIL Image

        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        png_bytes = buffer.getvalue()
        return base64.b64encode(png_bytes).decode('utf-8')

    # Step 2: Create list of base64-encoded PNGs
    png_frames = []
    for frame in your_time_series_data:  # list of images
        png_b64 = image_to_base64(frame)
        png_frames.append(png_b64)

    # Step 3: Create the data package
    data_package = MyrezeDataPackage(
        id="animated-weather-overlay",
        data={"png_bytes": png_frames},  # List of base64 PNG strings
        time=Time.series([
            "2023-01-01T00:00:00Z",
            "2023-01-01T01:00:00Z",
            "2023-01-01T02:00:00Z"
        ]),
        threejs_visualization=THREEAnimatedPNGRenderer(),
        visualization_type="animated_overlay",
        metadata={
            "description": "Animated weather radar sequence",
            "frame_rate": 2.0,  # frames per second
            "loop": True,
            "total_frames": len(png_frames)
        }
    )

    # Step 4: Render the animation
    png_sequence = data_package.to_threejs(params={})
    # Returns List[bytes] - each item is PNG image data

    # Step 5: Use in your application
    for i, png_bytes in enumerate(png_sequence):
        with open(f'frame_{i:03d}.png', 'wb') as f:
            f.write(png_bytes)
    ```

    ### Product Class Implementation:

    ```python
    from myreze.store.product import Product
    from myreze.data import MyrezeDataPackage, Time
    from myreze.viz.threejs.png_renderer import THREEAnimatedPNGRenderer

    class AnimatedWeatherProduct(Product):
        def __init__(self):
            super().__init__(
                product_id="animated-weather-radar",
                name="Animated Weather Radar",
                description="Time series weather radar imagery",
                source="NOAA",
                data_types=["radar", "precipitation"],
                spatial_coverage={"type": "bbox", "coordinates": [...]},
                temporal_coverage={"start": "2023-01-01", "end": "2023-12-31"},
                availability={"public": True},
                visualization_targets=["ThreeJS"],
                visualization_type="animated_overlay"
            )

        async def generate_package(
            self, spatial_region, temporal_region, visualization=None
        ):
            # Fetch your time series data for the given region/time
            time_series_data = await self.fetch_radar_data(
                spatial_region, temporal_region
            )

            # Convert to base64 PNG frames
            png_frames = []
            timestamps = []
            for timestamp, radar_data in time_series_data.items():
                png_frame = self.convert_radar_to_png(radar_data)
                png_b64 = base64.b64encode(png_frame).decode('utf-8')
                png_frames.append(png_b64)
                timestamps.append(timestamp)

            return MyrezeDataPackage(
                id=f"radar-{spatial_region['id']}-{temporal_region['start']}",
                data={"png_bytes": png_frames},
                time=Time.series(timestamps),
                threejs_visualization=THREEAnimatedPNGRenderer(),
                visualization_type="animated_overlay",
                metadata={
                    "frame_rate": 1.0,
                    "loop": True,
                    "total_frames": len(png_frames),
                    "spatial_bounds": spatial_region,
                    "temporal_bounds": temporal_region
                }
            )
    ```

    ### Data Structure Requirements:

    - **data['png_bytes']**: Must be a list of base64-encoded PNG strings
    - **time**: Should be Time.series() with timestamps matching frame count
    - **visualization_type**: Recommended values: "animated_overlay",
      "time_series", "sequence"
    - **metadata**: Include animation parameters like frame_rate, loop,
      total_frames

    ### Error Handling:

    The renderer will raise ValueError if:
    - No 'png_bytes' key found in data
    - 'png_bytes' is not a list
    - The list is empty
    - Any item in the list cannot be base64 decoded
    """

    def render(
        self, data: Dict[str, Any], params: Optional[Dict[str, Any]] = None
    ) -> List[bytes]:
        """
        Render the data package as a list of PNG bytes for animation.

        Args:
            data: Data dictionary containing base64-encoded PNG data list
            params: Optional rendering parameters (unused for PNG)

        Returns:
            List of PNG images as bytes, suitable for animation sequences

        Raises:
            ValueError: If png_bytes is missing, not a list, empty, or contains
                       invalid data
        """
        if params is None:
            params = {}

        # Extract base64-encoded PNG data from the data dictionary
        png_bytes_b64 = data.get("png_bytes")
        if png_bytes_b64 is None:
            raise ValueError("No 'png_bytes' data found in data dictionary")

        # Must be a list for animated renderer
        if not isinstance(png_bytes_b64, list):
            raise ValueError(
                f"THREEAnimatedPNGRenderer requires png_bytes to be a list, "
                f"got {type(png_bytes_b64)}. Use THREEPNGRenderer for single "
                f"images."
            )

        if len(png_bytes_b64) == 0:
            raise ValueError("Empty png_bytes list provided")

        # Decode all base64 strings to bytes
        png_frames = []
        for i, png_b64 in enumerate(png_bytes_b64):
            try:
                if isinstance(png_b64, str):
                    # Decode base64 string to bytes
                    png_bytes = base64.b64decode(png_b64)
                    png_frames.append(png_bytes)
                elif isinstance(png_b64, bytes):
                    # Handle bytes for backwards compatibility
                    png_frames.append(png_b64)
                else:
                    raise ValueError(
                        f"Frame {i}: png_bytes items must be base64 strings "
                        f"or bytes, got {type(png_b64)}"
                    )
            except Exception as e:
                raise ValueError(
                    f"Frame {i}: Failed to decode base64 PNG data: {str(e)}"
                )

        return png_frames


@ThreeJSRenderer.register
class PNGTexture(THREEPNGRenderer):
    """Alias for THREEPNGRenderer to match usage in NWSRadarProduct."""

    pass
