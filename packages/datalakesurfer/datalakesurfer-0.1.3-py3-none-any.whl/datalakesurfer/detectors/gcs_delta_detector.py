import json
import tempfile
import os
from deltalake import DeltaTable
from datalakesurfer.detectors.gcs_base_detector import GCSBaseFormatDetector

class GCSDeltaDetector(GCSBaseFormatDetector):
    format_name = "delta"

    def detect(self) -> bool:
        tmp_path = None
        try:
            # Write service account info to a temp file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp_file:
                json.dump(self.service_account_info, tmp_file)
                tmp_path = tmp_file.name

            DELTA_PATH = f"{self.file_system_name}/{self.directory_path}"
            storage_options = {"GOOGLE_SERVICE_ACCOUNT_PATH": tmp_path}
            DeltaTable(f"gs://{DELTA_PATH}", storage_options=storage_options)
            return True
        except Exception:
            return False
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)