from typing import Dict, List
from deltalake import DeltaTable
from datalakesurfer.schemas.base_schema import BaseSchemaRetriever
from datalakesurfer.utils.transform_dtype import MapDataType

class FabricDeltaSchemaRetriever(BaseSchemaRetriever):
    """
    FabricDeltaSchemaRetriever extracts the schema for a Delta Lake table in Microsoft Fabric OneLake.

    This class connects to the specified Delta Lake table using the provided Fabric OneLake
    connection parameters and retrieves the schema as a list of column definitions.

    Methods:
        get_schema(): Returns the schema as a list of dictionaries with column names and types.
                      If an error occurs, returns a dictionary with status "error" and the error message.
    """
    def get_schema(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Retrieve the schema for the Delta Lake table at the specified directory in Fabric OneLake.

        Returns:
            list[dict]: A list of dictionaries, each containing 'column_name' and 'dtype' keys.
                        If an error occurs, returns a dictionary with status "error" and the error message.
        """
        try:
            storage_options = {
                "bearer_token": self.token,
                "use_fabric_endpoint": "true"
            }
            arrow_fields = DeltaTable(
                f"abfss://{self.file_system_name}@{self.account_name}.dfs.fabric.microsoft.com/{self.directory_path}",
                storage_options=storage_options
            ).schema().fields

            schema_list = [
                {"column_name": field.name, "dtype": str(field.type.type)}
                for field in arrow_fields
            ]
            schema = MapDataType().fnMapDataType(schema_list=schema_list,sourceType="delta")
            return schema
        except Exception as e:
            return {"status": "error", "message": str(e)}
