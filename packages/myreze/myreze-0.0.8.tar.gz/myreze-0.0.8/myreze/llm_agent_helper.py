"""
LLM Agent Helper Module for Myreze

This module provides comprehensive discovery and assistance functions specifically
designed for LLM-based agents working with the Myreze toolkit. It offers
programmatic access to schemas, examples, and guidance for creating and
interpreting MyrezeDataPackages.

Key Features:
- Schema discovery and validation
- Data structure templates
- Example generation
- Error diagnosis
- Best practice guidance
"""

from typing import Dict, Any, List, Optional, Tuple
import json
from myreze.data import (
    MyrezeDataPackage,
    Time,
    VISUALIZATION_TYPES,
    VISUALIZATION_SCHEMAS,
)
from myreze.data.validate import (
    validate_visualization_data,
    suggest_visualization_type,
    get_visualization_requirements,
)


class MyrezeAgentHelper:
    """
    Comprehensive helper class for LLM agents working with Myreze.

    This class provides methods for discovering module capabilities,
    validating data structures, generating examples, and providing
    guidance for common tasks.
    """

    @staticmethod
    def get_module_overview() -> Dict[str, Any]:
        """
        Get a comprehensive overview of the Myreze module capabilities.

        Returns:
            Dictionary with module structure and capabilities
        """
        return {
            "purpose": "Geospatial data packaging and visualization toolkit",
            "core_components": {
                "data": "MyrezeDataPackage, Time, Geometry - data structures",
                "viz": "Renderers for ThreeJS, Unreal Engine, PNG export",
                "store": "Product catalog and HTTP API for data services",
            },
            "supported_visualization_types": VISUALIZATION_TYPES,
            "key_concepts": {
                "visualization_type": "Semantic hint for data interpretation",
                "time_handling": "Timestamp, Span, or Series of timestamps",
                "renderers": "Platform-specific visualization generators",
                "metadata": "Additional info for processing and display",
            },
            "common_workflows": [
                "Create data package -> Validate -> Serialize -> Transfer",
                "Receive package -> Inspect type -> Process -> Visualize",
                "Generate product -> Register -> Serve via HTTP API",
            ],
        }

    @staticmethod
    def get_visualization_guide() -> Dict[str, Dict[str, Any]]:
        """
        Get comprehensive guide for all visualization types.

        Returns:
            Dictionary mapping visualization types to detailed guidance
        """
        guide = {}

        for viz_type in VISUALIZATION_TYPES:
            schema = VISUALIZATION_SCHEMAS.get(viz_type, {})
            guide[viz_type] = {
                "description": schema.get(
                    "description", f"Visualization type: {viz_type}"
                ),
                "required_fields": schema.get("required_fields", []),
                "optional_fields": schema.get("optional_fields", []),
                "use_cases": MyrezeAgentHelper._get_use_cases(viz_type),
                "data_template": MyrezeAgentHelper._get_data_template(viz_type),
                "common_mistakes": MyrezeAgentHelper._get_common_mistakes(viz_type),
            }

        return guide

    @staticmethod
    def _get_use_cases(viz_type: str) -> List[str]:
        """Get common use cases for a visualization type."""
        use_cases = {
            "flat_overlay": [
                "Weather maps (temperature, precipitation, pressure)",
                "Satellite imagery overlays",
                "Land use classification maps",
                "Pollution concentration maps",
            ],
            "heatmap": [
                "Temperature distributions",
                "Population density maps",
                "Risk assessment maps",
                "Intensity surfaces",
            ],
            "point_cloud": [
                "Weather station readings",
                "Sensor network data",
                "GPS tracking points",
                "Survey measurement points",
            ],
            "vector_field": [
                "Wind patterns",
                "Ocean currents",
                "Magnetic field data",
                "Flow visualizations",
            ],
            "trajectory": [
                "Storm tracks",
                "Vehicle routes",
                "Animal migration paths",
                "Time-based movement data",
            ],
            "terrain": [
                "Elevation models",
                "3D landscape visualization",
                "Topographic data",
                "Bathymetry data",
            ],
        }
        return use_cases.get(viz_type, [f"Custom {viz_type} visualizations"])

    @staticmethod
    def _get_data_template(viz_type: str) -> Dict[str, Any]:
        """Get a data structure template for a visualization type."""
        templates = {
            "flat_overlay": {
                "grid": "[[value, value, ...], [value, value, ...], ...]",
                "bounds": "[west, south, east, north]",
                "resolution": "degrees_per_pixel",
                "units": "measurement_unit",
            },
            "heatmap": {
                "grid": "[[value, value, ...], [value, value, ...], ...]",
                "bounds": "[west, south, east, north]",
                "values_range": "[min_value, max_value]",
                "colormap": "viridis|plasma|coolwarm|...",
            },
            "point_cloud": {
                "locations": '[{"lat": float, "lon": float, "elevation": float}, ...]',
                "values": "[measurement1, measurement2, ...]",
                "point_ids": '["id1", "id2", ...]',
            },
            "vector_field": {
                "grid_points": '{"lats": [...], "lons": [...]}',
                "u_component": "[[east_west_values, ...], ...]",
                "v_component": "[[north_south_values, ...], ...]",
                "magnitude": "[[speed_values, ...], ...]",
            },
            "trajectory": {
                "positions": '[{"lat": float, "lon": float, "timestamp": "ISO8601"}, ...]',
                "values": "[measurement_at_each_position, ...]",
                "track_id": "unique_identifier",
            },
        }
        return templates.get(viz_type, {"data": "Custom structure for " + viz_type})

    @staticmethod
    def _get_common_mistakes(viz_type: str) -> List[str]:
        """Get common mistakes for a visualization type."""
        mistakes = {
            "flat_overlay": [
                "Grid dimensions don't match bounds",
                "Missing or incorrect bounds format",
                "Non-numeric values in grid",
                "Inconsistent data types",
            ],
            "heatmap": [
                "Missing values_range for color scaling",
                "Grid contains NaN or infinite values",
                "Bounds don't match data extent",
            ],
            "point_cloud": [
                "Locations and values arrays have different lengths",
                "Missing lat/lon coordinates",
                "Invalid coordinate values (outside ±180/±90)",
            ],
            "vector_field": [
                "Grid dimensions don't match for u/v components",
                "Missing magnitude calculation",
                "Inconsistent coordinate systems",
            ],
            "trajectory": [
                "Positions not sorted by time",
                "Missing timestamp information",
                "Inconsistent position format",
            ],
        }
        return mistakes.get(viz_type, ["Validate data structure against schema"])

    @staticmethod
    def analyze_data_structure(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a data structure and provide recommendations.

        Args:
            data: Data dictionary to analyze

        Returns:
            Analysis results with recommendations
        """
        analysis = {
            "structure_summary": {},
            "suggested_viz_types": [],
            "validation_results": {},
            "recommendations": [],
        }

        # Analyze structure
        analysis["structure_summary"] = {
            "fields": list(data.keys()),
            "field_types": {k: type(v).__name__ for k, v in data.items()},
            "array_shapes": {
                k: getattr(v, "shape", len(v) if hasattr(v, "__len__") else "scalar")
                for k, v in data.items()
            },
        }

        # Get suggestions
        analysis["suggested_viz_types"] = suggest_visualization_type(data)

        # Validate against suggested types
        for viz_type in analysis["suggested_viz_types"][:3]:  # Check top 3 suggestions
            errors = validate_visualization_data(data, viz_type)
            analysis["validation_results"][viz_type] = {
                "valid": len(errors) == 0,
                "errors": errors,
            }

        # Generate recommendations
        if analysis["suggested_viz_types"]:
            best_type = analysis["suggested_viz_types"][0]
            analysis["recommendations"].append(
                f"Recommended visualization_type: '{best_type}'"
            )

            # Check for common issues
            if "grid" in data and "bounds" not in data:
                analysis["recommendations"].append(
                    "Add 'bounds' field for grid-based data"
                )

            if "locations" in data and "values" in data:
                if len(data.get("locations", [])) != len(data.get("values", [])):
                    analysis["recommendations"].append(
                        "Ensure locations and values arrays have same length"
                    )
        else:
            analysis["recommendations"].append(
                "Unable to determine visualization type - check data structure"
            )

        return analysis

    @staticmethod
    def generate_package_template(
        viz_type: str,
        package_id: str = "example-package",
        include_metadata: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate a complete package template for a visualization type.

        Args:
            viz_type: Visualization type to generate template for
            package_id: Package identifier
            include_metadata: Whether to include example metadata

        Returns:
            Complete package template dictionary
        """
        if viz_type not in VISUALIZATION_TYPES:
            raise ValueError(f"Unknown visualization type: {viz_type}")

        template = {
            "version": "1.0.0",
            "type": "MyrezeDataPackage",
            "id": package_id,
            "data": MyrezeAgentHelper._get_data_template(viz_type),
            "time": {"type": "Timestamp", "value": "2023-01-01T12:00:00Z"},
            "visualization_type": viz_type,
            "threejs_visualization": None,
            "unreal_visualization": None,
        }

        if include_metadata:
            template["metadata"] = MyrezeAgentHelper._get_metadata_template(viz_type)

        return template

    @staticmethod
    def _get_metadata_template(viz_type: str) -> Dict[str, Any]:
        """Get metadata template for a visualization type."""
        base_metadata = {
            "description": f"Example {viz_type} visualization",
            "data_source": "example_generator",
            "created_at": "2023-01-01T12:00:00Z",
        }

        type_specific = {
            "flat_overlay": {
                "colormap": "viridis",
                "opacity": 0.8,
                "layer_name": "Data Layer",
            },
            "heatmap": {
                "colormap": "viridis",
                "opacity": 0.8,
                "smooth_interpolation": True,
            },
            "point_cloud": {
                "point_size": 5,
                "color_scale": "value",
                "show_labels": False,
            },
            "vector_field": {
                "arrow_scale": 1.0,
                "color_by": "magnitude",
                "density": "medium",
            },
            "trajectory": {"animate": True, "trail_length": 24, "color_by": "time"},
        }

        base_metadata.update(type_specific.get(viz_type, {}))
        return base_metadata

    @staticmethod
    def validate_package_dict(package_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive validation of a package dictionary.

        Args:
            package_dict: Package dictionary to validate

        Returns:
            Validation results with detailed feedback
        """
        results = {"valid": True, "errors": [], "warnings": [], "suggestions": []}

        try:
            # Basic structure validation
            required_fields = ["version", "type", "id", "data", "time"]
            for field in required_fields:
                if field not in package_dict:
                    results["errors"].append(f"Missing required field: {field}")
                    results["valid"] = False

            # Visualization type validation
            viz_type = package_dict.get("visualization_type", "")
            if viz_type and viz_type not in VISUALIZATION_TYPES:
                results["warnings"].append(f"Unknown visualization type: {viz_type}")

            # Data structure validation
            if "data" in package_dict and viz_type:
                data_errors = validate_visualization_data(
                    package_dict["data"], viz_type
                )
                if data_errors:
                    results["errors"].extend(data_errors)
                    results["valid"] = False

            # Time validation
            time_data = package_dict.get("time", {})
            if not isinstance(time_data, dict) or "type" not in time_data:
                results["errors"].append("Invalid time structure")
                results["valid"] = False

            # Suggestions
            if not package_dict.get("metadata"):
                results["suggestions"].append(
                    "Consider adding metadata for better visualization"
                )

            if not package_dict.get("threejs_visualization") and not package_dict.get(
                "unreal_visualization"
            ):
                results["suggestions"].append(
                    "Add at least one renderer for visualization output"
                )

        except Exception as e:
            results["errors"].append(f"Validation error: {str(e)}")
            results["valid"] = False

        return results

    @staticmethod
    def get_troubleshooting_guide() -> Dict[str, List[str]]:
        """
        Get comprehensive troubleshooting guide for common issues.

        Returns:
            Dictionary mapping problem categories to solutions
        """
        return {
            "data_validation_errors": [
                "Check that required fields are present for your visualization type",
                "Verify data types match expected formats (arrays, numbers, strings)",
                "Ensure array dimensions are consistent (e.g., grid dimensions)",
                "Validate coordinate values are within valid ranges",
            ],
            "visualization_type_selection": [
                "Use grid + bounds for flat_overlay or heatmap",
                "Use locations + values for point_cloud",
                "Use grid_points + u_component + v_component for vector_field",
                "Use positions with timestamps for trajectory",
            ],
            "time_format_issues": [
                "All timestamps must be ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)",
                "Span must have start < end",
                "Series timestamps must be sorted chronologically",
                "Use Time.timestamp(), Time.span(), or Time.series() helper methods",
            ],
            "serialization_problems": [
                "NumPy arrays are automatically converted to lists for JSON",
                "Bytes data is converted to base64 strings",
                "Use validate_on_init=True to catch issues early",
                "Check for circular references in complex data structures",
            ],
            "renderer_issues": [
                "Ensure renderer instances are created, not classes",
                "Use appropriate renderer for your target platform",
                "Check that renderer is registered in the registry",
                "Verify renderer has required methods implemented",
            ],
        }


# Convenience functions for quick access
def get_schema_for_type(viz_type: str) -> Dict[str, Any]:
    """Quick access to schema for a visualization type."""
    return get_visualization_requirements(viz_type)


def validate_data_for_type(data: Dict[str, Any], viz_type: str) -> List[str]:
    """Quick validation of data for a visualization type."""
    return validate_visualization_data(data, viz_type)


def suggest_type_for_data(data: Dict[str, Any]) -> List[str]:
    """Quick suggestion of visualization types for data."""
    return suggest_visualization_type(data)


def create_example_package(viz_type: str) -> Dict[str, Any]:
    """Quick creation of example package template."""
    helper = MyrezeAgentHelper()
    return helper.generate_package_template(viz_type)


# Module discovery function
def discover_myreze_capabilities() -> Dict[str, Any]:
    """
    Comprehensive discovery function for LLM agents.

    Returns:
        Complete capability overview of the Myreze module
    """
    helper = MyrezeAgentHelper()

    return {
        "module_overview": helper.get_module_overview(),
        "visualization_guide": helper.get_visualization_guide(),
        "troubleshooting": helper.get_troubleshooting_guide(),
        "available_types": VISUALIZATION_TYPES,
        "schemas": {
            viz_type: get_schema_for_type(viz_type) for viz_type in VISUALIZATION_TYPES
        },
        "usage_patterns": {
            "create_package": "MyrezeDataPackage(id, data, time, viz_type, metadata)",
            "validate_package": "validate_package_dict(package.to_dict())",
            "serialize_package": "package.to_json()",
            "load_package": "MyrezeDataPackage.from_json(json_str)",
        },
    }
