try:
    import pandas as pd

    HAS_PANDAS = True
    PD_DATAFRAME = pd.DataFrame
    PD_SERIES = pd.Series
    PD_INDEX = pd.Index
    PD_HASH_OBJECT_FN = pd.util.hash_pandas_object
except ImportError:
    HAS_PANDAS = False
    PD_DATAFRAME = None
    PD_SERIES = None
    PD_INDEX = None
    PD_HASH_OBJECT_FN = None

try:
    import geopandas as gpd

    HAS_GEOPANDAS = True
    GPD_GEODATAFRAME = gpd.GeoDataFrame
except ImportError:
    HAS_GEOPANDAS = False
    GPD_GEODATAFRAME = None

try:
    import mercantile

    HAS_MERCANTILE = True
    MERCANTILE_TILE = mercantile.Tile
except ImportError:
    HAS_MERCANTILE = False
    MERCANTILE_TILE = None

try:
    import shapely

    HAS_SHAPELY = True
    SHAPELY_GEOMETRY = shapely.Geometry
    SHAPELY_POLYGON = shapely.Polygon
except ImportError:
    HAS_SHAPELY = False
    SHAPELY_GEOMETRY = None
    SHAPELY_POLYGON = None

try:
    import aiofiles  # noqa: F401

    HAS_AIOFILES = True
except ImportError:
    HAS_AIOFILES = False
