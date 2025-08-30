"""
GCSFormatDetector detects the data format (Iceberg, Delta, or Parquet) of a directory in Google Cloud Storage (GCS).

This class uses specialized detector classes for each supported format and provides methods to
identify the format and, if applicable, detect partitioning information for Parquet datasets.

Attributes:
    DETECTORS (list): List of detector classes to use for format detection.

Methods:
    detect_format(): Detects the format of the directory (Iceberg, Delta, or Parquet).
    detect_partitions(): Returns partitioning metadata for Parquet datasets if the format is Parquet.
"""

from datalakesurfer.models.gcs_models import GCSRequest
from datalakesurfer.detectors.gcs_iceberg_detector import GCSIcebergDetector
from datalakesurfer.detectors.gcs_delta_detector import GCSDeltaDetector
from datalakesurfer.detectors.gcs_parquet_detector import GCSParquetDetector

class GCSFormatDetector:
    DETECTORS = [GCSIcebergDetector, GCSDeltaDetector, GCSParquetDetector]

    def __init__(self, **kwargs):
        """
        Initialize the format detector with GCS connection parameters.

        Args:
            service_account_info (dict): GCP service account credentials.
            file_system_name (str): GCS bucket name.
            directory_path (str): Path within the bucket.
        """
        validated = GCSRequest(**kwargs)
        self.service_account_info = validated.service_account_info
        self.file_system_name = validated.file_system_name
        self.directory_path = validated.directory_path

    def detect_format(self):
        """
        Detect the format of the directory (Iceberg, Delta, or Parquet) on GCS.

        Returns:
            dict: A dictionary with status and detected format. If no format is detected,
                  returns "unsupportedFormat".
        """
        for detector_cls in self.DETECTORS:
            detector = detector_cls(
                self.service_account_info,
                self.file_system_name,
                self.directory_path
            )
            if detector.detect():
                return {"status": "success", "format": detector.format_name}
        return {"status": "success", "format": "unsupportedFormat"}

    def detect_partitions(self):
        """
        Detect partition information for Parquet datasets in GCS.
        Only runs if format is parquet.

        Returns:
            dict: Partitioning metadata for the Parquet dataset.
        """
        parquet_detector = GCSParquetDetector(
            self.service_account_info,
            self.file_system_name,
            self.directory_path
        )
        return parquet_detector.detect_partitions()