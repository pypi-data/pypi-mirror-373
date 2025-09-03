import inspect
import json
import uuid
from io import StringIO
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Union, get_args, get_origin

try:
    from types import UnionType
except ImportError:
    # compatibility with Python 3.9
    UnionType = type(Union[int, str])

from fused._optional_deps import (
    GPD_GEODATAFRAME,
    HAS_GEOPANDAS,
    HAS_MERCANTILE,
    HAS_PANDAS,
    HAS_SHAPELY,
    PD_DATAFRAME,
    SHAPELY_GEOMETRY,
)

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import geopandas as gpd
except ImportError:
    gpd = None

try:
    import shapely
except ImportError:
    shapely = None

try:
    import mercantile
except ImportError:
    mercantile = None


if TYPE_CHECKING:
    import geopandas as gpd
    import mercantile
    import pandas as pd
    import shapely

    from fused.types import Bbox, Bounds, TileGDF, TileXYZ


FALSE_CASEFOLDED = "false".casefold()
GEOJSON_CRS = 4326


def _parse_bbox(val: str) -> Union[list, "gpd.GeoDataFrame"]:
    deserialized = json.loads(val)
    if isinstance(deserialized, list):
        return deserialized
    if HAS_GEOPANDAS:
        return gpd.GeoDataFrame.from_features(deserialized, crs=GEOJSON_CRS)
    return val


def _parse_to_gdf(val: Any) -> "gpd.GeoDataFrame":
    if isinstance(val, gpd.GeoDataFrame):
        return val
    elif isinstance(val, str):
        deserialized = json.loads(val)
        if isinstance(deserialized, list):
            return gpd.GeoDataFrame(
                {}, geometry=[shapely.box(*deserialized)], crs=GEOJSON_CRS
            )
        return gpd.GeoDataFrame.from_features(deserialized, crs=GEOJSON_CRS)
    raise NotImplementedError(f"Not sure how to convert type `{val}` to GeoDataFrame")


def _parse_to_df(val: Any) -> "pd.DataFrame":
    if isinstance(val, pd.DataFrame):
        return val
    elif isinstance(val, str):
        return pd.read_json(StringIO(val))
    raise NotImplementedError(f"Not sure how to convert type `{val}` to DataFrame")


def convert_to_tile_gdf(val: Any, add_xyz: bool = True) -> "TileGDF":
    if not HAS_GEOPANDAS:
        raise ImportError(
            "GeoPandas is not installed, but is required for running a UDF with "
            "a TileGDF or ViewportGDF parameter."
        )
    if isinstance(val, str):
        val = _parse_bbox(val)
    if isinstance(val, list):
        val = gpd.GeoDataFrame({}, geometry=[shapely.box(*val)], crs=GEOJSON_CRS)
    if isinstance(val, gpd.GeoDataFrame):
        if (
            add_xyz
            and not all(c in val.columns for c in ["x", "y", "z"])
            and HAS_MERCANTILE
        ):
            tile = mercantile.bounding_tile(*val.total_bounds)
            val = val.assign(x=tile.x, y=tile.y, z=tile.z)
            val = val[["x", "y", "z", "geometry"]]
        return val

    raise NotImplementedError(f"Not sure how to convert type `{val}` to TileGDF")


def _parse_to_geometry(val: Any) -> "shapely.Geometry":
    if not HAS_SHAPELY:
        raise ImportError(
            "shapely is not installed, but is required for running a UDF with "
            "a Geometry parameter."
        )
    if isinstance(val, str):
        return shapely.from_wkt(val)
    if isinstance(val, shapely.Geometry):
        return val
    raise NotImplementedError(
        f"Not sure how to convert type `{val}` to shapely.Geometry"
    )


def convert_to_tile_xyz(val: Any) -> "TileXYZ":
    if not HAS_MERCANTILE:
        raise ImportError(
            "mercantile is not installed, but is required for running a UDF with "
            "a TileXYZ parameter."
        )
    if isinstance(val, str):
        val = _parse_bbox(val)
    if HAS_GEOPANDAS and isinstance(val, gpd.GeoDataFrame):
        if all(c in val.columns for c in ["x", "y", "z"]):
            return mercantile.Tile(*val.iloc[0][["x", "y", "z"]])
        else:
            return mercantile.bounding_tile(*val.total_bounds)
    if isinstance(val, list):
        return mercantile.bounding_tile(*val)
    raise NotImplementedError(f"not sure how to convert type `{val}` to TileXYZ")


def convert_to_bounds(val: Any) -> "Bounds":
    if isinstance(val, str):
        val = _parse_bbox(val)
    if isinstance(val, list):
        if not len(val) == 4:
            raise ValueError(f"Expected 4 values for bounds, got {len(val)}")
        return val
    if isinstance(val, gpd.GeoDataFrame):
        return val.total_bounds.tolist()
    raise NotImplementedError(f"not sure how to convert type `{val}` to Bounds")


def convert_to_bbox(val: Any) -> "Bbox":
    if not HAS_SHAPELY:
        raise ImportError(
            "shapely is not installed, but is required for running a UDF with "
            "a Bbox parameter."
        )
    if isinstance(val, str):
        val = _parse_bbox(val)
    if isinstance(val, list):
        return shapely.box(*val)
    if isinstance(val, gpd.GeoDataFrame):
        return shapely.box(*val.total_bounds)
    raise NotImplementedError(f"not sure how to convert type `{val}` to Bbox")


def _resolve_annotation(param: inspect.Parameter | None):
    annotation = param.annotation if param else inspect._empty
    if annotation is inspect._empty:
        return annotation

    origin = get_origin(annotation)
    if origin is not None:
        if origin is Union or origin is UnionType:
            args = get_args(annotation)
            # Handle Optional and (x | None)
            if len(args) == 2:
                if args[0] is type(None):
                    return args[1]
                if args[1] is type(None):
                    return args[0]
            # TODO, handle e.g. Union types. Look into using Pydantic for this. Leave as is for now.
        else:
            return origin
    return annotation


def coerce_arg(
    val: Any, param: inspect.Parameter | None, default_annotation: Any | None = None
) -> Any:
    """
    Args:
        val: The value to coerce
        param: How the parameter is defined on the function, or None if there is no corresponding
               parameter (which happens when passing kwargs).
        default_annotation: If the parameter annotation is empty or the parmeter is None, a default
                            annotation to use as a backup. E.g. for kwargs allows setting them as
                            `str` without affecting the parsing of named parameters with empty
                            annotations.
    """
    # Needed due to circular import issue
    from fused.types import Bbox, Bounds, Tile, TileGDF, TileXYZ, ViewportGDF

    # TODO: perhaps use https://docs.python.org/3/library/typing.html#typing.get_type_hints
    annotation = _resolve_annotation(param)
    if annotation is inspect._empty:
        if default_annotation:
            # Default unannotated parameters and kwargs to str
            annotation = default_annotation
        else:
            return val

    # Temporary solution for properly handling non-stdlib annotations
    if isinstance(annotation, str):
        if "GeoDataFrame" in annotation and HAS_GEOPANDAS:
            annotation = GPD_GEODATAFRAME
        elif "DataFrame" in annotation and HAS_PANDAS:
            annotation = PD_DATAFRAME

    if annotation is str:
        return str(val)
    if annotation is int:
        if isinstance(val, str):
            # base 0 will cause the integer to be interpreted as a integer literal similar to how
            # code would be read. Possible improvement to help handle 0x...:
            # https://docs.python.org/3/library/functions.html#int
            # Only strings should be passed in to `int` if the base is passed too. Integers and so
            # on will not be converted correctly.
            return int(val, base=10)
        return int(val)
    if annotation is float:
        return float(val)
    if annotation is bool:
        if isinstance(val, str) and val.casefold() == FALSE_CASEFOLDED:
            return False
        return bool(val)
    if annotation in [list, dict, List, Dict, Iterable] and isinstance(val, str):
        return json.loads(val)
    if annotation is tuple:
        return tuple(json.loads(val))
    if annotation is uuid.UUID:
        return uuid.UUID(val)
    if annotation in [Tile, TileGDF, ViewportGDF]:
        return convert_to_tile_gdf(val, add_xyz=annotation in [Tile, TileGDF])
    if annotation is TileXYZ:
        return convert_to_tile_xyz(val)
    if annotation is Bounds:
        return convert_to_bounds(val)
    if annotation is Bbox:
        return convert_to_bbox(val)
    if HAS_GEOPANDAS and annotation is GPD_GEODATAFRAME:
        # load as geojson
        return _parse_to_gdf(val)
    if HAS_PANDAS and annotation is PD_DATAFRAME:
        # load as json
        return _parse_to_df(val)
    if (
        HAS_SHAPELY
        and isinstance(annotation, type)
        and issubclass(annotation, SHAPELY_GEOMETRY)
    ):
        return _parse_to_geometry(val)

    # Unknown, fall back to not doing anything with it
    return val
