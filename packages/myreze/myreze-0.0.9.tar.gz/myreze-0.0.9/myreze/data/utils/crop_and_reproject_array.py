import numpy as np
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling, transform_bounds
from rasterio.transform import from_bounds


class ArrayProcessor:
    """
    Class for processing georeferenced numpy arrays with cropping, reprojection,
    and resampling capabilities.
    """
    def __init__(self):
        self.bbox = None  # Output bounding box [xmin, ymin, xmax, ymax]
        self.resolution = 1024  # Output resolution (pixels)
        self.crs = 'EPSG:3857'  # Default to Web Mercator
        self.resampling = Resampling.cubic_spline  # Default resampling method

    def process_array(self, data_array, src_transform, src_crs):
        """
        Process the input array by cropping, resampling, and reprojecting
        to the specified output parameters.

        Args:
            data_array: NumPy array with the source data
            src_transform: Source transform
            src_crs: Source coordinate reference system

        Returns:
            NumPy array: Processed array at specified resolution and extent
        """
        if self.bbox is None:
            raise ValueError("Output bounding box not specified")

        # Extract bounding box coordinates
        xmin, ymin, xmax, ymax = self.bbox

        # Validate against source bounds
        src_height, src_width = data_array.shape
        src_bounds = (
            src_transform.c,                                  # left
            src_transform.f + src_transform.e * src_height,   # bottom
            src_transform.c + src_transform.a * src_width,    # right
            src_transform.f                                   # top
        )

        # Clip the bbox to the source bounds
        valid_xmin = max(xmin, src_bounds[0])
        valid_ymin = max(ymin, src_bounds[1])
        valid_xmax = min(xmax, src_bounds[2])
        valid_ymax = min(ymax, src_bounds[3])

        if valid_xmin >= valid_xmax or valid_ymin >= valid_ymax:
            raise ValueError("Specified bounding box is outside the raster extent")

        # Transform bounds to destination CRS
        dst_bounds = transform_bounds(src_crs, self.crs, valid_xmin, valid_ymin, valid_xmax, valid_ymax)
        dst_xmin, dst_ymin, dst_xmax, dst_ymax = dst_bounds

        # Calculate width and height in the destination CRS
        width = dst_xmax - dst_xmin
        height = dst_ymax - dst_ymin

        # Create a square extent centered on the original bounds (optional, can be customized)
        if width > height:
            # Height is smaller, expand it to make a square
            center_y = (dst_ymin + dst_ymax) / 2
            dst_ymin = center_y - width / 2
            dst_ymax = center_y + width / 2
        else:
            # Width is smaller, expand it to make a square
            center_x = (dst_xmin + dst_xmax) / 2
            dst_xmin = center_x - height / 2
            dst_xmax = center_x + height / 2

        # Create transform for the square output
        dst_transform = from_bounds(dst_xmin, dst_ymin, dst_xmax, dst_ymax, self.resolution, self.resolution)

        # Create square output array
        resampled_data = np.empty((self.resolution, self.resolution), dtype=data_array.dtype)

        # Reproject data
        reproject(
            source=data_array,
            destination=resampled_data,
            src_transform=src_transform,
            src_crs=src_crs,
            dst_transform=dst_transform,
            dst_crs=self.crs,
            resampling=self.resampling
        )

        # Return the processed array with metadata
        output_metadata = {
            'transform': dst_transform,
            'crs': self.crs,
            'bounds': [dst_xmin, dst_ymin, dst_xmax, dst_ymax],
            'resolution': self.resolution,
            'shape': resampled_data.shape
        }

        return resampled_data, output_metadata


def process_georeferenced_array(data_array, src_transform, src_crs,
                               bbox, resolution=1024, dst_crs='EPSG:3857',
                               resampling_method=Resampling.cubic_spline):
    """
    Convenience function to process a georeferenced array without needing to create
    an ArrayProcessor instance manually.

    Args:
        data_array: NumPy array with the source data
        src_transform: Source transform
        src_crs: Source coordinate reference system
        bbox: Bounding box [xmin, ymin, xmax, ymax]
        resolution: Output resolution in pixels
        dst_crs: Destination coordinate reference system
        resampling_method: Resampling method from rasterio.warp.Resampling

    Returns:
        tuple: (processed_array, metadata)
    """
    processor = ArrayProcessor()
    processor.bbox = bbox
    processor.resolution = resolution
    processor.crs = dst_crs
    processor.resampling = resampling_method

    return processor.process_array(data_array, src_transform, src_crs)


def save_as_geotiff(array, transform, crs, output_path, nodata=None):
    """
    Save a processed numpy array as a GeoTIFF file with proper geospatial metadata.
    This function is for verification purposes only.

    Args:
        array: The processed NumPy array
        transform: Affine transform for the output raster
        crs: Coordinate reference system for the output
        output_path: Path where the GeoTIFF will be saved
        nodata: Optional nodata value
    """
    # Define metadata for the GeoTIFF
    metadata = {
        'driver': 'GTiff',
        'height': array.shape[0],
        'width': array.shape[1],
        'count': 1,
        'dtype': array.dtype,
        'crs': crs,
        'transform': transform,
        'nodata': nodata,
    }

    # Save the array as a GeoTIFF
    with rasterio.open(output_path, 'w', **metadata) as dst:
        dst.write(array, 1)  # Write to the first band

    print(f"GeoTIFF saved to: {output_path}")
