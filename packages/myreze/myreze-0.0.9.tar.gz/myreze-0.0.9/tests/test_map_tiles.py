"""
Tests for map tile functionality in MyrezeDataPackage.

This module tests the map_tile() method and underlying XYZ tile rendering
functionality, including coordinate transformations, tile bounds calculation,
and various data formats.
"""

import unittest
import numpy as np
import base64
import io
from PIL import Image
import warnings

from myreze.data import MyrezeDataPackage, Time
from myreze.viz.tiles.xyz import (
    xyz_tile_bounds,
    deg_to_web_mercator,
    web_mercator_to_deg,
    bounds_to_web_mercator,
    apply_colormap,
    render_xyz_tile,
    encode_tile_png,
)


class TestXYZTileCoordinates(unittest.TestCase):
    """Test XYZ tile coordinate system calculations."""

    def test_xyz_tile_bounds(self):
        """Test calculation of tile bounds in Web Mercator."""
        # Test tile 0,0,0 (the whole world)
        minx, miny, maxx, maxy = xyz_tile_bounds(0, 0, 0)
        expected_extent = 2 * np.pi * 6378137.0  # Earth circumference
        self.assertAlmostEqual(maxx - minx, expected_extent, places=0)
        self.assertAlmostEqual(maxy - miny, expected_extent, places=0)

        # Test zoom level 1 (4 tiles total)
        minx, miny, maxx, maxy = xyz_tile_bounds(0, 0, 1)
        expected_size = expected_extent / 2
        self.assertAlmostEqual(maxx - minx, expected_size, places=0)
        self.assertAlmostEqual(maxy - miny, expected_size, places=0)

        # Test specific tile coordinates
        minx, miny, maxx, maxy = xyz_tile_bounds(301, 384, 10)
        # This should be roughly in the NYC area
        self.assertTrue(-8500000 < minx < -8000000)  # Rough Web Mercator X for NYC
        self.assertTrue(4900000 < miny < 5000000)  # Rough Web Mercator Y for NYC

    def test_coordinate_conversion(self):
        """Test longitude/latitude to Web Mercator conversion."""
        # Test known coordinate pairs
        lon, lat = -74.0, 40.7  # NYC
        x, y = deg_to_web_mercator(lon, lat)

        # Convert back
        lon2, lat2 = web_mercator_to_deg(x, y)

        self.assertAlmostEqual(lon, lon2, places=5)
        self.assertAlmostEqual(lat, lat2, places=5)

        # Test bounds conversion
        bounds_wgs84 = (-74.0, 40.7, -73.9, 40.8)
        bounds_mercator = bounds_to_web_mercator(bounds_wgs84, "EPSG:4326")

        # Should be 4-tuple of Web Mercator coordinates
        self.assertEqual(len(bounds_mercator), 4)
        self.assertTrue(all(isinstance(x, float) for x in bounds_mercator))

        # Web Mercator coordinates should be much larger than degrees
        self.assertTrue(abs(bounds_mercator[0]) > 1000000)

    def test_invalid_zoom_levels(self):
        """Test handling of invalid zoom levels."""
        with self.assertRaises(ValueError):
            xyz_tile_bounds(0, 0, -1)


class TestColormapApplication(unittest.TestCase):
    """Test colormap application to scalar data."""

    def test_apply_colormap_basic(self):
        """Test basic colormap application."""
        data = np.array([[0, 50, 100], [25, 75, 100]])

        rgba = apply_colormap(data, colormap="viridis", vmin=0, vmax=100)

        # Should be RGBA format
        self.assertEqual(rgba.shape, (2, 3, 4))
        self.assertEqual(rgba.dtype, np.uint8)

        # Alpha channel should be fully opaque by default
        self.assertTrue(np.all(rgba[:, :, 3] == 255))

    def test_apply_colormap_nodata(self):
        """Test colormap with nodata values."""
        data = np.array([[0, -999, 100], [25, 75, -999]])

        rgba = apply_colormap(data, colormap="viridis", vmin=0, vmax=100, nodata=-999)

        # Nodata pixels should be transparent
        nodata_mask = data == -999
        self.assertTrue(np.all(rgba[nodata_mask, 3] == 0))

        # Valid pixels should be opaque
        valid_mask = data != -999
        self.assertTrue(np.all(rgba[valid_mask, 3] == 255))

    def test_apply_colormap_fallback(self):
        """Test colormap fallback when invalid colormap is provided."""
        data = np.array([[0, 50, 100]])

        # Should not raise an error with invalid colormap, but should warn and use viridis
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            rgba = apply_colormap(data, colormap="nonexistent", vmin=0, vmax=100)

            # Should have issued a warning
            self.assertTrue(len(w) > 0)
            self.assertTrue(any("nonexistent" in str(warning.message) for warning in w))

        self.assertEqual(rgba.shape, (1, 3, 4))


class TestTileRendering(unittest.TestCase):
    """Test tile rendering functionality."""

    def setUp(self):
        """Set up test data."""
        # Create a simple 10x10 grid covering NYC area
        self.grid_data = {
            "grid": np.random.rand(10, 10) * 30 + 10,  # Temperature-like data
        }
        self.grid_metadata = {
            "bounds": [-74.1, 40.6, -73.8, 40.9],  # NYC area in WGS84
            "crs": "EPSG:4326",
            "colormap": "viridis",
        }

        # Create PNG data
        img = Image.new("RGBA", (100, 100), (255, 0, 0, 128))  # Semi-transparent red
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        png_bytes = buffer.getvalue()

        self.png_data = {"png_bytes": base64.b64encode(png_bytes).decode("utf-8")}
        self.png_metadata = {
            "bounds": [-74.1, 40.6, -73.8, 40.9],
            "crs": "EPSG:4326",
        }

        # Create single-channel grayscale PNG data
        grayscale_img = Image.new("L", (50, 50))  # Grayscale mode
        # Create a simple gradient
        pixels = []
        for y in range(50):
            for x in range(50):
                # Create a diagonal gradient
                value = int(255 * (x + y) / 100)
                pixels.append(value)
        grayscale_img.putdata(pixels)

        buffer = io.BytesIO()
        grayscale_img.save(buffer, format="PNG")
        grayscale_bytes = buffer.getvalue()

        self.grayscale_data = {
            "png_bytes": base64.b64encode(grayscale_bytes).decode("utf-8")
        }
        self.grayscale_metadata = {
            "bounds": [-74.1, 40.6, -73.8, 40.9],
            "crs": "EPSG:4326",
            "colormap": "viridis",  # Apply colormap to grayscale data
        }

    def test_render_grid_tile(self):
        """Test rendering a tile from grid data."""
        # Request a tile that should overlap with our data
        rgba_tile = render_xyz_tile(
            data=self.grid_data,
            metadata=self.grid_metadata,
            x=301,
            y=384,
            z=10,  # NYC area at zoom 10
            tile_size=256,
        )

        # Should return 256x256 RGBA array
        self.assertEqual(rgba_tile.shape, (256, 256, 4))
        self.assertEqual(rgba_tile.dtype, np.uint8)

        # Should not be entirely transparent (some data should be rendered)
        self.assertTrue(np.any(rgba_tile[:, :, 3] > 0))

    def test_render_png_tile(self):
        """Test rendering a tile from PNG data."""
        rgba_tile = render_xyz_tile(
            data=self.png_data,
            metadata=self.png_metadata,
            x=301,
            y=384,
            z=10,
            tile_size=256,
        )

        self.assertEqual(rgba_tile.shape, (256, 256, 4))
        self.assertEqual(rgba_tile.dtype, np.uint8)

    def test_render_grayscale_png_tile(self):
        """Test rendering a tile from single-channel grayscale PNG data."""
        rgba_tile = render_xyz_tile(
            data=self.grayscale_data,
            metadata=self.grayscale_metadata,
            x=301,
            y=384,
            z=10,
            tile_size=256,
        )

        self.assertEqual(rgba_tile.shape, (256, 256, 4))
        self.assertEqual(rgba_tile.dtype, np.uint8)

        # Should have applied colormap (not just grayscale)
        # Check that it's not purely grayscale (R != G != B for some pixels)
        # Since we applied viridis colormap, there should be color variation
        unique_colors = np.unique(rgba_tile.reshape(-1, 4), axis=0)
        # Should have more than just grayscale values
        non_grayscale = np.any(
            (unique_colors[:, 0] != unique_colors[:, 1])
            | (unique_colors[:, 1] != unique_colors[:, 2])
        )
        self.assertTrue(
            non_grayscale,
            "Colormap should have been applied to create non-grayscale colors",
        )

    def test_render_grayscale_png_no_colormap(self):
        """Test rendering grayscale PNG without colormap application."""
        # Use metadata without colormap
        grayscale_metadata_no_colormap = {
            "bounds": [-74.1, 40.6, -73.8, 40.9],
            "crs": "EPSG:4326",
        }

        rgba_tile = render_xyz_tile(
            data=self.grayscale_data,
            metadata=grayscale_metadata_no_colormap,
            x=301,
            y=384,
            z=10,
            tile_size=256,
        )

        self.assertEqual(rgba_tile.shape, (256, 256, 4))
        self.assertEqual(rgba_tile.dtype, np.uint8)

    def test_render_no_overlap_tile(self):
        """Test rendering a tile with no data overlap."""
        # Request a tile far from our data (e.g., somewhere in Asia)
        rgba_tile = render_xyz_tile(
            data=self.grid_data,
            metadata=self.grid_metadata,
            x=100,
            y=100,
            z=10,  # Far from NYC
            tile_size=256,
        )

        # Should return transparent tile
        self.assertEqual(rgba_tile.shape, (256, 256, 4))
        self.assertTrue(np.all(rgba_tile == 0))

    def test_render_invalid_data(self):
        """Test error handling for invalid data."""
        with self.assertRaises(ValueError):
            render_xyz_tile(
                data={},  # No grid or png_bytes
                metadata=self.grid_metadata,
                x=0,
                y=0,
                z=1,
            )

        with self.assertRaises(ValueError):
            render_xyz_tile(
                data=self.grid_data, metadata={}, x=0, y=0, z=1  # No bounds
            )

    def test_zoom_clamping(self):
        """Test zoom level clamping."""
        # Very high zoom should be clamped
        rgba_tile = render_xyz_tile(
            data=self.grid_data,
            metadata=self.grid_metadata,
            x=0,
            y=0,
            z=25,  # Higher than max
            tile_size=256,
        )
        self.assertEqual(rgba_tile.shape, (256, 256, 4))

        # Very low zoom should be clamped
        rgba_tile = render_xyz_tile(
            data=self.grid_data,
            metadata=self.grid_metadata,
            x=0,
            y=0,
            z=0,  # Lower than min
            tile_size=256,
        )
        self.assertEqual(rgba_tile.shape, (256, 256, 4))


class TestTileEncoding(unittest.TestCase):
    """Test tile encoding functionality."""

    def setUp(self):
        """Set up test RGBA data."""
        self.rgba_data = np.random.randint(0, 256, (256, 256, 4), dtype=np.uint8)

    def test_encode_bytes(self):
        """Test encoding as bytes."""
        result = encode_tile_png(self.rgba_data, return_format="bytes")

        self.assertIsInstance(result, bytes)
        self.assertTrue(result.startswith(b"\x89PNG"))  # PNG header

    def test_encode_base64(self):
        """Test encoding as base64."""
        result = encode_tile_png(self.rgba_data, return_format="base64")

        self.assertIsInstance(result, str)
        # Should be valid base64
        decoded = base64.b64decode(result)
        self.assertTrue(decoded.startswith(b"\x89PNG"))

    def test_encode_image(self):
        """Test encoding as PIL Image."""
        result = encode_tile_png(self.rgba_data, return_format="image")

        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.mode, "RGBA")
        self.assertEqual(result.size, (256, 256))

    def test_encode_invalid_format(self):
        """Test error handling for invalid format."""
        with self.assertRaises(ValueError):
            encode_tile_png(np.random.rand(256, 256, 3), return_format="bytes")


class TestMapTileMethod(unittest.TestCase):
    """Test the map_tile method on MyrezeDataPackage."""

    def setUp(self):
        """Set up test packages."""
        # Grid-based package
        self.grid_package = MyrezeDataPackage(
            id="test-grid-tiles",
            data={"grid": np.random.rand(50, 50) * 30 + 10},
            time=Time.timestamp("2023-06-15T14:30:00Z"),
            metadata={
                "bounds": [-74.1, 40.6, -73.8, 40.9],
                "crs": "EPSG:4326",
                "colormap": "viridis",
            },
            visualization_type="map_tile",
        )

        # PNG-based package
        img = Image.new("RGB", (100, 100), (0, 255, 0))  # Green image
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        png_bytes = buffer.getvalue()

        self.png_package = MyrezeDataPackage(
            id="test-png-tiles",
            data={"png_bytes": base64.b64encode(png_bytes).decode("utf-8")},
            time=Time.timestamp("2023-06-15T14:30:00Z"),
            metadata={
                "bounds": [-74.1, 40.6, -73.8, 40.9],
                "crs": "EPSG:4326",
            },
            visualization_type="map_tile",
        )

        # Create single-channel grayscale package
        grayscale_img = Image.new("L", (80, 80))  # Grayscale mode
        # Create elevation-like data
        pixels = []
        for y in range(80):
            for x in range(80):
                # Create a mountain-like elevation pattern
                center_x, center_y = 40, 40
                distance = np.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                elevation = max(0, 255 - int(distance * 6))  # Peak in center
                pixels.append(elevation)
        grayscale_img.putdata(pixels)

        buffer = io.BytesIO()
        grayscale_img.save(buffer, format="PNG")
        grayscale_bytes = buffer.getvalue()

        self.grayscale_package = MyrezeDataPackage(
            id="test-grayscale-tiles",
            data={"png_bytes": base64.b64encode(grayscale_bytes).decode("utf-8")},
            time=Time.timestamp("2023-06-15T14:30:00Z"),
            metadata={
                "bounds": [-74.1, 40.6, -73.8, 40.9],
                "crs": "EPSG:4326",
                "colormap": "terrain",  # Good for elevation data
                "min_value": 0,
                "max_value": 255,
            },
            visualization_type="map_tile",
        )

    def test_map_tile_bytes(self):
        """Test map_tile method returning bytes."""
        result = self.grid_package.map_tile(x=301, y=384, z=10)

        self.assertIsInstance(result, bytes)
        self.assertTrue(result.startswith(b"\x89PNG"))

    def test_map_tile_base64(self):
        """Test map_tile method returning base64."""
        result = self.grid_package.map_tile(x=301, y=384, z=10, return_format="base64")

        self.assertIsInstance(result, str)
        # Should be valid base64 PNG
        decoded = base64.b64decode(result)
        self.assertTrue(decoded.startswith(b"\x89PNG"))

    def test_map_tile_image(self):
        """Test map_tile method returning PIL Image."""
        result = self.grid_package.map_tile(x=301, y=384, z=10, return_format="image")

        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.mode, "RGBA")
        self.assertEqual(result.size, (256, 256))

    def test_map_tile_with_style(self):
        """Test map_tile method with custom styling."""
        result = self.grid_package.map_tile(
            x=301, y=384, z=10, style={"colormap": "plasma", "vmin": 15, "vmax": 25}
        )

        self.assertIsInstance(result, bytes)
        self.assertTrue(result.startswith(b"\x89PNG"))

    def test_map_tile_png_data(self):
        """Test map_tile method with PNG data."""
        result = self.png_package.map_tile(x=301, y=384, z=10)

        self.assertIsInstance(result, bytes)
        self.assertTrue(result.startswith(b"\x89PNG"))

    def test_map_tile_custom_size(self):
        """Test map_tile method with custom tile size."""
        result = self.grid_package.map_tile(
            x=301, y=384, z=10, tile_size=512, return_format="image"
        )

        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.size, (512, 512))

    def test_map_tile_no_overlap(self):
        """Test map_tile method with no data overlap."""
        # Request tile far from data
        result = self.grid_package.map_tile(
            x=0, y=0, z=5, return_format="image"  # Far from NYC
        )

        self.assertIsInstance(result, Image.Image)

        # Should be transparent (all alpha = 0)
        rgba_array = np.array(result)
        self.assertTrue(np.all(rgba_array[:, :, 3] == 0))

    def test_map_tile_grayscale_png_with_colormap(self):
        """Test map_tile method with single-channel PNG and colormap."""
        result = self.grayscale_package.map_tile(
            x=301, y=384, z=10, return_format="image"
        )

        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.mode, "RGBA")
        self.assertEqual(result.size, (256, 256))

        # Check that colormap was applied (should have colors, not just grayscale)
        rgba_array = np.array(result)
        unique_colors = np.unique(rgba_array.reshape(-1, 4), axis=0)

        # Should have non-grayscale colors due to terrain colormap
        non_grayscale = np.any(
            (unique_colors[:, 0] != unique_colors[:, 1])
            | (unique_colors[:, 1] != unique_colors[:, 2])
        )
        self.assertTrue(
            non_grayscale, "Terrain colormap should create non-grayscale colors"
        )

    def test_map_tile_grayscale_png_override_colormap(self):
        """Test overriding colormap via style parameter."""
        result = self.grayscale_package.map_tile(
            x=301,
            y=384,
            z=10,
            style={"colormap": "plasma", "vmin": 50, "vmax": 200},
            return_format="image",
        )

        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.size, (256, 256))

        # Should have applied plasma colormap instead of terrain
        rgba_array = np.array(result)
        # Plasma typically has purple/pink colors - check for non-grayscale
        unique_colors = np.unique(rgba_array.reshape(-1, 4), axis=0)
        non_grayscale = np.any(
            (unique_colors[:, 0] != unique_colors[:, 1])
            | (unique_colors[:, 1] != unique_colors[:, 2])
        )
        self.assertTrue(non_grayscale)

    def test_map_tile_grayscale_png_as_grayscale(self):
        """Test using grayscale PNG as grayscale (no colormap)."""
        # Create a package without colormap
        grayscale_img = Image.new("L", (50, 50), 128)  # Uniform gray
        buffer = io.BytesIO()
        grayscale_img.save(buffer, format="PNG")
        grayscale_bytes = buffer.getvalue()

        grayscale_no_colormap = MyrezeDataPackage(
            id="test-grayscale-no-colormap",
            data={"png_bytes": base64.b64encode(grayscale_bytes).decode("utf-8")},
            time=Time.timestamp("2023-06-15T14:30:00Z"),
            metadata={
                "bounds": [-74.1, 40.6, -73.8, 40.9],
                "crs": "EPSG:4326",
                # No colormap specified
            },
            visualization_type="map_tile",
        )

        result = grayscale_no_colormap.map_tile(
            x=301, y=384, z=10, return_format="image"
        )

        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.size, (256, 256))

        # Should be grayscale (R == G == B for all pixels)
        rgba_array = np.array(result)
        non_transparent_pixels = rgba_array[
            rgba_array[:, :, 3] > 0
        ]  # Skip transparent pixels
        if len(non_transparent_pixels) > 0:
            # Check that R == G == B for non-transparent pixels (grayscale)
            is_grayscale = np.all(
                (non_transparent_pixels[:, 0] == non_transparent_pixels[:, 1])
                & (non_transparent_pixels[:, 1] == non_transparent_pixels[:, 2])
            )
            self.assertTrue(
                is_grayscale, "Should be grayscale when no colormap is applied"
            )

    def test_serialization_roundtrip(self):
        """Test that packages can be serialized and deserialized with map_tile support."""
        # Serialize package
        package_dict = self.grid_package.to_dict()

        # Recreate from dict
        recreated_package = MyrezeDataPackage.from_dict(package_dict)

        # Should still be able to generate tiles
        result = recreated_package.map_tile(x=301, y=384, z=10)
        self.assertIsInstance(result, bytes)
        self.assertTrue(result.startswith(b"\x89PNG"))


class TestMapTileIntegration(unittest.TestCase):
    """Integration tests for map tile functionality."""

    def test_real_world_coordinates(self):
        """Test with real-world coordinate examples."""
        # Create package covering Manhattan
        manhattan_data = {
            "grid": np.random.rand(100, 100) * 25 + 5,  # Temperature data
        }
        manhattan_metadata = {
            "bounds": [-74.02, 40.70, -73.93, 40.78],  # Manhattan bounds
            "crs": "EPSG:4326",
            "colormap": "coolwarm",
        }

        package = MyrezeDataPackage(
            id="manhattan-temperature",
            data=manhattan_data,
            time=Time.timestamp("2023-07-15T15:00:00Z"),
            metadata=manhattan_metadata,
            visualization_type="map_tile",
        )

        # Test different zoom levels
        for zoom in [8, 10, 12, 14]:
            # Calculate tile coordinates that should overlap Manhattan
            # (This is a simplified calculation)
            base_x = int(2 ** (zoom - 1))  # Rough center X
            base_y = int(2 ** (zoom - 1))  # Rough center Y

            result = package.map_tile(x=base_x, y=base_y, z=zoom, return_format="image")
            self.assertIsInstance(result, Image.Image)
            self.assertEqual(result.size, (256, 256))

    def test_performance_basic(self):
        """Basic performance test for tile generation."""
        import time

        # Create a reasonably sized dataset
        large_data = {
            "grid": np.random.rand(500, 500) * 100,
        }
        large_metadata = {
            "bounds": [-75.0, 40.0, -73.0, 42.0],
            "crs": "EPSG:4326",
        }

        package = MyrezeDataPackage(
            id="performance-test",
            data=large_data,
            time=Time.timestamp("2023-01-01T00:00:00Z"),
            metadata=large_metadata,
            visualization_type="map_tile",
        )

        # Time tile generation
        start_time = time.time()
        result = package.map_tile(x=300, y=380, z=10)
        end_time = time.time()

        # Should complete reasonably quickly (under 5 seconds for this size)
        self.assertLess(end_time - start_time, 5.0)
        self.assertIsInstance(result, bytes)


if __name__ == "__main__":
    # Suppress warnings during tests
    warnings.filterwarnings("ignore", category=UserWarning)

    unittest.main(verbosity=2)
