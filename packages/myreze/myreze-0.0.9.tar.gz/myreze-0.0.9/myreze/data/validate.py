"""
Validation schemas and functions for MyrezeDataPackage.

This module provides comprehensive validation for data packages, including
schema definitions that LLM agents can use to understand expected data
structures for different visualization types.
"""

from typing import Dict, Any, List
import numpy as np
import isodate


# Schema definitions for LLM agent discovery
MDP_BASE_SCHEMA = {
    "type": "object",
    "required": ["version", "type", "id", "data", "time"],
    "properties": {
        "version": {"type": "string", "pattern": r"^\d+\.\d+\.\d+$"},
        "type": {"type": "string", "enum": ["MyrezeDataPackage"]},
        "id": {"type": "string", "minLength": 1},
        "data": {"type": "object"},
        "time": {
            "type": "object",
            "required": ["type", "value"],
            "properties": {
                "type": {"type": "string", "enum": ["Timestamp", "Span", "Series"]}
            },
        },
        "visualization_type": {"type": "string"},
        "metadata": {"type": "object"},
        "unreal_visualization": {"type": ["object", "null"]},
        "threejs_visualization": {"type": ["object", "null"]},
    },
}

VISUALIZATION_DATA_SCHEMAS = {
    "flat_overlay": {
        "description": "2D map overlays like weather maps, satellite imagery",
        "required_fields": ["grid", "bounds"],
        "optional_fields": ["resolution", "units", "colormap", "opacity"],
        "field_specifications": {
            "grid": {
                "type": "2D array",
                "description": "2D numpy array or nested list of scalar values",
                "format": "array[height][width] of numbers",
            },
            "bounds": {
                "type": "array",
                "description": "Geographic bounding box",
                "format": "[west, south, east, north] in degrees",
                "example": "[-74.0, 40.7, -73.9, 40.8]",
            },
            "resolution": {
                "type": "number",
                "description": "Spatial resolution in degrees per pixel",
                "example": "0.01",
            },
            "units": {
                "type": "string",
                "description": "Physical units of the data values",
                "example": "celsius, meters, percentage",
            },
        },
    },
    "point_cloud": {
        "description": "Discrete data points like sensor readings, weather stations",
        "required_fields": ["locations", "values"],
        "optional_fields": ["point_ids", "colors", "sizes", "timestamps"],
        "field_specifications": {
            "locations": {
                "type": "array of objects",
                "description": "Geographic locations of data points",
                "format": "[{lat: float, lon: float, elevation?: float}, ...]",
                "example": '[{"lat": 40.7, "lon": -74.0, "elevation": 10}]',
            },
            "values": {
                "type": "array",
                "description": "Measurement values at each location",
                "format": "Array of numbers matching locations length",
                "example": "[25.3, 24.1, 26.2]",
            },
            "point_ids": {
                "type": "array of strings",
                "description": "Unique identifiers for each point",
                "example": '["sensor_001", "sensor_002"]',
            },
        },
    },
    "heatmap": {
        "description": "Continuous surfaces like temperature, pressure fields",
        "required_fields": ["grid", "bounds"],
        "optional_fields": ["values_range", "colormap", "opacity", "interpolation"],
        "field_specifications": {
            "grid": {
                "type": "2D array",
                "description": "2D array of continuous scalar values",
                "format": "array[height][width] of numbers",
            },
            "bounds": {
                "type": "array",
                "description": "Geographic bounding box",
                "format": "[west, south, east, north] in degrees",
            },
            "values_range": {
                "type": "array",
                "description": "Min and max values for color scaling",
                "format": "[min_value, max_value]",
                "example": "[0, 100]",
            },
        },
    },
    "vector_field": {
        "description": "Directional data like wind, ocean currents",
        "required_fields": ["grid_points", "u_component", "v_component"],
        "optional_fields": ["magnitude", "arrow_scale", "color_by"],
        "field_specifications": {
            "grid_points": {
                "type": "object",
                "description": "Grid coordinate arrays",
                "format": '{"lats": [...], "lons": [...]}',
                "example": '{"lats": [40.0, 40.1, 40.2], "lons": [-74.0, -73.9, -73.8]}',
            },
            "u_component": {
                "type": "2D array",
                "description": "East-west component of vectors",
                "format": "2D array matching grid dimensions",
            },
            "v_component": {
                "type": "2D array",
                "description": "North-south component of vectors",
                "format": "2D array matching grid dimensions",
            },
        },
    },
    "point_data_svg": {
        "description": "Location-based data with custom SVG visualizations",
        "required_fields": ["location-based structure"],
        "optional_fields": ["metadata per location"],
        "field_specifications": {
            "location_id": {
                "type": "object",
                "description": (
                    "Each location contains measurements, templates, metadata"
                ),
                "format": (
                    '{"measurements": {...}, "svg_template": "...", "metadata": {...}}'
                ),
                "example": (
                    '{"measurements": {"temp": 25.0}, "svg_template": '
                    '"<svg>...</svg>", "metadata": {"name": "Station 1"}}'
                ),
            },
            "measurements": {
                "type": "object",
                "description": "Measurement values for template substitution",
                "format": "Dictionary of measurement keys and values",
                "example": '{"temperature": 25.0, "humidity": 60.0}',
            },
            "svg_template": {
                "type": "string",
                "description": "SVG template with placeholder variables",
                "format": "SVG string with {variable} placeholders",
                "example": '"<svg><text>{temperature}°C</text></svg>"',
            },
            "metadata": {
                "type": "object",
                "description": "Additional metadata for template substitution",
                "format": "Dictionary of metadata keys and values",
                "example": '{"station_name": "Central Park", "coordinates": {...}}',
            },
        },
    },
}


def validate_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    """
    Validate data against a JSON schema-like structure.

    This is a simplified validator focusing on the most common validation
    needs for MyrezeDataPackage. For production use, consider using
    a full JSON schema validation library.

    Args:
        data: Data dictionary to validate
        schema: Schema definition dictionary

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    # Check required fields
    required = schema.get("required", [])
    for field in required:
        if field not in data:
            errors.append(f"Required field '{field}' is missing")

    # Check field types and values
    properties = schema.get("properties", {})
    for field, field_schema in properties.items():
        if field in data:
            value = data[field]
            expected_type = field_schema.get("type")

            if expected_type == "string" and not isinstance(value, str):
                errors.append(f"Field '{field}' must be a string")
            elif expected_type == "object" and not isinstance(value, dict):
                errors.append(f"Field '{field}' must be an object")
            elif expected_type == "array" and not isinstance(value, list):
                errors.append(f"Field '{field}' must be an array")

            # Check enum values
            if "enum" in field_schema and value not in field_schema["enum"]:
                errors.append(f"Field '{field}' must be one of {field_schema['enum']}")

    return errors


def validate_mdp(data: Dict[str, Any]) -> None:
    """
    Validate a MyrezeDataPackage against the MDP schema.

    Args:
        data: Dictionary representation of MyrezeDataPackage

    Raises:
        ValueError: If validation fails with detailed error message

    Example:
        >>> try:
        ...     validate_mdp(package_dict)
        ...     print("Package is valid")
        ... except ValueError as e:
        ...     print(f"Validation failed: {e}")
    """
    errors = validate_schema(data, MDP_BASE_SCHEMA)

    if errors:
        raise ValueError(
            f"MyrezeDataPackage validation failed:\n"
            + "\n".join(f"  - {error}" for error in errors)
        )

    # Validate time structure
    time_data = data.get("time", {})
    time_type = time_data.get("type")
    time_value = time_data.get("value")

    try:
        if time_type == "Timestamp":
            isodate.parse_datetime(time_value)
        elif time_type == "Span":
            if (
                not isinstance(time_value, dict)
                or "start" not in time_value
                or "end" not in time_value
            ):
                raise ValueError("Span must have start and end")
            start = isodate.parse_datetime(time_value["start"])
            end = isodate.parse_datetime(time_value["end"])
            if start >= end:
                raise ValueError("Span start must be before end")
        elif time_type == "Series":
            if not isinstance(time_value, list) or len(time_value) == 0:
                raise ValueError("Series must be non-empty list")
            times = [isodate.parse_datetime(t) for t in time_value]
            if times != sorted(times):
                raise ValueError("Series timestamps must be sorted")
    except Exception as e:
        raise ValueError(f"Time validation failed: {e}")


def validate_visualization_data(data: Dict[str, Any], viz_type: str) -> List[str]:
    """
    Validate data structure against visualization type requirements.

    Args:
        data: Data dictionary from MyrezeDataPackage
        viz_type: Visualization type string

    Returns:
        List of validation error messages (empty if valid)

    Example:
        >>> errors = validate_visualization_data(data, "heatmap")
        >>> if errors:
        ...     print("Validation errors:", errors)
        ... else:
        ...     print("Data structure is valid for heatmap visualization")
    """
    if viz_type not in VISUALIZATION_DATA_SCHEMAS:
        return [f"Unknown visualization type: {viz_type}"]

    schema = VISUALIZATION_DATA_SCHEMAS[viz_type]
    errors = []

    # Check required fields
    required_fields = schema.get("required_fields", [])
    for field in required_fields:
        if field not in data:
            errors.append(f"Required field '{field}' missing for {viz_type}")

    # Validate specific field formats
    field_specs = schema.get("field_specifications", {})
    for field, spec in field_specs.items():
        if field in data:
            value = data[field]
            field_type = spec.get("type")

            if field_type == "2D array":
                if isinstance(value, np.ndarray):
                    if len(value.shape) != 2:
                        errors.append(f"Field '{field}' must be 2D array")
                elif isinstance(value, list):
                    if not all(isinstance(row, list) for row in value):
                        errors.append(f"Field '{field}' must be 2D nested list")
                else:
                    errors.append(f"Field '{field}' must be 2D array or nested list")

            elif field_type == "array" and not isinstance(value, list):
                errors.append(f"Field '{field}' must be an array")

            elif field_type == "array of objects":
                if not isinstance(value, list):
                    errors.append(f"Field '{field}' must be an array")
                elif not all(isinstance(item, dict) for item in value):
                    errors.append(f"Field '{field}' must be array of objects")

    return errors


def get_schemas() -> Dict[str, Any]:
    """
    Get all available schemas for LLM agent discovery.

    Returns:
        Dictionary containing all schema definitions

    Example:
        >>> schemas = get_schemas()
        >>> print("Available schemas:", list(schemas.keys()))
        >>> heatmap_schema = schemas["visualization_data"]["heatmap"]
        >>> print("Heatmap required fields:", heatmap_schema["required_fields"])
    """
    return {
        "mdp_base": MDP_BASE_SCHEMA,
        "visualization_data": VISUALIZATION_DATA_SCHEMAS,
    }


def get_visualization_requirements(viz_type: str) -> Dict[str, Any]:
    """
    Get requirements for a specific visualization type.

    Args:
        viz_type: Visualization type string

    Returns:
        Dictionary with requirements, or empty dict if type unknown

    Example:
        >>> reqs = get_visualization_requirements("point_cloud")
        >>> print(f"Required fields: {reqs['required_fields']}")
        >>> print(f"Description: {reqs['description']}")
    """
    return VISUALIZATION_DATA_SCHEMAS.get(viz_type, {})


def suggest_visualization_type(data: Dict[str, Any]) -> List[str]:
    """
    Suggest appropriate visualization types based on data structure.

    Args:
        data: Data dictionary to analyze

    Returns:
        List of suggested visualization type strings, ordered by confidence

    Example:
        >>> suggestions = suggest_visualization_type({"grid": [[1,2],[3,4]], "bounds": [...]})
        >>> print(f"Suggested types: {suggestions}")
    """
    suggestions = []

    # Check for grid-based data
    if "grid" in data and "bounds" in data:
        if isinstance(data.get("grid"), (list, np.ndarray)):
            suggestions.extend(["flat_overlay", "heatmap"])

    # Check for point-based data
    if "locations" in data and "values" in data:
        suggestions.append("point_cloud")

    # Check for vector data
    if all(field in data for field in ["grid_points", "u_component", "v_component"]):
        suggestions.append("vector_field")

    # Check for trajectory data
    if "positions" in data and isinstance(data.get("positions"), list):
        if len(data["positions"]) > 1:
            suggestions.append("trajectory")

    return suggestions
