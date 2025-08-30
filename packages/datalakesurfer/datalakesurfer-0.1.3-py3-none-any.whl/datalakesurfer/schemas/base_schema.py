from abc import ABC, abstractmethod
from typing import Dict, List

"""
BaseSchemaRetriever defines the abstract interface for retrieving schema information
from various data sources in Azure Data Lake Storage (ADLS) Gen2 or Microsoft Fabric OneLake.

GCSBaseSchemaRetriever defines the abstract interface for retrieving schema information
from Google Cloud Storage (GCS).

S3BaseSchemaRetriever defines the abstract interface for retrieving schema information
from Amazon S3.

Subclasses should implement the get_schema method to extract and return the schema
of the dataset located at the specified directory.

Azure Attributes:
    account_name (str): The storage account or workspace name.
    file_system_name (str): The file system (container) name.
    directory_path (str): The path to the directory to inspect.
    token (str): The authentication token.
    expires_on (str): The token expiration timestamp.

GCS Attributes:
    service_account_info (dict): GCP service account credentials.
    file_system_name (str): GCS bucket name.
    directory_path (str): Path within the bucket.

S3 Attributes:
    aws_access_key_id (str): AWS access key.
    aws_secret_access_key (str): AWS secret key.
    aws_region (str): AWS region.
    file_system_name (str): S3 bucket name.
    directory_path (str): Path within the bucket.

Methods:
    get_schema(): Abstract method to be implemented by subclasses. Should return
                  the schema as a dictionary mapping table names to lists of column
                  definitions (each as a dict with column name and type).
"""

class BaseSchemaRetriever(ABC):
    def __init__(self, account_name, file_system_name, directory_path, token, expires_on):
        """
        Initialize the schema retriever with connection parameters.

        Args:
            account_name (str): The storage account or workspace name.
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
    def get_schema(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Retrieve the schema information for the dataset.

        Returns:
            Dict[str, List[Dict[str, str]]]: A dictionary mapping table names to lists of
            column definitions (each as a dict with column name and type).
        """
        pass

class GCSBaseSchemaRetriever(ABC):
    def __init__(self, service_account_info, file_system_name, directory_path):
        """
        Initialize the schema retriever with GCS connection parameters.

        Args:
            service_account_info (dict): GCP service account credentials.
            file_system_name (str): GCS bucket name.
            directory_path (str): Path within the bucket.
        """
        self.service_account_info = service_account_info
        self.file_system_name = file_system_name
        self.directory_path = directory_path

    @abstractmethod
    def get_schema(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Retrieve the schema information for the dataset in GCS.

        Returns:
            Dict[str, List[Dict[str, str]]]: A dictionary mapping table names to lists of
            column definitions (each as a dict with column name and type).
        """
        pass

class S3BaseSchemaRetriever(ABC):
    def __init__(self, aws_access_key_id, aws_secret_access_key, aws_region, file_system_name, directory_path):
        """
        Initialize the schema retriever with S3 connection parameters.

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
    def get_schema(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Retrieve the schema information for the dataset in S3.

        Returns:
            Dict[str, List[Dict[str, str]]]: A dictionary mapping table names to lists of
            column definitions (each as a dict with column name and type).
        """
        pass
