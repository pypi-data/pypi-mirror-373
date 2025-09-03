import base64
from io import BytesIO
from typing import TYPE_CHECKING, Iterable, Optional, Union

if TYPE_CHECKING:
    import geopandas as gpd


def _normalize_url(url: str) -> str:
    if url.endswith("/"):
        return url[:-1]
    return url


def get_chunks_metadata(url: str) -> "gpd.GeoDataFrame":
    """Returns a GeoDataFrame with each chunk in the table as a row.

    Args:
        url: URL of the table.
    """
    import geopandas as gpd
    import pyarrow.parquet as pq
    import shapely

    url = _normalize_url(url) + "/_sample"

    # do not use pq.read_metadata as it may segfault in versions >= 12 (tested on 15.0.1)
    table = pq.read_table(url)
    metadata = _rewrite_metadata_to_target_version(table.schema.metadata)

    metadata_bytes = metadata[b"fused:_metadata"]
    fused_meta_buffer = base64.b64decode(metadata_bytes)
    with BytesIO(fused_meta_buffer) as bio:
        df = pq.read_table(bio).to_pandas()
    geoms = shapely.box(
        df["bbox_minx"], df["bbox_miny"], df["bbox_maxx"], df["bbox_maxy"]
    )
    return gpd.GeoDataFrame(df, geometry=geoms, crs="EPSG:4326")


def _rewrite_metadata_to_target_version(
    kvmeta: dict[bytes, bytes],
) -> dict[bytes, bytes]:
    """
    Rewrites the metadata to the target internal fused format version (v5).
    """
    format_version = kvmeta.get(b"fused:format_version", None)
    if format_version is None:
        raise ValueError("Dataset does not have Fused metadata.")

    if format_version == b"4":
        newmeta = {
            **kvmeta,
            b"fused:format_version": b"5",
        }

        metabytes = base64.decodebytes(kvmeta[b"fused:_metadata"])
        metabytes2 = metabytes[:20] + metabytes[20 + 20 :]
        metabytes3 = base64.encodebytes(metabytes2)

        newmeta[b"fused:_metadata"] = metabytes3
        return newmeta

    elif format_version == b"5":
        return kvmeta

    else:
        raise ValueError("Dataset has an incompatible metadata version.")


def get_chunk_from_table(
    url: str,
    file_id: Union[str, int, None],
    chunk_id: Optional[int],
    *,
    columns: Optional[Iterable[str]] = None,
) -> "gpd.GeoDataFrame":
    """Returns a chunk from a table and chunk coordinates.

    This can be called with file_id and chunk_id from `get_chunks_metadata`.

    Args:
        url: URL of the table.
        file_id: File ID to read.
        chunk_id: Chunk ID to read.
        columns: Read only the specified columns.
    """
    import geopandas as gpd
    import geopandas.io.arrow
    import pyarrow.parquet as pq

    if file_id is None:
        data = gpd.read_parquet(url)
    else:
        url = _normalize_url(url) + f"/{file_id}.parquet"

        with pq.ParquetFile(url) as file:
            if chunk_id is not None:
                table = file.read_row_group(chunk_id, columns=columns)
            else:
                table = file.read(columns=columns)

            if b"geo" in table.schema.metadata:
                data = geopandas.io.arrow._arrow_to_geopandas(table)
            else:
                data = table.to_pandas()

    if isinstance(data, (gpd.GeoDataFrame, gpd.GeoSeries)):
        if data.crs is None:
            data = data.set_crs(4326)
    return data
