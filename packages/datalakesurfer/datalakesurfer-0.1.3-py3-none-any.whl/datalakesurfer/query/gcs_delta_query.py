import json
import os
import tempfile
from deltalake import DeltaTable
import duckdb
import pyarrow as pa
import pandas as pd
from datalakesurfer.query.base_query import GCSBaseQueryRetriever

class GCSDeltaQueryRetriever(GCSBaseQueryRetriever):
    """
    Query multiple Delta tables in GCS.
    """
    def query(self, tables: dict, query: str) -> pd.DataFrame:
        tmp_path = None
        conn = duckdb.connect()
        try:
            # Save creds to temp file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp_file:
                json.dump(self.service_account_info, tmp_file)
                tmp_path = tmp_file.name

            storage_options = {"GOOGLE_SERVICE_ACCOUNT_PATH": tmp_path}
            for alias, delta_path in tables.items():
                dt = DeltaTable(f"gs://{delta_path}", storage_options=storage_options)
                arrow_table = dt.to_pyarrow_table()
                conn.register(alias, arrow_table)

            # Run the real query
            return conn.execute(query).df()

        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
            conn.close()