import os
from typing import List

from kumoapi.data_source import DeleteUploadedFileRequest
from kumoapi.source_table import (
    DataSourceType,
    FileType,
    S3SourceTableRequest,
    SourceTableConfigRequest,
    SourceTableConfigResponse,
)
from typing_extensions import override

from kumoai import global_state
from kumoai.connector.base import Connector
from kumoai.connector.utils import (
    CONNECTOR_ID_MAP,
    MAX_PARTITION_SIZE,
    MIN_PARTITION_SIZE,
    _upload_partitioned_csv,
    _upload_partitioned_parquet,
    _upload_single_file,
    logger,
)


class FileUploadConnector(Connector):
    r"""Defines a connector to files directly uploaded to Kumo, either as
    'parquet' or 'csv' (non-partitioned) data.

    To get started with file upload, please first upload a table with
    the :meth:`upload` method in the :class:`FileUploadConnector` class.
    You can then access
    this table behind the file upload connector as follows:

    .. code-block:: python

        import kumoai

        # Create the file upload connector:
        connector = kumoai.FileUploadConnector(file_type="parquet")

        # Upload the table; assume it is stored at `/data/users.parquet`
        connector.upload(name="users", path="/data/users.parquet")

        # Check that the file upload connector has a `users` table:
        assert connector.has_table("users")

    Args:
        file_type: The file type of uploaded data. Can be either ``"csv"``
            or ``"parquet"``.
    """
    def __init__(self, file_type: str) -> None:
        r"""Creates the connector to uploaded files of type
        :obj:`file_type`.
        """
        assert file_type.lower() in {'parquet', 'csv'}
        self._file_type = file_type.lower()

    @property
    def name(self) -> str:
        return f'{self._file_type}_upload_connector'

    @override
    @property
    def source_type(self) -> DataSourceType:
        return DataSourceType.S3

    @property
    def file_type(self) -> FileType:
        return (FileType.PARQUET
                if self._file_type == 'parquet' else FileType.CSV)

    def _get_table_config(self, table_name: str) -> SourceTableConfigResponse:
        req = SourceTableConfigRequest(connector_id=self.name,
                                       table_name=table_name,
                                       source_type=self.source_type,
                                       file_type=None)
        return global_state.client.source_table_api.get_table_config(req)

    @override
    def _source_table_request(self,
                              table_names: List[str]) -> S3SourceTableRequest:
        return S3SourceTableRequest(s3_root_dir="", connector_id=self.name,
                                    table_names=table_names, file_type=None)

    def upload(
        self,
        name: str,
        path: str,
        auto_partition: bool = True,
        partition_size_mb: int = 250,
    ) -> None:
        r"""Synchronously uploads a table located on your
        local machine to the Kumo data plane.

        Tables uploaded in this way can be accessed with
        this ``FileUploadConnector`` using the provided name,
        for example: ``connector_obj["my_table"]``

        For files larger than 1GB, the table will be automatically partitioned
        into smaller chunks and uploaded with common prefix that allows
        FileUploadConnector to union them when reading.

        .. warning::
            Uploaded tables must be single files, either in parquet or CSV
            format(must match connector type).
            Partitioned tables are not currently supported.

        .. code-block:: python

            import kumoai
            connector = kumoai.FileUploadConnector(file_type="parquet")

            # Upload a small table
            connector.upload(name="users", path="/data/users.parquet")

            # Upload a large parquet table (will be automatically partitioned)
            connector.upload(name="transactions",
                        path="/data/large_transactions.parquet")

            # Disable auto-partitioning (will raise error for large files)
            upload(name="users", path="/data/users.parquet",
                        auto_partition=False)

            # Create a file upload connector for CSV files.
            connectorCSV = kumoai.FileUploadConnector(file_type="csv")

            # Upload a large CSV table (will be automatically partitioned)
            connectorCSV.upload(name="sales", path="/data/large_sales.csv")

        Args:
            name: The name of the table to be uploaded. The uploaded table can
                be accessed from the
                :class:`~kumoai.connector.FileUploadConnector` with this name.
            path: The full path of the table to be uploaded, on the local
                machine. File Type must match the connector type.
            auto_partition: Whether to automatically
                partition large files (>1GB).
                If False and file is >1GB, raises ValueError. Supports both
                Parquet and CSV files.
            partition_size_mb: The size of each partition in MB. Only used if
                auto_partition is True.
        """
        # Validate file type matches connector type
        if not path.lower().endswith("." + self._file_type):
            raise ValueError(f"File {path} must match connector path type: "
                             f"{self._file_type}.")

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

        logger.info(
            "File %s is large with size %s, partitioning for upload...", path,
            file_size)
        if path.endswith('.parquet'):
            _upload_partitioned_parquet(name, path, partition_size)
        else:
            _upload_partitioned_csv(name, path, partition_size)

    def delete(
        self,
        name: str,
        file_type: str,
    ) -> None:
        r"""Synchronously deletes a previously uploaded table from the Kumo
        data plane.

        .. code-block:: python

            # Assume we have uploaded a `.parquet` table named `users`, and a
            # `FileUploadConnector` has been created called `connector`, and
            # we want to delete this table from Kumo:
            connector.delete(name="users", file_type="parquet")

        Args:
            name: The name of the table to be deleted. This table must have
                previously been uploaded with a call to
                :meth:`~kumoai.connector.FileUploadConnector.upload`.
            file_type: The file type of the table to be deleted; this can
                either be :obj:`"parquet"` or :obj:`"csv"`, and must match the
                connector file_type.
        """
        if file_type.lower() != self._file_type:
            raise ValueError(f"File type {file_type} does not match "
                             f"connector file type {self._file_type}.")

        if not self.has_table(name):
            raise ValueError(f"The table '{name}' does not exist in {self}. "
                             f"Please check the existence of the source data.")

        req = DeleteUploadedFileRequest(
            source_table_name=name,
            connector_id=CONNECTOR_ID_MAP[file_type],
        )
        global_state.client.connector_api.delete_file_upload(req)
        logger.info("Successfully deleted table %s from Kumo.", name)
