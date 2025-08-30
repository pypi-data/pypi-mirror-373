import gcsfs
import duckdb
from typing import Dict, List
from datalakesurfer.schemas.base_schema import GCSBaseSchemaRetriever
from datalakesurfer.utils.transform_dtype import MapDataType

class GCSIcebergSchemaRetriever(GCSBaseSchemaRetriever):
    """
    Extracts the schema for an Iceberg table in GCS.
    """
    def get_schema(self) -> Dict[str, List[Dict[str, str]]]:
        try:
            fs = gcsfs.GCSFileSystem(token=self.service_account_info)
            bucket_path = f"{self.file_system_name}/{self.directory_path}"
            conn = duckdb.connect()
            try:
                conn.register_filesystem(fs)
                conn.sql("INSTALL iceberg; LOAD iceberg;")
                schema_result = conn.sql(
                    f"DESCRIBE (SELECT * FROM iceberg_scan('gs://{bucket_path}', allow_moved_paths=true) LIMIT 1)"
                ).fetchall()
                schema_list = [
                    {
                        "column_name": schema[0],
                        "dtype": "TIMESTAMP" if schema[1] == "TIMESTAMP WITH TIME ZONE" else schema[1]
                    }
                    for schema in schema_result
                ]
                schema = MapDataType().fnMapDataType(schema_list=schema_list,sourceType="iceberg")
                return schema
            finally:
                conn.close()
        except Exception as e:
            return {"status": "error", "message": str(e)}