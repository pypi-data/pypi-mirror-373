"""
FabricParquetDetector implements the detection logic for Parquet datasets in Microsoft Fabric OneLake.

This detector uses pyarrow and adlfs to connect to Fabric OneLake and determine if a given directory
is a Parquet dataset. It can also detect partitioning information for Parquet datasets.

Attributes:
    format_name (str): The name of the format this detector identifies ("parquet").

Methods:
    detect(): Returns True if the directory is a Parquet dataset in Fabric OneLake, otherwise False.
    detect_partitions(): Returns partitioning metadata for the Parquet dataset.
"""

import pyarrow.dataset as ds
from adlfs import AzureBlobFileSystem
from datalakesurfer.utils.credentials import CustomTokenCredential


class FabricParquetDetector:
    format_name = "parquet"

    def __init__(self, account_name, file_system_name, directory_path, token, expires_on):
        """
        Initialize the detector with Fabric OneLake connection parameters.

        Args:
            account_name (str): The Fabric OneLake account name.
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
        Determine if the given path is a Parquet dataset in Fabric OneLake.

        Returns:
            bool: True if the directory is a Parquet dataset, False otherwise.
        """
        try:
            credential = CustomTokenCredential(token=self.token, expires_on=self.expires_on)
            fs = AzureBlobFileSystem(account_name="onelake", anon=False, credential=credential)
            fs.account_host = "onelake.blob.fabric.microsoft.com"
            fs.do_connect()

            full_path = f"{self.file_system_name}/{self.directory_path}"
            dataset = ds.dataset(full_path, filesystem=fs, format="parquet", partitioning="hive")

            return bool(dataset.schema.names)
        except Exception:
            return False

    def detect_partitions(self):
        """
        Detect partition information for a Parquet dataset in Fabric OneLake.

        Returns:
            dict: A dictionary with status, isPartitioned flag, and partition column metadata.
                  If an error occurs, returns a dictionary with status "error" and the error message.
        """
        try:
            credential = CustomTokenCredential(token=self.token, expires_on=self.expires_on)
            fs = AzureBlobFileSystem(account_name="onelake", anon=False, credential=credential)
            fs.account_host = "onelake.blob.fabric.microsoft.com"
            fs.do_connect()

            full_path = f"{self.file_system_name}/{self.directory_path}"

            parquet_schema = ds.dataset(full_path, filesystem=fs, format="parquet", partitioning=None).schema
            partitioning = ds.dataset(full_path, filesystem=fs, format="parquet", partitioning="hive").partitioning

            partition_columns = []
            if partitioning is not None and hasattr(partitioning, "schema"):
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
