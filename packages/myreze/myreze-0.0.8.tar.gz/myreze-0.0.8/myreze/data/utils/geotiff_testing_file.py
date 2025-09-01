#!/usr/bin/env python
"""
Test script for zarr data processing and GeoTIFF output.
This script demonstrates:
1. Loading data from a zarr file
2. Extracting a weather variable with timestep/level interpolation
3. Cropping to a specific region
4. Reprojecting to a desired CRS
5. Saving the result as a GeoTIFF
"""

import os

# Import our modules
from myreze.data.utils.zarr_reader import read_zarr_data
from myreze.data.utils.crop_and_reproject_array import (
    process_georeferenced_array,
    save_as_geotiff
)

# Configuration for the test
ZARR_PATH = "C:/Users/Havard/prediction_20250403_164054_gdas_20250402_12_gencast_Enhanced.zarr"  # Path to zarr dataset
VARIABLE = "2m_temperature"              # Weather variable to extract
OUTPUT_PATH = "C:/Users/Havard/Desktop/output_test.tif"       # Output GeoTIFF path
TIMESTEP = 0                       # Timestep index (can be float for interpolation)
LEVEL = 12                          # Level index (can be float for interpolation)
BBOX = [-140, -20, -47, 58]          # Bounding box [xmin, ymin, xmax, ymax]
RESOLUTION = 1024                    # Output resolution in pixels
OUTPUT_CRS = 'EPSG:3857'             # Output coordinate reference system

def process_zarr_to_array(zarr_path, weather_layer, timestep, level,
                         output_bbox, resolution=1024, output_crs='EPSG:3857'):
    """
    Combined pipeline that extracts data from zarr and processes it.
    This function connects the zarr_reader and crop_and_reproject modules.

    Args:
        zarr_path: Path to the zarr dataset
        weather_layer: Name of the variable to extract
        timestep: Time index or interpolation value
        level: Level index or interpolation value (if applicable)
        output_bbox: Bounding box for output [xmin, ymin, xmax, ymax]
        resolution: Output resolution in pixels
        output_crs: Destination coordinate reference system

    Returns:
        tuple: (processed_array, metadata)
    """
    # Extract data from zarr file
    data_array, transform, crs, input_metadata = read_zarr_data(
        zarr_path, weather_layer, timestep, level
    )

    # Process the array (uses default cubic_spline resampling from crop_and_reproject_array)
    processed_array, output_metadata = process_georeferenced_array(
        data_array, transform, crs,
        bbox=output_bbox,
        resolution=resolution,
        dst_crs=output_crs
    )

    # Add information about the source data to the output metadata
    output_metadata.update({
        'source': {
            'zarr_path': zarr_path,
            'weather_layer': weather_layer,
            'timestep': timestep,
            'level': level
        }
    })

    return processed_array, output_metadata

def main():
    """Main function to process zarr data and save as GeoTIFF."""
    print(f"Processing zarr file: {ZARR_PATH}")
    print(f"Extracting variable: {VARIABLE}")
    print(f"Timestep: {TIMESTEP}, Level: {LEVEL}")

    try:
        # Check if zarr file exists
        if not os.path.exists(ZARR_PATH):
            raise FileNotFoundError(f"Zarr file not found: {ZARR_PATH}")

        # Process zarr data to array (using the combined function in this test script)
        print("\nProcessing zarr data...")
        result_array, result_metadata = process_zarr_to_array(
            ZARR_PATH,
            VARIABLE,
            TIMESTEP,
            LEVEL,
            output_bbox=BBOX,
            resolution=RESOLUTION,
            output_crs=OUTPUT_CRS
        )

        print(f"Result array shape: {result_array.shape}")
        print(f"Output CRS: {result_metadata['crs']}")

        # Save as GeoTIFF
        print(f"\nSaving to GeoTIFF: {OUTPUT_PATH}")
        save_as_geotiff(
            result_array,
            result_metadata['transform'],
            result_metadata['crs'],
            OUTPUT_PATH
        )

    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

    return 0

if __name__ == "__main__":
    main()
