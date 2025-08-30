import pyarrow as pa
import duckdb
import pandas as pd
from deltalake import DeltaTable
from datalakesurfer.query.base_query import ADLSBaseQueryRetriever

class ADLSDeltaQueryRetriever(ADLSBaseQueryRetriever):
    """
    Query multiple Delta tables in Azure Data Lake Storage Gen2.
    """
    def query(self, tables: dict, query: str) -> pd.DataFrame:
        conn = duckdb.connect()
        try:
            for alias, delta_path in tables.items():
                storage_options = {
                    "bearer_token": self.token,
                    "use_fabric_endpoint": "false"
                }
                dt = DeltaTable(
                    f"abfss://{self.file_system_name}@{self.account_name}.dfs.core.windows.net/{delta_path}",
                    storage_options=storage_options
                )
                arrow_table = dt.to_pyarrow_table()
                conn.register(alias, arrow_table)
            return conn.execute(query).df()

        finally:
            conn.close()