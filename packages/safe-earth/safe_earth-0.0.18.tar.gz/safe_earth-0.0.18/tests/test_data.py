import pytest
import shapely
import geopandas as gpd

def test_antimeridian_coordinate_equivalence():
    gdf = gpd.read_file('src/safe_earth/data/strata/gdf_territory_region_income.csv')
    gdf['geometry'] = gdf['geometry'].apply(shapely.wkt.loads)
    gdf = gpd.GeoDataFrame(gdf, geometry='geometry')
    pos_antimeridian = shapely.LineString([(180,-90),(180,90)])
    pos_intersects = gdf[gdf.geometry.intersects(pos_antimeridian)]
    neg_antimeridian = shapely.LineString([(-180,-90),(-180,90)])
    neg_intersects = gdf[gdf.geometry.intersects(neg_antimeridian)]
    assert (pos_intersects == neg_intersects).all().all()
