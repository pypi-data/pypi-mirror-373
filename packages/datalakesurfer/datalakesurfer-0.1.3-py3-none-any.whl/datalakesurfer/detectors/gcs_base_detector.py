"""
GCSBaseFormatDetector defines the abstract interface for all GCS format detectors.

Attributes:
    service_account_info (dict): GCP service account credentials as a dict.
    file_system_name (str): GCS bucket name.
    directory_path (str): Path within the bucket.

Methods:
    detect(): Abstract method to be implemented by subclasses.
"""

from abc import ABC, abstractmethod

class GCSBaseFormatDetector(ABC):
    format_name: str = None  # e.g., "delta", "iceberg", "parquet"

    def __init__(self, service_account_info, file_system_name, directory_path):
        """
        Initialize the detector with GCS connection parameters.

        Args:
            service_account_info (dict): GCP service account credentials.
            file_system_name (str): GCS bucket name.
            directory_path (str): Path within the bucket.
        """
        self.service_account_info = service_account_info
        self.file_system_name = file_system_name
        self.directory_path = directory_path

    @abstractmethod
    def detect(self) -> bool:
        pass