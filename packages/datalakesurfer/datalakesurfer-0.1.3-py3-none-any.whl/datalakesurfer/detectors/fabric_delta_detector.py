"""
FabricDeltaDetector implements the detection logic for Delta Lake tables in Microsoft Fabric OneLake.

This detector attempts to instantiate a DeltaTable using the provided Fabric OneLake
connection parameters. If successful, it identifies the directory as a Delta Lake table.

Attributes:
    format_name (str): The name of the format this detector identifies ("delta").

Methods:
    detect(): Returns True if the directory is a Delta Lake table in Fabric OneLake, otherwise False.
"""

from deltalake import DeltaTable
from datalakesurfer.utils.credentials import CustomTokenCredential


class FabricDeltaDetector:
    format_name = "delta"

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
        Attempt to instantiate a DeltaTable at the specified Fabric OneLake directory.

        Returns:
            bool: True if the directory is a Delta Lake table in Fabric OneLake, False otherwise.
        """
        try:
            storage_options = {"bearer_token": self.token, "use_fabric_endpoint": "true"}
            DeltaTable(
                f"abfss://{self.file_system_name}@{self.account_name}.dfs.fabric.microsoft.com/{self.directory_path}",
                storage_options=storage_options
            )
            return True
        except Exception:
            return False
