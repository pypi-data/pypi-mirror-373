"""
Defines the S3Request model for validating Amazon S3 connection parameters.

The S3Request model uses Pydantic for data validation and includes custom field validators
to ensure that all required fields are present and correctly formatted.

Attributes:
    aws_access_key_id (str): AWS access key.
    aws_secret_access_key (str): AWS secret key.
    aws_region (str): AWS region.
    file_system_name (str): S3 bucket name.
    directory_path (str): Directory path within the bucket.

Validators:
    - Ensures required fields are not empty.
"""

from pydantic import BaseModel, Field, field_validator

class S3Request(BaseModel):
    aws_access_key_id: str = Field(..., description="AWS access key")
    aws_secret_access_key: str = Field(..., description="AWS secret key")
    aws_region: str = Field(..., description="AWS region")
    file_system_name: str = Field(..., description="S3 bucket name")
    directory_path: str = Field(..., description="Directory path within the bucket")

    @field_validator("aws_access_key_id", "aws_secret_access_key", "aws_region", "file_system_name", "directory_path")
    def check_not_empty(cls, value):
        if not value or not str(value).strip():
            raise ValueError("Field must not be empty")
        return value