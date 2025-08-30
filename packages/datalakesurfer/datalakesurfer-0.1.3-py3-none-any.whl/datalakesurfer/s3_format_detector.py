"""
S3FormatDetector detects the data format (Iceberg, Delta, or Parquet) of a directory in Amazon S3.

This class uses specialized detector classes for each supported format and provides methods to
identify the format and, if applicable, detect partitioning information for Parquet datasets.

Attributes:
    DETECTORS (list): List of detector classes to use for format detection.

Methods:
    detect_format(): Detects the format of the directory (Iceberg, Delta, or Parquet).
    detect_partitions(): Returns partitioning metadata for Parquet datasets if the format is Parquet.
"""
from datalakesurfer.models.s3_models import S3Request
from datalakesurfer.detectors.s3_iceberg_detector import S3IcebergDetector
from datalakesurfer.detectors.s3_delta_detector import S3DeltaDetector
from datalakesurfer.detectors.s3_parquet_detector import S3ParquetDetector

class S3FormatDetector:
    DETECTORS = [S3IcebergDetector, S3DeltaDetector, S3ParquetDetector]

    def __init__(self, **kwargs):
        """
        Initialize the format detector with S3 connection parameters.

        Args:
            aws_access_key_id (str): AWS access key.
            aws_secret_access_key (str): AWS secret key.
            aws_region (str): AWS region.
            file_system_name (str): S3 bucket name.
            directory_path (str): Path within the bucket.
        """
        validated = S3Request(**kwargs)
        self.aws_access_key_id = validated.aws_access_key_id
        self.aws_secret_access_key = validated.aws_secret_access_key
        self.aws_region = validated.aws_region
        self.file_system_name = validated.file_system_name
        self.directory_path = validated.directory_path

    def detect_format(self):
        """
        Detect the format of the directory (Iceberg, Delta, or Parquet) on S3.

        Returns:
            dict: A dictionary with status and detected format. If no format is detected,
                  returns "unsupportedFormat".
        """
        for detector_cls in self.DETECTORS:
            detector = detector_cls(
                self.aws_access_key_id,
                self.aws_secret_access_key,
                self.aws_region,
                self.file_system_name,
                self.directory_path
            )
            if detector.detect():
                return {"status": "success", "format": detector.format_name}
        return {"status": "success", "format": "unsupportedFormat"}

    def detect_partitions(self):
        """
        Detect partition information for Parquet datasets in S3.
        Only runs if format is parquet.

        Returns:
            dict: Partitioning metadata for the Parquet dataset.
        """
        parquet_detector = S3ParquetDetector(
            self.aws_access_key_id,
            self.aws_secret_access_key,
            self.aws_region,
            self.file_system_name,
            self.directory_path
        )
        return parquet_detector.detect_partitions()