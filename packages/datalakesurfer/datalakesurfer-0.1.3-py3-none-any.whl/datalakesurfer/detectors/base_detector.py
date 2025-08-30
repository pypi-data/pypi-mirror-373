"""
BaseFormatDetector defines the abstract interface for all format detectors in the datalakesurfer project.

Each detector should inherit from this class and implement the `detect` method, which determines
if a given directory in ADLS Gen2 matches the specific data format (e.g., Delta, Iceberg, Parquet).

Attributes:
    format_name (str): The name of the format this detector identifies (e.g., "delta", "iceberg", "parquet").

Methods:
    detect(): Abstract method to be implemented by subclasses. Should return True if the directory matches
              the format, otherwise False.
"""

from abc import ABC, abstractmethod

class BaseFormatDetector(ABC):
    format_name: str = None  # e.g., "delta", "iceberg", "parquet"

    def __init__(self, account_name, file_system_name, directory_path, token, expires_on):
        """
        Initialize the detector with ADLS Gen2 connection parameters.

        Args:
            account_name (str): The ADLS Gen2 account name.
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

    @abstractmethod
    def detect(self) -> bool:
        """
        Determine if the directory matches the specific data format.

        Returns:
            bool: True if the directory matches the format, False otherwise.
        """
        pass
