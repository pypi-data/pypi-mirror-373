from typing import Dict, List
import duckdb
from fsspec import filesystem
from datalakesurfer.schemas.base_schema import BaseSchemaRetriever
from datalakesurfer.utils.credentials import CustomTokenCredential
from datalakesurfer.utils.transform_dtype import MapDataType

class IcebergSchemaRetriever(BaseSchemaRetriever):
    """
    IcebergSchemaRetriever extracts the schema for an Iceberg table in ADLS Gen2.

    This class connects to the specified Iceberg table using the provided ADLS Gen2
    connection parameters and retrieves the schema as a list of column definitions.

    Methods:
        get_schema(): Returns the schema as a list of dictionaries with column names and types.
                      If an error occurs, returns a dictionary with status "error" and the error message.
    """
    def get_schema(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Retrieve the schema for the Iceberg table at the specified directory in ADLS Gen2.

        Returns:
            list[dict]: A list of dictionaries, each containing 'column_name' and 'dtype' keys.
                        If an error occurs, returns a dictionary with status "error" and the error message.
        """
        try:
            credential = CustomTokenCredential(
                token=self.token,
                expires_on=self.expires_on
            )
            fs = filesystem("abfs", account_name=self.account_name, credential=credential)
            conn = duckdb.connect()
            try:
                conn.register_filesystem(fs)
                conn.sql("INSTALL iceberg; LOAD iceberg;")
                result = conn.sql(
                    f"""
                    DESCRIBE (
                        SELECT * FROM iceberg_scan(
                            'abfs://{self.file_system_name}@{self.account_name}.dfs.core.windows.net/{self.directory_path}',
                            allow_moved_paths=true
                        ) LIMIT 1
                    )
                    """
                ).fetchall()
                schema_list = [
                    {"column_name": col[0], "dtype": col[1]}
                    for col in result
                ]
                schema = MapDataType().fnMapDataType(schema_list=schema_list,sourceType="iceberg")
                return schema

            finally:
                conn.unregister_filesystem("abfs")
                conn.close()

        except Exception as e:
            return {"status": "error", "message": str(e)}
