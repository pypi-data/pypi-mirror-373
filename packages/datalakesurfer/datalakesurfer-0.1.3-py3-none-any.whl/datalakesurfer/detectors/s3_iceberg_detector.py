import s3fs
import duckdb
from datalakesurfer.detectors.s3_base_detector import S3BaseFormatDetector

class S3IcebergDetector(S3BaseFormatDetector):
    format_name = "iceberg"

    def detect(self) -> bool:
        try:
            fs = s3fs.S3FileSystem(
                key=self.aws_access_key_id,
                secret=self.aws_secret_access_key
            )
            bucket_path = f"{self.file_system_name}/{self.directory_path}"
            conn = duckdb.connect()
            try:
                conn.register_filesystem(fs)
                conn.sql("INSTALL iceberg; LOAD iceberg;")
                conn.sql(
                    f"DESCRIBE (SELECT * FROM iceberg_scan('s3://{bucket_path}', allow_moved_paths=true) LIMIT 1)"
                ).fetchall()
                return True
            finally:
                conn.close()
        except Exception:
            return False