#!/usr/bin/env python
"""
Tests for data package functionality.
"""

import unittest
from myreze.data import MyrezeDataPackage, Geometry


class TestDataPackage(unittest.TestCase):
    def test_create_data_package(self):
        """Test creating a data package."""
        data_package = MyrezeDataPackage()
        self.assertIsInstance(data_package, MyrezeDataPackage)

    def test_geometry(self):
        """Test geometry functionality."""
        geometry = Geometry()
        self.assertIsInstance(geometry, Geometry)


if __name__ == "__main__":
    unittest.main()
