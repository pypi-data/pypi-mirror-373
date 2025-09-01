# Myreze

Myreze is a data passing, processing and visualization toolkit for handling geospatial data and rendering it through different visualization engines. It provides a unified interface for managing, validating, and visualizing geospatial data with time components. The packages are designed to be versatile enough to represent a wide range of data and visualization options, encode semantic information for agentic LLM systems, while being serializeable so it can be passed as a response to a HTTP request.

**Enhanced with AI Integration**: Myreze includes extended AI-generated docstrings and intelligent data validation to simplify integration with AI agents and automated workflows.

## Installation

```bash
pip install -e .
```

## Core Concepts

Myreze is built around these core concepts:

- **Data Packages**: Container for geospatial data with time information
- **Time**: Flexible time representation (timestamps, spans, series)
- **Stores & Products**: Data distribution system for creating and serving data packages
- **Renderers**: Visualization schemas for different platforms (might choose a different name for these in the future)
- **Visualization Types**: Metadata indicating how data should be interpreted and rendered
- **Agent Context**: Extendable metadata for LLM-based interpretation

## Quick Start

### Creating Your First Data Package

```python
from myreze.data import MyrezeDataPackage, Time
import numpy as np

# Create time information
time_data = Time.timestamp("2023-01-01T12:00:00Z")

# Create a simple weather data package
weather_data = {
    "grid": np.random.rand(50, 50),  # Temperature values
    "bounds": [-74.0, 40.7, -73.9, 40.8],  # NYC area [west, south, east, north]
    "units": "celsius"
}

data_package = MyrezeDataPackage(
    id="my-weather-data",
    data=weather_data,
    time=time_data,
    visualization_type="heatmap",  # Tells receivers how to visualize this data
    metadata={
        "description": "Temperature data for NYC area",
        "source": "weather_station"
    }
)

# Export to JSON for sharing
json_data = data_package.to_json()
print(f"Created package: {data_package.id}")
```

## Understanding Visualization Types

The `visualization_type` field is crucial - it tells anyone receiving your data package how to interpret and visualize it. Think of it as instructions for the visualization engine.

### Common Visualization Types

| Type             | Use Case                         | Data Structure        |
| ---------------- | -------------------------------- | --------------------- |
| `"flat_overlay"` | Weather radar, satellite imagery | 2D grid or image data |
| `"png_overlay"`  | -                                | -                     |

### Example: Weather Radar Overlay

```python
# Weather radar data showing precipitation across a region
import numpy as np

radar_data = {
    "grid": np.random.rand(100, 100),  # Precipitation intensity (0-1)
    "bounds": [-74.5, 40.5, -73.5, 41.0],  # NYC area [west, south, east, north]
    "resolution": 0.01,  # degrees per grid cell
    "units": "mm/hour"
}

radar_package = MyrezeDataPackage(
    id="precipitation-radar",
    data=radar_data,
    time=Time.timestamp("2023-06-15T14:30:00Z"),
    visualization_type="flat_overlay",  # 2D map overlay
    metadata={
        "parameter": "precipitation_intensity",
        "colormap": "blues",
        "opacity": 0.7,
        "data_source": "weather_radar"
    }
)
```

## Creating Data Stores and Products

Myreze includes a system for creating data services that can generate and serve data packages on demand.

### Basic Store Setup

```python
from myreze.store.product import Product
from myreze.store.provider import ProductProvider
from myreze.store.server import StoreServer
from myreze.data import MyrezeDataPackage, Time
import numpy as np

class WeatherProduct(Product):
    """A product that generates weather data on demand."""
    
    async def generate_package(self, spatial_region, temporal_region, visualization=None):
        # Generate or fetch data based on the requested region
        weather_data = {
            "grid": np.random.rand(100, 100) * 30,  # Temperature 0-30°C
            "bounds": spatial_region["coordinates"],
            "units": "celsius"
        }
        
        return MyrezeDataPackage(
            id=f"weather-{temporal_region['value']}",
            data=weather_data,
            time=Time.from_dict(temporal_region),
            visualization_type="heatmap",
            metadata={"generated_at": "2023-01-01T12:00:00Z"}
        )

class MyWeatherProvider(ProductProvider):
    """Provider offering weather products."""
    
    async def get_products(self):
        return [
            WeatherProduct(
                product_id="current-weather",
                name="Current Weather Data",
                description="Real-time temperature and precipitation data",
                spatial_coverage={
                    "type": "BoundingBox",
                    "coordinates": [[-180, -90], [180, 90]]
                },
                visualization_type="heatmap"
            )
        ]

# Start the server
provider = MyWeatherProvider()
server = StoreServer(provider)
server.run()  # Runs on http://localhost:8000
```

### Using the Store API

Once your store is running, clients can discover and order data:

```bash
# List available products
curl http://localhost:8000/products

# Order specific data
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "current-weather",
    "spatial_region": {
      "type": "BoundingBox", 
      "coordinates": [[-74.1, 40.6], [-73.9, 40.9]]
    },
    "temporal_region": {
      "type": "Timestamp", 
      "value": "2023-01-01T12:00:00Z"
    }
  }'
```

You can test these enpoints in your browser when running the server (try it!).

## Visualization with Different Engines

Ideally, we'd like to accomodate various rendering environments, but for now we are focusing on Unreal and ThreeJS.

### Three.js (Web Visualization)

```python
from myreze.viz import ThreeJSRenderer

# Add Three.js visualization to your package
data_package = MyrezeDataPackage(
    id="web-viz-example",
    data=your_data,
    time=your_time,
    threejs_visualization=ThreeJSRenderer(),
    visualization_type="heatmap"
)

# Generate web-ready visualization
web_viz = data_package.to_threejs()
```

### Unreal Engine (3D Visualization)

```python
from myreze.viz import UnrealRenderer

# Add Unreal Engine visualization
data_package = MyrezeDataPackage(
    id="3d-viz-example",
    data=terrain_data,
    time=your_time,
    unreal_visualization=UnrealRenderer(),
    visualization_type="terrain"
)

# Generate 3D visualization
unreal_viz = data_package.to_unreal(params={"quality": "high"})
```

## Time Handling Made Simple

Myreze supports three types of time representations:

```python
from myreze.data import Time

# Single point in time
timestamp = Time.timestamp("2023-01-01T12:00:00Z")

# Time range
timespan = Time.span("2023-01-01T00:00:00Z", "2023-01-02T00:00:00Z")

# Multiple time points (for time series data)
timeseries = Time.series([
    "2023-01-01T00:00:00Z",
    "2023-01-01T01:00:00Z",
    "2023-01-01T02:00:00Z"
])
```

## Package Components

- **myreze.data**: Core data structures and validation
- **myreze.store**: Data distribution system (products, providers, servers)
- **myreze.viz**: Visualization renderers for various platforms
  - **threejs**: Web-based 3D visualizations
  - **unreal**: Unreal Engine visualizations
  - **png**: Static image export

## Data Conventions

For consistency across all Myreze packages, follow these conventions:

- **Coordinate System and projection**: Use EPSG:4326 for geolocations. 
- **Orientation**: Let the Y component point up in returned geometries

## AI Integration Features

Myreze is enhanced with intelligent features for AI workflows:

- **Extended Docstrings**: All classes and methods include comprehensive AI-generated documentation. Try typing help(...) on any part of the module when having it loaded in IPython.
- **Smart Validation**: Automatic data structure validation with helpful error messages
- **Type Discovery**: Built-in methods to discover available visualization types and requirements
- **Schema Information**: Programmatic access to data structure requirements

```python
# Discover available visualization types
viz_types = MyrezeDataPackage.get_available_visualization_types()

# Get schema requirements for a specific type
schema_info = package.get_schema_info()
```

## Development

### Update PyPI 

(this is mostly for Audun)

```shell
python -m build
python -m twine upload dist/*
```

## Dependencies

Check `pyproject.toml`

## Documentation

See the [API documentation](docs/api.md) and [tutorial](docs/tutorial.md) for more information.

## Examples

Check out the `examples/` directory for complete working examples:

- `create_data_package.py`: Comprehensive data package examples
- `create_store.py`: Setting up data stores and products
- `enhanced_demo.py`: Advanced features demonstration
