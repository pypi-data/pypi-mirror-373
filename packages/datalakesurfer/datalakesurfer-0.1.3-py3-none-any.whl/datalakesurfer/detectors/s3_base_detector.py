"""
S3BaseFormatDetector defines the abstract interface for all S3 format detectors.

Attributes:
    aws_access_key_id (str): AWS access key.
    aws_secret_access_key (str): AWS secret key.
    aws_region (str): AWS region.
    file_system_name (str): S3 bucket name.
    directory_path (str): Path within the bucket.

Methods:
    detect(): Abstract method to be implemented by subclasses.
"""

from abc import ABC, abstractmethod

class S3BaseFormatDetector(ABC):
    format_name: str = None  # e.g., "delta", "iceberg", "parquet"

    def __init__(self, aws_access_key_id, aws_secret_access_key, aws_region, file_system_name, directory_path):
        """
        Initialize the detector with S3 connection parameters.

        Args:
            aws_access_key_id (str): AWS access key.
            aws_secret_access_key (str): AWS secret key.
            aws_region (str): AWS region.
            file_system_name (str): S3 bucket name.
            directory_path (str): Path within the bucket.
        """
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_region = aws_region
        self.file_system_name = file_system_name
        self.directory_path = directory_path

    @abstractmethod
    def detect(self) -> bool:
        pass