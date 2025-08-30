"""
Defines the GCSRequest model for validating Google Cloud Storage (GCS) connection parameters.

The GCSRequest model uses Pydantic for data validation and includes custom field validators
to ensure that all required fields are present and correctly formatted.

Attributes:
    service_account_info (dict): GCP service account credentials as a dictionary.
    file_system_name (str): GCS bucket name.
    directory_path (str): Directory path within the bucket.

Validators:
    - Ensures required fields are not empty.
    - Validates the service account info for required keys.
"""

from pydantic import BaseModel, Field, field_validator

class GCSRequest(BaseModel):
    service_account_info: dict = Field(..., description="GCP service account credentials as a dictionary")
    file_system_name: str = Field(..., description="GCS bucket name")
    directory_path: str = Field(..., description="Directory path within the bucket")

    @field_validator("service_account_info")
    def validate_service_account_info(cls, value):
        # Basic check for required keys in service account dict
        required_keys = {"type", "project_id", "private_key_id", "private_key", "client_email"}
        if not isinstance(value, dict):
            raise ValueError("service_account_info must be a dictionary")
        missing = required_keys - set(value.keys())
        if missing:
            raise ValueError(f"Missing required service account keys: {missing}")
        return value

    @field_validator("file_system_name", "directory_path")
    def check_not_empty(cls, value):
        if not value or not str(value).strip():
            raise ValueError("Field must not be empty")
        return value