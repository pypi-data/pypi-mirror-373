"""
Defines the ADLSRequest model for validating Azure Data Lake Storage (ADLS) Gen2 connection parameters.

The ADLSRequest model uses Pydantic for data validation and includes custom field validators
to ensure that all required fields are present and correctly formatted.

Attributes:
    account_name (str): Storage account name.
    file_system_name (str): File system (container) name.
    directory_path (str): Directory path within the file system.
    token (str): Access token for authentication.
    expires_on (int): Token expiration timestamp.

Validators:
    - Validates storage account name and file system name using SourceValidators.
    - Ensures required fields are not empty.
    - Validates the expires_on field for correct timestamp.
"""

from pydantic import BaseModel, Field, field_validator
from datalakesurfer.utils.validators import SourceValidators

class ADLSRequest(BaseModel):
    account_name: str = Field(..., description="Storage account name")
    file_system_name: str = Field(..., description="File system name")
    directory_path: str = Field(..., description="Directory path")
    token: str = Field(..., description="Access token")
    expires_on: int = Field(..., description="Token expiration timestamp")

    @field_validator("account_name", mode="before")
    def validate_account_name(cls, value):
        return SourceValidators.validate_storage_account_name(value)

    @field_validator("file_system_name", mode="before")
    def validate_container_name(cls, value):
        return SourceValidators.validate_container_name(value)

    @field_validator("account_name", "file_system_name", "directory_path", "token")
    def check_not_empty(cls, value):
        return SourceValidators.not_empty(value)

    @field_validator("expires_on")
    def check_expires_on(cls, value):
        return SourceValidators.validate_expires_on(value)
