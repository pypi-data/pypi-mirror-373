import gcsfs
import pyarrow.dataset as ds
from typing import Dict, List
from datalakesurfer.schemas.base_schema import GCSBaseSchemaRetriever
from datalakesurfer.utils.transform_dtype import MapDataType

class GCSParquetSchemaRetriever(GCSBaseSchemaRetriever):
    """
    Extracts the schema for a Parquet dataset in GCS.
    """
    def get_schema(self) -> Dict[str, List[Dict[str, str]]]:
        try:
            fs = gcsfs.GCSFileSystem(token=self.service_account_info)
            BUCKET_PATH = f"{self.file_system_name}/{self.directory_path}"
            dataset = ds.dataset(BUCKET_PATH, filesystem=fs, format="parquet", partitioning="hive")
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

    def detect_partitions(self):
        """
        Detect partition information for a Parquet dataset in GCS.

        Returns:
            dict: Partitioning metadata for the Parquet dataset.
        """
        try:
            fs = gcsfs.GCSFileSystem(token=self.service_account_info)
            BUCKET_PATH = f"{self.file_system_name}/{self.directory_path}"
            parquet_schema = ds.dataset(BUCKET_PATH, filesystem=fs, format="parquet", partitioning=None).schema
            partitioning = ds.dataset(BUCKET_PATH, filesystem=fs, format="parquet", partitioning="hive").partitioning

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