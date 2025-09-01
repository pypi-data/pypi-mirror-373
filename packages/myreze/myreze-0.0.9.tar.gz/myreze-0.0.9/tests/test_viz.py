#!/usr/bin/env python
"""
Tests for visualization functionality.
"""

import unittest
from myreze.viz import Visualization, UnrealRenderer, ThreeJSRenderer, PNGRenderer


class TestVisualization(unittest.TestCase):
    def test_visualization(self):
        """Test visualization base class."""
        viz = Visualization()
        self.assertIsInstance(viz, Visualization)

    def test_unreal_renderer(self):
        """Test Unreal Engine renderer."""
        renderer = UnrealRenderer()
        self.assertIsInstance(renderer, UnrealRenderer)

    def test_threejs_renderer(self):
        """Test Three.js renderer."""
        renderer = ThreeJSRenderer()
        self.assertIsInstance(renderer, ThreeJSRenderer)

    def test_png_renderer(self):
        """Test PNG renderer."""
        renderer = PNGRenderer()
        self.assertIsInstance(renderer, PNGRenderer)


if __name__ == "__main__":
    unittest.main()
