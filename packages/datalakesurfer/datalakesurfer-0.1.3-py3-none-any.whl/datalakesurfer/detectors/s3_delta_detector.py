from deltalake import DeltaTable
from datalakesurfer.detectors.s3_base_detector import S3BaseFormatDetector

class S3DeltaDetector(S3BaseFormatDetector):
    format_name = "delta"

    def detect(self) -> bool:
        try:
            DELTA_PATH = f"{self.file_system_name}/{self.directory_path}"
            storage_options = {
                "AWS_ACCESS_KEY_ID": self.aws_access_key_id,
                "AWS_SECRET_ACCESS_KEY": self.aws_secret_access_key,
                "AWS_REGION": self.aws_region
            }
            DeltaTable(f"s3://{DELTA_PATH}", storage_options=storage_options)
            return True
        except Exception:
            return False