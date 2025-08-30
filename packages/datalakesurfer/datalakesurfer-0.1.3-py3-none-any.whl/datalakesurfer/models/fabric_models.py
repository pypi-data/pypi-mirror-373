"""
Defines the FabricRequest model for validating Microsoft Fabric OneLake connection parameters.

The FabricRequest model uses Pydantic for data validation and includes custom field validators
to ensure that all required fields are present and correctly formatted.

Attributes:
    file_system_name (str): Fabric workspace container name.
    directory_path (str): Directory path in Fabric OneLake.
    token (str): Access token for authentication.
    expires_on (int): Token expiration timestamp.

Validators:
    - Validates the file system (container) name using SourceValidators.
    - Ensures required fields are not empty.
    - Validates the expires_on field for correct timestamp.
"""

from pydantic import BaseModel, Field, field_validator
from datalakesurfer.utils.validators import SourceValidators

class FabricRequest(BaseModel):
    file_system_name: str = Field(..., description="Fabric workspace container name")
    directory_path: str = Field(..., description="Directory path in Fabric OneLake")
    token: str = Field(..., description="Access token")
    expires_on: int = Field(..., description="Token expiration timestamp")

    @field_validator("file_system_name", mode="before")
    def validate_container_name(cls, value):
        return SourceValidators.validate_container_name(value)

    @field_validator("file_system_name", "directory_path", "token")
    def check_not_empty(cls, value):
        return SourceValidators.not_empty(value)

    @field_validator("expires_on")
    def check_expires_on(cls, value):
        return SourceValidators.validate_expires_on(value)
