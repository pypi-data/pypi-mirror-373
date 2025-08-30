"""
IcebergDetector implements the detection logic for Iceberg tables in ADLS Gen2.

This detector attempts to connect to the specified directory in ADLS Gen2 using DuckDB and the
Iceberg extension. If it can successfully describe the table, it identifies the directory as an Iceberg table.

Attributes:
    format_name (str): The name of the format this detector identifies ("iceberg").

Methods:
    detect(): Returns True if the directory is an Iceberg table in ADLS Gen2, otherwise False.
"""

import duckdb
from fsspec import filesystem
from datalakesurfer.detectors.base_detector import BaseFormatDetector
from datalakesurfer.utils.credentials import CustomTokenCredential

class IcebergDetector(BaseFormatDetector):
    format_name = "iceberg"

    def detect(self) -> bool:
        """
        Attempt to determine if the given path is an Iceberg table in ADLS Gen2.

        Returns:
            bool: True if the directory is an Iceberg table in ADLS Gen2, False otherwise.
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
                conn.sql(
                    f"DESCRIBE (SELECT * FROM iceberg_scan('abfs://{self.file_system_name}@{self.account_name}.dfs.core.windows.net/{self.directory_path}', allow_moved_paths=true) LIMIT 1)"
                ).fetchall()
                return True
            finally:
                conn.unregister_filesystem("abfs")
                conn.close()
        except Exception:
            return False
