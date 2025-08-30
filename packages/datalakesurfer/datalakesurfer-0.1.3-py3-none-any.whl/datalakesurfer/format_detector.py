"""
FormatDetector detects the data format (Iceberg, Delta, or Parquet) of a directory in Azure Data Lake Storage (ADLS) Gen2.

This class uses specialized detector classes for each supported format and provides methods to
identify the format and, if applicable, detect partitioning information for Parquet datasets.

Attributes:
    DETECTORS (list): List of detector classes to use for format detection.

Methods:
    detect_format(): Detects the format of the directory (Iceberg, Delta, or Parquet).
    detect_partitions(): Returns partitioning metadata for Parquet datasets if the format is Parquet.
"""

from datalakesurfer.models.adls_models import ADLSRequest
from datalakesurfer.detectors.iceberg_detector import IcebergDetector
from datalakesurfer.detectors.delta_detector import DeltaDetector
from datalakesurfer.detectors.parquet_detector import ParquetDetector


class FormatDetector:
    DETECTORS = [IcebergDetector, DeltaDetector, ParquetDetector]

    def __init__(self, **kwargs):
        """
        Initialize the format detector with ADLS Gen2 connection parameters.

        Args:
            account_name (str): The ADLS Gen2 account name.
            file_system_name (str): The file system (container) name.
            directory_path (str): The path to the directory to inspect.
            token (str): The authentication token.
            expires_on (str): The token expiration timestamp.
        """
        # Validate incoming parameters using ADLSRequest model
        validated = ADLSRequest(**kwargs)
        self.account_name = validated.account_name
        self.file_system_name = validated.file_system_name
        self.directory_path = validated.directory_path
        self.token = validated.token
        self.expires_on = validated.expires_on

    def detect_format(self):
        """
        Detect the format of the directory (Iceberg, Delta, or Parquet) on ADLS Gen2.

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
        Detect partition information for Parquet datasets in ADLS Gen2.
        Only runs if format is parquet.

        Returns:
            dict: Partitioning metadata for the Parquet dataset.
        """
        parquet_detector = ParquetDetector(
            self.account_name,
            self.file_system_name,
            self.directory_path,
            self.token,
            self.expires_on
        )
        return parquet_detector.detect_partitions()