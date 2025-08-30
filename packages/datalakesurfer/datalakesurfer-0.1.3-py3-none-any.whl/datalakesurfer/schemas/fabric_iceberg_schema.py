"""
FabricIcebergSchemaRetriever extracts the schema for an Iceberg table in Microsoft Fabric OneLake.

This class connects to the specified Iceberg table using the provided Fabric OneLake
connection parameters and retrieves the schema as a list of column definitions.

Methods:
    get_schema(): Returns the schema as a list of dictionaries with column names and types.
                  If an error occurs, returns a dictionary with status "error" and the error message.
"""

from typing import Dict, List
import duckdb
from adlfs import AzureBlobFileSystem
from datalakesurfer.schemas.base_schema import BaseSchemaRetriever
from datalakesurfer.utils.credentials import CustomTokenCredential
from datalakesurfer.utils.transform_dtype import MapDataType

class FabricIcebergSchemaRetriever(BaseSchemaRetriever):
    """
    Retrieves the schema for an Iceberg table in Microsoft Fabric OneLake.
    """
    def get_schema(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Retrieve the schema for the Iceberg table at the specified directory in Fabric OneLake.

        Returns:
            list[dict]: A list of dictionaries, each containing 'column_name' and 'dtype' keys.
                        If an error occurs, returns a dictionary with status "error" and the error message.
        """
        try:
            credential = CustomTokenCredential(self.token, self.expires_on)
            fs = AzureBlobFileSystem(account_name="onelake", anon=False, credential=credential)
            fs.account_host = "onelake.blob.fabric.microsoft.com"
            fs.do_connect()
            conn = duckdb.connect()
            try:
                conn.register_filesystem(fs)
                conn.sql("INSTALL iceberg; LOAD iceberg;")
                schema_result = conn.sql(
                    f"DESCRIBE (SELECT * FROM iceberg_scan('abfs://{self.file_system_name}@{self.account_name}.dfs.fabric.microsoft.com/{self.directory_path}', allow_moved_paths=true) LIMIT 1)"
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
