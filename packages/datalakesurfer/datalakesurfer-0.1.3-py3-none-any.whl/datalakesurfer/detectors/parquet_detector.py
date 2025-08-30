"""
ParquetDetector implements the detection logic for Parquet datasets in ADLS Gen2.

This detector uses pyarrow and pyarrowfs_adlgen2 to connect to ADLS Gen2 and determine if a given directory
is a Parquet dataset. It can also detect partitioning information for Parquet datasets.

Attributes:
    format_name (str): The name of the format this detector identifies ("parquet").

Methods:
    detect(): Returns True if the directory is a Parquet dataset in ADLS Gen2, otherwise False.
    detect_partitions(): Returns partitioning metadata for the Parquet dataset.
"""

import pyarrow.dataset as ds
import pyarrow.fs
import pyarrowfs_adlgen2
from datalakesurfer.utils.credentials import CustomTokenCredential
from datalakesurfer.utils.exceptions import FormatDetectionError, FileSystemError


class ParquetDetector:
    format_name = "parquet"

    def __init__(self, account_name, file_system_name, directory_path, token, expires_on):
        """
        Initialize the detector with ADLS Gen2 connection parameters.

        Args:
            account_name (str): The ADLS Gen2 account name.
            file_system_name (str): The file system (container) name.
            directory_path (str): The path to the directory to inspect.
            token (str): The authentication token.
            expires_on (str): The token expiration timestamp.
        """
        self.account_name = account_name
        self.file_system_name = file_system_name
        self.directory_path = directory_path
        self.token = token
        self.expires_on = expires_on

    def detect(self) -> bool:
        """
        Determine if the given path is a Parquet dataset in ADLS Gen2.

        Returns:
            bool: True if the directory is a Parquet dataset, False otherwise.
        """
        try:
            credential = CustomTokenCredential(self.token, self.expires_on)
            handler = pyarrowfs_adlgen2.AccountHandler.from_account_name(
                self.account_name, credential=credential
            )
            fs = pyarrow.fs.PyFileSystem(handler)
            full_path = f"{self.file_system_name}/{self.directory_path}"
            dataset = ds.dataset(full_path, filesystem=fs, format="parquet", partitioning="hive")
            return bool(dataset.schema.names)
        except Exception as e:
            raise FormatDetectionError("Failed to detect Parquet format", cause=e)

    def detect_partitions(self):
        """
        Detect partition information for a Parquet dataset in ADLS Gen2.

        Returns:
            dict: A dictionary with status, isPartitioned flag, and partition column metadata.
                  If an error occurs, returns a dictionary with status "error" and the error message.
        """
        try:
            credential = CustomTokenCredential(self.token, self.expires_on)
            handler = pyarrowfs_adlgen2.AccountHandler.from_account_name(
                self.account_name, credential=credential
            )
            fs = pyarrow.fs.PyFileSystem(handler)
            full_path = f"{self.file_system_name}/{self.directory_path}"

            parquet_schema = ds.dataset(full_path, filesystem=fs, format="parquet", partitioning=None).schema
            partitioning = ds.dataset(full_path, filesystem=fs, format="parquet", partitioning="hive").partitioning

            partition_columns = []
            if partitioning and hasattr(partitioning, "schema"):
                partition_columns = [
                    {"column_name": col.name, "dtype": str(col.type)}
                    for col in partitioning.schema
                    if col.name not in parquet_schema.names
                ]

            return {
                "status": "success",
                "isPartitioned": bool(partition_columns),
                "partition_columns": partition_columns
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}
