from deltalake import DeltaTable
from typing import Dict, List
from datalakesurfer.schemas.base_schema import S3BaseSchemaRetriever
from datalakesurfer.utils.transform_dtype import MapDataType

class S3DeltaSchemaRetriever(S3BaseSchemaRetriever):
    """
    Extracts the schema for a Delta Lake table in S3.
    """
    def get_schema(self) -> Dict[str, List[Dict[str, str]]]:
        try:
            DELTA_PATH = f"{self.file_system_name}/{self.directory_path}"
            storage_options = {
                "AWS_ACCESS_KEY_ID": self.aws_access_key_id,
                "AWS_SECRET_ACCESS_KEY": self.aws_secret_access_key,
                "AWS_REGION": self.aws_region
            }
            arrow_fields = DeltaTable(f"s3://{DELTA_PATH}", storage_options=storage_options).schema().fields
            schema_list = [
                {"column_name": field.name, "dtype": str(field.type.type)}
                for field in arrow_fields
            ]
            schema = MapDataType().fnMapDataType(schema_list=schema_list,sourceType="delta")
            return schema
        except Exception as e:
            return {"status": "error", "message": str(e)}