'''
The data returned from the get_era5 method in this file contains 
modified Copernicus Climate Change Service information 2025.
'''

from typing import Literal, List
import numpy as np
import pandas as pd
import xarray as xr
import zarr
import cfgrib
import gcsfs
import fsspec
from safe_earth.data.climate import wb2_stores

class ERA5Var:
    def __init__(self, variable_name_in_xarray: str, vertical_level: int = None, name: str = None):
        self.variable = variable_name_in_xarray
        self.level = vertical_level
        if name:
            self.name = name
        elif vertical_level:
            self.name = f'{variable_name_in_xarray}_{vertical_level}'
        else:
            self.name = variable_name_in_xarrays

# TODO: support more resolutions
def get_era5(
        resolution: Literal['240x121', '1440x721'],
        time: slice = slice('2020-01-01T00', '2021-01-11T00'),
        variables: List[ERA5Var] = [ERA5Var('temperature', 850, 'T850'), ERA5Var('geopotential', 500, 'Z500')],
    ) -> xr.Dataset:
    '''
    Get ERA5 data from the WeatherBench 2 API, by default gets data for 2020
    plus 10 days to accommodate lead times up to 10 days.
    '''

    if not resolution in wb2_stores.era5:
        raise ValueError(f'Resolution {resolution} is not supported')
    else:
        store = wb2_stores.era5[resolution]

    era5 = xr.open_zarr(
        store,
        storage_options={"token": "anon"}, 
        consolidated=True
    )
    era5 = era5.sel(time=time)

    for v in variables:
        if v.level:
            era5[v.name] = era5[v.variable].sel(level=v.level)
        else:
            era5[v.name] = era5[v.variable]
    era5 = era5[[v.name for v in variables]]

    if resolution == '240x121':
        era5['latitude'] = np.round(era5['latitude'], 1)
        era5['longitude'] = np.round(era5['longitude'], 1)
        era5 = era5.assign_coords(longitude=(((era5.longitude + 180) % 360) - 180)) # TODO: will likely need to do this at all resolutions
    # TODO: support more resolutions

    return era5
