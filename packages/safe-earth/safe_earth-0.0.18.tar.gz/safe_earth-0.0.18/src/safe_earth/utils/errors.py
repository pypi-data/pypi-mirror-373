import geopandas as gpd
import pandas as pd
import numpy as np
from typing import List

def rmse_wrapper(
        gdf: gpd.GeoDataFrame,
        variables: list, 
        lead_times: list, 
        loss_metrics: List[str],
        added_cols: dict[str, str] = None
    ) -> pd.DataFrame:

    output = []
    for variable in variables: # TODO: generalize to any dimension that isn't geometry or in loss_metrics
        for lead_time in lead_times: # TODO: generalize to any dimension that isn't geometry or in loss_metrics
            data = {'variable': variable, 'lead_time': lead_time}
            data.update(added_cols)
            for metric in loss_metrics:
                rmse = rmse_calculator(gdf[gdf.variable==variable][gdf.lead_time==lead_time], metric)
                data.update({f'rmse_{metric}': rmse})
            output.append(data)
    return pd.DataFrame(output)

def rmse_calculator(
        gdf: gpd.GeoDataFrame,
        metric: str,
    ) -> np.float64:

    if not type(gdf[metric]) == list:
        values = np.concatenate(gdf[metric].values)
    else:
        values = gdf[metric]
    return np.sqrt(np.nanmean(values))