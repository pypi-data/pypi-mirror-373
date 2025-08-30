import os
from deltalake import DeltaTable
import duckdb
import pyarrow as pa
import pandas as pd
from datalakesurfer.query.base_query import S3BaseQueryRetriever

class S3DeltaQueryRetriever(S3BaseQueryRetriever):
    """
    Query multiple Delta tables in S3 using DuckDB SQL.
    """
    def query(self, tables: dict, query: str) -> pd.DataFrame:
        conn = duckdb.connect()
        try:
            storage_options = {
                "AWS_ACCESS_KEY_ID": self.aws_access_key_id,
                "AWS_SECRET_ACCESS_KEY": self.aws_secret_access_key,
                "AWS_REGION": self.aws_region
            }

            for alias, delta_path in tables.items():
                dt = DeltaTable(f"s3://{delta_path}", storage_options=storage_options)
                arrow_table = dt.to_pyarrow_table()
                conn.register(alias, arrow_table)

            return conn.execute(query).df()

        finally:
            conn.close()