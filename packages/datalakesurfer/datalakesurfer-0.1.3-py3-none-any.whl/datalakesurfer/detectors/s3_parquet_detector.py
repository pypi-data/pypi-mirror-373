import s3fs
import pyarrow.dataset as ds
from datalakesurfer.detectors.s3_base_detector import S3BaseFormatDetector

class S3ParquetDetector(S3BaseFormatDetector):
    format_name = "parquet"

    def detect(self) -> bool:
        try:
            fs = s3fs.S3FileSystem(
                key=self.aws_access_key_id,
                secret=self.aws_secret_access_key
            )
            BUCKET_PATH = f"{self.file_system_name}/{self.directory_path}"
            dataset = ds.dataset(BUCKET_PATH, filesystem=fs, format="parquet", partitioning="hive")
            return bool(dataset.schema.names)
        except Exception:
            return False

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