import asyncio
import io
import math
import os
import re
import tempfile
import time
import warnings
from logging import getLogger
from typing import Any, Callable, Generator, List, Tuple

import aiohttp
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from kumoapi.data_source import (
    CompleteFileUploadRequest,
    DeleteUploadedFileRequest,
    PartUploadMetadata,
    StartFileUploadRequest,
    StartFileUploadResponse,
)
from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio

from kumoai import global_state
from kumoai.exceptions import HTTPException
from kumoai.futures import _KUMO_EVENT_LOOP

CHUNK_SIZE = 100 * 10**6  # 100 MB
MAX_PARTITION_SIZE = 1000 * 1024**2  # 1GB
MIN_PARTITION_SIZE = 100 * 1024**2  # 100MB

logger = getLogger(__name__)

CONNECTOR_ID_MAP = {
    "csv": "csv_upload_connector",
    "parquet": "parquet_upload_connector",
}


async def put(
    session: aiohttp.ClientSession,
    url: str,
    data: bytes,
    part_no: int,
) -> Tuple[int, str]:
    r"""Performs an asynchronous PUT request to upload data to a presigned S3
    URL, and returns a tuple corresponding to the uploaded part number and
    the Etag of the header.

    Args:
        session: the ``aiohttp`` client session to use for the request
        url: the S3 presigned URL to PUT ``data`` to
        data: the data (``bytes``) that should be PUT to ``url``
        part_no: the part number of the data to be PUT
    """
    # TODO(manan): add retry...
    async with session.put(url, data=data) as res:
        logger.debug("PUT part_no=%s bytes=%s", part_no, len(data))
        _ = await res.text()
        if res.status != 200:
            raise RuntimeError(
                f"PUT URL={url} failed: with status {res.status}: "
                f"{res}")
        headers = res.headers
        return (part_no + 1, headers['Etag'])


async def multi_put(
    loop: asyncio.AbstractEventLoop,
    urls: List[str],
    data: Generator[bytes, None, None],
    tqdm_bar_position: int = 0,
) -> List[PartUploadMetadata]:
    r"""Performs multiple asynchronous PUT requests of the data yielded
    from the ``data`` generator to the specified URLs. If the data
    generator is exhausted early, only a subset of URLs are used. If
    the data generator is not exhausted by the URLs, uploaded data may
    be corrupted!
    """
    # TODO(manan): retry
    # TODO(manan): properly stream chunks
    async with aiohttp.ClientSession(
        loop=loop,
        connector=aiohttp.TCPConnector(verify_ssl=False),
        headers={'Content-Type': 'binary'},
    ) as session:
        results = await tqdm_asyncio.gather(
            *[
                put(session, url, data, i)
                for i, (url, data) in enumerate(zip(urls, data))
            ], desc="Uploading chunks", position=tqdm_bar_position,
            leave=False)
        for r in results:
            if isinstance(r, BaseException):
                raise r
        return [PartUploadMetadata(v[0], v[1]) for v in results]


def stream_read(
    f: io.BufferedReader,
    chunk_size: int,
) -> Generator[bytes, None, None]:
    r"""Streams ``chunk_size`` contiguous bytes from buffered reader
    ``f`` each time the generator is yielded from.
    """
    while True:
        byte_buf = f.read(chunk_size)
        if len(byte_buf) == 0:
            # StopIteration:
            break
        yield byte_buf


def upload_table(
    name: str,
    path: str,
    auto_partition: bool = True,
    partition_size_mb: int = 250,
) -> None:
    r"""Synchronously uploads a table located on your local machine to the
    Kumo data plane. Tables uploaded in this way can be accessed with a
    :class:`~kumoai.connector.FileUploadConnector`.

    For files larger than 1GB, the table will be automatically partitioned
    into smaller chunks and uploaded with common prefix that allows
    FileUploadConnector to union them when reading.

    .. warning::
        Uploaded tables must be single files, either in parquet or CSV
        format. Partitioned tables are not currently supported.

    .. code-block:: python

        import kumoai
        from kumoai.connector import upload_table

        # Upload a small table
        upload_table(name="users", path="/data/users.parquet")

        # Upload a large parquet table (will be automatically partitioned)
        upload_table(name="transactions",
                     path="/data/large_transactions.parquet")

        # Upload a large CSV table (will be automatically partitioned)
        upload_table(name="sales", path="/data/large_sales.csv")

        # Disable auto-partitioning (will raise error for large files)
        upload_table(name="users", path="/data/users.parquet",
                     auto_partition=False)

    Args:
        name: The name of the table to be uploaded. The uploaded table can
            be accessed from the :class:`~kumoai.connector.FileUploadConnector`
            with this name.
        path: The full path of the table to be uploaded, on the local
            machine.
        auto_partition: Whether to automatically partition large files (>1GB).
            If False and file is >1GB, raises ValueError. Supports both
            Parquet and CSV files.
        partition_size_mb: The size of each partition in MB. Only used if
            auto_partition is True.
    """
    warnings.warn(
        "upload_table is deprecated; use "
        "FileUploadConnector.upload instead.", DeprecationWarning,
        stacklevel=2)

    # Validate file type
    if not (path.endswith(".parquet") or path.endswith(".csv")):
        raise ValueError(f"Path {path} must be either a CSV or Parquet "
                         f"file. Partitioned data is not currently "
                         f"supported.")

    file_size = os.path.getsize(path)

    # Route based on file size
    if file_size < MAX_PARTITION_SIZE:
        return _upload_single_file(name, path)

    if not auto_partition:
        raise ValueError(f"File {path} is {file_size / (1024**3):.2f}GB, "
                         f"which exceeds the 1GB limit. Enable "
                         f"auto_partition=True to automatically partition "
                         f"large files.")

    # Partition and upload large files
    partition_size = partition_size_mb * 1024**2
    if (partition_size > MAX_PARTITION_SIZE
            or partition_size < MIN_PARTITION_SIZE):
        raise ValueError(f"Partition size {partition_size_mb}MB must be "
                         f"between {MIN_PARTITION_SIZE / 1024**2}MB and "
                         f"{MAX_PARTITION_SIZE / 1024**2}MB.")

    logger.info("File %s is large with size %s, partitioning for upload...",
                path, file_size)
    if path.endswith('.parquet'):
        _upload_partitioned_parquet(name, path, partition_size)
    else:
        _upload_partitioned_csv(name, path, partition_size)


def _handle_duplicate_names(names: List[str]) -> List[str]:

    unique_names = []
    unique_names_with_counts = {}

    for name in names:
        if name not in unique_names:
            # The first instance of a column name will retain its name
            # without change.
            unique_names_with_counts[name] = 0
            unique_names.append(name)
        else:
            # Subsequent instances of a duplicated column name will have
            # numerals added to disambiguate.
            unique_names_with_counts[name] += 1
            new_name = f"{name}_{unique_names_with_counts[name]}"
            while new_name in names or new_name in unique_names:
                unique_names_with_counts[name] += 1
                new_name = f"{name}_{unique_names_with_counts[name]}"

            unique_names.append(new_name)
    return unique_names


def _sanitize_columns(names: List[str]) -> Tuple[List[str], bool]:
    _SAN_RE = re.compile(r"[^0-9A-Za-z]+")
    new = [_SAN_RE.sub("_", n).strip("_") for n in names]
    new = _handle_duplicate_names(new)
    return new, new != names


def sanitize_file(src_path: str) -> Tuple[str, bool]:
    """Sanitizes the columns of a CSV or Parquet file by replacing invalid
    characters with underscores.
    Returns a tuple of the new path and a boolean indicating if the file was
    changed. If the file was not changed, the original path is returned.
    If the file was changed, a temporary file is created and returned.
    The temporary file should be deleted by the caller.

    Args:
        src_path: The path to the CSV or Parquet file to sanitize.

    Returns:
        A tuple of the new path and a boolean indicating if the file was
        changed. If the file was not changed, the original path is returned.
        If the file was changed, a temporary file is created and returned.
    """
    if src_path.endswith('.parquet'):
        pf = pq.ParquetFile(src_path)
        new_names, changed = _sanitize_columns(pf.schema.names)
        if not changed:
            return src_path, False
        temp_file = tempfile.NamedTemporaryFile(suffix='.parquet',
                                                delete=False)
        # Create schema with sanitized column names
        original_schema = pf.schema.to_arrow_schema()
        fields = [
            field.with_name(new_name)
            for field, new_name in zip(original_schema, new_names)
        ]
        sanitized_schema = pa.schema(fields)
        writer = pq.ParquetWriter(temp_file.name, sanitized_schema)
        for i in range(pf.num_row_groups):
            tbl = pf.read_row_group(i).rename_columns(new_names)
            writer.write_table(tbl)
        writer.close()
        return temp_file.name, True
    elif src_path.endswith('.csv'):
        cols = pd.read_csv(src_path, nrows=0).columns.tolist()
        new_cols, changed = _sanitize_columns(cols)
        if not changed:
            return src_path, False

        tmp = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
        tmp_path = tmp.name
        tmp.close()

        reader = pd.read_csv(src_path, chunksize=1_000_000)
        with open(tmp_path, 'w', encoding='utf-8', newline='') as out:
            out.write(','.join(new_cols) + '\n')  # header once
            for chunk in reader:
                chunk.columns = new_cols
                chunk.to_csv(out, header=False, index=False)

        return tmp_path, True
    else:
        raise ValueError(
            f"File {src_path} must be either a CSV or Parquet file.")


def _upload_single_file(
    name: str,
    path: str,
    tqdm_bar_position: int = 0,
) -> None:
    r"""Upload a single file (original upload_table logic)."""
    # Validate:
    if not (path.endswith(".parquet") or path.endswith(".csv")):
        raise ValueError(f"Path {path} must be either a CSV or Parquet "
                         f"file. Partitioned data is not currently "
                         f"supported.")

    # Prepare upload (number of parts based on total size):
    file_type = 'parquet' if path.endswith('parquet') else 'csv'
    path, temp_file_created = sanitize_file(path)
    sz = os.path.getsize(path)
    if tqdm_bar_position == 0:
        logger.info("Uploading table %s (path: %s), size=%s bytes", name, path,
                    sz)

    upload_res = _start_table_upload(
        table_name=name,
        file_type=file_type,
        file_size_bytes=sz,
    )

    # Chunk and upload:
    urls = list(upload_res.presigned_part_urls.values())
    loop = _KUMO_EVENT_LOOP
    part_metadata_list_fut = asyncio.run_coroutine_threadsafe(
        multi_put(loop, urls=urls, data=stream_read(
            open(path, 'rb'),
            CHUNK_SIZE,
        ), tqdm_bar_position=tqdm_bar_position), loop)
    part_metadata_list = part_metadata_list_fut.result()

    # Complete:
    if tqdm_bar_position == 0:
        logger.info("Upload complete. Validating table %s.", name)
    for i in range(5):
        try:
            _complete_table_upload(
                table_name=name,
                file_type=file_type,
                upload_path=upload_res.temp_upload_path,
                upload_id=upload_res.upload_id,
                parts_metadata=part_metadata_list,
            )
        except HTTPException as e:
            if e.status_code == 500 and i < 4:
                # TODO(manan): this can happen when DELETE above has
                # not propagated. So we retry with delay here. We
                # assume DELETE is processed reasonably quickly:
                time.sleep(2**(i - 1))
                continue
            else:
                raise e
        else:
            break

    if tqdm_bar_position == 0:
        logger.info("Completed uploading table %s to Kumo.", name)
    if temp_file_created:
        os.unlink(path)


def _upload_partitioned_parquet(
    name: str,
    path: str,
    partition_size: int,
) -> None:
    r"""Upload a large parquet file by partitioning it into smaller chunks."""
    logger.info("File %s is large, partitioning for upload...", path)

    pf = pq.ParquetFile(path)
    new_columns, _ = _sanitize_columns(pf.schema.names)
    # Calculate partitions
    partitions = []
    part_idx = 0
    current_size = 0
    current_row_groups: list[int] = []

    for rg_idx in range(pf.num_row_groups):
        rg_size = pf.metadata.row_group(rg_idx).total_byte_size

        if rg_size > MAX_PARTITION_SIZE:
            raise ValueError(f"Row group {rg_idx} is larger than the "
                             f"maximum partition size {MAX_PARTITION_SIZE} "
                             f"bytes")

        if current_size + rg_size > partition_size and current_row_groups:
            partitions.append((part_idx, current_row_groups.copy()))
            part_idx += 1
            current_row_groups = []
            current_size = 0

        current_row_groups.append(rg_idx)
        current_size += rg_size

    if current_row_groups:
        partitions.append((part_idx, current_row_groups))

    logger.info("Splitting %s into %d partitions", path, len(partitions))

    def writer(path: str, row_groups: List[int]) -> None:
        # Create schema with sanitized column names
        original_schema = pf.schema.to_arrow_schema()
        fields = [
            field.with_name(new_name)
            for field, new_name in zip(original_schema, new_columns)
        ]
        sanitized_schema = pa.schema(fields)
        pq_writer = pq.ParquetWriter(path, sanitized_schema)
        for rg_idx in row_groups:
            tbl = pf.read_row_group(rg_idx).rename_columns(new_columns)
            pq_writer.write_table(tbl)
        pq_writer.close()

    _upload_all_partitions(partitions, name, ".parquet", writer)
    # validation done by _upload_single_file on each partition
    logger.info("Upload complete. Validated table %s.", name)


def _upload_partitioned_csv(
    name: str,
    path: str,
    partition_size: int,
) -> None:
    r"""Upload a large CSV file by partitioning it into smaller chunks."""
    # calculate partitions
    partitions = []
    part_idx = 0
    columns = pd.read_csv(path, nrows=0).columns.tolist()
    new_columns, _ = _sanitize_columns(columns)
    with open(path, 'r', encoding='utf-8') as f:
        # preserve header per partition
        _ = f.readline()  # skip header
        header = ','.join(new_columns) + '\n'
        header_size = len(header.encode('utf-8'))

        current_lines = [header]

        current_size = header_size

        for line in f:
            line_size = len(line.encode('utf-8'))

            if (current_size + line_size > partition_size
                    and len(current_lines) > 1):
                partitions.append((part_idx, current_lines.copy()))
                part_idx += 1
                current_lines = [header]  # Start new partition with header
                current_size = header_size

            current_lines.append(line)
            current_size += line_size

        if len(current_lines) > 1:  # More than just header
            partitions.append((part_idx, current_lines))

    logger.info("Splitting %s into %d partitions", path, len(partitions))

    def writer(path: str, lines: List[str]) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    _upload_all_partitions(partitions, name, ".csv", writer)
    # validation done by _upload_single_file on each partition
    logger.info("Upload complete. Validated table %s.", name)


def _upload_all_partitions(
    partitions: List[Tuple[int, Any]],
    name: str,
    file_suffix: str,
    writer: Callable[[str, Any], None],
) -> None:
    with tqdm(partitions, desc=f"Uploading {name}", position=0) as pbar:
        for part_idx, partition_data in pbar:
            partition_desc = f"Part {part_idx+1}/{len(partitions)}"
            pbar.set_postfix_str(partition_desc)

            _create_and_upload_partition(
                name=name,
                part_idx=part_idx,
                file_suffix=file_suffix,
                partition_writer=writer,
                partition_data=partition_data,
                tqdm_bar_position=1,
            )


def _create_and_upload_partition(
    name: str,
    part_idx: int,
    file_suffix: str,
    partition_writer: Callable[[str, Any], None],
    partition_data: Any,
    tqdm_bar_position: int = 0,
) -> None:
    r"""Create a partition file, write to it, upload it, and delete the
    local copy.
    """
    partition_name = (f"{name}{file_suffix}/"
                      f"part_{part_idx+1:04d}{file_suffix}")

    with tempfile.NamedTemporaryFile(suffix=file_suffix,
                                     delete=False) as temp_file:
        partition_path = temp_file.name

    try:
        partition_writer(partition_path, partition_data)

        # Upload partition immediately with a nested progress bar
        _upload_single_file(partition_name, partition_path,
                            tqdm_bar_position=tqdm_bar_position)

    finally:
        # clean up the temporary file, even if the upload fails
        try:
            os.unlink(partition_path)
        except OSError:
            pass  # File might already be deleted or not exist


def delete_uploaded_table(
    name: str,
    file_type: str,
) -> None:
    r"""Now deprecated in favor of
    :func:`kumoai.connector.file_upload_connector.FileUploadConnector.delete`.
    Synchronously deletes a previously uploaded table from the Kumo data
    plane.

    .. code-block:: python

        import kumoai
        from kumoai.connector import delete_uploaded_table

        # Assume we have uploaded a `.parquet` table named `users`,
        # and we want to delete this table from Kumo:
        delete_uploaded_table(name="users", file_type="parquet")

        # Assume we have uploaded a `.csv` table named `orders`,
        # and we want to delete this table from Kumo:
        delete_uploaded_table(name="orders", file_type="csv")

    Args:
        name: The name of the table to be deleted. This table must have
            previously been uploaded with a call to
            :meth:`~kumoai.connector.upload_table`.
        file_type: The file type of the table to be deleted; this can either
            be :obj:`"parquet"` or :obj:`"csv"`
    """
    warnings.warn(
        "delete_uploaded_table is deprecated; use "
        "FileUploadConnector.delete instead.", DeprecationWarning,
        stacklevel=2)
    assert file_type in {'parquet', 'csv'}
    req = DeleteUploadedFileRequest(
        source_table_name=name,
        connector_id=CONNECTOR_ID_MAP[file_type],
    )
    global_state.client.connector_api.delete_file_upload(req)
    logger.info("Successfully deleted table %s from Kumo.", name)


def replace_table(
    name: str,
    path: str,
    file_type: str,
) -> None:
    r"""Replaces an existing uploaded table on the Kumo data plane with a new
    table.

    .. code-block:: python

        import kumoai
        from kumoai.connector import replace_table

        # Replace an existing `.csv` table named `users`
        # with a new version located at `/data/new_users.csv`:
        replace_table(
            name="users",
            path="/data/new_users.csv",
            file_type="csv",
        )

    Args:
        name: The name of the table to be replaced. This table must have
            previously been uploaded with a call to
            :meth:`~kumoai.connector.upload_table`.
        path: The full path of the new table to be uploaded, on the
            local machine.
        file_type: The file type of the table to be replaced; this
            can either be :obj:`"parquet"` or :obj:`"csv"`.

    Raises:
        ValueError: If the specified path does not point to a valid
            `.csv` or `.parquet` file.
    """
    # Validate:
    if not (path.endswith(".parquet") or path.endswith(".csv")):
        raise ValueError(f"Path {path} must be either a CSV or Parquet "
                         f"file. Partitioned data is not currently "
                         f"supported.")

    try:
        logger.info("Deleting previously uploaded table %s of type %s.", name,
                    file_type)
        delete_uploaded_table(name=name, file_type=file_type)
    except Exception:
        # TODO(manan): fix this...
        pass

    logger.info("Uploading table %s.", name)
    upload_table(name=name, path=path)
    logger.info("Successfully replaced table %s with the new table.", name)


def _start_table_upload(
    table_name: str,
    file_type: str,
    file_size_bytes: float,
) -> StartFileUploadResponse:
    assert file_type in CONNECTOR_ID_MAP.keys()
    req = StartFileUploadRequest(
        source_table_name=table_name,
        connector_id=CONNECTOR_ID_MAP[file_type],
        num_parts=max(1, math.ceil(file_size_bytes / CHUNK_SIZE)),
    )
    return global_state.client.connector_api.start_file_upload(req)


def _complete_table_upload(
    table_name: str,
    file_type: str,
    upload_path: str,
    upload_id: str,
    parts_metadata: List[PartUploadMetadata],
) -> None:
    assert file_type in CONNECTOR_ID_MAP.keys()

    req = CompleteFileUploadRequest(
        source_table_name=table_name,
        connector_id=CONNECTOR_ID_MAP[file_type],
        temp_upload_path=upload_path,
        upload_id=upload_id,
        parts_metadata=parts_metadata,
    )
    return global_state.client.connector_api.complete_file_upload(req)
