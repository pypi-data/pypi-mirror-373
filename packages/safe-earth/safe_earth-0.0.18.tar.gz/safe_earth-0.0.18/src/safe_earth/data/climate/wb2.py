from typing import List
import numpy as np
import xarray as xr
import zarr
import cfgrib
import gcsfs
import fsspec
from safe_earth.data.climate import wb2_stores
from safe_earth.data.climate.era5 import ERA5Var

def get_wb2_preds(
        model_name: str,
        resolution: str,
        lead_times: List[np.timedelta64],
        time: slice = slice('2020-01-01', '2020-12-31'),
        variables: List[ERA5Var] = [ERA5Var('temperature', 850, 'T850'), ERA5Var('geopotential', 500, 'Z500')]
    ) -> xr.Dataset:

    if not model_name in wb2_stores.models:
        raise ValueError(f'Model {model_name} not exposed through WB2 API, check data/wb2_stores.py')
    elif not resolution in wb2_stores.models[model_name]:
        raise ValueError(f'Resolution {resolution} not available for model {model_name}, check data/wb2_stores.py')

    ds = xr.open_zarr(wb2_stores.models[model_name][resolution])
    ds = ds.sel(time=time)

    for v in variables:
        if v.level:
            ds[v.name] = ds[v.variable].sel(level=v.level)
        else:
            ds[v.name] = ds[v.variable]
    ds = ds[[v.name for v in variables]]

    # TODO: support more resolutions
    if resolution == '240x121':
        ds['latitude'] = np.round(ds['latitude'], 1) # TODO: generalize/remove if not 240x121
        ds['longitude'] = np.round(ds['longitude'], 1) # TODO: generalize/remove if not 240x121
        ds = ds.assign_coords(longitude=(((ds.longitude + 180) % 360) - 180)) # TODO: will likely need to do this at all resolutions

    ds = ds.sel(prediction_timedelta=ds.prediction_timedelta.isin(lead_times))

    return ds
