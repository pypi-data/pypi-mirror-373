"""
Interface to Mongo for using Mongo as a buffer for chunked data transfer.

We use Mongo as a buffer because we cannot guarantee that all of the requests
for individual chunks will hit the same worker. While we could use streamed responses for the download,
they're not available for upload, so for simplicity we use the same approach in both directions.

The intended usage pattern is that a single message is stored as a single "chunk set".
The chunk set is first "filled" (either by the client or the server), then "emptied" to obtain the data
(again, by either the client or the server).

Note that while this can be used for pagination, it is not in itself pagination.

We plan to gather most of this material into ew_common after the chunked transfer interface has been rolled out
to its three main users (ew_geostore, ew_specklia, ew_online_processing_service) and proven effective for each.
At that point, this entire module will move into ew_common. Note that the chunked transfer interface will always
require MongoDB or a similar provision to work correctly.

IMPORTANT: THE VERSION HERE IN THE SPECKLIA PACKAGE MUST NOT BE MADE DEPENDENT UPON EW_COMMON SINCE EW_COMMON
IS PRIVATE BUT THIS PACKAGE IS PUBLIC!
"""

import struct
import time
from enum import Enum
from io import BytesIO
from logging import Logger
from typing import List, Tuple, Union

import requests
from geopandas import GeoDataFrame
from geopandas import read_feather as read_geofeather
from pandas import DataFrame, read_feather

log = Logger(__name__)

CHUNK_DB_NAME = "data_transfer_chunks"
CHUNK_METADATA_COLLECTION_NAME = "chunk_metadata"
MAX_CHUNK_AGE_SECONDS = 3600
MAX_CHUNK_SIZE_BYTES = 5 * 1024**2  # must be small enough to fit into an HTTP GET Request
CHUNK_DOWNLOAD_RETRIES = 10
CHUNK_DOWNLOAD_TIMEOUT_S = 10


class ChunkSetStatus(Enum):
    """
    Chunk set status.

    Prevents the accidental access of chunk sets that have not yet received all of their data.
    """

    FILLING = 0
    EMPTYING = 1


def upload_chunks(api_address: str, chunks: List[Tuple[int, bytes]]) -> str:
    """
    Upload data chunks.

    Upload a series of data chunks through the chunked transfer mechanism.
    This method is for use on the client, not the server.

    Parameters
    ----------
    api_address : str
        The full URL of the API, including port but not including endpoint, e.g. "http://127.0.0.1:9999"
    chunks : List[Tuple[int, bytes]]
        A list of tuples containing the ordinal number of the chunk and each chunk

    Returns
    -------
    str
        The chunk set uuid of the uploaded chunks
    """
    # post the first chunk to start the upload
    response = requests.post(api_address + f"/chunk/upload/{chunks[0][0]}-of-{len(chunks)}", data=chunks[0][1])
    response.raise_for_status()
    log.debug("response from very first /chunk/upload was '%s'", response.json())
    chunk_set_uuid = response.json()["chunk_set_uuid"]

    # post the rest of the chunks in a random order
    for i, chunk in chunks[1:]:
        response = requests.post(api_address + f"/chunk/upload/{chunk_set_uuid}/{i}-of-{len(chunks)}", data=chunk)
        response.raise_for_status()
        log.debug("response from subsequent /chunk/upload/uuid call was '%s'", response.text)

    return chunk_set_uuid


def download_chunks(api_address: str, chunk_set_uuid: str, num_chunks: int) -> bytes:
    """
    Download data chunks.

    Download a series of data chunks sequentially through the chunked transfer mechanism.

    Parameters
    ----------
    api_address : str
        The full URL of the API, including port but not including endpoint, e.g. "http://127.0.0.1:9999"
    chunk_set_uuid : str
        The uuid of the chunk set to download.
    num_chunks : int
        The number of chunks to download.

    Returns
    -------
    bytes
        The concatenated data from all the chunks.

    Raises
    ------
    RuntimeError
        If the download fails after a number of retries.
    """
    chunks = []
    for chunk_ordinal in range(1, num_chunks + 1):
        retries = 0
        success = False
        while retries < CHUNK_DOWNLOAD_RETRIES and not success:
            try:
                this_chunk_response = requests.get(
                    f"{api_address}/chunk/download/{chunk_set_uuid}/{chunk_ordinal}", timeout=CHUNK_DOWNLOAD_TIMEOUT_S
                )
                this_chunk_response.raise_for_status()
                ordinal = struct.unpack("i", this_chunk_response.content[:4])[0]
                chunk = this_chunk_response.content[4:]
                assert ordinal == chunk_ordinal, f"Chunk ordinal mismatch: expected {chunk_ordinal}, got {ordinal}"
                chunks.append(chunk)
                success = True
            except (requests.Timeout, requests.ConnectionError) as e:
                retries += 1
                log.warning("Request failed with %s. Retrying (%s/%s)...", e, retries, CHUNK_DOWNLOAD_RETRIES)
                time.sleep(1)  # Small backoff before retrying
        if not success:
            error_message = (
                f"Failed to download from chunk set {chunk_set_uuid} after {CHUNK_DOWNLOAD_TIMEOUT_S} attempts."
            )
            log.error(error_message)
            raise RuntimeError(error_message)

    # Let the server know that we are done with this data and it can be deleted.
    requests.delete(f"{api_address}/chunk/delete/{chunk_set_uuid}")

    return b"".join(chunks)


def split_into_chunks(data: bytes, chunk_size: int = MAX_CHUNK_SIZE_BYTES) -> List[Tuple[int, bytes]]:
    """
    Split data into compressed chunks for transport.

    Parameters
    ----------
    data : bytes
        The data to be split into chunks.
    chunk_size: int
        The maximum number of bytes allowed in each chunk.

    Returns
    -------
    List[Tuple[int, bytes]]
        A list of tuples containing the ordinal number of the chunk and each chunk
    """
    return list(enumerate((data[i : i + chunk_size] for i in range(0, len(data), chunk_size)), start=1))


def deserialise_dataframe(data: bytes) -> Union[DataFrame, GeoDataFrame]:
    """
    Convert a binary serialised feather table to pandas dataframe.

    Parameters
    ----------
    data : bytes
        Binary serialised feather table.

    Returns
    -------
    Union[DataFrame, GeoDataFrame]
        Input table converted to a pandas dataframe.

    Raises
    ------
    ValueError
        When bytes can't be interpreted as meaningful dataframe.
    """
    try:
        buffer = BytesIO(data)
        df = read_geofeather(buffer)  # type: ignore
    except ValueError as e:
        # First attempt to deserialise as a geodataframe. If geo meta is missing, we expect a clear ValueError
        # and we then load as a plain dataframe instead.
        if "Missing geo meta" in e.args[0] or "'geo' metadata" in e.args[0]:
            try:
                df = read_feather(BytesIO(data))
            except ValueError as e:
                raise ValueError("Couldn't deserialise table format") from e
        else:
            raise ValueError("Couldn't deserialise table format") from e
    return df  # type: ignore


def serialise_dataframe(df: Union[DataFrame, GeoDataFrame]) -> bytes:
    """
    Serialise a dataframe using the feather table format.

    Parameters
    ----------
    df: Union[DataFrame, GeoDataFrame]
        Input dataframe

    Returns
    -------
    bytes
        Serialised feather table.
    """
    feather_buffer = BytesIO()
    # Browser implementations of feather do not support compressed feather formats.
    df.to_feather(feather_buffer, compression="uncompressed")
    feather_buffer.seek(0)
    return feather_buffer.getvalue()
