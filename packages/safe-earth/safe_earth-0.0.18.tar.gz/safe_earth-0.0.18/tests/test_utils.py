import pytest
import pdb
import math
import numpy as np
import xarray as xr
import pygmt
import shapely
from safe_earth.utils.surface_area import *
from safe_earth.utils.xarray_funcs import *
from safe_earth.utils.geometry_funcs import *

# https://mathworld.wolfram.com/OblateSpheroid.html
# 2*math.pi*a*a+math.pi*(c**2/e)*math.log((1+e)/(1-e)) # inprecise to use python for calculation
EARTH_SURFACE_AREA = 510065604944206.145

def test_surface_area_shape():
    areas = get_cell_areas((2,4))
    assert areas.shape == (2,4)

    areas = get_cell_areas((2,5))
    assert areas.shape == (2,5)

    areas = get_cell_areas((4,2), lat_index=1)
    assert areas.shape == (4,2)

    areas = get_cell_areas((5,2), lat_index=1)
    assert areas.shape == (5,2)

    areas = get_cell_areas((4,8))
    assert areas.shape == (4,8)

    areas = get_cell_areas((32,64))
    assert areas.shape == (32,64)

    areas = get_cell_areas((720,1440))
    assert areas.shape == (720,1440)

    areas = get_cell_areas((4320,8640))
    assert areas.shape == (4320,8640)

    areas = get_cell_areas((21600,43200))
    assert areas.shape == (21600,43200)

    areas = get_cell_areas((10,400))
    assert areas.shape == (10,400)

def test_total_surface_area():
    areas = get_cell_areas((2,4))
    assert np.allclose(np.sum(areas), EARTH_SURFACE_AREA)

    areas = get_cell_areas((4,8))
    assert np.allclose(np.sum(areas), EARTH_SURFACE_AREA)

    areas = get_cell_areas((32,64))
    assert np.allclose(np.sum(areas), EARTH_SURFACE_AREA)

    areas = get_cell_areas((720, 1440))
    assert np.allclose(np.sum(areas), EARTH_SURFACE_AREA)

    areas = get_cell_areas((721, 1440))
    assert np.allclose(np.sum(areas), EARTH_SURFACE_AREA)

    areas = get_cell_areas((1440, 720), lat_index=1)
    assert np.allclose(np.sum(areas), EARTH_SURFACE_AREA)

    areas = get_cell_areas((1440, 721), lat_index=1)
    assert np.allclose(np.sum(areas), EARTH_SURFACE_AREA)

    areas = get_cell_areas((4320,8640))
    assert np.allclose(np.sum(areas), EARTH_SURFACE_AREA)

    areas = get_cell_areas((21600,43200))
    assert np.allclose(np.sum(areas), EARTH_SURFACE_AREA)

    areas = get_cell_areas((43200,86400))
    assert np.allclose(np.sum(areas), EARTH_SURFACE_AREA)

    areas = get_cell_areas((10,400))
    assert np.allclose(np.sum(areas), EARTH_SURFACE_AREA)

def test_surface_area_max_is_equator():
    areas = get_cell_areas((2,4))
    equator_top_index = (areas.shape[0]//2)-1
    argmax = np.unravel_index(np.argmax(areas), areas.shape)
    assert equator_top_index == argmax[0]
    assert np.allclose(areas[equator_top_index], areas[equator_top_index+1])

    areas = get_cell_areas((4,8))
    equator_top_index = (areas.shape[0]//2)-1
    argmax = np.unravel_index(np.argmax(areas), areas.shape)
    assert equator_top_index == argmax[0]
    assert np.allclose(areas[equator_top_index], areas[equator_top_index+1])

    areas = get_cell_areas((32,64))
    equator_top_index = (areas.shape[0]//2)-1
    argmax = np.unravel_index(np.argmax(areas), areas.shape)
    assert equator_top_index == argmax[0]
    assert np.allclose(areas[equator_top_index], areas[equator_top_index+1])

    areas = get_cell_areas((720, 1440))
    equator_top_index = (areas.shape[0]//2)-1
    argmax = np.unravel_index(np.argmax(areas), areas.shape)
    assert equator_top_index == argmax[0]
    assert np.allclose(areas[equator_top_index], areas[equator_top_index+1])

    areas = get_cell_areas((721, 1440))
    equator_index = areas.shape[0]//2
    argmax = np.unravel_index(np.argmax(areas), areas.shape)
    assert equator_index == argmax[0]
    assert np.allclose(areas[equator_index-1], areas[equator_index+1])

    areas = get_cell_areas((1440, 720), lat_index=1)
    equator_top_index = (areas.shape[1]//2)-1
    argmax = np.unravel_index(np.argmax(areas), areas.shape)
    assert equator_top_index == argmax[1]
    assert np.allclose(areas[0, equator_top_index], areas[0, equator_top_index+1])

    areas = get_cell_areas((1440, 721), lat_index=1)
    equator_index = (areas.shape[1]//2)
    argmax = np.unravel_index(np.argmax(areas), areas.shape)
    assert equator_index == argmax[1]
    assert np.allclose(areas[0, equator_index-1], areas[0, equator_index+1])

    areas = get_cell_areas((4320,8640))
    equator_top_index = (areas.shape[0]//2)-1
    argmax = np.unravel_index(np.argmax(areas), areas.shape)
    assert equator_top_index == argmax[0]
    assert np.allclose(areas[equator_top_index], areas[equator_top_index+1])

    areas = get_cell_areas((21600,43200))
    equator_top_index = (areas.shape[0]//2)-1
    argmax = np.unravel_index(np.argmax(areas), areas.shape)
    assert equator_top_index == argmax[0]
    assert np.allclose(areas[equator_top_index], areas[equator_top_index+1])

    areas = get_cell_areas((10,400))
    equator_top_index = (areas.shape[0]//2)-1
    argmax = np.unravel_index(np.argmax(areas), areas.shape)
    assert equator_top_index == argmax[0]
    assert np.allclose(areas[equator_top_index], areas[equator_top_index+1])

def test_surface_area_is_monotonic_over_lat():
    areas = get_cell_areas((2,4))
    for i in range(areas.shape[0]//2-1):
        assert np.all(areas[i] == areas[i, 0])
        assert areas[i, 0] < areas[i+1, 0]
    assert np.all(areas[areas.shape[0]//2-1] == areas[areas.shape[0]//2-1, 0])
    for i in range(areas.shape[0]//2, areas.shape[0]-1):
        assert np.all(areas[i] == areas[i, 0])
        assert areas[i, 0] > areas[i+1, 0]
    assert np.all(areas[areas.shape[0]-1] == areas[areas.shape[0]-1, 0])

    areas = get_cell_areas((4,8))
    for i in range(areas.shape[0]//2-1):
        assert np.all(areas[i] == areas[i, 0])
        assert areas[i, 0] < areas[i+1, 0]
    assert np.all(areas[areas.shape[0]//2-1] == areas[areas.shape[0]//2-1, 0])
    for i in range(areas.shape[0]//2, areas.shape[0]-1):
        assert np.all(areas[i] == areas[i, 0])
        assert areas[i, 0] > areas[i+1, 0]
    assert np.all(areas[areas.shape[0]-1] == areas[areas.shape[0]-1, 0])

    areas = get_cell_areas((32,64))
    for i in range(areas.shape[0]//2-1):
        assert np.all(areas[i] == areas[i, 0])
        assert areas[i, 0] < areas[i+1, 0]
    assert np.all(areas[areas.shape[0]//2-1] == areas[areas.shape[0]//2-1, 0])
    for i in range(areas.shape[0]//2, areas.shape[0]-1):
        assert np.all(areas[i] == areas[i, 0])
        assert areas[i, 0] > areas[i+1, 0]
    assert np.all(areas[areas.shape[0]-1] == areas[areas.shape[0]-1, 0])

    areas = get_cell_areas((720, 1440))
    for i in range(areas.shape[0]//2-1):
        assert np.all(areas[i] == areas[i, 0])
        assert areas[i, 0] < areas[i+1, 0]
    assert np.all(areas[areas.shape[0]//2-1] == areas[areas.shape[0]//2-1, 0])
    for i in range(areas.shape[0]//2, areas.shape[0]-1):
        assert np.all(areas[i] == areas[i, 0])
        assert areas[i, 0] > areas[i+1, 0]
    assert np.all(areas[areas.shape[0]-1] == areas[areas.shape[0]-1, 0])

    areas = get_cell_areas((721, 1440))
    for i in range(areas.shape[0]//2):
        assert np.all(areas[i] == areas[i, 0])
        assert areas[i, 0] < areas[i+1, 0]
    assert np.all(areas[areas.shape[0]//2] == areas[areas.shape[0]//2, 0])
    for i in range(areas.shape[0]//2, areas.shape[0]-1):
        assert np.all(areas[i] == areas[i, 0])
        assert areas[i, 0] > areas[i+1, 0]
    assert np.all(areas[areas.shape[0]-1] == areas[areas.shape[0]-1, 0])

    areas = get_cell_areas((1440, 720), lat_index=1)
    for i in range(areas.shape[1]//2-1):
        assert np.all(areas[:, i] == areas[0, i])
        assert areas[0, i] < areas[0, i+1]
    assert np.all(areas[:, areas.shape[1]//2-1] == areas[0, areas.shape[1]//2-1])
    for i in range(areas.shape[1]//2, areas.shape[1]-1):
        assert np.all(areas[:, i] == areas[0, i])
        assert areas[0, i] > areas[0, i+1]
    assert np.all(areas[:, areas.shape[1]-1] == areas[0, areas.shape[1]-1])

    areas = get_cell_areas((1440, 721), lat_index=1)
    for i in range(areas.shape[1]//2): 
        assert np.all(areas[:, i] == areas[0, i])
        assert areas[0, i] < areas[0, i+1]
    assert np.all(areas[:, areas.shape[1]//2] == areas[0, areas.shape[1]//2])
    for i in range(areas.shape[1]//2, areas.shape[1]-1):
        assert np.all(areas[:, i] == areas[0, i])
        assert areas[0, i] > areas[0, i+1]
    assert np.all(areas[:, areas.shape[1]-1] == areas[0, areas.shape[1]-1])

    areas = get_cell_areas((4320,8640))
    for i in range(areas.shape[0]//2-1):
        assert np.all(areas[i] == areas[i, 0])
        assert areas[i, 0] < areas[i+1, 0]
    assert np.all(areas[areas.shape[0]//2-1] == areas[areas.shape[0]//2-1, 0])
    for i in range(areas.shape[0]//2, areas.shape[0]-1):
        assert np.all(areas[i] == areas[i, 0])
        assert areas[i, 0] > areas[i+1, 0]
    assert np.all(areas[areas.shape[0]-1] == areas[areas.shape[0]-1, 0])

    areas = get_cell_areas((21600,43200))
    for i in range(areas.shape[0]//2-1):
        assert np.all(areas[i] == areas[i, 0])
        assert areas[i, 0] < areas[i+1, 0]
    assert np.all(areas[areas.shape[0]//2-1] == areas[areas.shape[0]//2-1, 0])
    for i in range(areas.shape[0]//2, areas.shape[0]-1):
        assert np.all(areas[i] == areas[i, 0])
        assert areas[i, 0] > areas[i+1, 0]
    assert np.all(areas[areas.shape[0]-1] == areas[areas.shape[0]-1, 0])

    areas = get_cell_areas((10,400))
    for i in range(areas.shape[0]//2-1):
        assert np.all(areas[i] == areas[i, 0])
        assert areas[i, 0] < areas[i+1, 0]
    assert np.all(areas[areas.shape[0]//2-1] == areas[areas.shape[0]//2-1, 0])
    for i in range(areas.shape[0]//2, areas.shape[0]-1):
        assert np.all(areas[i] == areas[i, 0])
        assert areas[i, 0] > areas[i+1, 0]
    assert np.all(areas[areas.shape[0]-1] == areas[areas.shape[0]-1, 0])

def test_surface_area_symmetric_over_equator():
    areas = get_cell_areas((2,4))
    for i in range(areas.shape[0]//2):
        assert np.allclose(areas[i], areas[-(i+1)])

    areas = get_cell_areas((4,8))
    for i in range(areas.shape[0]//2):
        assert np.allclose(areas[i], areas[-(i+1)])
    
    areas = get_cell_areas((32,64))
    for i in range(areas.shape[0]//2):
        assert np.allclose(areas[i], areas[-(i+1)])
    
    areas = get_cell_areas((720, 1440))
    for i in range(areas.shape[0]//2):     
        assert np.allclose(areas[i], areas[-(i+1)])

    areas = get_cell_areas((721, 1440))
    for i in range(areas.shape[0]//2):     
        assert np.allclose(areas[i], areas[-(i+1)])

    areas = get_cell_areas((1440, 720), lat_index=1)
    for i in range(areas.shape[1]//2):     
        assert np.allclose(areas[:, i], areas[:, -(i+1)])

    areas = get_cell_areas((1440, 721), lat_index=1)
    for i in range(areas.shape[1]//2):     
        assert np.allclose(areas[:, i], areas[:, -(i+1)])
    
    areas = get_cell_areas((4320,8640)) 
    for i in range(areas.shape[0]//2):
        assert np.allclose(areas[i], areas[-(i+1)])
    
    areas = get_cell_areas((21600,43200)) 
    for i in range(areas.shape[0]//2):
        assert np.allclose(areas[i], areas[-(i+1)])

    areas = get_cell_areas((10,400))
    for i in range(areas.shape[0]//2):
        assert np.allclose(areas[i], areas[-(i+1)])

def test_approximate_equatorial_grid_distance():
    # equatorial circumference: 40075017m

    areas = areas = get_cell_areas((720, 1440))
    assert np.allclose(np.sqrt(np.max(areas)), 40075017/1440)

    areas = areas = get_cell_areas((1440, 720), lat_index=1)
    assert np.allclose(np.sqrt(np.max(areas)), 40075017/1440)

    areas = get_cell_areas((4320,8640))
    assert np.allclose(np.sqrt(np.max(areas)), 40075017/8640)

    areas = get_cell_areas((21600,43200)) 
    assert np.allclose(np.sqrt(np.max(areas)), 40075017/43200)

def test_water_coverage_sanity_check():
    landmask = pygmt.datasets.load_earth_mask(resolution='15s', registration='pixel')
    landmask = flip_xarray_over_equator(landmask, 'lat')
    areas = get_cell_areas(landmask.shape)
    ocean_area = np.where(landmask==0, 1, 0)*areas
    lake_area = np.where(landmask==2, 1, 0)*areas
    lake_in_lake_area = np.where(landmask==4, 1, 0)*areas
    perc_water = (np.sum(ocean_area)+np.sum(lake_area)+np.sum(lake_in_lake_area))/np.sum(areas)
    assert 0.707 <= perc_water <= 0.713

def test_latitude_flipping():
    # test on xr DataArray
    landmask = pygmt.datasets.load_earth_mask(resolution='01m', registration='pixel')
    flipped_landmask = flip_xarray_over_equator(landmask, 'lat')
    assert np.allclose(landmask, landmask)
    assert not np.allclose(landmask, flipped_landmask)
    for i in range(len(landmask.lat.values)//2):
        assert np.allclose(landmask.isel(lat=i), flipped_landmask.isel(lat=-(i+1)))

    # test on xr Dataset
    ds = xr.open_zarr(
        'gs://weatherbench2/datasets/era5/1959-2023_01_10-6h-64x32_equiangular_conservative.zarr', 
        storage_options={"token": "anon"}, 
        consolidated=True)
    ds = ds.isel(time=0)
    ds = ds[['2m_temperature', 'wind_speed']]
    flipped_ds = flip_xarray_over_equator(ds, 'latitude')
    assert np.allclose(ds.to_dataarray(), ds.to_dataarray())
    assert not np.allclose(ds.to_dataarray(), flipped_ds.to_dataarray())
    for i in range(len(ds.latitude.values)//2):
        assert np.allclose(ds.isel(latitude=i).to_dataarray(), flipped_ds.isel(latitude=-(i+1)).to_dataarray())

def test_longitude_shifting():
    # test on xr DataArray
    landmask = pygmt.datasets.load_earth_mask(resolution='01m', registration='pixel')
    n_shift = 100
    shifted_landmask = shift_xarray(landmask, n_shift, 'lon')
    assert np.allclose(landmask, landmask)
    assert not np.allclose(landmask, shifted_landmask)
    num_lon = len(landmask.lon.values)
    for i in range(num_lon//2):
        assert np.allclose(landmask.isel(lon=i), shifted_landmask.isel(lon=(i+n_shift)%num_lon))

    # test on xr Dataset
    ds = xr.open_zarr(
        'gs://weatherbench2/datasets/era5/1959-2023_01_10-6h-64x32_equiangular_conservative.zarr', 
        storage_options={"token": "anon"}, 
        consolidated=True)
    ds = ds.isel(time=0)
    ds = ds[['2m_temperature', 'wind_speed']]
    num_lon = len(ds.longitude.values)
    n_shift =  num_lon//2
    shifted_ds = shift_xarray(ds, n_shift, 'longitude')
    assert np.allclose(ds.to_dataarray(), ds.to_dataarray())
    assert not np.allclose(ds.to_dataarray(), shifted_ds.to_dataarray())
    for i in range(num_lon//2):
        assert np.allclose(ds.isel(longitude=i).to_dataarray(), shifted_ds.isel(longitude=(i+n_shift)%num_lon).to_dataarray())

def test_antimeridian_splitting():
    for lon in [180, -180]:
        point = shapely.Point(lon, 42)
        poly = square_polygons_from_points([point], polygon_edge_in_degrees=1.5)
        assert len(poly) == 1
        poly = poly[0]
        assert type(poly) == shapely.MultiPolygon
        intersecting_point = shapely.Point(-179.9, 41.8)
        assert poly.intersects(intersecting_point)
        intersecting_point2 = shapely.Point(179.8, 41.8)
        assert poly.intersects(intersecting_point2)
        non_intersecting_point = shapely.Point(-71.4, 41.8)
        assert not poly.intersects(non_intersecting_point)
    