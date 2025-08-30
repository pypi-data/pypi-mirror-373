"""
FabricIcebergDetector implements the detection logic for Iceberg tables in Microsoft Fabric OneLake.

This detector attempts to connect to the specified directory in Fabric OneLake using DuckDB and the
Iceberg extension. If it can successfully describe the table, it identifies the directory as an Iceberg table.

Attributes:
    format_name (str): The name of the format this detector identifies ("iceberg").

Methods:
    detect(): Returns True if the directory is an Iceberg table in Fabric OneLake, otherwise False.
"""

import duckdb
from adlfs import AzureBlobFileSystem
from datalakesurfer.utils.credentials import CustomTokenCredential


class FabricIcebergDetector:
    format_name = "iceberg"

    def __init__(self, account_name, file_system_name, directory_path, token, expires_on):
        """
        Initialize the detector with Fabric OneLake connection parameters.

        Args:
            account_name (str): The Fabric OneLake account name.
            file_system_name (str): The file system (container) name.
            directory_path (str): The path to the directory to inspect.
            token (str): The authentication token.
            expires_on (str): The token expiration timestamp.
        """
        self.account_name = account_name
        self.file_system_name = file_system_name
        self.directory_path = directory_path
        self.token = token
        self.expires_on = expires_on

    def detect(self) -> bool:
        """
        Attempt to determine if the given path is an Iceberg table in Fabric OneLake.

        Returns:
            bool: True if the directory is an Iceberg table in Fabric OneLake, False otherwise.
        """
        try:
            credential = CustomTokenCredential(token=self.token, expires_on=self.expires_on)
            fs = AzureBlobFileSystem(account_name="onelake", anon=False, credential=credential)
            fs.account_host = "onelake.blob.fabric.microsoft.com"
            fs.do_connect()

            conn = duckdb.connect()
            try:
                conn.register_filesystem(fs)
                conn.sql("INSTALL iceberg; LOAD iceberg;")
                conn.sql(
                    f"DESCRIBE (SELECT * FROM iceberg_scan("
                    f"'abfs://{self.file_system_name}@{self.account_name}.dfs.fabric.microsoft.com/{self.directory_path}', "
                    f"allow_moved_paths=true) LIMIT 1)"
                ).fetchall()
                conn.unregister_filesystem(name="abfs")
                return True
            except Exception:
                return False
            finally:
                conn.close()
        except Exception:
            return False
