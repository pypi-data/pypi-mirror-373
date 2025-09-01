"""
Tests for renderer interpolation functionality.

This module tests the new interpolation capabilities in Planar4channelTextureRenderer
and THREEPNGRenderer, ensuring they can handle native resolution data and interpolate
to desired output resolutions.
"""

import unittest
import numpy as np
import base64
import io
from PIL import Image

from myreze.data import MyrezeDataPackage, Time
from myreze.viz.threejs.flat_overlay import Planar4channelTextureRenderer
from myreze.viz.threejs.png_renderer import THREEPNGRenderer


class TestPlanar4channelTextureRendererInterpolation(unittest.TestCase):
    """Test interpolation functionality in Planar4channelTextureRenderer."""

    def setUp(self):
        """Set up test data."""
        # Create small native resolution texture data
        self.small_texture_rgb = np.random.randint(
            0, 256, (100, 150, 3), dtype=np.uint8
        )
        self.small_texture_rgba = np.random.randint(
            0, 256, (100, 150, 4), dtype=np.uint8
        )
        self.small_texture_gray = np.random.randint(0, 256, (100, 150), dtype=np.uint8)
        self.small_texture_single_channel = np.random.randint(
            0, 256, (100, 150, 1), dtype=np.uint8
        )

        # Create float texture data
        self.float_texture = np.random.rand(80, 120, 4).astype(np.float32)

        self.renderer = Planar4channelTextureRenderer()

    def test_default_interpolation_2048x2048(self):
        """Test default interpolation to 2048x2048."""
        data = {"texture": self.small_texture_rgba}

        result = self.renderer.render(data)

        self.assertEqual(result.shape, (2048, 2048, 4))
        self.assertEqual(result.dtype, np.uint8)

    def test_custom_size_square(self):
        """Test custom square size interpolation."""
        data = {"texture": self.small_texture_rgba}
        params = {"size": 512}

        result = self.renderer.render(data, params)

        self.assertEqual(result.shape, (512, 512, 4))
        self.assertEqual(result.dtype, np.uint8)

    def test_custom_size_rectangular(self):
        """Test custom rectangular size interpolation."""
        data = {"texture": self.small_texture_rgba}
        params = {"size": (800, 600)}

        result = self.renderer.render(data, params)

        self.assertEqual(result.shape, (600, 800, 4))  # height, width, channels
        self.assertEqual(result.dtype, np.uint8)

    def test_different_interpolation_methods(self):
        """Test different interpolation methods."""
        data = {"texture": self.small_texture_rgba}
        methods = ["nearest", "bilinear", "bicubic", "lanczos"]

        for method in methods:
            params = {"size": 256, "interpolation": method}
            result = self.renderer.render(data, params)

            self.assertEqual(result.shape, (256, 256, 4))
            self.assertEqual(result.dtype, np.uint8)

    def test_rgb_to_rgba_conversion(self):
        """Test RGB to RGBA conversion during interpolation."""
        data = {"texture": self.small_texture_rgb}
        params = {"size": 256}

        result = self.renderer.render(data, params)

        self.assertEqual(result.shape, (256, 256, 4))
        # Alpha channel should be 255 (fully opaque)
        self.assertTrue(np.all(result[:, :, 3] == 255))

    def test_grayscale_to_rgba_conversion(self):
        """Test grayscale to RGBA conversion during interpolation."""
        data = {"texture": self.small_texture_gray}
        params = {"size": 256}

        result = self.renderer.render(data, params)

        self.assertEqual(result.shape, (256, 256, 4))
        # R, G, B channels should be identical (grayscale)
        self.assertTrue(np.array_equal(result[:, :, 0], result[:, :, 1]))
        self.assertTrue(np.array_equal(result[:, :, 1], result[:, :, 2]))
        # Alpha channel should be 255
        self.assertTrue(np.all(result[:, :, 3] == 255))

    def test_single_channel_explicit_dimension(self):
        """Test single channel with explicit dimension (H, W, 1)."""
        data = {"texture": self.small_texture_single_channel}
        params = {"size": 256}

        result = self.renderer.render(data, params)

        self.assertEqual(result.shape, (256, 256, 4))
        # Should be converted to grayscale RGBA
        self.assertTrue(np.array_equal(result[:, :, 0], result[:, :, 1]))
        self.assertTrue(np.array_equal(result[:, :, 1], result[:, :, 2]))

    def test_float_texture_conversion(self):
        """Test float texture data conversion."""
        data = {"texture": self.float_texture}
        params = {"size": 256}

        result = self.renderer.render(data, params)

        self.assertEqual(result.shape, (256, 256, 4))
        self.assertEqual(result.dtype, np.uint8)
        # Values should be in valid uint8 range
        self.assertTrue(np.all(result >= 0))
        self.assertTrue(np.all(result <= 255))

    def test_no_interpolation_same_size(self):
        """Test that no interpolation occurs when input is already target size."""
        # Create data that's already 256x256
        exact_size_texture = np.random.randint(0, 256, (256, 256, 4), dtype=np.uint8)
        data = {"texture": exact_size_texture}
        params = {"size": 256}

        result = self.renderer.render(data, params)

        self.assertEqual(result.shape, (256, 256, 4))
        # Result should be identical to input (no interpolation artifacts)
        np.testing.assert_array_equal(result, exact_size_texture)

    def test_invalid_size_parameter(self):
        """Test error handling for invalid size parameters."""
        data = {"texture": self.small_texture_rgba}

        with self.assertRaises(ValueError):
            self.renderer.render(data, {"size": "invalid"})

        with self.assertRaises(ValueError):
            self.renderer.render(data, {"size": (100,)})  # Single element tuple

        with self.assertRaises(ValueError):
            self.renderer.render(data, {"size": (100, 200, 300)})  # Too many elements

    def test_invalid_interpolation_method(self):
        """Test error handling for invalid interpolation methods."""
        data = {"texture": self.small_texture_rgba}

        with self.assertRaises(ValueError):
            self.renderer.render(data, {"interpolation": "invalid_method"})

    def test_invalid_texture_format(self):
        """Test error handling for invalid texture formats."""
        # 5-channel texture
        invalid_texture = np.random.randint(0, 256, (100, 150, 5), dtype=np.uint8)
        data = {"texture": invalid_texture}

        with self.assertRaises(ValueError):
            self.renderer.render(data)

        # 1D texture
        invalid_texture_1d = np.random.randint(0, 256, (100,), dtype=np.uint8)
        data = {"texture": invalid_texture_1d}

        with self.assertRaises(ValueError):
            self.renderer.render(data)


class TestTHREEPNGRendererInterpolation(unittest.TestCase):
    """Test interpolation functionality in THREEPNGRenderer."""

    def setUp(self):
        """Set up test data."""
        self.renderer = THREEPNGRenderer()

        # Create small test images
        self.small_rgb_img = Image.new("RGB", (100, 150), color=(255, 0, 0))
        self.small_rgba_img = Image.new("RGBA", (100, 150), color=(0, 255, 0, 128))
        self.small_gray_img = Image.new("L", (100, 150), color=128)

        # Convert to base64
        self.rgb_png_b64 = self._image_to_base64(self.small_rgb_img)
        self.rgba_png_b64 = self._image_to_base64(self.small_rgba_img)
        self.gray_png_b64 = self._image_to_base64(self.small_gray_img)

    def _image_to_base64(self, image):
        """Helper to convert PIL Image to base64."""
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def test_default_interpolation_2048x2048(self):
        """Test default interpolation to 2048x2048."""
        data = {"png_bytes": self.rgb_png_b64}

        result_bytes = self.renderer.render(data)

        # Verify it's valid PNG
        self.assertTrue(result_bytes.startswith(b"\x89PNG"))

        # Load and check dimensions
        result_img = Image.open(io.BytesIO(result_bytes))
        self.assertEqual(result_img.size, (2048, 2048))

    def test_custom_size_square(self):
        """Test custom square size interpolation."""
        data = {"png_bytes": self.rgb_png_b64}
        params = {"size": 512}

        result_bytes = self.renderer.render(data, params)
        result_img = Image.open(io.BytesIO(result_bytes))

        self.assertEqual(result_img.size, (512, 512))

    def test_custom_size_rectangular(self):
        """Test custom rectangular size interpolation."""
        data = {"png_bytes": self.rgba_png_b64}
        params = {"size": (800, 600)}

        result_bytes = self.renderer.render(data, params)
        result_img = Image.open(io.BytesIO(result_bytes))

        self.assertEqual(result_img.size, (800, 600))

    def test_different_interpolation_methods(self):
        """Test different interpolation methods."""
        data = {"png_bytes": self.rgb_png_b64}
        methods = ["nearest", "bilinear", "bicubic", "lanczos"]

        for method in methods:
            params = {"size": 256, "interpolation": method}
            result_bytes = self.renderer.render(data, params)

            # Verify valid PNG
            self.assertTrue(result_bytes.startswith(b"\x89PNG"))

            # Check size
            result_img = Image.open(io.BytesIO(result_bytes))
            self.assertEqual(result_img.size, (256, 256))

    def test_jpeg_output_format(self):
        """Test JPEG output format."""
        data = {"png_bytes": self.rgb_png_b64}
        params = {"size": 256, "format": "JPEG", "quality": 90}

        result_bytes = self.renderer.render(data, params)

        # Verify it's JPEG
        self.assertTrue(result_bytes.startswith(b"\xff\xd8\xff"))

        # Check size
        result_img = Image.open(io.BytesIO(result_bytes))
        self.assertEqual(result_img.size, (256, 256))
        self.assertEqual(result_img.format, "JPEG")

    def test_rgba_to_jpeg_conversion(self):
        """Test RGBA to JPEG conversion (removes transparency)."""
        data = {"png_bytes": self.rgba_png_b64}
        params = {"size": 256, "format": "JPEG"}

        result_bytes = self.renderer.render(data, params)
        result_img = Image.open(io.BytesIO(result_bytes))

        self.assertEqual(result_img.format, "JPEG")
        self.assertEqual(result_img.mode, "RGB")  # No transparency in JPEG

    def test_grayscale_interpolation(self):
        """Test grayscale image interpolation."""
        data = {"png_bytes": self.gray_png_b64}
        params = {"size": 256}

        result_bytes = self.renderer.render(data, params)
        result_img = Image.open(io.BytesIO(result_bytes))

        self.assertEqual(result_img.size, (256, 256))
        self.assertEqual(result_img.mode, "L")  # Should remain grayscale

    def test_no_interpolation_same_size(self):
        """Test that original bytes are returned when no size change needed."""
        # Create image that's already 2048x2048 (default target)
        large_img = Image.new("RGB", (2048, 2048), color=(255, 0, 0))
        large_png_b64 = self._image_to_base64(large_img)

        data = {"png_bytes": large_png_b64}

        result_bytes = self.renderer.render(data)
        original_bytes = base64.b64decode(large_png_b64)

        # Should return original bytes (no re-encoding)
        self.assertEqual(result_bytes, original_bytes)

    def test_list_png_bytes(self):
        """Test handling of list of PNG bytes (uses first)."""
        data = {"png_bytes": [self.rgb_png_b64, self.rgba_png_b64]}
        params = {"size": 256}

        result_bytes = self.renderer.render(data, params)
        result_img = Image.open(io.BytesIO(result_bytes))

        self.assertEqual(result_img.size, (256, 256))

    def test_bytes_input(self):
        """Test direct bytes input (backwards compatibility)."""
        png_bytes = base64.b64decode(self.rgb_png_b64)
        data = {"png_bytes": png_bytes}
        params = {"size": 256}

        result_bytes = self.renderer.render(data, params)
        result_img = Image.open(io.BytesIO(result_bytes))

        self.assertEqual(result_img.size, (256, 256))

    def test_invalid_size_parameter(self):
        """Test error handling for invalid size parameters."""
        data = {"png_bytes": self.rgb_png_b64}

        with self.assertRaises(ValueError):
            self.renderer.render(data, {"size": "invalid"})

        with self.assertRaises(ValueError):
            self.renderer.render(data, {"size": (100,)})

    def test_invalid_interpolation_method(self):
        """Test error handling for invalid interpolation methods."""
        data = {"png_bytes": self.rgb_png_b64}

        with self.assertRaises(ValueError):
            self.renderer.render(data, {"interpolation": "invalid_method"})

    def test_invalid_output_format(self):
        """Test error handling for invalid output formats."""
        data = {"png_bytes": self.rgb_png_b64}

        with self.assertRaises(ValueError):
            self.renderer.render(data, {"format": "TIFF"})

    def test_invalid_png_data(self):
        """Test error handling for invalid PNG data."""
        data = {"png_bytes": base64.b64encode(b"not a png").decode("utf-8")}

        with self.assertRaises(ValueError):
            self.renderer.render(data)

    def test_missing_png_bytes(self):
        """Test error handling when png_bytes is missing."""
        data = {}

        with self.assertRaises(ValueError):
            self.renderer.render(data)

    def test_empty_png_bytes_list(self):
        """Test error handling for empty PNG bytes list."""
        data = {"png_bytes": []}

        with self.assertRaises(ValueError):
            self.renderer.render(data)


class TestBackwardsCompatibility(unittest.TestCase):
    """Test that the changes are backwards compatible."""

    def test_planar_renderer_backwards_compatibility(self):
        """Test that Planar4channelTextureRenderer works with existing 2048x2048 data."""
        renderer = Planar4channelTextureRenderer()

        # Create existing format data (2048x2048)
        existing_texture = np.random.randint(0, 256, (2048, 2048, 4), dtype=np.uint8)
        data = {"texture": existing_texture}

        # Should work without params (backwards compatible)
        result = renderer.render(data)

        self.assertEqual(result.shape, (2048, 2048, 4))
        # Should be identical since no interpolation needed
        np.testing.assert_array_equal(result, existing_texture)

    def test_png_renderer_backwards_compatibility(self):
        """Test that THREEPNGRenderer works with existing data."""
        renderer = THREEPNGRenderer()

        # Create existing format data
        img = Image.new("RGBA", (2048, 2048), color=(255, 0, 0, 128))
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        png_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        data = {"png_bytes": png_b64}

        # Should work without params (backwards compatible)
        result_bytes = renderer.render(data)

        # Should return original bytes (no change needed)
        original_bytes = base64.b64decode(png_b64)
        self.assertEqual(result_bytes, original_bytes)

    def test_integration_with_data_package(self):
        """Test integration with MyrezeDataPackage."""
        # Create package with small native resolution data
        small_texture = np.random.randint(0, 256, (200, 300, 4), dtype=np.uint8)

        package = MyrezeDataPackage(
            id="test-interpolation",
            data={"texture": small_texture},
            time=Time.timestamp("2023-01-01T00:00:00Z"),
            threejs_visualization=Planar4channelTextureRenderer(),
            visualization_type="flat_overlay",
        )

        # Test default rendering (should interpolate to 2048x2048)
        result = package.to_threejs()
        self.assertEqual(result.shape, (2048, 2048, 4))

        # Test custom size
        result_custom = package.to_threejs(params={"size": 512})
        self.assertEqual(result_custom.shape, (512, 512, 4))


if __name__ == "__main__":
    unittest.main(verbosity=2)
