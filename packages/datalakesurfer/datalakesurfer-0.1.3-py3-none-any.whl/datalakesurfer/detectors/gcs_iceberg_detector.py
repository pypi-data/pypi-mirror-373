import gcsfs
import duckdb
from datalakesurfer.detectors.gcs_base_detector import GCSBaseFormatDetector

class GCSIcebergDetector(GCSBaseFormatDetector):
    format_name = "iceberg"

    def detect(self) -> bool:
        try:
            fs = gcsfs.GCSFileSystem(token=self.service_account_info)
            bucket_path = f"{self.file_system_name}/{self.directory_path}"
            conn = duckdb.connect()
            try:
                conn.register_filesystem(fs)
                conn.sql("INSTALL iceberg; LOAD iceberg;")
                conn.sql(
                    f"DESCRIBE (SELECT * FROM iceberg_scan('gs://{bucket_path}', allow_moved_paths=true) LIMIT 1)"
                ).fetchall()
                return True
            finally:
                conn.close()
        except Exception:
            return False