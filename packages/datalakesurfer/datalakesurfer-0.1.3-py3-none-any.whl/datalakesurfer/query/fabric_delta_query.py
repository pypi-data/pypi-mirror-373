import pyarrow as pa
import duckdb
import pandas as pd
from deltalake import DeltaTable
from datalakesurfer.query.base_query import FabricBaseQueryRetriever

class FabricDeltaQueryRetriever(FabricBaseQueryRetriever):
    """
    Query multiple Delta tables in Microsoft Fabric OneLake.
    """
    def query(self, tables: dict, query: str) -> pd.DataFrame:
        conn = duckdb.connect()
        try:
            for alias, delta_path in tables.items():
                storage_options = {
                    "bearer_token": self.token,
                    "use_fabric_endpoint": "true"
                }
                dt = DeltaTable(
                    f"abfss://{self.file_system_name}@{self.account_name}.dfs.fabric.microsoft.com/{delta_path}",
                    storage_options=storage_options
                )
                arrow_table = dt.to_pyarrow_table()
                conn.register(alias, arrow_table)

            return conn.execute(query).df()

        finally:
            conn.close()