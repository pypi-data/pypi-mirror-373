#!/usr/bin/env python
"""
Tests for PointDataRenderer functionality.

This test covers the full lifecycle of creating, serializing, deserializing,
and rendering SVGs from point data packages.
"""

import unittest
import json
from myreze.data import MyrezeDataPackage, Time
from myreze.viz.threejs.point_data_renderer import PointDataRenderer


class TestPointDataRenderer(unittest.TestCase):
    def setUp(self):
        """Set up test data for point data renderer tests."""
        self.sample_data = {
            "STATION_001": {
                "measurements": {
                    "temperature": 22.5,
                    "humidity": 58.3,
                    "pressure": 1013.2,
                },
                "svg_template": """
<svg width="100" height="60" xmlns="http://www.w3.org/2000/svg">
    <rect width="100" height="60" fill="#f0f8ff" stroke="#333" 
          stroke-width="1"/>
    <text x="50" y="20" text-anchor="middle" 
          font-size="10">{station_name}</text>
    <text x="50" y="35" text-anchor="middle" 
          font-size="12">{temperature}°C</text>
    <text x="50" y="50" text-anchor="middle" 
          font-size="8">{humidity}% RH</text>
</svg>
                """.strip(),
                "metadata": {
                    "station_name": "Test Station",
                    "coordinates": {"lat": 40.7829, "lon": -73.9654},
                    "elevation": 42,
                },
            },
            "STATION_002": {
                "measurements": {
                    "temperature": 24.1,
                    "humidity": 62.7,
                    "pressure": 1012.8,
                },
                "svg_template": """
<svg width="100" height="60" xmlns="http://www.w3.org/2000/svg">
    <rect width="100" height="60" fill="#f0fff0" stroke="#333" stroke-width="1"/>
    <text x="50" y="20" text-anchor="middle" font-size="10">{station_name}</text>
    <text x="50" y="35" text-anchor="middle" font-size="12">{temperature}°C</text>
    <text x="50" y="50" text-anchor="middle" font-size="8">{humidity}% RH</text>
</svg>
                """.strip(),
                "metadata": {
                    "station_name": "Test Station 2",
                    "coordinates": {"lat": 40.7033, "lon": -74.0170},
                    "elevation": 8,
                },
            },
        }

    def test_point_data_renderer_creation(self):
        """Test creating a PointDataRenderer instance."""
        renderer = PointDataRenderer()
        self.assertIsInstance(renderer, PointDataRenderer)

    def test_create_point_data_package(self):
        """Test creating a MyrezeDataPackage with point data."""
        package = MyrezeDataPackage(
            id="test-point-data",
            data=self.sample_data,
            time=Time.timestamp("2023-07-15T14:30:00Z"),
            threejs_visualization=PointDataRenderer(),
            visualization_type="point_data_svg",
            metadata={
                "description": "Test point data package",
                "total_stations": len(self.sample_data),
            },
        )

        self.assertIsInstance(package, MyrezeDataPackage)
        self.assertEqual(package.id, "test-point-data")
        self.assertEqual(package.visualization_type, "point_data_svg")
        self.assertIsInstance(package.threejs_visualization, PointDataRenderer)
        self.assertEqual(len(package.data), 2)

    def test_serialize_deserialize_cycle(self):
        """Test serializing and deserializing a point data package."""
        # Create original package
        original_package = MyrezeDataPackage(
            id="serialize-test",
            data=self.sample_data,
            time=Time.timestamp("2023-07-15T14:30:00Z"),
            threejs_visualization=PointDataRenderer(),
            visualization_type="point_data_svg",
            metadata={"test": "serialization"},
        )

        # Serialize to JSON
        json_data = original_package.to_json()
        self.assertIsInstance(json_data, str)

        # Verify JSON is valid
        parsed_json = json.loads(json_data)
        self.assertIn("id", parsed_json)
        self.assertIn("data", parsed_json)
        self.assertIn("time", parsed_json)
        self.assertEqual(parsed_json["id"], "serialize-test")
        self.assertEqual(parsed_json["visualization_type"], "point_data_svg")

        # Deserialize back to package
        deserialized_package = MyrezeDataPackage.from_json(json_data)

        # Verify deserialized package matches original
        self.assertEqual(deserialized_package.id, original_package.id)
        self.assertEqual(
            deserialized_package.visualization_type, original_package.visualization_type
        )
        self.assertEqual(len(deserialized_package.data), len(original_package.data))

        # Check specific data integrity
        self.assertIn("STATION_001", deserialized_package.data)
        self.assertIn("STATION_002", deserialized_package.data)

        station_001 = deserialized_package.data["STATION_001"]
        self.assertEqual(station_001["measurements"]["temperature"], 22.5)
        self.assertEqual(station_001["metadata"]["station_name"], "Test Station")
        self.assertIn("<svg", station_001["svg_template"])

    def test_render_svgs_from_package(self):
        """Test rendering SVGs from a point data package."""
        # Create package
        package = MyrezeDataPackage(
            id="render-test",
            data=self.sample_data,
            time=Time.timestamp("2023-07-15T14:30:00Z"),
            threejs_visualization=PointDataRenderer(),
            visualization_type="point_data_svg",
        )

        # Render SVGs
        svg_outputs = package.to_threejs()

        # Verify outputs
        self.assertIsInstance(svg_outputs, dict)
        self.assertEqual(len(svg_outputs), 2)
        self.assertIn("STATION_001", svg_outputs)
        self.assertIn("STATION_002", svg_outputs)

        # Check SVG content for STATION_001
        svg_001 = svg_outputs["STATION_001"]
        self.assertIsInstance(svg_001, str)
        self.assertIn("<svg", svg_001)
        self.assertIn("</svg>", svg_001)
        self.assertIn("Test Station", svg_001)  # station_name substituted
        self.assertIn("22.5°C", svg_001)  # temperature substituted
        self.assertIn("58.3% RH", svg_001)  # humidity substituted

        # Check SVG content for STATION_002
        svg_002 = svg_outputs["STATION_002"]
        self.assertIsInstance(svg_002, str)
        self.assertIn("<svg", svg_002)
        self.assertIn("</svg>", svg_002)
        self.assertIn("Test Station 2", svg_002)  # station_name substituted
        self.assertIn("24.1°C", svg_002)  # temperature substituted
        self.assertIn("62.7% RH", svg_002)  # humidity substituted

    def test_full_serialize_deserialize_render_cycle(self):
        """Test the complete cycle: create -> serialize -> deserialize -> render."""
        # Step 1: Create original package
        original_package = MyrezeDataPackage(
            id="full-cycle-test",
            data=self.sample_data,
            time=Time.timestamp("2023-07-15T14:30:00Z"),
            threejs_visualization=PointDataRenderer(),
            visualization_type="point_data_svg",
            metadata={"test": "full_cycle"},
        )

        # Step 2: Serialize to JSON
        json_data = original_package.to_json()

        # Step 3: Deserialize from JSON
        restored_package = MyrezeDataPackage.from_json(json_data)

        # Step 4: Render SVGs from restored package
        svg_outputs = restored_package.to_threejs()

        # Step 5: Verify the complete cycle worked
        self.assertIsInstance(svg_outputs, dict)
        self.assertEqual(len(svg_outputs), 2)

        # Verify template substitution worked correctly after serialization cycle
        svg_001 = svg_outputs["STATION_001"]
        self.assertIn("Test Station", svg_001)
        self.assertIn("22.5°C", svg_001)
        self.assertIn("58.3% RH", svg_001)

        svg_002 = svg_outputs["STATION_002"]
        self.assertIn("Test Station 2", svg_002)
        self.assertIn("24.1°C", svg_002)
        self.assertIn("62.7% RH", svg_002)

        # Verify both SVGs are valid XML structure
        for station_id, svg_content in svg_outputs.items():
            self.assertTrue(
                svg_content.count("<svg") == 1,
                f"Station {station_id}: Should have exactly one <svg> tag",
            )
            self.assertTrue(
                svg_content.count("</svg>") == 1,
                f"Station {station_id}: Should have exactly one </svg> tag",
            )

    def test_svg_list_generation(self):
        """Test creating a list of SVG strings from the package."""
        # Create and render package
        package = MyrezeDataPackage(
            id="svg-list-test",
            data=self.sample_data,
            time=Time.timestamp("2023-07-15T14:30:00Z"),
            threejs_visualization=PointDataRenderer(),
            visualization_type="point_data_svg",
        )

        svg_dict = package.to_threejs()

        # Convert to list of SVGs (as requested in user query)
        svg_list = list(svg_dict.values())

        self.assertIsInstance(svg_list, list)
        self.assertEqual(len(svg_list), 2)

        # Verify each item in list is a valid SVG string
        for svg in svg_list:
            self.assertIsInstance(svg, str)
            self.assertIn("<svg", svg)
            self.assertIn("</svg>", svg)

        # Also test getting location IDs and SVGs as paired lists
        location_ids = list(svg_dict.keys())
        svg_values = list(svg_dict.values())

        self.assertEqual(len(location_ids), len(svg_values))
        self.assertIn("STATION_001", location_ids)
        self.assertIn("STATION_002", location_ids)

    def test_error_handling_in_serialized_package(self):
        """Test error handling with serialized packages."""
        # Create package with potential error (missing template variable)
        error_data = {
            "GOOD_STATION": {
                "measurements": {"temp": 20.0},
                "svg_template": "<svg><text>{temp}°C</text></svg>",
                "metadata": {"name": "Good"},
            },
            "BAD_STATION": {
                "measurements": {"temp": 25.0},
                "svg_template": "<svg><text>{missing_var}°C</text></svg>",
                "metadata": {"name": "Bad"},
            },
        }

        package = MyrezeDataPackage(
            id="error-test",
            data=error_data,
            time=Time.timestamp("2023-07-15T14:30:00Z"),
            threejs_visualization=PointDataRenderer(),
            visualization_type="point_data_svg",
        )

        # Serialize and deserialize
        json_data = package.to_json()
        restored_package = MyrezeDataPackage.from_json(json_data)

        # Test error handling modes work after serialization
        svg_outputs_skip = restored_package.to_threejs(
            params={"error_handling": "skip"}
        )
        self.assertEqual(len(svg_outputs_skip), 1)  # Only good station rendered
        self.assertIn("GOOD_STATION", svg_outputs_skip)

        svg_outputs_placeholder = restored_package.to_threejs(
            params={"error_handling": "placeholder"}
        )
        self.assertEqual(
            len(svg_outputs_placeholder), 2
        )  # Both stations, one with error placeholder
        self.assertIn("GOOD_STATION", svg_outputs_placeholder)
        self.assertIn("BAD_STATION", svg_outputs_placeholder)
        self.assertIn("Error:", svg_outputs_placeholder["BAD_STATION"])


if __name__ == "__main__":
    unittest.main()
