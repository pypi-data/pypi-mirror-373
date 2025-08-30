from abc import ABC, abstractmethod
from typing import Any

class GCSBaseQueryRetriever(ABC):
    def __init__(self, service_account_info: dict):
        self.service_account_info = service_account_info

    @abstractmethod
    def query(self, tables: dict, query: str, **kwargs) -> Any:
        """
        Run a SQL query across multiple tables in GCS.
        Args:
            tables (dict): Mapping of {table_name: delta_path} example tables = {"sales": "storagebucket0001/SalesOrder","customers": "storagebucket0001/Customer"}.
            query (str): SQL query string referencing those table names, example SELECT s.ProductName, SUM(s.SalesAmount) FROM sales s JOIN customers c ON s.CustomerID = c.CustomerID GROUP BY s.ProductName
        Returns:
            Query result (e.g., Pandas DataFrame).
        """
        pass

class S3BaseQueryRetriever(ABC):
    def __init__(self, aws_access_key_id: str, aws_secret_access_key: str, aws_region: str):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_region = aws_region

    @abstractmethod
    def query(self, tables: dict, query: str, **kwargs) -> Any:
        """
        Run a SQL query across multiple tables in S3.
        Args:
            tables (dict): Mapping of {table_name: delta_path} example tables = {"sales": "storagebucket0001/SalesOrder","customers": "storagebucket0001/Customer"}.
            query (str): SQL query string referencing those table names, example SELECT s.ProductName, SUM(s.SalesAmount) FROM sales s JOIN customers c ON s.CustomerID = c.CustomerID GROUP BY s.ProductName
        Returns:
            Query result (e.g., Pandas DataFrame).
        """
        pass

class ADLSBaseQueryRetriever(ABC):
    def __init__(self, account_name: str, file_system_name: str, token: str, expires_on: int):
        self.account_name = account_name
        self.file_system_name = file_system_name
        self.token = token
        self.expires_on = expires_on

    @abstractmethod
    def query(self, tables: dict, query: str, **kwargs) -> Any:
        """
        Run a SQL query across multiple tables in ADLS Gen2.
        Args:
            tables (dict): Mapping of {table_name: delta_path} example tables = {"sales": "<RootFolderAfterContainerName>/SalesOrder","customers": "<RootFolderAfterContainerName>/Customer"}.
            query (str): SQL query string referencing those table names, example SELECT s.ProductName, SUM(s.SalesAmount) FROM sales s JOIN customers c ON s.CustomerID = c.CustomerID GROUP BY s.ProductName
        Returns:
            Query result (e.g., Pandas DataFrame).
        """
        pass

class FabricBaseQueryRetriever(ABC):
    def __init__(self, account_name: str, file_system_name: str, token: str, expires_on: int):
        self.account_name = account_name
        self.file_system_name = file_system_name
        self.token = token
        self.expires_on = expires_on

    @abstractmethod
    def query(self, tables: dict, query: str, **kwargs) -> Any:
        """
        Run a SQL query across multiple tables in Microsoft Fabric Lakehouse.
        Args:
            tables (dict): Mapping of {table_name: delta_path} example tables = {"sales": "<RootFolderAfterContainerName>/SalesOrder","customers": "<RootFolderAfterContainerName>/Customer"}.
            query (str): SQL query string referencing those table names, example SELECT s.ProductName, SUM(s.SalesAmount) FROM sales s JOIN customers c ON s.CustomerID = c.CustomerID GROUP BY s.ProductName
        Returns:
            Query result (e.g., Pandas DataFrame).
        """
        pass