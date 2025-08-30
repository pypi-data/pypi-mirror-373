"""
ParquetSchemaRetriever extracts the schema and partition information for a Parquet dataset in ADLS Gen2.

This class connects to the specified Parquet dataset using the provided ADLS Gen2
connection parameters and retrieves the schema as a list of column definitions. It can also
detect partitioning information for the dataset.

Methods:
    get_schema(): Returns the schema as a list of dictionaries with column names and types.
                  If an error occurs, returns a dictionary with status "error" and the error message.
    detect_partitions(): Returns partitioning metadata for the Parquet dataset, including
                         whether the dataset is partitioned and the partition columns.
"""

from typing import Dict, List
import pyarrow.dataset as ds
import pyarrow.fs
import pyarrowfs_adlgen2
from datalakesurfer.schemas.base_schema import BaseSchemaRetriever
from datalakesurfer.utils.credentials import CustomTokenCredential
from datalakesurfer.utils.transform_dtype import MapDataType

class ParquetSchemaRetriever(BaseSchemaRetriever):
    def get_schema(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Retrieve the schema for the Parquet dataset at the specified directory in ADLS Gen2.

        Returns:
            list[dict]: A list of dictionaries, each containing 'column_name' and 'dtype' keys.
                        If an error occurs, returns a dictionary with status "error" and the error message.
        """
        try:
            credential = CustomTokenCredential(
                token=self.token,
                expires_on=self.expires_on
            )
            handler = pyarrowfs_adlgen2.AccountHandler.from_account_name(self.account_name, credential=credential)
            fs = pyarrow.fs.PyFileSystem(handler)
            dataset = ds.dataset(
                f"{self.file_system_name}/{self.directory_path}",
                filesystem=fs,
                format="parquet",
                partitioning="hive"
            )
            schema_list = [
                {"column_name": field.name, "dtype": str(field.type)}
                for field in dataset.schema
            ]
            if not schema_list:
                return {"status": "error", "message": "The specified directory is empty or does not exist."}
            schema = MapDataType().fnMapDataType(schema_list=schema_list,sourceType="parquet")
            return schema

        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def detect_partitions(self) -> str:
        """
        Detect if the (Parquet) directory on ADLS Gen2 is partitioned. Applies to only PARQUET
        Returns:
            - "isPartitioned": True - if partitioned else False
            - "partitionedColumns": Returns Partitioned Columns, else []
        """
        try:
            isPartitioned = False
            partition_columns = []
            credential = CustomTokenCredential(token=self.token,expires_on=self.expires_on)
            full_path = f"{self.file_system_name}/{self.directory_path}"
            ##Get Partition Columns for Delta and Parquet formats.
            handler = pyarrowfs_adlgen2.AccountHandler.from_account_name(self.account_name, credential=credential)
            fs = pyarrow.fs.PyFileSystem(handler)
            parquet_schema = ds.dataset(full_path, filesystem=fs, format="parquet", partitioning=None).schema
            partitioning = ds.dataset(full_path, filesystem=fs, format="parquet" , partitioning="hive").partitioning
            # Extract the partitioned columns (only if partitioning exists and is valid)
            if partitioning is not None and hasattr(partitioning, 'schema'):
                partition_columns = [{"column_name": col.name, "dtype": str(col.type)} for col in partitioning.schema if col.name not in parquet_schema.names]
                if partition_columns:
                    isPartitioned = True
            return {"status": "success", "isPartitioned": isPartitioned,"partition_columns":partition_columns}
        except Exception as e:
            return {"status": "error", "message": str(e)}