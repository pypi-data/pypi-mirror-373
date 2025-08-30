import gcsfs
import pyarrow.dataset as ds
from datalakesurfer.detectors.gcs_base_detector import GCSBaseFormatDetector

class GCSParquetDetector(GCSBaseFormatDetector):
    format_name = "parquet"

    def detect(self) -> bool:
        try:
            fs = gcsfs.GCSFileSystem(token=self.service_account_info)
            BUCKET_PATH = f"{self.file_system_name}/{self.directory_path}"
            dataset = ds.dataset(BUCKET_PATH, filesystem=fs, format="parquet", partitioning="hive")
            return bool(dataset.schema.names)
        except Exception:
            return False

    def detect_partitions(self):
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