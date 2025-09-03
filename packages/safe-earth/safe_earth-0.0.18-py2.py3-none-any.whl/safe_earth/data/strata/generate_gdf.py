from pygeoboundaries_geolab import get_gdf
import geopandas as gpd
import os

# TODO: check if commit is out of date (https://api.github.com/repos/wmgeolab/geoBoundaries/commits/main) and if so, regenerate gdf
def gdf_file_up_to_date() -> bool:
    return True

def need_to_download_gdf_file() -> bool:
    file_exists = os.path.exists('safe_earth/data/strata/gdf_territory_region_income.csv')
    need_to_download = (file_exists and gdf_file_up_to_date())
    return need_to_download

# TODO: make directory settable by user
def generate_gdf_file(generate_json: bool = False):
    gdf = get_gdf('ALL', ['UNSDG-subregion', 'worldBankIncomeGroup', 'maxAreaSqKM'])
    gdf = gdf.drop(columns=['shapeISO', 'shapeID', 'shapeGroup', 'shapeType'])
    gdf = gpd.GeoDataFrame(gdf, geometry=gdf['geometry'])
    gdf = gdf.set_geometry('geometry').set_crs(4326)
    gdf.to_csv(os.getcwd()+'/gdf_territory_region_income.csv', index=False)
    if generate_json:
        gdf.to_file(os.getcwd()+'/territory_region_income.geojson', driver='GeoJSON')
