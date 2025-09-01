from myreze.viz.threejs.threejs import ThreeJSRenderer
from myreze.viz.threejs.trimesh_utilities import attach_texture_to_mesh
from typing import Dict, Any, Optional
import numpy as np
import trimesh
from PIL import Image


@ThreeJSRenderer.register
class FlatOverlayRenderer(ThreeJSRenderer):
    """Render a flat overlay."""

    def render(
        self, data: "MyrezeDataPackage", params: Optional[Dict[str, Any]] = None
    ) -> str:
        """Render the data package as a Three.js object."""

        texture = np.array(data)

        return texture  # plane.export(file_type="glb")


@ThreeJSRenderer.register
class Planar4channelTextureRenderer(ThreeJSRenderer):
    """Render a flat overlay with a 4 channel texture.

    This renderer now accepts native resolution data and interpolates it to the
    desired output resolution (default 2048x2048). This allows high-resolution
    datasets to be passed as MyrezeDataPackages and interpolated on-demand.
    """

    def render(
        self, data: "MyrezeDataPackage", params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Render the data package as a Three.js texture with interpolation.

        Args:
            data: Data dictionary containing texture data
            params: Optional rendering parameters:
                - size: Output resolution as (width, height) tuple or int (default: 2048)
                - interpolation: Interpolation method - "bilinear", "nearest", "bicubic" (default: "bilinear")

        Returns:
            Interpolated texture array with shape (height, width, channels)
        """
        if params is None:
            params = {}

        # Extract texture data
        texture = np.array(data["texture"])

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

        # Handle different input formats
        if texture.ndim == 2:
            # Single channel - convert to RGBA
            texture = np.stack(
                [texture, texture, texture, np.full_like(texture, 255)], axis=-1
            )
        elif texture.ndim == 3:
            if texture.shape[2] == 1:
                # Single channel with explicit dimension
                single_channel = texture[:, :, 0]
                texture = np.stack(
                    [
                        single_channel,
                        single_channel,
                        single_channel,
                        np.full_like(single_channel, 255),
                    ],
                    axis=-1,
                )
            elif texture.shape[2] == 3:
                # RGB - add alpha channel
                alpha = np.full(
                    (texture.shape[0], texture.shape[1], 1), 255, dtype=texture.dtype
                )
                texture = np.concatenate([texture, alpha], axis=-1)
            elif texture.shape[2] == 4:
                # Already RGBA - use as is
                pass
            else:
                raise ValueError(f"Unsupported texture format: {texture.shape}")
        else:
            raise ValueError(f"Unsupported texture dimensions: {texture.shape}")

        # Get current dimensions
        current_height, current_width = texture.shape[:2]

        # Skip interpolation if already at target size
        if current_width == target_width and current_height == target_height:
            return texture

        # Convert to PIL Image for interpolation
        # Ensure data is in uint8 format
        if texture.dtype != np.uint8:
            if texture.dtype in [np.float32, np.float64]:
                # Assume float data is in [0, 1] range
                texture = (texture * 255).astype(np.uint8)
            else:
                # Convert other integer types
                texture = texture.astype(np.uint8)

        # Create PIL Image
        if texture.shape[2] == 4:
            pil_image = Image.fromarray(texture, mode="RGBA")
        elif texture.shape[2] == 3:
            pil_image = Image.fromarray(texture, mode="RGB")
        else:
            raise ValueError(f"Unsupported number of channels: {texture.shape[2]}")

        # Perform interpolation
        interpolated_image = pil_image.resize(
            (target_width, target_height), resample=pil_resample
        )

        # Convert back to numpy array
        interpolated_texture = np.array(interpolated_image)

        # Ensure 4-channel output for consistency
        if interpolated_texture.shape[2] == 3:
            alpha = np.full((target_height, target_width, 1), 255, dtype=np.uint8)
            interpolated_texture = np.concatenate(
                [interpolated_texture, alpha], axis=-1
            )

        return interpolated_texture


@ThreeJSRenderer.register
class DummyRenderer(ThreeJSRenderer):
    """Render a flat overlay with a 4 channel texture."""

    def render(
        self, data: "MyrezeDataPackage", params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Render the data package as a Three.js object."""

        texture = np.random.uniform(0, 1, (256, 256)).astype(np.float32)

        # Create a 2d horizontal GLB plane with alpha channel texture
        plane = trimesh.Trimesh(
            vertices=np.array([[0, 0, 0], [1, 0, 0], [0, 0, 1], [1, 0, 1]]),
            faces=np.array([[2, 1, 0], [3, 1, 2]]),
        )
        plane = attach_texture_to_mesh(plane, texture)

        return texture  # plane.export(file_type="glb")
