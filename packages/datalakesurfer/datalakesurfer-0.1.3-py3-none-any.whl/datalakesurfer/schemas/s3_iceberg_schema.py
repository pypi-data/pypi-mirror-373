import s3fs
import duckdb
from typing import Dict, List
from datalakesurfer.schemas.base_schema import S3BaseSchemaRetriever
from datalakesurfer.utils.transform_dtype import MapDataType

class S3IcebergSchemaRetriever(S3BaseSchemaRetriever):
    """
    Extracts the schema for an Iceberg table in S3.
    """
    def get_schema(self) -> Dict[str, List[Dict[str, str]]]:
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
                schema_result = conn.sql(
                    f"DESCRIBE (SELECT * FROM iceberg_scan('s3://{bucket_path}', allow_moved_paths=true) LIMIT 1)"
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