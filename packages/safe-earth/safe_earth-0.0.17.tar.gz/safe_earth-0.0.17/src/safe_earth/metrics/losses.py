import xarray as xr
import geopandas as gpd
import pandas as pd
import shapely
from safe_earth.utils.surface_area import *
from safe_earth.utils.geometry_funcs import *
from typing import List
import pdb

def climate_weighted_l2(
        data: xr.Dataset, 
        ground_truth: xr.Dataset,
        lon_dim: str,
        lat_dim: str,
        lead_time_dim: str,
        reduction_dims: List[str] = ['time'],
        use_polygons: bool = True,
        polygon_edge_in_degrees: float = 1.5 # TODO: remove with automatic polygon creation
    ) -> gpd.GeoDataFrame:
    '''
    Get the cell-area-weighted l2 loss of every variable (that is common to both
    data and ground_truth) at every gridpoint defined by (lon, lat) pairs.

    Parameters
    ----------
    data: xr.Dataset
        A dataset which includes predictions for some set of variables at a set
        of coordinates.
    ground_truth: xr.Dataset
        The data which has all of the ground truth data for all of the 
        variables in data. Loss will be calculated for every variable
        that is in both data and ground_truth.
    lon_dim: str TODO: default of None & dynamically handle common values (lon, long, longitude)
        The name of the dimension that stores the longitude in both data and
        ground_truth arrays.
    lat_dim: str TODO: default of None & dynamically handle common values (lat, latitude)
        The name of the dimension that stores the latitude in both data and
        ground_truth arrays.
    lead_time_dim: str
        The name of the dimension that stores the prediction lead times
    reduction_dims: List[str]
        The name of coordinates/dimensions in the arrays to reduce over. Every
        gridpoint (Point, or polygon if use_polygons==True) will have a l2
        column that will be a list of values, one value for each index it has
        a reduced dim. The actual reduction will occur later in calculating
        the error.
    use_polygons: bool
        If True, then each coordinate is turned into a polygon rather than a
        Point. All polygons are non-overlapping and generated with a greedy
        algorithm that will draw the borders at the mean of each dimension
        with its neighboring coordinate. The result of using polygons is that
        the prediction the metric calculated at that gridpoint will be
        attributed to every metadata group that the polygon overlaps, rather
        than just the metadata group that the exact coordinate point is at.
        For territory, subregion, and income, the metric will be attributed
        to all of the territories/subregions/income group that overlap with
        the polygon. For landcover, the majority of the landcover type of the
        land it overlaps will be assigned.
    polygon_edge_in_degrees: float
        The length of polygon edges used if use_polygons==True.

    Returns
    -------
    gpd.GeoDataFrame
        A dataframe with unique geometries for each gridpoint (Point, or
        polygon if use_polygon==True) where the l2 loss is added as a
        dataframe column (it will be a list where each value is the l2 at that
        gridpoint for each of its values in reduction_dims [by defualt, each
        timestep]). There will be a column in the dataframe for each variable
        in data.
    '''
    
    if not ((data[lon_dim] == ground_truth[lon_dim]).all() and (data[lat_dim] == ground_truth[lat_dim]).all()):
        raise ValueError('Shapes of data and ground_truth must be the same, with coordinates in the same order')
    
    # TODO: handle non-empty preserved_dims
    preserved_dims = [dim for dim in data.dims if (not (dim in [lat_dim, lon_dim, lead_time_dim] or dim in reduction_dims))]
    if not preserved_dims == []:
        raise ValueError("Dimension preservation is not yet supported")
    
    lat_weights = get_cell_weights((data.sizes[lon_dim], data.sizes[lat_dim]), lat_index=1)
    variables = [v for v in data.data_vars if v in ground_truth.data_vars]

    output_gdf = gpd.GeoDataFrame()
    for lead_time in data[lead_time_dim]:
        lead_time_int = np.timedelta64(lead_time.values, 'h').astype(int)
        # TODO: call general/non-climate method that does the looping over variables

        for variable in variables:
            preds = data[variable].sel(prediction_timedelta=lead_time)
            preds = preds.transpose(lon_dim, lat_dim, *reduction_dims, *preserved_dims)
            gt = ground_truth[variable].sel(time=ground_truth.time.isin(preds.time+lead_time))
            gt = gt.transpose(lon_dim, lat_dim, *reduction_dims, *preserved_dims)
            
            # TODO: pass preds and values to different (even more) subfunctions, one for each loss function
            diffs = preds.values - gt.values
            lat_weights = lat_weights.reshape(lat_weights.shape + (1,)*(diffs.ndim-lat_weights.ndim))
            weighted_l2 = lat_weights*(diffs**2)
            reduction_array_len = np.prod([data.sizes[dim] for dim in reduction_dims])
            weighted_l2 = weighted_l2.reshape(
                data.sizes[lon_dim]*data.sizes[lat_dim], 
                reduction_array_len, 
                *weighted_l2.shape[2+len(reduction_dims):]
            )
            
            mesh_lon, mesh_lat = np.meshgrid(data[lon_dim].values, data[lat_dim].values, indexing='ij')
            flat_lons = mesh_lon.flatten()
            flat_lats = mesh_lat.flatten()
            geometry = [shapely.Point(xy) for xy in zip(flat_lons, flat_lats)]
            if use_polygons:
                geometry = square_polygons_from_points(geometry, polygon_edge_in_degrees)

            df = pd.DataFrame({
                lon_dim: flat_lons,
                lat_dim: flat_lats,
                "weighted_l2": [row[~np.isnan(row)].tolist() for row in weighted_l2]
            })
            gdf = gpd.GeoDataFrame(df, geometry=geometry, crs=4326)
            gdf['variable'] = variable
            gdf['lead_time'] = lead_time_int

            output_gdf = pd.concat([output_gdf, gdf], ignore_index=True)

    return output_gdf
