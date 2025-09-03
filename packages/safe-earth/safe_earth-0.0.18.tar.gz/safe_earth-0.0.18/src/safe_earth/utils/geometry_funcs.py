import shapely
from typing import List, Union
import pandas as pd
import geopandas as gpd

# TODO: support automatic per-point edge length detection to handle non-equiangularity
def square_polygons_from_points(
        geometry: List[shapely.Point],
        polygon_edge_in_degrees: int,
    ) -> List[shapely.Polygon]:
    '''
    Converts an array of geometry Points to Polygons that are
    polygon_edge_in_degrees x polygon_edge_in_degrees degrees in shape and that
    are centered on the Point.

    Parameters
    ----------
    geometry: List[shapely.Point]
        The array of input Points, which are (lon, lat) coordinates.
    polygon_edge_in_degrees: int
        The edge length of each polygon in degrees.

    Returns
    -------
    List[shapely.Polygon]
        Array of Polygons in the same order.
    '''

    return [point_to_square_polygon(p, polygon_edge_in_degrees) for p in geometry]

def point_to_square_polygon(
        point: shapely.Point,
        polygon_edge_in_degrees: float,
    ) -> Union[shapely.Polygon, shapely.MultiPolygon]:
    '''
    Helper function that takes in one Point and gets the square polygon
    including it subject to the constraints of the coordinate system defined
    as longitude ranging from [-180, 180) and latitude [-90, 90].
    '''

    xmin = (((point.x-polygon_edge_in_degrees/2 + 180) % 360) - 180)
    ymin = max(min(point.y-polygon_edge_in_degrees/2, 90), -90)
    xmax = (((point.x+polygon_edge_in_degrees/2 + 180) % 360) - 180)
    ymax = max(min(point.y+polygon_edge_in_degrees/2, 90), -90)
    if xmin > xmax:
        poly = split_antimeridian_square(xmin, ymin, xmax, ymax)
    else:
        poly = shapely.box(xmin, ymin, xmax, ymax)
    return poly

def split_antimeridian_square(
        min_lon: float,
        min_lat: float,
        max_lon: float,
        max_lat: float
    ) -> shapely.MultiPolygon:
    '''
    Gets the two rectangles that combined form the square polygon,
    returned as a multipolygon. Solves the cross-meridian problem
    while not duplicating any loss values.
    '''

    left = shapely.Polygon([
        (-180.0, min_lat),
        (-180.0, max_lat),
        (max_lon, max_lat),
        (max_lon, min_lat),
        (-180.0, min_lat)
    ])
    
    right = shapely.Polygon([
        (min_lon, min_lat),
        (min_lon, max_lat),
        (180.0, max_lat),
        (180.0, min_lat),
        (min_lon, min_lat)
    ])
    
    return shapely.MultiPolygon([left, right])

# TODO: add conversion for other columns passed in as dict from name to type
def df2gdf(df: pd.DataFrame) -> gpd.GeoDataFrame:
    df['geometry'] = df['geometry'].apply(shapely.wkt.loads)
    gdf = gpd.GeoDataFrame(df, geometry='geometry')
    return gdf
