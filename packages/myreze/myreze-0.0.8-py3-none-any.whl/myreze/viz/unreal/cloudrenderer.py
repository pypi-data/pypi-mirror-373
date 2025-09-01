from myreze.viz.unreal.unreal import UnrealRenderer
from typing import Dict, Any, Optional

import numpy as np
from matplotlib.colors import LinearSegmentedColormap


MONO_BLUE_COLORS = [
    "#0A1931",  # Almost black blue (extremely cold)
    "#10305A",  # Very dark blue (very cold)
    "#134074",  # Dark navy (cold)
    "#13618C",  # Medium navy (moderately cold)
    "#1C89B8",  # Medium blue (cool)
    "#42A5C6",  # Medium-light blue (slightly cool)
    "#6BBDD0",  # Light blue (mild cool)
    "#97D0DD",  # Very light blue (minimal cool)
    "#C6E1E9",  # Pale blue (near neutral)
    "#EDF5F7",  # Almost white blue (neutral)
]


@UnrealRenderer.register
class CloudRenderer(UnrealRenderer):
    """Render a CloudRenderer object."""

    def render(
        self, data: "MyrezeDataPackage", params: Optional[Dict[str, Any]] = None
    ) -> str:
        """Render the data package as a Unreal Engine object."""

        # Parameters ------------
        COLORMAP = MONO_BLUE_COLORS
        # ------------------------

        # Colorize data
        cmap = LinearSegmentedColormap.from_list("custom_temp", COLORMAP)
        rgba = cmap(data.get("grid"))

        # Alpha
        alpha = data.get("grid")
        rgba[:, :, 3] = alpha

        rgba_uint8 = (rgba * 255).astype(np.uint8)

        return rgba_uint8
