import numpy as np
import xarray as xr
import math
import pdb

def flip_xarray_over_equator(
    array: xr.core.dataarray.DataArray | xr.core.dataset.Dataset,
    latitude_coord_name: str) \
    -> xr.core.dataarray.DataArray | xr.core.dataset.Dataset:

    assert latitude_coord_name in ['lat', 'latitude']
    if latitude_coord_name == 'lat':
        flipped_array = array.reindex(lat=list(reversed(array.lat)))
    elif latitude_coord_name == 'latitude':
        flipped_array = array.reindex(latitude=list(reversed(array.latitude)))
    return flipped_array

def shift_xarray(
    array: xr.core.dataarray.DataArray | xr.core.dataset.Dataset,
    num_indices_to_shift_by: int,
    longitude_coord_name: str) \
    -> xr.core.dataarray.DataArray | xr.core.dataset.Dataset:

    assert longitude_coord_name in ['lon', 'long', 'longitude']
    if longitude_coord_name == 'lon':
        shifted_array = array.roll(lon=num_indices_to_shift_by, roll_coords=True)
    elif longitude_coord_name == 'long':
        shifted_array = array.roll(long=num_indices_to_shift_by, roll_coords=True)
    elif longitude_coord_name == 'longitude':
        shifted_array = array.roll(longitude=num_indices_to_shift_by, roll_coords=True)
    return shifted_array
