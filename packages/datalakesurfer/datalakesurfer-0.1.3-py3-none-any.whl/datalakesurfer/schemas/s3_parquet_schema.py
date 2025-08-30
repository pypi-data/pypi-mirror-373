import s3fs
import pyarrow.dataset as ds
from typing import Dict, List
from datalakesurfer.schemas.base_schema import S3BaseSchemaRetriever
from datalakesurfer.utils.transform_dtype import MapDataType

class S3ParquetSchemaRetriever(S3BaseSchemaRetriever):
    """
    Extracts the schema for a Parquet dataset in S3.
    """
    def get_schema(self) -> Dict[str, List[Dict[str, str]]]:
        try:
            fs = s3fs.S3FileSystem(
                key=self.aws_access_key_id,
                secret=self.aws_secret_access_key
            )
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
        try:
            fs = s3fs.S3FileSystem(
                key=self.aws_access_key_id,
                secret=self.aws_secret_access_key
            )
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