import numpy as np
import xarray as xr
import math
import pdb

def get_cell_weights(data_shape: tuple, lat_index: int = 0) -> np.array:
    assert len(data_shape) == 2
    assert 0 <= lat_index <= 1
    assert data_shape[lat_index] < data_shape[1-lat_index]
    areas = get_cell_areas(data_shape, lat_index)
    if lat_index == 0:
        vertical_mean = np.mean(areas[:,0])
    else:
        vertical_mean = np.mean(areas[0,:])
    return areas/vertical_mean

def get_cell_areas(data_shape: tuple, lat_index: int = 0) -> np.array:
    '''
    Returns an np.array with the same shape as data that has the area of the cell 
    covered by each gridpoint.
    lat_index is the index into data_shape which represents the latitude dimension.

    Assumes data at [0,0] is positioned at a pole (+/- 90 degrees).

    # TODO: support non-equiangularity, requires passing in latitude & longitude coords from xarray
    Assumes the difference delta_lat in latitude between samples is constant,
    Assumes the difference delta_lon in longitude between samples is constant,
    But it is not true that delta_lat must equal delta_lon.
    '''

    assert len(data_shape) == 2
    assert 0 <= lat_index <= 1
    assert data_shape[lat_index] < data_shape[1-lat_index]
    lat_indexed = lat_index == 0
    lon_n = max(data_shape)
    lat_n = min(data_shape)
    pixel_reg_lat = (lat_n%2 == 0)

    cell_areas = np.zeros(data_shape)
    if not lat_indexed:
        cell_areas = np.rot90(cell_areas)

    # Earth constants
    equatorial_rad = 6378137 # unit: m, equal to a & b
    polar_rad = 6356752 # unit: m, equal to c

    # equation constants, precalculated at high-precision
    coeff = 127373471233042.22 # pi*a*c
    eps = 0.08209504417650265 # sqrt(a**2/c**2 - 1)
    eps_squared = 0.0067395962783419227
    a_over_c = 1.003364139422145 # a/c
    arsinh_eps = 0.08200310815403547
    last_cap = 0

    for i in range(lat_n//2):
        phi = np.deg2rad(90-(i+1)*(180/lat_n))
        h = polar_rad - (calc_rad_at_phi(phi) * math.sin(phi))
        f1 = 1 - h/polar_rad
        f2 = math.sqrt(1 + eps_squared*f1*f1)
        omega_L = coeff * ( a_over_c - f1*f2 + (arsinh_eps-math.asinh(eps*f1))/eps )
        cell_areas[i] = (omega_L - last_cap)/lon_n
        last_cap = omega_L

    # get area centered on equator
    if not pixel_reg_lat:
        phi *= -1
        h = polar_rad - (calc_rad_at_phi(phi) * math.sin(phi))
        f1 = 1 - h/polar_rad
        f2 = math.sqrt(1 + eps_squared*f1*f1)
        omega_L = coeff * ( a_over_c - f1*f2 + (arsinh_eps-math.asinh(eps*f1))/eps )
        equator_centered_SA = (omega_L - last_cap)/lon_n
        cell_areas[lat_n//2] = equator_centered_SA

    cell_areas[lat_n//2:] = cell_areas[::-1][lat_n//2:]
    if not lat_indexed:
        cell_areas = np.rot90(cell_areas, k=-1)

    return cell_areas # unit: m^2

def calc_rad_at_phi(phi):
    equatorial_rad = 6378137 # unit: m
    polar_rad = 6356752 # unit: m
    f1 = ((equatorial_rad**2)*math.cos(phi))**2
    f2 = ((polar_rad**2)*math.sin(phi))**2
    f3 = (equatorial_rad*math.cos(phi))**2
    f4 = (polar_rad*math.sin(phi))**2
    radius = math.sqrt((f1+f2)/(f3+f4))
    return radius
