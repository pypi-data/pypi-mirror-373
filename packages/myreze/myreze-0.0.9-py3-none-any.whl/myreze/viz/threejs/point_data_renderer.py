from myreze.viz.threejs.threejs import ThreeJSRenderer
from typing import Dict, Any, Optional, List, Union
import re
import json


@ThreeJSRenderer.register
class PointDataRenderer(ThreeJSRenderer):
    """
    Render point-based data with location-specific SVG visualizations.

    This renderer processes point data organized by location, generating customized
    SVG files for each location using template substitution. It's designed for
    scenarios where you have discrete measurement points (weather stations, sensors,
    monitoring sites) that need individualized visual representations.

    ## Data Structure Requirements

    The renderer expects data structured with locations as top-level keys, where
    each location contains measurements, SVG templates, and metadata:

    ```python
    data = {
        "location_id_1": {
            "measurements": {
                "temperature": 25.3,
                "humidity": 65.2,
                "pressure": 1013.2
            },
            "svg_template": "<svg>...{temperature}...{humidity}...</svg>",
            "metadata": {
                "station_name": "Central Park",
                "coordinates": {"lat": 40.7829, "lon": -73.9654},
                "elevation": 42
            }
        },
        "location_id_2": {
            # Similar structure...
        }
    }
    ```

    ## Template Processing

    SVG templates support Python string formatting with keys from measurements
    and metadata. The renderer will substitute placeholders like `{temperature}`,
    `{station_name}`, etc. with actual values.

    ### Template Example:
    ```svg
    <svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
        <circle cx="50" cy="50" r="{radius}" fill="red"/>
        <text x="50" y="80" text-anchor="middle">{temperature}°C</text>
        <title>{station_name}</title>
    </svg>
    ```

    ## Creating a Product with PointDataRenderer

    ### Example Usage:

    ```python
    from myreze.data import MyrezeDataPackage, Time
    from myreze.viz.threejs.point_data_renderer import PointDataRenderer

    # Step 1: Prepare your point data
    weather_stations = {
        "NYC_001": {
            "measurements": {
                "temperature": 22.5,
                "humidity": 58.3,
                "wind_speed": 12.1
            },
            "svg_template": '''
                <svg width="120" height="80" xmlns="http://www.w3.org/2000/svg">
                    <rect width="120" height="80" fill="#f0f8ff" stroke="#333" stroke-width="2"/>
                    <text x="60" y="25" text-anchor="middle" font-size="14">{station_name}</text>
                    <text x="60" y="45" text-anchor="middle" font-size="12">{temperature}°C</text>
                    <text x="60" y="60" text-anchor="middle" font-size="10">{humidity}% RH</text>
                </svg>
            ''',
            "metadata": {
                "station_name": "Central Park",
                "coordinates": {"lat": 40.7829, "lon": -73.9654},
                "station_type": "urban"
            }
        },
        "NYC_002": {
            "measurements": {
                "temperature": 24.1,
                "humidity": 62.7,
                "wind_speed": 8.3
            },
            "svg_template": '''
                <svg width="120" height="80" xmlns="http://www.w3.org/2000/svg">
                    <rect width="120" height="80" fill="#f0fff0" stroke="#333" stroke-width="2"/>
                    <text x="60" y="25" text-anchor="middle" font-size="14">{station_name}</text>
                    <text x="60" y="45" text-anchor="middle" font-size="12">{temperature}°C</text>
                    <text x="60" y="60" text-anchor="middle" font-size="10">{humidity}% RH</text>
                </svg>
            ''',
            "metadata": {
                "station_name": "Battery Park",
                "coordinates": {"lat": 40.7033, "lon": -74.0170},
                "station_type": "coastal"
            }
        }
    }

    # Step 2: Create the data package
    data_package = MyrezeDataPackage(
        id="weather-stations-svg",
        data=weather_stations,
        time=Time.timestamp("2023-07-15T14:30:00Z"),
        threejs_visualization=PointDataRenderer(),
        visualization_type="point_data_svg",
        metadata={
            "description": "Weather station data with custom SVG visualizations",
            "total_stations": len(weather_stations),
            "region": "New York City"
        }
    )

    # Step 3: Render the SVG files
    svg_outputs = data_package.to_threejs(params={})
    # Returns Dict[str, str] - location IDs mapped to SVG strings

    # Step 4: Use the generated SVGs
    for location_id, svg_content in svg_outputs.items():
        with open(f'{location_id}_visualization.svg', 'w') as f:
            f.write(svg_content)
    ```

    ### Product Class Implementation:

    ```python
    from myreze.store.product import Product
    from myreze.data import MyrezeDataPackage, Time
    from myreze.viz.threejs.point_data_renderer import PointDataRenderer

    class WeatherStationProduct(Product):
        def __init__(self):
            super().__init__(
                product_id="weather-stations-svg",
                name="Weather Station SVG Visualizations",
                description="Real-time weather data with custom SVG displays",
                source="National Weather Service",
                data_types=["weather", "point_measurements"],
                spatial_coverage={"type": "points", "coordinates": [...]},
                temporal_coverage={"start": "2023-01-01", "end": "2023-12-31"},
                availability={"public": True},
                visualization_targets=["ThreeJS"],
                visualization_type="point_data_svg"
            )

        async def generate_package(
            self, spatial_region, temporal_region, visualization=None
        ):
            # Fetch weather station data for the given region/time
            stations_data = await self.fetch_station_data(
                spatial_region, temporal_region
            )

            # Create location-based data structure
            formatted_data = {}
            for station in stations_data:
                station_id = station['id']
                formatted_data[station_id] = {
                    "measurements": {
                        "temperature": station['temperature'],
                        "humidity": station['humidity'],
                        "pressure": station['pressure'],
                        "wind_speed": station['wind_speed']
                    },
                    "svg_template": self.get_station_template(station['type']),
                    "metadata": {
                        "station_name": station['name'],
                        "coordinates": {
                            "lat": station['latitude'],
                            "lon": station['longitude']
                        },
                        "elevation": station['elevation'],
                        "station_type": station['type']
                    }
                }

            return MyrezeDataPackage(
                id=f"stations-{spatial_region['id']}-{temporal_region['start']}",
                data=formatted_data,
                time=Time.timestamp(temporal_region['start']),
                threejs_visualization=PointDataRenderer(),
                visualization_type="point_data_svg",
                metadata={
                    "region_bounds": spatial_region,
                    "temporal_bounds": temporal_region,
                    "total_stations": len(formatted_data)
                }
            )
    ```

    ### Advanced Template Features:

    The renderer supports advanced template substitution including:

    1. **Conditional formatting**: Use Python string methods
    2. **Calculated values**: Derive values from measurements
    3. **Nested data access**: Access nested metadata fields

    ```python
    # Example with calculated values and conditionals
    advanced_template = '''
    <svg width="150" height="100" xmlns="http://www.w3.org/2000/svg">
        <rect width="150" height="100" fill="{bg_color}" stroke="#333"/>
        <text x="75" y="30" text-anchor="middle">{station_name}</text>
        <text x="75" y="50" text-anchor="middle">{temperature}°C</text>
        <text x="75" y="70" text-anchor="middle">Comfort: {comfort_level}</text>
    </svg>
    '''

    # The renderer can handle calculated fields passed in measurements:
    measurements = {
        "temperature": 25.5,
        "humidity": 60.0,
        "bg_color": "#ffeecc" if temperature > 20 else "#ccddff",
        "comfort_level": "Good" if 18 <= temperature <= 26 else "Poor"
    }
    ```

    ## Error Handling

    The renderer provides comprehensive error handling and will raise ValueError for:
    - Missing required data structure elements
    - Invalid SVG template syntax
    - Template substitution failures
    - Missing measurement or metadata keys referenced in templates

    ## Parameters

    The render method accepts optional parameters:

    - **template_validation** (bool): Validate SVG templates before processing (default: True)
    - **error_handling** (str): How to handle template errors ('strict', 'skip', 'placeholder')
    - **encoding** (str): Output encoding for SVG strings (default: 'utf-8')
    """

    def render(
        self, data: Dict[str, Any], params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        Render point data as location-specific SVG visualizations.

        Args:
            data: Dictionary with location IDs as keys, each containing:
                  - measurements: Dict of measurement values
                  - svg_template: SVG template string with placeholders
                  - metadata: Additional metadata for template substitution
            params: Optional rendering parameters:
                   - template_validation (bool): Validate templates (default: True)
                   - error_handling (str): Error handling mode (default: 'strict')
                   - encoding (str): Output encoding (default: 'utf-8')

        Returns:
            Dictionary mapping location IDs to rendered SVG strings

        Raises:
            ValueError: If required data structure is missing or invalid
            KeyError: If template references missing measurement/metadata keys
        """
        if params is None:
            params = {}

        # Extract parameters
        template_validation = params.get("template_validation", True)
        error_handling = params.get("error_handling", "strict")
        encoding = params.get("encoding", "utf-8")

        if not isinstance(data, dict):
            raise ValueError(
                f"PointDataRenderer requires data to be a dictionary with "
                f"location IDs as keys, got {type(data)}"
            )

        if len(data) == 0:
            raise ValueError("Empty data dictionary provided")

        rendered_svgs = {}

        for location_id, location_data in data.items():
            try:
                svg_content = self._render_location_svg(
                    location_id, location_data, template_validation, error_handling
                )
                rendered_svgs[location_id] = svg_content

            except Exception as e:
                if error_handling == "strict":
                    raise ValueError(
                        f"Failed to render SVG for location '{location_id}': {str(e)}"
                    )
                elif error_handling == "skip":
                    continue  # Skip this location
                elif error_handling == "placeholder":
                    rendered_svgs[location_id] = self._create_error_svg(
                        location_id, str(e)
                    )
                else:
                    raise ValueError(f"Unknown error_handling mode: {error_handling}")

        return rendered_svgs

    def _render_location_svg(
        self,
        location_id: str,
        location_data: Dict[str, Any],
        template_validation: bool,
        error_handling: str,
    ) -> str:
        """
        Render SVG for a single location.

        Args:
            location_id: Unique identifier for the location
            location_data: Data dictionary for this location
            template_validation: Whether to validate template syntax
            error_handling: Error handling mode

        Returns:
            Rendered SVG string for this location

        Raises:
            KeyError: If required fields are missing
            ValueError: If template processing fails
        """
        # Validate required structure
        required_fields = ["measurements", "svg_template"]
        for field in required_fields:
            if field not in location_data:
                raise KeyError(
                    f"Location '{location_id}' missing required field: '{field}'"
                )

        measurements = location_data["measurements"]
        svg_template = location_data["svg_template"]
        metadata = location_data.get("metadata", {})

        # Validate that measurements and metadata are dictionaries
        if not isinstance(measurements, dict):
            raise ValueError(
                f"Location '{location_id}': measurements must be a dictionary, "
                f"got {type(measurements)}"
            )

        if not isinstance(metadata, dict):
            raise ValueError(
                f"Location '{location_id}': metadata must be a dictionary, "
                f"got {type(metadata)}"
            )

        # Create combined substitution dictionary
        # Metadata can override measurements if there are key conflicts
        substitution_vars = {**measurements, **metadata}

        # Add location_id as a special variable
        substitution_vars["location_id"] = location_id

        # Validate template if requested
        if template_validation:
            self._validate_svg_template(svg_template, location_id)

        # Perform template substitution
        try:
            rendered_svg = svg_template.format(**substitution_vars)
        except KeyError as e:
            missing_key = str(e).strip("'")
            available_keys = list(substitution_vars.keys())
            raise KeyError(
                f"Location '{location_id}': Template references undefined key "
                f"'{missing_key}'. Available keys: {available_keys}"
            )
        except ValueError as e:
            raise ValueError(
                f"Location '{location_id}': Template formatting error: {str(e)}"
            )

        return rendered_svg

    def _validate_svg_template(self, svg_template: str, location_id: str) -> None:
        """
        Validate basic SVG template syntax.

        Args:
            svg_template: SVG template string to validate
            location_id: Location ID for error messages

        Raises:
            ValueError: If template has invalid syntax
        """
        if not isinstance(svg_template, str):
            raise ValueError(
                f"Location '{location_id}': svg_template must be a string, "
                f"got {type(svg_template)}"
            )

        if not svg_template.strip():
            raise ValueError(f"Location '{location_id}': svg_template cannot be empty")

        # Basic SVG validation - check for svg tags
        if "<svg" not in svg_template.lower():
            raise ValueError(
                f"Location '{location_id}': svg_template must contain <svg> element"
            )

        if "</svg>" not in svg_template.lower():
            raise ValueError(
                f"Location '{location_id}': svg_template must have closing </svg> tag"
            )

        # Check for balanced braces in template placeholders
        brace_count = svg_template.count("{") - svg_template.count("}")
        if brace_count != 0:
            raise ValueError(
                f"Location '{location_id}': svg_template has unbalanced template "
                f"braces {{ }}. Found {svg_template.count('{')} opening and "
                f"{svg_template.count('}')} closing braces."
            )

    def _create_error_svg(self, location_id: str, error_message: str) -> str:
        """
        Create a placeholder SVG when template processing fails.

        Args:
            location_id: Location ID for the error
            error_message: Error description

        Returns:
            Simple error SVG string
        """
        return f"""
        <svg width="200" height="100" xmlns="http://www.w3.org/2000/svg">
            <rect width="200" height="100" fill="#ffeeee" stroke="#ff0000" stroke-width="2"/>
            <text x="100" y="30" text-anchor="middle" font-size="12" fill="#cc0000">
                Error: {location_id}
            </text>
            <text x="100" y="50" text-anchor="middle" font-size="10" fill="#666666">
                Template processing failed
            </text>
            <text x="100" y="70" text-anchor="middle" font-size="8" fill="#999999">
                {error_message[:50]}...
            </text>
        </svg>
        """.strip()
