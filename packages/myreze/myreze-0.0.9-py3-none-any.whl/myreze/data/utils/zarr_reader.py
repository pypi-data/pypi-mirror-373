import numpy as np
import xarray as xr
import os
from rasterio.transform import from_origin


class ZarrReader:
    """
    Class for managing input data from zarr files and extracting weather variables
    with interpolation capabilities.
    """
    def __init__(self, zarr_path=None):
        self.zarr_path = zarr_path
        self.ds = None
        self.weather_layer = None  # Variable name to extract (e.g., 'temperature')
        self.timestep = 0  # Can be float for interpolation (e.g., 10.5)
        self.level = 0  # Can be float for interpolation (e.g., 2.5)

    def load_dataset(self, chunks=False):
        """
        Load the zarr dataset from the specified path
        """
        if not self.zarr_path:
            raise ValueError("Zarr path is not set")

        self.ds = xr.open_zarr(self.zarr_path, chunks=chunks, decode_timedelta=True)
        if chunks is False:
            self.ds = self.ds.compute()
        return self.ds

    def extract_array(self):
        """
        Extract a numpy array from the zarr dataset for the specified weather layer,
        with interpolation for timestep and level if necessary.

        Returns:
            tuple: (data_array, transform, crs, metadata)
        """
        if self.ds is None:
            raise ValueError("Dataset not loaded. Call load_dataset() first.")

        if self.weather_layer is None:
            raise ValueError("Weather layer not specified")

        variable_name = self.weather_layer
        time_idx = float(self.timestep)

        # Check if the variable has a level dimension
        has_level = 'level' in self.ds[variable_name].dims
        level_idx = float(self.level) if has_level else None

        # Time interpolation indices
        time_idx_floor = int(np.floor(time_idx))
        time_idx_ceil = int(np.ceil(time_idx))

        # Handle edge case for integer time index
        if time_idx_floor == time_idx_ceil:
            time_idx_ceil = time_idx_floor + 1
            if time_idx_ceil >= len(self.ds.time):
                time_idx_ceil = time_idx_floor
                time_idx_floor = max(0, time_idx_floor - 1)

        time_weight = (time_idx - time_idx_floor) / max(1, time_idx_ceil - time_idx_floor)

        # Common selection parameters (if dataset has these dimensions)
        select_params = {}
        if 'sample' in self.ds[variable_name].dims:
            select_params['sample'] = 0
        if 'batch' in self.ds[variable_name].dims:
            select_params['batch'] = 0

        # Extract and interpolate data
        if has_level and level_idx is not None:
            # Level interpolation indices
            level_idx_floor = int(np.floor(level_idx))
            level_idx_ceil = int(np.ceil(level_idx))

            # Handle edge case for integer level index
            if level_idx_floor == level_idx_ceil:
                level_idx_ceil = level_idx_floor + 1
                if level_idx_ceil >= len(self.ds.level):
                    level_idx_ceil = level_idx_floor
                    level_idx_floor = max(0, level_idx_floor - 1)

            level_weight = (level_idx - level_idx_floor) / max(1, level_idx_ceil - level_idx_floor)

            # Get data for all four corners for bilinear interpolation
            data_tl = self.ds[variable_name].isel(time=time_idx_floor, level=level_idx_floor, **select_params).values
            data_tr = self.ds[variable_name].isel(time=time_idx_ceil, level=level_idx_floor, **select_params).values
            data_bl = self.ds[variable_name].isel(time=time_idx_floor, level=level_idx_ceil, **select_params).values
            data_br = self.ds[variable_name].isel(time=time_idx_ceil, level=level_idx_ceil, **select_params).values

            # Bilinear interpolation
            top = (1 - time_weight) * data_tl + time_weight * data_tr
            bottom = (1 - time_weight) * data_bl + time_weight * data_br
            data_array = (1 - level_weight) * top + level_weight * bottom
        else:
            # Time interpolation only
            data_floor = self.ds[variable_name].isel(time=time_idx_floor, **select_params).values
            data_ceil = self.ds[variable_name].isel(time=time_idx_ceil, **select_params).values
            data_array = (1 - time_weight) * data_floor + time_weight * data_ceil

        # Check if latitudes need flipping (make sure north is up)
        if self.ds.lat[0].item() < self.ds.lat[-1].item():
            data_array = np.flipud(data_array)

        # Handle longitude wrapping to ensure -180 to 180 range
        lon_values = self.ds.lon.values
        if np.any(lon_values >= 180):
            split_index = np.where(lon_values >= 180)[0][0]
            data_array = np.roll(data_array, -split_index, axis=1)

        # Calculate grid cell size from dataset
        if hasattr(self.ds, 'lon') and hasattr(self.ds, 'lat'):
            lon_res = abs(float(self.ds.lon[1] - self.ds.lon[0]))
            lat_res = abs(float(self.ds.lat[1] - self.ds.lat[0]))
            # Use average resolution if they differ
            cell_size = (lon_res + lat_res) / 2
        else:
            # Default cell size if we can't determine from dataset
            cell_size = 0.25

        # Define the geospatial transform
        transform = from_origin(
            west=-180.0,
            north=90.0,
            xsize=cell_size,
            ysize=cell_size
        )

        # Define source CRS (WGS84)
        crs = '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'

        # Create metadata dictionary
        metadata = {
            'variable': variable_name,
            'timestep': self.timestep,
            'level': self.level if has_level else None,
            'cell_size': cell_size,
            'crs': crs,
            'bounds': [-180, -90, 180, 90],  # Global extent [west, south, east, north]
            'shape': data_array.shape,
            'dtype': str(data_array.dtype)
        }

        return data_array, transform, crs, metadata


def read_zarr_data(zarr_path, weather_layer, timestep=0, level=0):
    """
    Convenience function to extract data from a zarr file without needing to create
    a ZarrReader instance manually.

    Args:
        zarr_path: Path to the zarr dataset
        weather_layer: Name of the variable to extract
        timestep: Time index or interpolation value
        level: Level index or interpolation value (if applicable)

    Returns:
        tuple: (data_array, transform, crs, metadata)
    """
    reader = ZarrReader(zarr_path)
    reader.load_dataset()
    reader.weather_layer = weather_layer
    reader.timestep = timestep
    reader.level = level

    return reader.extract_array()
