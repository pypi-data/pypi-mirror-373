"""
Myreze: A comprehensive toolkit for geospatial data packaging and visualization

Myreze provides a unified interface for creating, validating, and visualizing
geospatial data packages that can be rendered across multiple platforms
(Three.js, Unreal Engine, PNG exports).

## Core Components

### Data Layer (`myreze.data`)
- **MyrezeDataPackage**: Main container for geospatial data with time and
  visualization metadata
- **Time**: Flexible time representation (timestamps, spans, series)
- **Geometry**: Geometric data structures for spatial information
- **Validation**: Schema validation for data packages

### Visualization Layer (`myreze.viz`)
- **Renderers**: Platform-specific visualization generators
  - ThreeJSRenderer: Web-based 3D visualizations
  - UnrealRenderer: Unreal Engine visualizations
  - PNGRenderer: Static image exports
- **Visualization Types**: Semantic indicators for data interpretation

### Store Layer (`myreze.store`)
- **Products**: Data source abstractions with spatial/temporal coverage
- **Providers**: Product catalog management
- **Server**: HTTP API for data package requests

## Quick Start for LLM Agents

```python
# 1. Import core components
from myreze.data import MyrezeDataPackage, Time
from myreze.viz import ThreeJSRenderer

# 2. Create a data package
import numpy as np

data = {
    "grid": np.random.rand(100, 100),  # 2D data array
    "bounds": [-74.0, 40.7, -73.9, 40.8],  # [west, south, east, north]
    "units": "temperature_celsius"
}

package = MyrezeDataPackage(
    id="example-heatmap",
    data=data,
    time=Time.timestamp("2023-01-01T12:00:00Z"),
    threejs_visualization=ThreeJSRenderer(),
    visualization_type="heatmap",  # Critical: tells receivers how to
                                   # interpret data
    metadata={
        "description": "Temperature data for NYC area",
        "colormap": "viridis",
        "min_value": -10,
        "max_value": 35
    }
)

# 3. Export and use
json_output = package.to_json()  # For HTTP transfer
visualization = package.to_threejs(params={})  # For rendering
```

## Key Concepts for LLM Agents

### Visualization Types (Semantic Data Classification)
- `"flat_overlay"`: 2D map layers (weather overlays, satellite imagery)
- `"point_cloud"`: Scattered data points (sensor readings, weather stations)
- `"heatmap"`: Continuous surfaces (temperature, pressure fields)
- `"vector_field"`: Directional data (wind, ocean currents)
- `"terrain"`: 3D elevation/topographic data
- `"trajectory"`: Time-based paths (storm tracks, vehicle routes)
- `"contour"`: Isoline representations (pressure contours)

### Data Structure Patterns by Visualization Type

**Flat Overlay:**
```python
data = {
    "grid": np.array([[...]]),  # 2D array of values
    "bounds": [west, south, east, north],  # Geographic bounds
    "resolution": 0.01,  # Degrees per pixel
    "units": "measurement_unit"
}
```

**Point Cloud:**
```python
data = {
    "locations": [{"lat": 40.7, "lon": -74.0, "elevation": 10}, ...],
    "values": [25.3, 24.1, 26.2],  # Measurements at each location
    "point_ids": ["sensor_001", "sensor_002", ...]
}
```

**Vector Field:**
```python
data = {
    "grid_points": {"lats": [...], "lons": [...]},
    "u_component": np.array([[...]]),  # East-west vectors
    "v_component": np.array([[...]]),  # North-south vectors
    "magnitude": np.array([[...]])     # Vector magnitudes
}
```

### Time Patterns
```python
# Single moment
Time.timestamp("2023-01-01T12:00:00Z")

# Time range
Time.span("2023-01-01T00:00:00Z", "2023-01-02T00:00:00Z")

# Time series
Time.series(["2023-01-01T00:00:00Z", "2023-01-01T01:00:00Z", ...])
```

## Common Patterns for LLM Agents

### Creating Data Packages
1. **Determine visualization type** based on data structure and intended use
2. **Structure data dictionary** according to visualization type patterns
3. **Set appropriate metadata** for rendering hints (colormaps, scales, units)
4. **Choose renderer(s)** based on target platform
5. **Validate before use** (recommended for production)

### Processing Received Packages
1. **Check visualization_type** to understand data semantics
2. **Inspect metadata** for rendering parameters
3. **Access data dictionary** using expected structure for that visualization type
4. **Use appropriate renderer** or custom processing logic

### Error Handling
- Always validate visualization_type against known types
- Check data structure matches expected pattern for visualization_type
- Verify time format compliance (ISO 8601)
- Handle missing optional fields gracefully

## Module Discovery Methods
Use these methods to programmatically discover module capabilities:

```python
# Get available visualization types
from myreze.data.core import VISUALIZATION_TYPES
print(VISUALIZATION_TYPES)

# Get available renderers
from myreze.viz.threejs.threejs import ThreeJSRenderer
print(list(ThreeJSRenderer._registry.keys()))

# Get data schemas
from myreze.data.validate import get_schemas
schemas = get_schemas()
```
"""

__version__ = "0.1.0"

# Export main components for easy access
from myreze.data import MyrezeDataPackage, Time, Geometry
from myreze.viz import ThreeJSRenderer, UnrealRenderer, PNGRenderer, FlatOverlayRenderer

__all__ = [
    "MyrezeDataPackage",
    "Time",
    "Geometry",
    "ThreeJSRenderer",
    "UnrealRenderer",
    "PNGRenderer",
    "FlatOverlayRenderer",
]
