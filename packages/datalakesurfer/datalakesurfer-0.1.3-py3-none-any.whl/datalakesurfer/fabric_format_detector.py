"""
FabricFormatDetector detects the data format (Iceberg, Delta, or Parquet) of a directory in Microsoft Fabric OneLake.

This class uses specialized detector classes for each supported format and provides methods to
identify the format and, if applicable, detect partitioning information for Parquet datasets.

Attributes:
    DETECTORS (list): List of detector classes to use for format detection.

Methods:
    detect_format(): Detects the format of the directory (Iceberg, Delta, or Parquet).
    detect_partitions(): Returns partitioning metadata for Parquet datasets if the format is Parquet.
"""

from datalakesurfer.detectors.fabric_iceberg_detector import FabricIcebergDetector
from datalakesurfer.detectors.fabric_delta_detector import FabricDeltaDetector
from datalakesurfer.detectors.fabric_parquet_detector import FabricParquetDetector

class FabricFormatDetector:
    DETECTORS = [FabricIcebergDetector, FabricDeltaDetector, FabricParquetDetector]

    def __init__(self, account_name, file_system_name, directory_path, token, expires_on):
        """
        Initialize the format detector with Fabric OneLake connection parameters.

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

    def detect_format(self):
        """
        Detect the format of the directory (Iceberg, Delta, or Parquet) on Fabric OneLake.

        Returns:
            dict: A dictionary with status and detected format. If no format is detected,
                  returns "unsupportedFormat".
        """
        for detector_cls in self.DETECTORS:
            detector = detector_cls(
                self.account_name,
                self.file_system_name,
                self.directory_path,
                self.token,
                self.expires_on
            )
            if detector.detect():
                return {"status": "success", "format": detector.format_name}
        return {"status": "success", "format": "unsupportedFormat"}

    def detect_partitions(self):
        """
        Detect partition information for Parquet datasets in Fabric OneLake.
        Only runs if format is parquet.

        Returns:
            dict: Partitioning metadata for the Parquet dataset, or an error message if not Parquet.
        """
        parquet_detector = FabricParquetDetector(
            self.account_name,
            self.file_system_name,
            self.directory_path,
            self.token,
            self.expires_on
        )
        return parquet_detector.detect_partitions()
