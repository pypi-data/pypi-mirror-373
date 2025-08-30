"""
DeltaDetector implements the detection logic for Delta Lake tables in ADLS Gen2.

This detector attempts to instantiate a DeltaTable using the provided ADLS Gen2
connection parameters. If successful, it identifies the directory as a Delta Lake table.

Attributes:
    format_name (str): The name of the format this detector identifies ("delta").

Methods:
    detect(): Returns True if the directory is a Delta Lake table, otherwise False.
"""

from deltalake import DeltaTable
from datalakesurfer.detectors.base_detector import BaseFormatDetector

class DeltaDetector(BaseFormatDetector):
    format_name = "delta"

    def detect(self) -> bool:
        """
        Attempt to instantiate a DeltaTable at the specified ADLS Gen2 directory.

        Returns:
            bool: True if the directory is a Delta Lake table, False otherwise.
        """
        try:
            storage_options = {"bearer_token": self.token, "use_fabric_endpoint": "false"}
            DeltaTable(
                f"abfss://{self.file_system_name}@{self.account_name}.dfs.core.windows.net/{self.directory_path}",
                storage_options=storage_options
            )
            return True
        except Exception:
            return False
