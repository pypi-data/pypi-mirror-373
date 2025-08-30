import json
import tempfile
import os
from deltalake import DeltaTable
from typing import Dict, List
from datalakesurfer.schemas.base_schema import GCSBaseSchemaRetriever
from datalakesurfer.utils.transform_dtype import MapDataType

class GCSDeltaSchemaRetriever(GCSBaseSchemaRetriever):
    """
    Extracts the schema for a Delta Lake table in GCS.
    """
    def get_schema(self) -> Dict[str, List[Dict[str, str]]]:
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp_file:
                json.dump(self.service_account_info, tmp_file)
                tmp_path = tmp_file.name

            DELTA_PATH = f"{self.file_system_name}/{self.directory_path}"
            storage_options = {"GOOGLE_SERVICE_ACCOUNT_PATH": tmp_path}
            arrow_fields = DeltaTable(f"gs://{DELTA_PATH}", storage_options=storage_options).schema().fields

            schema_list = [
                {"column_name": field.name, "dtype": str(field.type.type)}
                for field in arrow_fields
            ]
            schema = MapDataType().fnMapDataType(schema_list=schema_list,sourceType="delta")
            return schema
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)